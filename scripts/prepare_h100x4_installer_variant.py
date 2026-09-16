#!/usr/bin/env python3
"""Prepare a fail-closed, local-only H100x4 installer review variant.

This utility never executes, imports, or otherwise evaluates the installer.  It only
reads bytes from one explicitly named regular file, verifies its pinned digest, and
performs one exact byte-for-byte replacement.  The resulting file is intentionally a
local review artifact: it is not an upstream installer, a publication mechanism, or
an installation command.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any


PINNED_SOURCE_SHA256 = "6b00488ccf837ed6b7b5375270b75db284c3906f6aec832ad9c8573f44eaac6c"

# These byte strings are deliberately exact.  Do not loosen them into a regexp: a
# changed upstream block must be rejected rather than guessed at or partially changed.
OLD_BLOCK = b'''        if machine_id and send_mach_output:
            try:
                # Listed price * num_gpus * 1.25 (platform fee) must stay under MAX_RENTAL_DPH (128 at time of this comment. Clocked down to 120 to be safe)
                # Rearranged: gpu_pph <= 120 / (num_gpus * 1.25) == 96 / num_gpus.
                _gpu_count = get_gpu_count() or 1
                _gpu_pph = str(max(1, int(96 // _gpu_count)))
                process_open(["sudo","/var/lib/vastai_kaalia/start_self_test.sh", str(machine_id), _gpu_pph, "1", "0", server_url, machine_api_key, args.api_key], preexec_fn=os.setpgrp)
            except Exception as e:
                log(f"Error running self test: {e}", level=1)
'''

NEW_BLOCK = b'''        if machine_id and send_mach_output:
            log(
                "Automatic self-test/listing launch omitted in this LOCAL MODIFIED installer variant.",
                level=1,
            )
'''

HELPER_FILENAME = "start_self_test.sh"


class PreparationError(RuntimeError):
    """Raised whenever preparation cannot prove it is making exactly the approved edit."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lstat(path: Path, label: str) -> os.stat_result:
    try:
        return os.lstat(path)
    except FileNotFoundError as exc:
        raise PreparationError(f"{label} does not exist: {path}") from exc


def _reject_symlink(path: Path, label: str) -> None:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode):
        raise PreparationError(f"refusing symlink {label}: {path}")


def read_pinned_source(input_path: Path) -> bytes:
    """Read one regular, non-symlink input and enforce the immutable source digest."""

    _reject_symlink(input_path, "input")
    info = _lstat(input_path, "input")
    if not stat.S_ISREG(info.st_mode):
        raise PreparationError(f"input is not a regular file: {input_path}")
    data = input_path.read_bytes()
    digest = sha256_bytes(data)
    if digest != PINNED_SOURCE_SHA256:
        raise PreparationError(
            "input digest drift: expected "
            f"{PINNED_SOURCE_SHA256}, got {digest}"
        )
    try:
        ast.parse(data.decode("utf-8"), filename=str(input_path))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise PreparationError(f"pinned input did not parse as Python: {exc}") from exc
    return data


def _assert_exact_replacement_preconditions(source: bytes) -> None:
    new_count = source.count(NEW_BLOCK)
    if new_count:
        raise PreparationError(
            f"refusing already-modified input: found {new_count} replacement block(s)"
        )
    old_count = source.count(OLD_BLOCK)
    if old_count != 1:
        raise PreparationError(
            f"expected exactly one approved old block, found {old_count}"
        )


def _target_if_nodes(source_text: str) -> list[ast.If]:
    """Locate the exact ``if machine_id and send_mach_output`` AST node(s)."""

    parsed = ast.parse(source_text)
    expected_test = ast.dump(
        ast.parse("machine_id and send_mach_output", mode="eval").body,
        include_attributes=False,
    )
    return [
        node
        for node in ast.walk(parsed)
        if isinstance(node, ast.If)
        and ast.dump(node.test, include_attributes=False) == expected_test
    ]


def executable_helper_invocations(source_text: str) -> list[ast.Call]:
    """Return executable AST calls containing the self-test helper filename."""

    parsed = ast.parse(source_text)
    matches: list[ast.Call] = []
    for node in ast.walk(parsed):
        if not isinstance(node, ast.Call):
            continue
        if any(
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and HELPER_FILENAME in value.value
            for value in ast.walk(node)
        ):
            matches.append(node)
    return matches


