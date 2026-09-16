#!/usr/bin/env python3
"""Focused local-only tests for the reviewed H100x4 installer variant preparer.

The retained installer path is deliberately required via ``H100X4_ORIGINAL_INSTALLER``.
Tests never import or execute that installer; they parse bytes and execute only the
single extracted target AST node with fake globals and an intercepted ``process_open``.
"""

from __future__ import annotations

import ast
import difflib
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
import types
import unittest


SCRIPT_PATH = Path(__file__).resolve().with_name("prepare_h100x4_installer_variant.py")
SPEC = importlib.util.spec_from_file_location("h100x4_variant_preparer", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {SCRIPT_PATH}")
PREPARER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARER)


def source_block_text(source_text: str) -> str:
    """Extract the exact target node from actual installer text, preserving indent."""

    nodes = PREPARER._target_if_nodes(source_text)
    if len(nodes) != 1:
        raise AssertionError(f"expected one target AST node, got {len(nodes)}")
    node = nodes[0]
    lines = source_text.splitlines(keepends=True)
    return "".join(lines[node.lineno - 1 : node.end_lineno])


def execute_target_block(source_text: str, *, machine_id: object, send_output: object) -> tuple[list[tuple[tuple[object, ...], dict[str, object]]], list[tuple[tuple[object, ...], dict[str, object]]]]:
    """Execute only the parsed target ``if`` using inert fake globals."""

    target = PREPARER._target_if_nodes(source_text)[0]
    module = ast.Module(body=[target], type_ignores=[])
    ast.fix_missing_locations(module)
    opened: list[tuple[tuple[object, ...], dict[str, object]]] = []
    logs: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_process_open(*args: object, **kwargs: object) -> None:
        opened.append((args, kwargs))

    def fake_log(*args: object, **kwargs: object) -> None:
        logs.append((args, kwargs))

    fake_globals = {
        "machine_id": machine_id,
        "send_mach_output": send_output,
        "get_gpu_count": lambda: 4,
        "process_open": fake_process_open,
        "log": fake_log,
        "os": types.SimpleNamespace(setpgrp=object()),
        "server_url": "https://example.invalid",
        "machine_api_key": "fake-machine-key",
        "args": types.SimpleNamespace(api_key="fake-api-key"),
    }
    exec(compile(module, "<isolated-target-block>", "exec"), fake_globals, fake_globals)
    return opened, logs


