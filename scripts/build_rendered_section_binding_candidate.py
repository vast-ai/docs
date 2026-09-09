#!/usr/bin/env python3
"""Bind every P1 actionable Host section to retained rendered-route evidence.

This builder performs no browser or live execution. It reads the already retained,
independently audited rendered package and creates an isolated section-level composition
input. A heading match is bounded rendered-context evidence, not runtime validation, a
semantic score, a V&V PASS, P1 freeze, or human acceptance.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[1]
CONTEXT_PATH = Path("/private/tmp/procedure-baseline-p1-context-topology-rebase-candidate.json")
RENDER_ROOT = REPO / "verification/evidence/2026-08-30-rendered-p1"
MANIFEST_PATH = RENDER_ROOT / "manifest.sha256"
BINDING_PATH = RENDER_ROOT / "rendered-context-binding.json"
RENDER_REVIEW_PATH = Path("/private/tmp/rendered-p1-independent-review-2026-08-30.json")
DEFAULT_OUTPUT = Path("/private/tmp/host-docs-p1-rendered-section-bindings.json")

EXPECTED = {
    "context_candidate": "8c3e2ce0ecd954aa8e2f2d17492566ae0df5cdde741b4f352489b6e9646fade1",
    "manifest": "be9dabae00550bd08fbebdf9ef5e5f9d02f4b86603b9868fc820b262ee8a91ba",
    "rendered_binding": "38e21bece3665f30a214d353d8f8d82e46f7509e84926bbff54a0d9524b2c01a",
    "rendered_review": "d42ced7d69e4eba3d3c5d534a88ad3ef02325fb380aca50d60a37276e439b2d2",
}
EXPECTED_COUNTS = {"pages": 39, "sections": 254, "manifest_entries": 547}
HEADING_RE = re.compile(r'^\s*- heading "(.*)" \[level=(\d+),')
SOURCE_HEADING_RE = re.compile(r"^(#{1,6})\s+")
SCREENSHOT_RE = re.compile(r"^✓ Screenshot saved to (verification/evidence/2026-08-30-rendered-p1/screenshots/[^\s]+\.png)$")
PRIVATE_RE = re.compile(r"(?:/Users/|/private/tmp/|file://)")


class BindingError(RuntimeError):
    """The section binding cannot be built safely or deterministically."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BindingError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError(f"{path.name}: invalid UTF-8 JSON: {exc}") from exc
    require(isinstance(value, dict), f"{path.name}: top level must be an object")
    return value, raw


def normalize_heading(value: str) -> str:
    value = value.replace("`", "").replace("&amp;", "and")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError as exc:
        raise BindingError(f"artifact escapes repository: {path}") from exc


def parse_manifest() -> dict[str, str]:
    records: dict[str, str] = {}
    for line_no, line in enumerate(MANIFEST_PATH.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"manifest line {line_no} is malformed")
        digest, raw_path = match.groups()
        require(raw_path not in records, f"duplicate manifest path: {raw_path}")
        require(not Path(raw_path).is_absolute() and ".." not in Path(raw_path).parts,
                f"manifest path escapes repository: {raw_path}")
        artifact = REPO / raw_path
        require(artifact.is_file(), f"manifest artifact is missing: {raw_path}")
        require(sha256_path(artifact) == digest, f"manifest digest mismatch: {raw_path}")
        records[raw_path] = digest
    require(len(records) == EXPECTED_COUNTS["manifest_entries"], "manifest entry count changed")
    return records


def artifact_ref(path: Path, manifest: dict[str, str], role: str) -> dict[str, Any]:
    relative = repo_relative(path)
    require(relative in manifest, f"artifact is absent from retained manifest: {relative}")
    return {"artifact_ref": relative, "sha256": manifest[relative], "role": role}