def assert_suppression_invariant(source: bytes, *, expect_suppressed: bool) -> None:
    """Check the precise source-level safety property used by the focused tests."""

    try:
        source_text = source.decode("utf-8")
        ast.parse(source_text)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise PreparationError(f"candidate did not parse as Python: {exc}") from exc

    target_nodes = _target_if_nodes(source_text)
    if len(target_nodes) != 1:
        raise PreparationError(
            "expected exactly one executable conditional for machine_id and send_mach_output, "
            f"found {len(target_nodes)}"
        )
    helper_calls = executable_helper_invocations(source_text)
    if expect_suppressed:
        if helper_calls:
            raise PreparationError("self-test helper invocation remains in executable AST")
        if source.count(NEW_BLOCK) != 1 or source.count(OLD_BLOCK) != 0:
            raise PreparationError("replacement block is not the exact approved local variant")
    elif not helper_calls:
        raise PreparationError("expected original helper invocation was not present")


def controlled_diff(source: bytes, variant: bytes, input_path: Path, output_path: Path) -> str:
    """Produce only the changed hunk plus three real-source context lines."""

    try:
        source_text = source.decode("utf-8")
        variant_text = variant.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreparationError(f"cannot diff non-UTF-8 candidate: {exc}") from exc
    return "".join(
        difflib.unified_diff(
            source_text.splitlines(keepends=True),
            variant_text.splitlines(keepends=True),
            fromfile=f"{input_path.name} (pinned source)",
            tofile=f"{output_path.name} (local variant)",
            n=3,
        )
    )


def block_line_span(source: bytes, block: bytes) -> dict[str, int]:
    """Return the one-based inclusive line range for one exact byte block."""

    occurrences = source.count(block)
    if occurrences != 1:
        raise PreparationError(f"expected one block for line span, found {occurrences}")
    start_offset = source.index(block)
    start = source.count(b"\n", 0, start_offset) + 1
    return {"start": start, "end": start + block.count(b"\n") - 1}


def _create_restricted_output(output_path: Path, data: bytes) -> None:
    _reject_symlink(output_path, "output")
    if output_path.exists():
        raise PreparationError(f"refusing to overwrite existing output: {output_path}")
    parent_info = _lstat(output_path.parent, "output parent")
    if stat.S_ISLNK(parent_info.st_mode):
        raise PreparationError(f"refusing symlink output parent: {output_path.parent}")
    if not stat.S_ISDIR(parent_info.st_mode):
        raise PreparationError(f"output parent is not a directory: {output_path.parent}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(output_path, flags, 0o600)
    except FileExistsError as exc:
        raise PreparationError(f"refusing to overwrite existing output: {output_path}") from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(output_path, 0o600)
    except BaseException:
        # The exclusive file may be incomplete; preserve it rather than silently
        # overwriting it.  A reviewer can inspect/remove it deliberately.
        raise


def prepare(input_path: Path, output_path: Path) -> dict[str, Any]:
    """Prepare one new local artifact and return auditable, non-secret provenance."""

    if input_path == output_path:
        raise PreparationError("input and output paths must differ")
    source = read_pinned_source(input_path)
    _assert_exact_replacement_preconditions(source)
    variant = source.replace(OLD_BLOCK, NEW_BLOCK)
    if len(variant) != len(source) - len(OLD_BLOCK) + len(NEW_BLOCK):
        raise PreparationError("unexpected output length after exact replacement")
    assert_suppression_invariant(source, expect_suppressed=False)
    assert_suppression_invariant(variant, expect_suppressed=True)
    _create_restricted_output(output_path, variant)
    output_info = os.lstat(output_path)
    if stat.S_IMODE(output_info.st_mode) != 0o600:
        raise PreparationError("output mode is not restrictive 0600")
    return {
        "action": "prepared_local_modified_installer_variant",
        "scope": "only the explicit automatic self-test/listing helper launch block",
        "input": str(input_path),
        "output": str(output_path),
        "input_sha256": sha256_bytes(source),
        "output_sha256": sha256_bytes(variant),
        "output_mode_octal": "0600",
        "replacement_count": 1,
        "old_block_line_span": block_line_span(source, OLD_BLOCK),
        "new_block_line_span": block_line_span(variant, NEW_BLOCK),
        "source_ast_parse": "passed",
        "suppression_invariant": "original_fails_variant_passes",
        "controlled_diff": controlled_diff(source, variant, input_path, output_path),
        "limitations": (
            "This local edit suppresses only the explicit start_self_test.sh launch. "
            "It does not establish runtime, TUI, daemon, registration, download, "
            "diagnostic, pricing, or listing safety."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="pinned original installer")
    parser.add_argument("--output", required=True, type=Path, help="new local-only artifact")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        record = prepare(args.input, args.output)
    except PreparationError as exc:
        print(f"preparation refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