class PrepareH100x4InstallerVariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("H100X4_ORIGINAL_INSTALLER")
        if not configured:
            raise RuntimeError("H100X4_ORIGINAL_INSTALLER must explicitly name the retained source")
        cls.input_path = Path(configured)
        cls.original = PREPARER.read_pinned_source(cls.input_path)
        cls.original_text = cls.original.decode("utf-8")
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="h100x4-variant-tests-"))
        cls.variant_path = cls.temp_dir / "actual-local-variant"
        cls.record = PREPARER.prepare(cls.input_path, cls.variant_path)
        cls.variant = cls.variant_path.read_bytes()
        cls.variant_text = cls.variant.decode("utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        # Clean the generated local artifact after all tests, not the retained input.
        for child in cls.temp_dir.iterdir():
            child.unlink()
        cls.temp_dir.rmdir()

    def test_00_actual_pinned_source_parses_and_is_unmodified(self) -> None:
        self.assertEqual(PREPARER.sha256_bytes(self.original), PREPARER.PINNED_SOURCE_SHA256)
        ast.parse(self.original_text, filename=str(self.input_path))
        self.assertEqual(self.input_path.read_bytes(), self.original)

    def test_01_exact_replacement_changes_no_unrelated_bytes(self) -> None:
        expected = self.original.replace(PREPARER.OLD_BLOCK, PREPARER.NEW_BLOCK)
        self.assertEqual(self.variant, expected)
        index = self.original.index(PREPARER.OLD_BLOCK)
        self.assertEqual(self.original[:index], self.variant[:index])
        self.assertEqual(
            self.original[index + len(PREPARER.OLD_BLOCK) :],
            self.variant[index + len(PREPARER.NEW_BLOCK) :],
        )
        self.assertEqual(stat.S_IMODE(self.variant_path.stat().st_mode), 0o600)
        ast.parse(self.variant_text, filename=str(self.variant_path))

    def test_02_controlled_diff_is_real_source_hunk_with_exact_line_spans(self) -> None:
        expected_diff = "".join(
            difflib.unified_diff(
                self.original_text.splitlines(keepends=True),
                self.variant_text.splitlines(keepends=True),
                fromfile=f"{self.input_path.name} (pinned source)",
                tofile=f"{self.variant_path.name} (local variant)",
                n=3,
            )
        )
        self.assertEqual(self.record["controlled_diff"], expected_diff)
        self.assertEqual(self.record["controlled_diff"].count("@@"), 2)

        old_start = self.original.index(PREPARER.OLD_BLOCK)
        expected_old_span = {
            "start": self.original.count(b"\n", 0, old_start) + 1,
            "end": self.original.count(b"\n", 0, old_start) + len(PREPARER.OLD_BLOCK.splitlines()),
        }
        new_start = self.variant.index(PREPARER.NEW_BLOCK)
        expected_new_span = {
            "start": self.variant.count(b"\n", 0, new_start) + 1,
            "end": self.variant.count(b"\n", 0, new_start) + len(PREPARER.NEW_BLOCK.splitlines()),
        }
        self.assertEqual(self.record["old_block_line_span"], expected_old_span)
        self.assertEqual(self.record["new_block_line_span"], expected_new_span)
        original_lines = self.original_text.splitlines(keepends=True)
        for line_number in (
            expected_old_span["start"] - 2,
            expected_old_span["start"] - 1,
            expected_old_span["end"] + 1,
            expected_old_span["end"] + 2,
        ):
            self.assertIn(" " + original_lines[line_number - 1], expected_diff)

    def test_03_suppression_invariant_is_red_for_original_and_green_for_variant(self) -> None:
        with self.assertRaisesRegex(PREPARER.PreparationError, "self-test helper invocation remains"):
            PREPARER.assert_suppression_invariant(self.original, expect_suppressed=True)
        PREPARER.assert_suppression_invariant(self.original, expect_suppressed=False)
        PREPARER.assert_suppression_invariant(self.variant, expect_suppressed=True)
        self.assertFalse(PREPARER.executable_helper_invocations(self.variant_text))

    def test_04_actual_extracted_blocks_simulate_no_match_and_match_safely(self) -> None:
        self.assertEqual(source_block_text(self.original_text).encode("utf-8"), PREPARER.OLD_BLOCK)
        self.assertEqual(source_block_text(self.variant_text).encode("utf-8"), PREPARER.NEW_BLOCK)

        for source_text in (self.original_text, self.variant_text):
            opened, logs = execute_target_block(
                source_text, machine_id=None, send_output="successfully"
            )
            self.assertEqual(opened, [])
            self.assertEqual(logs, [])

        old_opened, old_logs = execute_target_block(
            self.original_text, machine_id="machine-123", send_output="successfully"
        )
        self.assertEqual(old_logs, [])
        self.assertEqual(len(old_opened), 1)
        old_args, old_kwargs = old_opened[0]
        self.assertEqual(
            old_args[0],
            [
                "sudo", "/var/lib/vastai_kaalia/start_self_test.sh", "machine-123", "24",
                "1", "0", "https://example.invalid", "fake-machine-key", "fake-api-key",
            ],
        )
        self.assertIn("preexec_fn", old_kwargs)

        new_opened, new_logs = execute_target_block(
            self.variant_text, machine_id="machine-123", send_output="successfully"
        )
        self.assertEqual(new_opened, [])
        self.assertEqual(len(new_logs), 1)
        self.assertIn("LOCAL MODIFIED installer variant", str(new_logs[0][0][0]))

    def test_05_already_modified_input_is_rejected_after_loading_actual_source(self) -> None:
        with self.assertRaisesRegex(PREPARER.PreparationError, "already-modified input"):
            PREPARER._assert_exact_replacement_preconditions(self.variant)

    def test_06_tampered_source_is_rejected_after_loading_actual_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h100x4-tamper-") as temporary:
            candidate = Path(temporary) / "tampered-input"
            candidate.write_bytes(self.original[:-1] + b"#")
            with self.assertRaisesRegex(PREPARER.PreparationError, "input digest drift"):
                PREPARER.prepare(candidate, Path(temporary) / "output")

    def test_07_existing_output_and_repeated_preparation_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h100x4-overwrite-") as temporary:
            directory = Path(temporary)
            output = directory / "output"
            output.write_text("do not overwrite", encoding="utf-8")
            with self.assertRaisesRegex(PREPARER.PreparationError, "refusing to overwrite"):
                PREPARER.prepare(self.input_path, output)
            fresh = directory / "fresh-output"
            PREPARER.prepare(self.input_path, fresh)
            with self.assertRaisesRegex(PREPARER.PreparationError, "refusing to overwrite"):
                PREPARER.prepare(self.input_path, fresh)

    def test_08_symlink_input_output_and_parent_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h100x4-symlink-") as temporary:
            directory = Path(temporary)
            linked_input = directory / "linked-input"
            linked_input.symlink_to(self.input_path)
            with self.assertRaisesRegex(PREPARER.PreparationError, "refusing symlink input"):
                PREPARER.prepare(linked_input, directory / "output")
            linked_output = directory / "linked-output"
            linked_output.symlink_to(directory / "nonexistent-target")
            with self.assertRaisesRegex(PREPARER.PreparationError, "refusing symlink output"):
                PREPARER.prepare(self.input_path, linked_output)
            real_parent = directory / "real-parent"
            real_parent.mkdir()
            linked_parent = directory / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaisesRegex(PREPARER.PreparationError, "refusing symlink output parent"):
                PREPARER.prepare(self.input_path, linked_parent / "output")


if __name__ == "__main__":
    unittest.main()