def heading_records(snapshot: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for line_no, line in enumerate(snapshot.splitlines(), 1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        accessible_name, raw_level = match.groups()
        visible_name = accessible_name.removeprefix("Navigate to header ")
        output.append({
            "accessible_name": accessible_name,
            "visible_name": visible_name,
            "normalized_visible_name": normalize_heading(visible_name),
            "level": int(raw_level),
            "snapshot_line": line_no,
        })
    return output


def section_registry(context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"page_id": page["id"], "route": page["route"], "section": copy.deepcopy(section)}
        for page in context["pages"]
        for section in page["actionable_section_records"]
    ]


def normalized_digest(candidate: dict[str, Any]) -> str:
    value = copy.deepcopy(candidate)
    value["integrity"]["normalized_content_sha256"] = None
    return sha256_bytes(canonical_json(value))


def build_candidate(context: dict[str, Any], rendered_binding: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    manifest = parse_manifest()
    registry = section_registry(context)
    registry_digest = sha256_bytes(canonical_json(registry))
    page_bindings: list[dict[str, Any]] = []
    total_sections = 0
    prefixed_heading_count = 0
    introduction_count = 0

    for page in context["pages"]:
        stem = page["route"].strip("/").replace("/", "-")
        files = {
            role: RENDER_ROOT / f"{stem}-{suffix}.txt"
            for role, suffix in {
                "open": "open", "wait": "wait", "snapshot": "snapshot", "screenshot_log": "screenshot",
                "page_errors": "errors", "console": "console",
            }.items()
        }
        require(all(path.is_file() for path in files.values()), f"{page['route']}: retained route artifact is missing")
        require(files["page_errors"].read_bytes() == b"", f"{page['route']}: retained page-error artifact is nonempty")
        snapshot_text = files["snapshot"].read_text(encoding="utf-8")
        headings = heading_records(snapshot_text)
        screenshot_line = files["screenshot_log"].read_text(encoding="utf-8").splitlines()[0]
        screenshot_match = SCREENSHOT_RE.fullmatch(screenshot_line)
        require(screenshot_match is not None, f"{page['route']}: screenshot log is malformed")
        screenshot_png = REPO / screenshot_match.group(1)
        require(screenshot_png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), f"{page['route']}: screenshot is not PNG")
        page_artifacts = [
            artifact_ref(files["open"], manifest, "ROUTE_OPEN_OBSERVATION"),
            artifact_ref(files["wait"], manifest, "PAGE_WAIT_OBSERVATION"),
            artifact_ref(files["snapshot"], manifest, "ACCESSIBILITY_SNAPSHOT"),
            artifact_ref(files["screenshot_log"], manifest, "SCREENSHOT_CAPTURE_LOG"),
            artifact_ref(screenshot_png, manifest, "FULL_PAGE_SCREENSHOT"),
            artifact_ref(files["page_errors"], manifest, "PAGE_ERROR_OBSERVATION"),
            artifact_ref(files["console"], manifest, "DEVELOPMENT_CONSOLE_OBSERVATION"),
        ]
        source_lines = (REPO / page["source_file"]).read_text(encoding="utf-8").splitlines()
        sections: list[dict[str, Any]] = []
        for section in page["actionable_section_records"]:
            expected_title = section["heading_path"][-1]
            if expected_title == "Introduction":
                expected_title = page["title"]
                expected_level = 1
                expected_basis = "PAGE_H1_FOR_RAW_INTRODUCTION_REGION"
                introduction_count += 1
            else:
                raw_line = source_lines[int(section["source_span"]["line_start"]) - 1]
                source_heading = SOURCE_HEADING_RE.match(raw_line)
                require(source_heading is not None, f"{section['id']}: source start is not a heading")
                expected_level = len(source_heading.group(1))
                expected_basis = "EXACT_RAW_MDX_HEADING_LEVEL_AND_NORMALIZED_TEXT"
            matches = [
                item for item in headings
                if item["level"] == expected_level
                and item["normalized_visible_name"] == normalize_heading(expected_title)
            ]
            require(len(matches) == 1, f"{section['id']}: expected exactly one rendered heading match, got {len(matches)}")
            observed = matches[0]
            prefixed = observed["accessible_name"].startswith("Navigate to header ")
            prefixed_heading_count += int(prefixed)
            sections.append({
                "section_id": section["id"],
                "raw_occurrence_id": section["raw_occurrence"]["id"],
                "rendered_occurrence_id": section["rendered_occurrence"]["id"],
                "procedure_refs": copy.deepcopy(section["procedure_refs"]),
                "expected_heading": expected_title,
                "expected_heading_level": expected_level,
                "expected_basis": expected_basis,
                "observed_heading": observed["visible_name"],
                "observed_accessible_name": observed["accessible_name"],
                "observed_heading_level": observed["level"],
                "snapshot_line": observed["snapshot_line"],
                "heading_match": "EXACT_NORMALIZED_TEXT_AND_LEVEL",
                "accessible_name_prefix_issue_present": prefixed,
                "anchor_expected": section["rendered_occurrence"]["anchor"],
                "anchor_observation": "NOT_DIRECTLY_OBSERVED_IN_ACCESSIBILITY_SNAPSHOT",
                "evidence_refs": [page_artifacts[2]["artifact_ref"]],
                "inspection_state": "CAPTURED_PENDING_INDEPENDENT_SECTION_REVIEW",
                "status": "UNVALIDATED",
            })
        total_sections += len(sections)
        page_bindings.append({
            "page_id": page["id"],
            "route": page["route"],
            "title": page["title"],
            "source_file": page["source_file"],
            "artifacts": page_artifacts,
            "sections": sections,
            "page_error_file_empty": True,
            "inspection_state": "CAPTURED_PENDING_INDEPENDENT_SECTION_REVIEW",
            "status": "UNVALIDATED",
        })

    require(len(page_bindings) == EXPECTED_COUNTS["pages"], "primary page count changed")
    require(total_sections == EXPECTED_COUNTS["sections"], "actionable section count changed")
    candidate = {
        "schema_version": "host-docs-p1-rendered-section-bindings/1.0",
        "record_type": "HOST_DOCS_P1_RENDERED_SECTION_BINDING_CANDIDATE",
        "state": "DRAFT_NOT_FROZEN",
        "status": "UNVALIDATED",
        "observation_class": "RENDERED_CONTEXT_ONLY",
        "source_identity": copy.deepcopy(rendered_binding["source_identity"]),
        "input_sha256": copy.deepcopy(EXPECTED),
        "section_registry_sha256": registry_digest,
        "rendered_package": {
            "manifest_ref": repo_relative(MANIFEST_PATH),
            "manifest_sha256": EXPECTED["manifest"],
            "manifest_entries": len(manifest),
            "captured_at_utc": rendered_binding["captured_at_utc"],
            "independent_review_decision": review["decision"],
            "independent_review_claim_limit": review["claim_limit"],
        },
        "method": {
            "raw_heading_basis": "Exact source file, start line, heading text, and heading level from reviewed context records.",
            "rendered_heading_basis": "Exactly one accessibility-snapshot heading with equal normalized visible text and equal level.",
            "introduction_rule": "A raw Introduction region binds to the page H1, not to an invented Introduction heading.",
            "claim_boundary": "Heading presence and page-level capture context only; no anchor, complete body text, command, Host, WAN, API, CLI runtime, paid, semantic, or authority claim is proven.",
        },
        "page_bindings": page_bindings,
        "counts": {
            "pages": len(page_bindings),
            "sections": total_sections,
            "exact_normalized_heading_level_matches": total_sections,
            "introduction_to_h1_bindings": introduction_count,
            "accessible_name_prefix_issue_occurrences": prefixed_heading_count,
            "page_error_files_empty": sum(item["page_error_file_empty"] for item in page_bindings),
            "pass_assigned": 0,
            "live_or_browser_execution_performed_by_builder": 0,
        },
        "unresolved_blockers": [
            "Every section remains UNVALIDATED pending independent section-level review.",
            "Expected anchors are not directly observed by the accessibility snapshot and remain unvalidated.",
            "The shared heading accessible-name prefix defect remains visible and is not normalized away as a product result.",
            "Rendered heading presence does not validate complete prose, commands, external behavior, authority, or semantic score.",
        ],
        "human_acceptance": "NOT_DECIDED",
        "integrity": {
            "normalized_content_sha256": None,
            "serialization": "UTF8_SORTED_KEYS_INDENT_2_TRAILING_NEWLINE",
        },
    }
    candidate["integrity"]["normalized_content_sha256"] = normalized_digest(candidate)
    return candidate


def preflight() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context, context_raw = load_json(CONTEXT_PATH)
    binding, binding_raw = load_json(BINDING_PATH)
    review, review_raw = load_json(RENDER_REVIEW_PATH)
    require(sha256_bytes(context_raw) == EXPECTED["context_candidate"], "context candidate bytes changed")
    require(sha256_path(MANIFEST_PATH) == EXPECTED["manifest"], "rendered manifest bytes changed")
    require(sha256_bytes(binding_raw) == EXPECTED["rendered_binding"], "rendered binding bytes changed")
    require(sha256_bytes(review_raw) == EXPECTED["rendered_review"], "rendered review bytes changed")
    require(binding.get("status") == "UNVALIDATED" and binding.get("observation_class") == "RENDERED_CONTEXT_ONLY",
            "rendered binding claim boundary changed")
    require(review.get("decision") == "GO_FOR_P1_COMPOSITION_AS_RENDERED_CONTEXT_EVIDENCE",
            "independent rendered review does not permit composition")
    require(context.get("state") == "DRAFT_NOT_FROZEN", "context candidate is not a draft")
    require(context.get("execution_readiness", {}).get("new_live_execution_allowed") is False,
            "context candidate unexpectedly permits live execution")
    return context, binding, review


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")
    else:
        yield path, value


def validate(candidate: dict[str, Any], expected: dict[str, Any]) -> None:
    require(candidate == expected, "candidate differs from deterministic retained-evidence rebuild")
    require(candidate["state"] == "DRAFT_NOT_FROZEN", "candidate is unexpectedly frozen")
    require(candidate["status"] == "UNVALIDATED", "candidate status changed")
    require(candidate["counts"]["pass_assigned"] == 0, "candidate assigns PASS")
    require(candidate["counts"]["live_or_browser_execution_performed_by_builder"] == 0, "candidate claims execution")
    require(candidate["integrity"]["normalized_content_sha256"] == normalized_digest(candidate), "candidate digest mismatch")
    section_ids = [section["section_id"] for page in candidate["page_bindings"] for section in page["sections"]]
    require(len(section_ids) == EXPECTED_COUNTS["sections"] and len(set(section_ids)) == len(section_ids),
            "section bindings are incomplete or duplicated")
    require(all(section["status"] == "UNVALIDATED" for page in candidate["page_bindings"] for section in page["sections"]),
            "a section result is not UNVALIDATED")
    for path, value in walk(candidate):
        if isinstance(value, str):
            require(not PRIVATE_RE.search(value), f"private path leaked at {path}")


def self_test(expected: dict[str, Any]) -> int:
    tests: list[tuple[str, bool]] = []

    def mutation(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        value = copy.deepcopy(expected)
        mutate(value)
        if name != "digest mutation fails closed":
            value["integrity"]["normalized_content_sha256"] = normalized_digest(value)
        try:
            validate(value, expected)
        except BindingError:
            tests.append((name, True))
        else:
            tests.append((name, False))

    mutation("page removal fails closed", lambda d: d["page_bindings"].pop())
    mutation("section removal fails closed", lambda d: d["page_bindings"][0]["sections"].pop())
    mutation("heading mutation fails closed", lambda d: d["page_bindings"][0]["sections"][0].update(observed_heading="forged"))
    mutation("level mutation fails closed", lambda d: d["page_bindings"][0]["sections"][0].update(observed_heading_level=6))
    mutation("artifact hash mutation fails closed", lambda d: d["page_bindings"][0]["artifacts"][0].update(sha256="0" * 64))
    mutation("error-state mutation fails closed", lambda d: d["page_bindings"][0].update(page_error_file_empty=False))
    mutation("PASS mutation fails closed", lambda d: d["page_bindings"][0]["sections"][0].update(status="PASS"))
    mutation("execution mutation fails closed", lambda d: d["counts"].update(live_or_browser_execution_performed_by_builder=1))
    mutation("private-path mutation fails closed", lambda d: d.update(note="/private/tmp/raw"))
    mutation("anchor overclaim fails closed", lambda d: d["page_bindings"][0]["sections"][0].update(anchor_observation="PASS"))
    mutation("review decision mutation fails closed", lambda d: d["rendered_package"].update(independent_review_decision="ACCEPTED"))
    mutation("digest mutation fails closed", lambda d: d["integrity"].update(normalized_content_sha256="f" * 64))
    failed = [name for name, passed in tests if not passed]
    require(not failed, "self-tests failed: " + "; ".join(failed))
    print(f"SELF-TEST PASS: {len(tests)}/{len(tests)} fail-closed mutations rejected")
    return len(tests)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", nargs="?", const=str(DEFAULT_OUTPUT))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    context, binding, review = preflight()
    expected = build_candidate(context, binding, review)
    validate(expected, expected)
    tests = self_test(expected) if args.self_test else 0
    if args.check is not None:
        path = Path(args.check)
        actual, actual_raw = load_json(path)
        validate(actual, expected)
        require(actual_raw == canonical_json(expected, pretty=True), "candidate serialization is not canonical")
        mode = "check"
    else:
        require(args.output.resolve() != (REPO / "verification/procedure-baseline-p1.json").resolve(),
                "refusing to overwrite canonical P1")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_json(expected, pretty=True))
        path = args.output
        mode = "write"
    print(json.dumps({
        "mode": mode,
        "path": str(path),
        "sha256": sha256_path(path),
        "normalized_content_sha256": expected["integrity"]["normalized_content_sha256"],
        "counts": expected["counts"],
        "self_tests": tests,
        "result": "PASS",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BindingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
