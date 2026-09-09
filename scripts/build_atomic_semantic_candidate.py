#!/usr/bin/env python3
"""Build and fail-closed validate the isolated Host Docs atomic-claim candidate.

This script deliberately does not alter Procedure Baseline P1.  It turns the 104
reconciled material-gap records into unscored discovery parents and exact-source
atomic semantic assertions.  Assertions are semantic assessment records only;
they never add procedures, branches, steps, commands, or runtime attempts.

The builder is deterministic for the pinned inputs.  It performs local source
inspection only and never invokes a documented command, browser, network, Host,
WAN, credentialed API, or paid operation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


REPO = Path(__file__).resolve().parents[1]
CANONICAL_PATH = REPO / "verification/procedure-baseline-p1.json"
RAW_PATH = Path("/private/tmp/host-docs-p1-raw-claim-gaps.json")
RECONCILE_PATH = Path("/private/tmp/host-docs-p1-gap-reconcile.json")
CLAIM_REVIEW_PATH = Path("/private/tmp/host-docs-p1-claim-schema-review.json")
GOAL_AUDIT_PATH = Path("/private/tmp/host-docs-p1-goal-schema-audit.json")
REJECTED_BUILDER_PATH = REPO / "scripts/build_procedure_claim_integration.py"
REJECTED_CANDIDATE_PATH = Path("/private/tmp/procedure-baseline-p1-claims-candidate.json")
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-atomic-claims-candidate.json")

EXPECTED_INPUT_SHA256 = {
    "canonical_baseline": "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912",
    "raw_claim_gap_audit": "0568cda70f237eb10823e75ce1deb3fef7873a658eb287266f3b52f03e494de1",
    "independent_gap_reconciliation": "a1ae714917f1da76bbd967a7f82d40117002dc636d81255e1132f61ef715566f",
    "claim_schema_review": "c3e3cd637c54c0bf8ca1ca1879a32ff97e122d916b9af94c95ec20a74828d743",
    "goal_schema_audit": "4aa7984dd7bac5abaa396ec9bdf14f90929fafcbe5015dca6788734387f1b090",
    "rejected_claim_integration_builder": "7ac1c24c1ed7f4702307aa6d2118942d030c0204961fab1e10a94e664e6b4ad4",
    "rejected_claim_integration_candidate": "51f51b18fd9833a3f0613dc3cc20cdcaa18cc3a1397e2fe10a54344849703ab8",
}

EXPECTED_TARGET = {
    "docs_head": "09d729e72fbcb2bdd2dead2b9dc5d5e1eeeffcf5",
    "docs_tree": "bfe3e9316893a2174b99779ce844e81f014d2b53",
    "legacy_inventory_source_revision": "5088d76b89856185f3ab15a628e4152ff140ab26",
    "legacy_content_fingerprint": "sha256:bc59a848d0cb8698097787b911bb9e5b6875570c7c58815baa6d1f48b2504b4d",
    "legacy_inventory_sha256": "9485b266d57764b6254fe578b5fe9cf128959129c2575d2a432164afc7dc39ab",
}

VV_STATUSES = {
    "UNVALIDATED", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE", "STALE"
}
ASSERTION_KINDS = {
    "PROCEDURE_STEP",
    "COMMAND",
    "FACTUAL_THRESHOLD",
    "LITERAL_ERROR",
    "EXTERNAL_BEHAVIOR",
    "PREREQUISITE",
    "EXCEPTION",
    "LIMITATION",
    "CLEANUP",
    "OUTCOME",
}
EXECUTION_UNIT_EFFECT = "NO_NEW_EXECUTABLE_TEST_UNIT"
SEMANTIC_SCOPE = "ATOMIC_ASSERTION_AUTHORITY_PROCEDURE_AND_RENDERED_CONTEXT"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LIST_RE = re.compile(r"^\s*(?:[-+*]|\d+[.)])\s+\S")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*([^\s`]*)?.*$")
TABLE_SEPARATOR_RE = re.compile(
    r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$"
)
FULL_JSX_RE = re.compile(r"^\s*</?[A-Za-z][^>]*?/?>\s*$")
FULL_COMMENT_RE = re.compile(r"^\s*\{/\*.*\*/\}\s*$")
STRONG_LABEL_RE = re.compile(r"^\s*\*\*([^*]+)\*\*:?\s*$")
SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9`*\[])")


class AtomicCandidateError(RuntimeError):
    """The candidate is not safe, source-exact, or deterministic."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AtomicCandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AtomicCandidateError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    require(isinstance(value, dict), f"{path}: top level is not an object")
    return value, data


def stable_id(prefix: str, namespace: str, *parts: Any) -> str:
    basis = namespace + "\0" + "\0".join(str(part) for part in parts)
    return prefix + sha256_text(basis)[:16]


def exact_keys(value: Any, required: set[str], context: str, *, optional: set[str] | None = None) -> None:
    require(isinstance(value, dict), f"{context}: expected object")
    optional = optional or set()
    unknown = set(value) - required - optional
    missing = required - set(value)
    require(not unknown, f"{context}: unknown fields {sorted(unknown)}")
    require(not missing, f"{context}: missing fields {sorted(missing)}")


def sorted_unique(values: Iterable[str], context: str) -> list[str]:
    output = sorted(set(values))
    require(len(output) == len(list(values)) if isinstance(values, list) else True,
            f"{context}: duplicate values")
    return output


def repo_source_path(raw: str) -> Path:
    candidate = Path(raw)
    require(not candidate.is_absolute() and ".." not in candidate.parts,
            f"source path escapes repository: {raw!r}")
    require(candidate.suffix == ".mdx" and raw.startswith(("host/", "snippets/")),
            f"source path is not allowlisted: {raw!r}")
    resolved = (REPO / candidate).resolve()
    require(REPO.resolve() in resolved.parents and resolved.is_file(),
            f"source path is not a repository file: {raw!r}")
    return resolved


@dataclass(frozen=True)
class SourceFile:
    path: str
    lines: tuple[str, ...]
    sha256: str
    heading_paths: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Segment:
    line_start: int
    column_start: int
    line_end: int
    column_end: int
    text_exact: str
    block_type: str
    heading_path: tuple[str, ...]
    local_context: str | None
    code_language: str | None = None


def clean_heading(value: str) -> str:
    value = re.sub(r"\s+\{#[^}]+\}\s*$", "", value)
    value = re.sub(r"[*_`]", "", value)
    return value.strip()


def load_source(raw: str) -> SourceFile:
    path = repo_source_path(raw)
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AtomicCandidateError(f"source is not UTF-8: {raw}") from exc
    lines = tuple(text.splitlines())
    stack: dict[int, str] = {}
    paths: list[tuple[str, ...]] = []
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            stack = {key: value for key, value in stack.items() if key < level}
            stack[level] = clean_heading(match.group(2))
        # Some MDX pages begin their authored body at h2/h3.  Missing parent
        # levels are not headings and must not be filled with invented labels.
        paths.append(tuple(stack[key] for key in sorted(stack)))
    return SourceFile(raw, lines, sha256_bytes(data), tuple(paths))


def extract_exact(source: SourceFile, start: int, col_start: int, end: int, col_end: int) -> str:
    require(1 <= start <= end <= len(source.lines), f"invalid source line range {source.path}:{start}-{end}")
    require(1 <= col_start <= len(source.lines[start - 1]) + 1,
            f"invalid start column {source.path}:{start}:{col_start}")
    require(0 <= col_end <= len(source.lines[end - 1]),
            f"invalid end column {source.path}:{end}:{col_end}")
    require(start != end or col_end >= col_start - 1,
            f"invalid same-line columns {source.path}:{start}:{col_start}-{col_end}")
    if start == end:
        return source.lines[start - 1][col_start - 1:col_end]
    parts = [source.lines[start - 1][col_start - 1:]]
    parts.extend(source.lines[start:end - 1])
    parts.append(source.lines[end - 1][:col_end])
    return "\n".join(parts)


def whole_line_segment(
    source: SourceFile,
    start: int,
    end: int,
    block_type: str,
    local_context: str | None,
    code_language: str | None = None,
) -> Segment:
    text = "\n".join(source.lines[start - 1:end])
    return Segment(
        start, 1, end, len(source.lines[end - 1]), text, block_type,
        source.heading_paths[start - 1], local_context, code_language,
    )


def paragraph_sentence_segments(segment: Segment) -> list[Segment]:
    """Split only unusually broad prose blocks; normal Markdown blocks stay intact.

    This is intentionally not a sentence-per-record tokenizer.  Lists, tables, code,
    short paragraphs, and two-sentence compound claims retain their authored semantic
    block.  Only prose with more than two sentences or more than 420 characters is
    divided at explicit punctuation boundaries, and short fragments are recombined.
    """
    if segment.block_type != "PARAGRAPH":
        return [segment]
    breaks = list(SENTENCE_BREAK_RE.finditer(segment.text_exact))
    if len(breaks) <= 1 and len(segment.text_exact) <= 420:
        return [segment]
    boundaries = [0] + [match.end() for match in breaks] + [len(segment.text_exact)]
    pieces: list[tuple[int, int]] = []
    for left, right in zip(boundaries, boundaries[1:]):
        while left < right and segment.text_exact[left].isspace():
            left += 1
        while right > left and segment.text_exact[right - 1].isspace():
            right -= 1
        if right > left:
            if pieces and right - left < 32:
                pieces[-1] = (pieces[-1][0], right)
            else:
                pieces.append((left, right))
    if len(pieces) > 1 and pieces[0][1] - pieces[0][0] < 32:
        pieces[1] = (pieces[0][0], pieces[1][1])
        pieces = pieces[1:]
    if len(pieces) <= 1:
        return [segment]

    # Navigation-only trailing sentences are surrounding context, not an
    # independently scorable product assertion.  Retain their exact bytes by
    # joining them to the preceding authored assertion.
    merged: list[tuple[int, int]] = []
    for left, right in pieces:
        prose = segment.text_exact[left:right].strip()
        navigation_only = bool(re.match(r"^(?:See|Read|Learn more)\s+\[", prose, flags=re.I))
        if navigation_only and merged:
            merged[-1] = (merged[-1][0], right)
        else:
            merged.append((left, right))
    pieces = merged
    if len(pieces) <= 1:
        return [segment]

    line_starts = [0]
    for match in re.finditer("\n", segment.text_exact):
        line_starts.append(match.end())

    def location(offset: int, *, end: bool) -> tuple[int, int]:
        line_index = 0
        for index, line_start in enumerate(line_starts):
            if line_start <= offset:
                line_index = index
            else:
                break
        relative = offset - line_starts[line_index]
        line_number = segment.line_start + line_index
        column = relative + (segment.column_start if line_index == 0 else 1)
        if end:
            column -= 1
        return line_number, column

    output: list[Segment] = []
    for left, right in pieces:
        start_line, start_col = location(left, end=False)
        end_line, end_col = location(right, end=True)
        text = segment.text_exact[left:right]
        output.append(Segment(
            start_line, start_col, end_line, end_col, text,
            "LONG_PARAGRAPH_ASSERTION", segment.heading_path,
            segment.local_context, segment.code_language,
        ))
    return output


def classify_source_span(source: SourceFile, start: int, end: int) -> tuple[list[Segment], list[dict[str, Any]]]:
    """Return meaningful Markdown blocks and explicit structural exclusions."""
    require(1 <= start <= end <= len(source.lines), f"invalid effective source {source.path}:{start}-{end}")
    selected: list[Segment] = []
    excluded: list[dict[str, Any]] = []
    index = start
    local_context: str | None = None

    def exclude(line_start: int, line_end: int, reason: str, rationale: str) -> None:
        text = "\n".join(source.lines[line_start - 1:line_end])
        excluded.append({
            "line_start": line_start,
            "line_end": line_end,
            "text_exact": text,
            "text_sha256": sha256_text(text),
            "reason": reason,
            "rationale": rationale,
        })

    while index <= end:
        line = source.lines[index - 1]
        stripped = line.strip()
        if not stripped:
            exclude(index, index, "MARKDOWN_WHITESPACE", "Blank source separation carries no independently scorable claim.")
            index += 1
            continue
        heading = HEADING_RE.match(line)
        if heading:
            local_context = None
            exclude(index, index, "MARKDOWN_HEADING", "Heading text identifies context; assertions are selected from the bounded content below it.")
            index += 1
            continue
        if FULL_COMMENT_RE.match(line):
            exclude(index, index, "NON_RENDERED_MDX_COMMENT", "The hidden MDX comment is not presented to Host readers.")
            index += 1
            continue
        fence = FENCE_RE.match(line)
        if fence:
            delimiter = fence.group(1)
            language = (fence.group(2) or "").lower() or None
            exclude(index, index, "CODE_FENCE_DELIMITER", "Fence syntax is structural context, not an assertion.")
            index += 1
            code_start = index
            code_end = index - 1
            while code_end + 1 <= end and not source.lines[code_end].lstrip().startswith(delimiter[:3]):
                code_end += 1
            code_lines = source.lines[code_start - 1:code_end]
            formula_block = bool(
                language == "text"
                and code_lines
                and (
                    any(item.lstrip().startswith("+") for item in code_lines)
                    or any(item.rstrip().endswith("=") for item in code_lines)
                )
            )
            if formula_block:
                selected.append(whole_line_segment(
                    source, code_start, code_end, "CODE_FORM", local_context, language
                ))
                index = code_end + 1
            while not formula_block and index <= code_end:
                if not source.lines[index - 1].strip():
                    exclude(index, index, "CODE_BLOCK_WHITESPACE", "Blank code-block separation carries no assertion.")
                    index += 1
                    continue
                group_start = index
                group_end = index
                if language in {"bash", "sh", "shell", "zsh", "powershell", "ps1", "cmd"}:
                    while group_end < end and source.lines[group_end - 1].rstrip().endswith("\\"):
                        group_end += 1
                selected.append(whole_line_segment(
                    source, group_start, group_end, "CODE_FORM", local_context, language
                ))
                index = group_end + 1
            if index <= end and source.lines[index - 1].lstrip().startswith(delimiter[:3]):
                exclude(index, index, "CODE_FENCE_DELIMITER", "Fence syntax is structural context, not an assertion.")
                index += 1
            continue
        if FULL_JSX_RE.match(line) or stripped in {"<>", "</>"}:
            title = re.search(r'\btitle=["\']([^"\']+)["\']', line)
            if title:
                local_context = title.group(1).strip()
            exclude(index, index, "MDX_COMPONENT_STRUCTURE", "The component/tag is rendering structure; its child prose is assessed separately.")
            index += 1
            continue
        if stripped.startswith("<a ") and stripped.endswith("/>"):
            exclude(index, index, "ANCHOR_STRUCTURE", "The explicit anchor changes navigation, not the user-facing behavioral claim.")
            index += 1
            continue
        strong = STRONG_LABEL_RE.match(line)
        if strong:
            local_context = strong.group(1).strip()
            exclude(index, index, "LOCAL_CONTEXT_LABEL", "The label scopes the following assertion and is retained as context, not scored independently.")
            index += 1
            continue
        if stripped in {"---", "***", "___"}:
            exclude(index, index, "MARKDOWN_SEPARATOR", "The separator carries no independently scorable claim.")
            index += 1
            continue
        if index < end and "|" in line and TABLE_SEPARATOR_RE.match(source.lines[index]):
            exclude(index, index, "TABLE_HEADER_CONTEXT", "Column names are retained as table context; each data row is independently bounded.")
            exclude(index + 1, index + 1, "TABLE_SEPARATOR", "Markdown table delimiter carries no claim.")
            index += 2
            while index <= end:
                row = source.lines[index - 1]
                if not row.strip() or "|" not in row:
                    break
                selected.append(whole_line_segment(source, index, index, "TABLE_ROW", local_context))
                index += 1
            continue
        if TABLE_SEPARATOR_RE.match(line):
            exclude(index, index, "TABLE_SEPARATOR", "Markdown table delimiter carries no claim.")
            index += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
            selected.append(whole_line_segment(source, index, index, "TABLE_ROW", local_context))
            index += 1
            continue
        if LIST_RE.match(line):
            item_start = index
            item_end = index
            cursor = index + 1
            while cursor <= end:
                following = source.lines[cursor - 1]
                if not following.strip() or LIST_RE.match(following) or HEADING_RE.match(following):
                    break
                if FENCE_RE.match(following) or FULL_JSX_RE.match(following) or "|" in following:
                    break
                if len(following) - len(following.lstrip()) > 0:
                    item_end = cursor
                    cursor += 1
                    continue
                break
            selected.append(whole_line_segment(source, item_start, item_end, "LIST_ITEM", local_context))
            index = item_end + 1
            continue

        paragraph_start = index
        paragraph_end = index
        cursor = index + 1
        while cursor <= end:
            following = source.lines[cursor - 1]
            if (not following.strip() or HEADING_RE.match(following) or FENCE_RE.match(following)
                    or FULL_JSX_RE.match(following) or FULL_COMMENT_RE.match(following)
                    or LIST_RE.match(following) or TABLE_SEPARATOR_RE.match(following)):
                break
            if cursor < end and "|" in following and TABLE_SEPARATOR_RE.match(source.lines[cursor]):
                break
            paragraph_end = cursor
            cursor += 1
        paragraph = whole_line_segment(source, paragraph_start, paragraph_end, "PARAGRAPH", local_context)
        next_nonblank = paragraph_end + 1
        while next_nonblank <= end and not source.lines[next_nonblank - 1].strip():
            next_nonblank += 1
        lead_in = paragraph.text_exact.strip().endswith(":") and next_nonblank <= end and (
            LIST_RE.match(source.lines[next_nonblank - 1])
            or FENCE_RE.match(source.lines[next_nonblank - 1])
            or "|" in source.lines[next_nonblank - 1]
        )
        navigation_only = bool(re.match(
            r"^(?:See|Read|Learn more)\s+\[[^\]]+\]\([^)]*\)",
            paragraph.text_exact.strip(),
            flags=re.I,
        ))
        if navigation_only:
            exclude(paragraph_start, paragraph_end, "NAVIGATION_ONLY", "The paragraph only routes readers to another page and makes no independently scorable behavior claim.")
        elif lead_in:
            local_context = paragraph.text_exact.strip()
            exclude(paragraph_start, paragraph_end, "CONTEXT_LEAD_IN", "The lead-in supplies surrounding context to following assertions but is not scored alone.")
        else:
            selected.extend(paragraph_sentence_segments(paragraph))
        index = paragraph_end + 1

    covered_lines = set()
    for segment in selected:
        covered_lines.update(range(segment.line_start, segment.line_end + 1))
    for item in excluded:
        covered_lines.update(range(item["line_start"], item["line_end"] + 1))
    require(covered_lines == set(range(start, end + 1)),
            f"source decomposition does not cover {source.path}:{start}-{end}")
    return selected, excluded


def normalize_prose(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[`*_]", "", value)
    value = value.strip().strip("|").strip()
    value = re.sub(r"\s*\|\s*", " | ", value)
    return re.sub(r"\s+", " ", value).strip()


def legacy_overlap_for(segment: Segment, file: str, legacy_claims: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    overlapping: list[str] = []
    exact: list[str] = []
    normalized = normalize_prose(segment.text_exact)
    for claim in legacy_claims:
        source = claim.get("source", {})
        if source.get("file") != file:
            continue
        if int(source.get("line_end", 0)) < segment.line_start or int(source.get("line_start", 0)) > segment.line_end:
            continue
        overlapping.append(claim["id"])
        if normalize_prose(str(claim.get("text", ""))) == normalized:
            exact.append(claim["id"])
    return sorted(set(overlapping)), sorted(set(exact))


def assertion_kind(parent_kind: str, segment: Segment) -> str:
    heading = " ".join(segment.heading_path).lower()
    text = segment.text_exact.lower()
    if segment.block_type == "CODE_FORM":
        if segment.code_language in {"bash", "sh", "shell", "zsh", "powershell", "ps1", "cmd"}:
            return "COMMAND"
        if parent_kind in {"formula", "threshold-bundle", "threshold-and-behavior", "threshold-and-timing"}:
            return "FACTUAL_THRESHOLD"
    if parent_kind in {"formula", "threshold-bundle", "threshold-and-behavior", "threshold-and-timing", "financial-model"}:
        return "FACTUAL_THRESHOLD"
    if parent_kind in {"prerequisite", "prerequisite-bundle", "application-prerequisite", "safety-gate", "security-instruction"}:
        return "PREREQUISITE"
    if parent_kind in {"cleanup", "expected-observable-and-cleanup"} or "cleanup" in heading:
        return "CLEANUP"
    if parent_kind in {"expected-observable", "runtime-contract", "state-contract", "evidence-contract"}:
        return "OUTCOME"
    if parent_kind in {"failure-behavior", "failure-and-evidence-contract", "failure-cause-bundle"}:
        if "`" in segment.text_exact or "error" in heading or "error" in text:
            return "LITERAL_ERROR"
        return "EXCEPTION"
    if parent_kind in {"limitation", "support-boundary", "legal-authority"}:
        return "LIMITATION"
    if parent_kind in {
        "community-procedure", "conditional-procedure", "cross-page-handoff",
        "cross-page-journey", "cross-page-routing", "decision-procedure",
        "destructive-procedure", "financial-procedure", "investigation-procedure",
        "ordered-procedure", "paid-procedure", "procedure-checkpoint",
        "procedure-context", "procedure-step", "ui-procedure",
    }:
        return "PROCEDURE_STEP"
    if any(word in heading for word in ("unsupported", "limitation", "cannot", "not supported")):
        return "LIMITATION"
    if any(word in heading for word in ("result", "status", "outcome", "what happens")):
        return "OUTCOME"
    return "EXTERNAL_BEHAVIOR"


def topology_maps(baseline: dict[str, Any]) -> dict[str, Any]:
    pages = baseline["pages"]
    procedures = baseline["procedures"]
    page_by_id = {item["id"]: item for item in pages}
    page_by_file = {item["source_file"]: item for item in pages}
    procedure_by_id = {item["id"]: item for item in procedures}
    branches: dict[str, tuple[str, dict[str, Any]]] = {}
    steps: dict[str, tuple[str, str, dict[str, Any]]] = {}
    for procedure in procedures:
        for branch in procedure["branches"]:
            require(branch["id"] not in branches, f"duplicate branch {branch['id']}")
            branches[branch["id"]] = (procedure["id"], branch)
            for step in branch["steps"]:
                require(step["id"] not in steps, f"duplicate step {step['id']}")
                steps[step["id"]] = (procedure["id"], branch["id"], step)
    fragments = {item["source_file"]: item for item in baseline["fragments"]}
    require((len(pages), len(procedures), len(branches), len(steps)) == (39, 82, 193, 454),
            "canonical topology denominator changed")
    return {
        "page_by_id": page_by_id,
        "page_by_file": page_by_file,
        "procedure_by_id": procedure_by_id,
        "branch_by_id": branches,
        "step_by_id": steps,
        "fragment_by_file": fragments,
    }


def source_type_for(file: str) -> str:
    if file == "host/self-test-reference.mdx":
        return "generated-self-test"
    if file.startswith("snippets/"):
        return "authored-shared-fragment"
    return "authored"


def page_and_routes(record: dict[str, Any], maps: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    page = maps["page_by_file"].get(record["source"]["file"])
    require(page is not None, f"{record['id']}: discovery source has no primary Host page")
    return page, [page["route"]]


def full_source_binding(
    source_record_id: str,
    role: str,
    file: str,
    start: int,
    end: int,
    routes: list[str],
    maps: dict[str, Any],
    *,
    primary: bool,
) -> dict[str, Any]:
    source = load_source(file)
    require(1 <= start <= end <= len(source.lines), f"{source_record_id}: invalid source span")
    text = "\n".join(source.lines[start - 1:end])
    page = maps["page_by_file"].get(file)
    fragment = maps["fragment_by_file"].get(file)
    require(page is not None or fragment is not None, f"{source_record_id}: unowned source {file}")
    if page:
        require(page["source_sha256"] == source.sha256, f"{source_record_id}: stale page source {file}")
    if fragment:
        require(fragment["source_sha256"] == source.sha256, f"{source_record_id}: stale fragment source {file}")
    return {
        "id": stable_id("SRC-", "host-docs-p1-source-binding-v1", source_record_id, role, file, start, end),
        "role": role,
        "primary_for_assertion_decomposition": primary,
        "file": file,
        "line_start": start,
        "line_end": end,
        "source_type": source_type_for(file),
        "source_file_sha256": source.sha256,
        "source_span_sha256": sha256_text(text),
        "page_id": page["id"] if page else None,
        "fragment_id": fragment["id"] if fragment else None,
        "rendered_routes": sorted(set(routes)),
    }


def source_bindings_for(record: dict[str, Any], routes: list[str], maps: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    discovery = full_source_binding(
        record["id"], "DISCOVERY_SOURCE", record["source"]["file"],
        record["source"]["line_start"], record["source"]["line_end"], routes, maps,
        primary=not bool(record["source_span_review"].get("corrected_sources")),
    )
    corrected = record["source_span_review"].get("corrected_sources", [])
    if not corrected:
        effective = copy.deepcopy(discovery)
        effective["role"] = "PRIMARY_ASSERTION_SOURCE"
        effective["id"] = stable_id(
            "SRC-", "host-docs-p1-source-binding-v1", record["id"],
            "PRIMARY_ASSERTION_SOURCE", effective["file"], effective["line_start"], effective["line_end"]
        )
        return discovery, [effective]
    effective = []
    for source in corrected:
        raw_role = source["role"]
        role = "PRIMARY_ASSERTION_SOURCE" if raw_role == "FULL_CLAIM_SOURCE" else raw_role
        effective.append(full_source_binding(
            record["id"], role, source["file"], source["line_start"], source["line_end"],
            routes, maps, primary=role in {"PRIMARY_ASSERTION_SOURCE", "IMPORTED_CLAIM_SOURCE"},
        ))
    effective.sort(key=lambda item: item["id"])
    require(sum(item["primary_for_assertion_decomposition"] for item in effective) == 1,
            f"{record['id']}: corrected sources do not identify exactly one assertion source")
    return discovery, effective


def grouped_target_bindings(record: dict[str, Any], maps: dict[str, Any]) -> list[dict[str, Any]]:
    target = record["target"]
    output = []
    for procedure_id in sorted(target["procedure_ids"]):
        branch_ids = sorted(
            branch_id for branch_id in target["branch_ids"]
            if maps["branch_by_id"][branch_id][0] == procedure_id
        )
        step_ids = sorted(
            step_id for step_id in target["step_ids"]
            if maps["step_by_id"][step_id][0] == procedure_id
        )
        output.append({
            "procedure_id": procedure_id,
            "branch_ids": branch_ids,
            "step_ids": step_ids,
            "procedure_field": target["procedure_field"],
        })
    return output


def step_overlaps(step: dict[str, Any], segment: Segment) -> bool:
    return any(
        int(span["start"]) <= segment.line_end and int(span["end"]) >= segment.line_start
        for span in step.get("source_lines", [])
    )


def assertion_target_contexts(
    assertion_id: str,
    record: dict[str, Any],
    segment: Segment,
    primary_file: str,
    raw_occurrence_id: str,
    rendered_occurrence_ids: dict[str, str],
    page: dict[str, Any],
    maps: dict[str, Any],
    authority_boundary: dict[str, Any],
    planned_method: dict[str, str],
) -> list[dict[str, Any]]:
    target = record["target"]
    contexts: list[tuple[str, str | None, list[str], str]] = []
    overlap_by_procedure: dict[str, list[str]] = defaultdict(list)
    if primary_file == record["source"]["file"]:
        for step_id in target["step_ids"]:
            proc_id, _, step = maps["step_by_id"][step_id]
            if step_overlaps(step, segment):
                overlap_by_procedure[proc_id].append(step_id)

    procedures_with_overlap = set(overlap_by_procedure)
    for procedure_id in sorted(target["procedure_ids"]):
        procedure_steps = sorted(overlap_by_procedure.get(procedure_id, []))
        if procedures_with_overlap and not procedure_steps:
            continue
        if procedure_steps:
            by_branch: dict[str, list[str]] = defaultdict(list)
            for step_id in procedure_steps:
                by_branch[maps["step_by_id"][step_id][1]].append(step_id)
            for branch_id in sorted(by_branch):
                contexts.append((procedure_id, branch_id, sorted(by_branch[branch_id]), "SOURCE_SPAN_OVERLAPS_TARGET_STEPS"))
            continue
        procedure_branches = sorted(
            branch_id for branch_id in target["branch_ids"]
            if maps["branch_by_id"][branch_id][0] == procedure_id
        )
        if procedure_branches:
            for branch_id in procedure_branches:
                branch_steps = sorted(
                    step_id for step_id in target["step_ids"]
                    if maps["step_by_id"][step_id][:2] == (procedure_id, branch_id)
                )
                contexts.append((procedure_id, branch_id, branch_steps, "BUNDLE_LEVEL_TARGET_FALLBACK_NO_EXACT_STEP_OVERLAP"))
        else:
            contexts.append((procedure_id, None, [], "PROCEDURE_LEVEL_NON_STEP_CLAIM"))

    require(contexts, f"{record['id']} / {assertion_id}: no target context")
    output = []
    for route in sorted(rendered_occurrence_ids):
        for procedure_id, branch_id, step_ids, binding_basis in contexts:
            procedure = maps["procedure_by_id"][procedure_id]
            refs = sorted(set(page.get("authority_refs", [])) | set(procedure.get("authority_refs", [])))
            context_id = stable_id(
                "CTX-", "host-docs-p1-assertion-context-v1", assertion_id, route,
                procedure_id, branch_id or "", ",".join(step_ids), target["procedure_field"],
            )
            semantic_id = stable_id("SEM-", "host-docs-p1-semantic-record-v1", context_id)
            output.append({
                "id": context_id,
                "raw_occurrence_id": raw_occurrence_id,
                "rendered_occurrence_id": rendered_occurrence_ids[route],
                "route": route,
                "procedure_id": procedure_id,
                "branch_id": branch_id,
                "step_ids": step_ids,
                "procedure_field": target["procedure_field"],
                "binding_basis": binding_basis,
                "authority_boundary": {
                    **copy.deepcopy(authority_boundary),
                    "authority_refs": refs,
                },
                "planned_method": copy.deepcopy(planned_method),
                "semantic_record": initial_semantic_record(semantic_id),
            })
    return sorted(output, key=lambda item: item["id"])


def initial_semantic_record(record_id: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "required": True,
        "scope": SEMANTIC_SCOPE,
        "status": "UNVALIDATED",
        "score": None,
        "rationale": None,
        "finding_class": None,
        "evidence_refs": [],
        "correction_id": None,
        "retest_id": None,
        "not_applicable_decision_ref": None,
    }


def assertion_key(kind: str, segment: Segment) -> str:
    semantic_basis = "\0".join([
        kind,
        "/".join(segment.heading_path),
        segment.local_context or "",
        normalize_prose(segment.text_exact),
    ])
    return kind.lower().replace("_", "-") + "-" + sha256_text(semantic_basis)[:12]


def atomic_source_binding(assertion_id: str, source: SourceFile, segment: Segment) -> dict[str, Any]:
    exact = extract_exact(
        source, segment.line_start, segment.column_start,
        segment.line_end, segment.column_end,
    )
    require(exact == segment.text_exact, f"{assertion_id}: source slice mismatch")
    return {
        "id": stable_id(
            "ASRC-", "host-docs-p1-atomic-source-v1", assertion_id, source.path,
            segment.heading_path, segment.local_context or "", sha256_text(exact),
        ),
        "file": source.path,
        "line_start": segment.line_start,
        "column_start": segment.column_start,
        "line_end": segment.line_end,
        "column_end": segment.column_end,
        "source_type": source_type_for(source.path),
        "source_file_sha256": source.sha256,
        "source_span_sha256": sha256_text(exact),
        "heading_path": list(segment.heading_path),
        "heading_path_state": "EXACT_MARKDOWN_HEADING_PATH" if segment.heading_path else "NO_MARKDOWN_HEADING_IN_SOURCE",
        "local_context": segment.local_context,
        "block_type": segment.block_type,
    }


def raw_occurrence(assertion_id: str, binding: dict[str, Any]) -> dict[str, Any]:
    occurrence_id = stable_id(
        "RAW-", "host-docs-p1-raw-assertion-occurrence-v1", assertion_id,
        binding["file"], binding["source_span_sha256"], "/".join(binding["heading_path"]),
    )
    return {
        "id": occurrence_id,
        "source_binding_id": binding["id"],
        "file": binding["file"],
        "heading_path": copy.deepcopy(binding["heading_path"]),
        "line_start": binding["line_start"],
        "column_start": binding["column_start"],
        "line_end": binding["line_end"],
        "column_end": binding["column_end"],
        "source_span_sha256": binding["source_span_sha256"],
    }


def rendered_occurrences(assertion_id: str, routes: list[str], page_id: str) -> list[dict[str, Any]]:
    return [{
        "id": stable_id("RND-", "host-docs-p1-rendered-assertion-occurrence-v1", assertion_id, route),
        "route": route,
        "page_id": page_id,
        "status": "UNVALIDATED",
        "evidence_refs": [],
        "review_state": "RENDERED_CONTEXT_REVIEW_PENDING",
    } for route in sorted(set(routes))]


def exact_legacy_duplicate(
    segment: Segment,
    file: str,
    legacy_claims: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    return legacy_overlap_for(segment, file, legacy_claims)


def build_bundle_and_assertions(
    record: dict[str, Any],
    raw_record: dict[str, Any],
    baseline: dict[str, Any],
    maps: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    page, routes = page_and_routes(record, maps)
    discovery_binding, effective_bindings = source_bindings_for(record, routes, maps)
    primary = [item for item in effective_bindings if item["primary_for_assertion_decomposition"]]
    require(len(primary) == 1, f"{record['id']}: expected exactly one primary effective source")
    primary_binding = primary[0]
    source = load_source(primary_binding["file"])
    selected, excluded = classify_source_span(
        source, primary_binding["line_start"], primary_binding["line_end"]
    )
    legacy_claims = baseline["claims"]
    assertions: list[dict[str, Any]] = []
    exact_duplicate_exclusions: list[dict[str, Any]] = []
    deferred_exact_duplicates: list[tuple[Segment, list[str], list[str]]] = []
    parent_kind = record["original_kind"]
    authority = raw_record["authority"]
    authority_boundary = {
        "state": authority["state"],
        "claim_limit": authority["claim_limit"],
        "candidate_sources": copy.deepcopy(authority["suggested_references"]),
        "owner_role": "HOST_DOCS_SOURCE_OWNER_UNASSIGNED",
        "decision_id": "AUTH-QUESTION-" + record["id"],
        "confirmed_source_identity": None,
    }
    planned_method = copy.deepcopy(raw_record["validation_method"])

    for segment in selected:
        overlapping_legacy, exact_legacy = exact_legacy_duplicate(segment, source.path, legacy_claims)
        if exact_legacy:
            deferred_exact_duplicates.append((segment, overlapping_legacy, exact_legacy))
            continue
        kind = assertion_kind(parent_kind, segment)
        key = assertion_key(kind, segment)
        assertion_id = stable_id(
            "AST-", "host-docs-p1-material-assertion-v1", record["id"], key
        )
        binding = atomic_source_binding(assertion_id, source, segment)
        raw = raw_occurrence(assertion_id, binding)
        rendered = rendered_occurrences(assertion_id, routes, page["id"])
        rendered_ids = {item["route"]: item["id"] for item in rendered}
        contexts = assertion_target_contexts(
            assertion_id, record, segment, source.path, raw["id"], rendered_ids,
            page, maps, authority_boundary, planned_method,
        )
        assertions.append({
            "id": assertion_id,
            "assertion_key": key,
            "bundle_id": stable_id("CLM-", "host-docs-p1-material-claim-v1", record["id"]),
            "source_record_id": record["id"],
            "kind": kind,
            "text_exact": segment.text_exact,
            "text_sha256": sha256_text(segment.text_exact),
            "source_binding": binding,
            "raw_occurrence": raw,
            "rendered_occurrences": rendered,
            "context_bindings": contexts,
            "legacy_overlap_claim_ids": overlapping_legacy,
            "authority_boundary": authority_boundary,
            "planned_method": planned_method,
            "source_review_state_ref": record["id"],
            "source_alignment_disposition": None,
            "execution_unit_effect": EXECUTION_UNIT_EFFECT,
            "status": "UNVALIDATED",
            "attempt_ids": [],
            "issue_ids": [],
            "correction_ids": [],
            "retest_ids": [],
            "atomicity_rationale": (
                "Exact authored Markdown semantic block retained as one independently scorable boundary."
                if segment.block_type != "LONG_PARAGRAPH_ASSERTION"
                else "A broad prose block was divided only at an explicit authored sentence boundary; the exact substring remains source-bound."
            ),
        })

    # Exact legacy semantic duplicates are excluded only when another independently
    # scorable assertion remains.  If a material parent would otherwise become empty,
    # retain the most specific exact block and expose the overlap for later canonical
    # deduplication rather than silently dropping a reconciled material record.
    if not assertions and deferred_exact_duplicates:
        deferred_exact_duplicates.sort(key=lambda item: (
            item[0].line_end - item[0].line_start,
            len(item[0].text_exact),
            item[0].line_start,
        ))
        segment, overlapping_legacy, exact_legacy = deferred_exact_duplicates.pop(0)
        kind = assertion_kind(parent_kind, segment)
        key = assertion_key(kind, segment)
        assertion_id = stable_id("AST-", "host-docs-p1-material-assertion-v1", record["id"], key)
        binding = atomic_source_binding(assertion_id, source, segment)
        raw = raw_occurrence(assertion_id, binding)
        rendered = rendered_occurrences(assertion_id, routes, page["id"])
        rendered_ids = {item["route"]: item["id"] for item in rendered}
        contexts = assertion_target_contexts(
            assertion_id, record, segment, source.path, raw["id"], rendered_ids,
            page, maps, authority_boundary, planned_method,
        )
        assertions.append({
            "id": assertion_id,
            "assertion_key": key,
            "bundle_id": stable_id("CLM-", "host-docs-p1-material-claim-v1", record["id"]),
            "source_record_id": record["id"],
            "kind": kind,
            "text_exact": segment.text_exact,
            "text_sha256": sha256_text(segment.text_exact),
            "source_binding": binding,
            "raw_occurrence": raw,
            "rendered_occurrences": rendered,
            "context_bindings": contexts,
            "legacy_overlap_claim_ids": overlapping_legacy,
            "authority_boundary": authority_boundary,
            "planned_method": planned_method,
            "source_review_state_ref": record["id"],
            "source_alignment_disposition": None,
            "execution_unit_effect": EXECUTION_UNIT_EFFECT,
            "status": "UNVALIDATED",
            "attempt_ids": [],
            "issue_ids": [],
            "correction_ids": [],
            "retest_ids": [],
            "atomicity_rationale": "Retained because excluding every exact legacy overlap would leave a reconciled material parent without an independently reviewable child; integration must explicitly deduplicate it.",
        })

    for segment, overlapping, exact in deferred_exact_duplicates:
        exclusion_id = stable_id(
            "EXC-", "host-docs-p1-atomic-exclusion-v1", record["id"], source.path,
            segment.line_start, segment.column_start, segment.line_end, segment.column_end,
            sha256_text(segment.text_exact), "EXACT_LEGACY_SEMANTIC_DUPLICATE",
        )
        exact_duplicate_exclusions.append({
            "id": exclusion_id,
            "file": source.path,
            "line_start": segment.line_start,
            "column_start": segment.column_start,
            "line_end": segment.line_end,
            "column_end": segment.column_end,
            "text_exact": segment.text_exact,
            "text_sha256": sha256_text(segment.text_exact),
            "reason": "EXACT_LEGACY_SEMANTIC_DUPLICATE",
            "rationale": "An existing frozen legacy occurrence has the same normalized exact prose and remains the canonical semantic occurrence; no duplicate assertion result is created.",
            "legacy_claim_ids": exact,
            "overlapping_legacy_claim_ids": overlapping,
        })

    require(assertions, f"{record['id']}: material bundle has no atomic assertion")
    assertion_ids = [item["id"] for item in assertions]
    require(len(assertion_ids) == len(set(assertion_ids)), f"{record['id']}: atomic assertion ID collision")

    structural_exclusions = []
    for item in excluded:
        exclusion_id = stable_id(
            "EXC-", "host-docs-p1-atomic-exclusion-v1", record["id"], source.path,
            item["line_start"], item["line_end"], item["text_sha256"], item["reason"],
        )
        structural_exclusions.append({
            "id": exclusion_id,
            "file": source.path,
            "line_start": item["line_start"],
            "column_start": 1,
            "line_end": item["line_end"],
            "column_end": len(source.lines[item["line_end"] - 1]),
            "text_exact": item["text_exact"],
            "text_sha256": item["text_sha256"],
            "reason": item["reason"],
            "rationale": item["rationale"],
            "legacy_claim_ids": [],
            "overlapping_legacy_claim_ids": [],
        })
    exclusions = sorted(structural_exclusions + exact_duplicate_exclusions, key=lambda item: item["id"])

    bundle_id = stable_id("CLM-", "host-docs-p1-material-claim-v1", record["id"])
    bundle = {
        "id": bundle_id,
        "origin": "RECONCILED_MATERIAL",
        "record_role": "DISCOVERY_BUNDLE_NOT_ATOMIC_SEMANTIC_RESULT",
        "source_record_id": record["id"],
        "source_set": record["source_set"],
        "reconciliation_classification": "ADD_MATERIAL_CLAIM",
        "discovery_summary": record["source_span_review"].get("corrected_summary") or record["original_summary"],
        "discovery_source_binding": discovery_binding,
        "effective_source_bindings": effective_bindings,
        "source_review_state": copy.deepcopy(record["source_span_review"]),
        "source_alignment_disposition": None,
        "page_id": page["id"],
        "route": page["route"],
        "target_bindings": grouped_target_bindings(record, maps),
        "legacy_overlap": copy.deepcopy(record["legacy_overlap"]),
        "primary_treatment": "non-executable-claim-bundle",
        "execution_unit_effect": EXECUTION_UNIT_EFFECT,
        "authority_boundary": authority_boundary,
        "planned_method": planned_method,
        "assertion_ids": sorted(assertion_ids),
        "exclusions": exclusions,
        "decomposition_policy": {
            "unit": "AUTHORED_MARKDOWN_SEMANTIC_BLOCK_WITH_SELECTIVE_LONG_PROSE_SPLIT",
            "sentence_tokenizer_for_every_sentence": False,
            "table_rows": "ONE_ROW_PER_ASSERTION_UNLESS_EXACT_LEGACY_DUPLICATE",
            "list_items": "ONE_AUTHORED_ITEM_PER_ASSERTION",
            "code_forms": "ONE_LOGICAL_SOURCE_FORM_PER_ASSERTION_WITH_CONTINUATIONS_GROUPED",
            "long_prose": "SPLIT_ONLY_WHEN_MORE_THAN_TWO_SENTENCES_OR_MORE_THAN_420_CHARACTERS",
            "structural_and_duplicate_exclusions_recorded": True,
        },
    }
    return bundle, sorted(assertions, key=lambda item: item["id"])


def validate_semantic(record: dict[str, Any], context: str) -> None:
    exact_keys(record, {
        "id", "required", "scope", "status", "score", "rationale",
        "finding_class", "evidence_refs", "correction_id", "retest_id",
        "not_applicable_decision_ref",
    }, context)
    require(record["id"].startswith("SEM-"), f"{context}: invalid semantic ID")
    require(record["required"] is True and record["scope"] == SEMANTIC_SCOPE,
            f"{context}: invalid required/scope")
    status = record["status"]
    score = record["score"]
    require(status in VV_STATUSES, f"{context}: invalid status {status!r}")
    require(score in {None, 1, 2, 3}, f"{context}: invalid score {score!r}")
    evidence = record["evidence_refs"]
    require(isinstance(evidence, list) and all(isinstance(item, str) and item for item in evidence),
            f"{context}: invalid evidence refs")
    if status == "UNVALIDATED":
        require(score is None and record["rationale"] is None and record["finding_class"] is None
                and evidence == [] and record["correction_id"] is None and record["retest_id"] is None
                and record["not_applicable_decision_ref"] is None,
                f"{context}: UNVALIDATED truth-table violation")
    elif status == "PASS":
        require(score == 3 and isinstance(record["rationale"], str) and record["rationale"]
                and record["finding_class"] == "EXACTLY_SUPPORTED" and evidence
                and record["not_applicable_decision_ref"] is None,
                f"{context}: PASS truth-table violation")
    elif status == "FAIL":
        require(score in {1, 2} and isinstance(record["rationale"], str) and record["rationale"]
                and record["finding_class"] in {"NO_SUPPORT", "PARTIAL_INCORRECT_OR_BROKEN"}
                and evidence and record["not_applicable_decision_ref"] is None,
                f"{context}: FAIL truth-table violation")
        require((score == 1) == (record["finding_class"] == "NO_SUPPORT"),
                f"{context}: FAIL score/finding mismatch")
    elif status == "BLOCKED":
        require(score is None and isinstance(record["rationale"], str) and record["rationale"]
                and record["finding_class"] == "AUTHORITY_ACCESS_OR_SAFETY_BLOCKER"
                and evidence and record["retest_id"] is None
                and record["not_applicable_decision_ref"] is None,
                f"{context}: BLOCKED truth-table violation")
    elif status == "NOT_APPLICABLE":
        require(score is None and isinstance(record["rationale"], str) and record["rationale"]
                and record["finding_class"] == "AUTHORIZED_NOT_APPLICABLE"
                and evidence and isinstance(record["not_applicable_decision_ref"], str)
                and record["not_applicable_decision_ref"]
                and record["correction_id"] is None and record["retest_id"] is None,
                f"{context}: NOT_APPLICABLE truth-table violation")
    elif status == "STALE":
        require(score is None and isinstance(record["rationale"], str) and record["rationale"]
                and record["finding_class"] == "STALE_SOURCE_AUTHORITY_OR_EVIDENCE"
                and evidence and record["not_applicable_decision_ref"] is None,
                f"{context}: STALE truth-table violation")


BUNDLE_FIELDS = {
    "id", "origin", "record_role", "source_record_id", "source_set",
    "reconciliation_classification", "discovery_summary", "discovery_source_binding",
    "effective_source_bindings", "source_review_state", "source_alignment_disposition",
    "page_id", "route", "target_bindings", "legacy_overlap", "primary_treatment",
    "execution_unit_effect", "authority_boundary", "planned_method", "assertion_ids",
    "exclusions", "decomposition_policy",
}
ASSERTION_FIELDS = {
    "id", "assertion_key", "bundle_id", "source_record_id", "kind", "text_exact",
    "text_sha256", "source_binding", "raw_occurrence", "rendered_occurrences",
    "context_bindings", "legacy_overlap_claim_ids", "authority_boundary", "planned_method",
    "source_review_state_ref", "source_alignment_disposition", "execution_unit_effect",
    "status", "attempt_ids", "issue_ids", "correction_ids", "retest_ids",
    "atomicity_rationale",
}


def validate_source_binding(binding: dict[str, Any], context: str, maps: dict[str, Any]) -> None:
    exact_keys(binding, {
        "id", "role", "primary_for_assertion_decomposition", "file", "line_start", "line_end",
        "source_type", "source_file_sha256", "source_span_sha256", "page_id", "fragment_id",
        "rendered_routes",
    }, context)
    source = load_source(binding["file"])
    require(source.sha256 == binding["source_file_sha256"], f"{context}: source file hash mismatch")
    text = "\n".join(source.lines[binding["line_start"] - 1:binding["line_end"]])
    require(sha256_text(text) == binding["source_span_sha256"], f"{context}: source span hash mismatch")
    page = maps["page_by_file"].get(binding["file"])
    fragment = maps["fragment_by_file"].get(binding["file"])
    require(binding["page_id"] == (page["id"] if page else None), f"{context}: page owner mismatch")
    require(binding["fragment_id"] == (fragment["id"] if fragment else None), f"{context}: fragment owner mismatch")
    require(binding["rendered_routes"] == sorted(set(binding["rendered_routes"])) and binding["rendered_routes"],
            f"{context}: rendered routes invalid")


def validate_authority_boundary(boundary: dict[str, Any], context: str, *, with_refs: bool) -> None:
    fields = {
        "state", "claim_limit", "candidate_sources", "owner_role", "decision_id",
        "confirmed_source_identity",
    }
    if with_refs:
        fields.add("authority_refs")
    exact_keys(boundary, fields, context)
    require(boundary["state"] in {"CONFIRMED", "PENDING_OWNER", "ADVISORY", "NOT_IDENTIFIED", "CONTRADICTED"},
            f"{context}: invalid authority state")
    require(isinstance(boundary["claim_limit"], str) and boundary["claim_limit"],
            f"{context}: empty claim limit")
    require(isinstance(boundary["candidate_sources"], list)
            and all(isinstance(item, str) and item for item in boundary["candidate_sources"]),
            f"{context}: invalid candidate sources")
    require(isinstance(boundary["owner_role"], str) and boundary["owner_role"]
            and isinstance(boundary["decision_id"], str) and boundary["decision_id"],
            f"{context}: untracked authority question")
    if boundary["state"] == "CONFIRMED":
        require(isinstance(boundary["confirmed_source_identity"], str)
                and boundary["confirmed_source_identity"],
                f"{context}: confirmed authority has no exact source identity")
    else:
        require(boundary["confirmed_source_identity"] is None,
                f"{context}: unresolved authority invents a confirmed source")
    if with_refs:
        require(boundary["authority_refs"] == sorted(set(boundary["authority_refs"])),
                f"{context}: authority refs are not sorted unique")


def validate_planned_method(method: dict[str, Any], context: str) -> None:
    exact_keys(method, {"semantic", "runtime", "source"}, context)
    require(all(isinstance(method[key], str) and method[key] for key in ("semantic", "runtime", "source")),
            f"{context}: planned method is incomplete")


def validate_candidate(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    raw: dict[str, Any],
    reconcile: dict[str, Any],
) -> None:
    exact_keys(candidate, {
        "schema_version", "record_type", "state", "mode", "created_at",
        "execution_performed", "browser_or_rendered_execution_performed", "human_acceptance",
        "source_identity", "topology_denominators", "method", "semantic_truth_table",
        "source_alignment_disposition_schema",
        "counts", "discovery_bundles", "atomic_assertions", "unresolved_blockers", "integrity",
    }, "candidate")
    require(candidate["schema_version"] == "host-docs-p1-atomic-semantic-candidate/1.0",
            "unexpected candidate schema")
    require(candidate["record_type"] == "HOST_DOCS_P1_ATOMIC_SEMANTIC_CANDIDATE",
            "unexpected candidate type")
    require(candidate["state"] == "DRAFT_NOT_FROZEN" and candidate["mode"] == "LOCAL_STATIC_SOURCE_RECONCILIATION_ONLY",
            "candidate state/mode overclaims")
    require(candidate["execution_performed"] is False
            and candidate["browser_or_rendered_execution_performed"] is False
            and candidate["human_acceptance"] == "NOT_DECIDED",
            "candidate overclaims execution or acceptance")
    serialized = canonical_bytes(candidate).decode("utf-8")
    for forbidden_path in ("/Users/", "/private/tmp/", "/root/", "/home/"):
        require(forbidden_path not in serialized,
                f"candidate exposes a machine-local/restricted path prefix: {forbidden_path}")
    require("-----BEGIN PRIVATE KEY-----" not in serialized
            and "-----BEGIN OPENSSH PRIVATE KEY-----" not in serialized,
            "candidate exposes private-key material")
    exact_keys(candidate["source_identity"], {
        "target", "baseline_id", "inputs", "prepared_by", "independence_limit",
        "created_at_basis", "rejected_input_disposition",
    }, "candidate.source_identity")
    require(candidate["source_identity"]["inputs"] == EXPECTED_INPUT_SHA256,
            "candidate input pins differ")
    require(candidate["source_identity"]["target"] == EXPECTED_TARGET,
            "candidate target pin differs")
    require(candidate["source_alignment_disposition_schema"] == {
        "initial_value": None,
        "object_fields": ["decision", "evidence_refs", "reviewed_at", "reviewer", "role"],
        "allowed_decisions": ["APPROVED_CROSS_SECTION_ROLE", "APPROVED_SHARED_FRAGMENT", "CORRECTED_TO_EXACT"],
        "rule": "A non-null value requires an independent reviewer, role, UTC timestamp, and nonempty evidence refs; raw source-review state strings are forbidden.",
    }, "source-alignment disposition schema differs from canonical reviewer contract")
    maps = topology_maps(baseline)
    topology = candidate["topology_denominators"]
    require(topology == {
        "pages": 39, "procedures": 82, "branches": 193, "steps": 454,
        "new_executable_test_units": 0,
    }, "candidate topology changed")

    material_records = [item for item in reconcile["reconciliation"] if item["classification"] == "ADD_MATERIAL_CLAIM"]
    material_ids = sorted(item["id"] for item in material_records)
    bundles = candidate["discovery_bundles"]
    assertions = candidate["atomic_assertions"]
    require(len(bundles) == 104 and len({item["id"] for item in bundles}) == 104,
            "candidate does not have 104 unique bundles")
    require(sorted(item["source_record_id"] for item in bundles) == material_ids,
            "candidate bundle source-record set differs")
    bundle_by_id = {item["id"]: item for item in bundles}
    assertion_by_id = {item["id"]: item for item in assertions}
    require(len(assertion_by_id) == len(assertions), "duplicate atomic assertion ID")
    require(assertions, "candidate has no assertions")
    raw_by_id = {item["id"]: item for item in raw["gaps"]}
    reconcile_by_id = {item["id"]: item for item in material_records}

    all_context_ids: set[str] = set()
    all_semantic_ids: set[str] = set()
    all_raw_ids: set[str] = set()
    all_rendered_ids: set[str] = set()
    for bundle in bundles:
        exact_keys(bundle, BUNDLE_FIELDS, f"bundle {bundle.get('id')}")
        source_id = bundle["source_record_id"]
        record = reconcile_by_id[source_id]
        require(bundle["id"] == stable_id("CLM-", "host-docs-p1-material-claim-v1", source_id),
                f"{source_id}: unstable bundle ID")
        require(bundle["origin"] == "RECONCILED_MATERIAL"
                and bundle["record_role"] == "DISCOVERY_BUNDLE_NOT_ATOMIC_SEMANTIC_RESULT"
                and bundle["reconciliation_classification"] == "ADD_MATERIAL_CLAIM",
                f"{source_id}: wrong bundle role")
        require("semantic_assessment" not in bundle and "status" not in bundle,
                f"{source_id}: discovery bundle illegally carries result")
        require(bundle["execution_unit_effect"] == EXECUTION_UNIT_EFFECT,
                f"{source_id}: bundle creates executable unit")
        require(bundle["source_review_state"] == record["source_span_review"],
                f"{source_id}: source review state changed")
        require(bundle["source_alignment_disposition"] is None,
                f"{source_id}: unreviewed alignment disposition is not null")
        validate_authority_boundary(bundle["authority_boundary"], f"{source_id}.authority", with_refs=False)
        validate_planned_method(bundle["planned_method"], f"{source_id}.method")
        validate_source_binding(bundle["discovery_source_binding"], f"{source_id}.discovery", maps)
        for binding in bundle["effective_source_bindings"]:
            validate_source_binding(binding, f"{source_id}.effective", maps)
        require(sum(item["primary_for_assertion_decomposition"] for item in bundle["effective_source_bindings"]) == 1,
                f"{source_id}: no unique primary effective source")
        require(bundle["assertion_ids"] == sorted(set(bundle["assertion_ids"])) and bundle["assertion_ids"],
                f"{source_id}: invalid bundle assertion IDs")
        require(all(assertion_id in assertion_by_id for assertion_id in bundle["assertion_ids"]),
                f"{source_id}: dangling assertion ID")
        require(all(assertion_by_id[item]["bundle_id"] == bundle["id"] for item in bundle["assertion_ids"]),
                f"{source_id}: assertion reverse link mismatch")
        primary_effective = next(
            item for item in bundle["effective_source_bindings"]
            if item["primary_for_assertion_decomposition"]
        )
        covered_lines: set[int] = set()
        for assertion_id in bundle["assertion_ids"]:
            child_source = assertion_by_id[assertion_id]["source_binding"]
            require(child_source["file"] == primary_effective["file"],
                    f"{source_id}: assertion is not bound to the primary effective source")
            require(primary_effective["line_start"] <= child_source["line_start"]
                    <= child_source["line_end"] <= primary_effective["line_end"],
                    f"{source_id}: assertion escapes its effective source span")
            covered_lines.update(range(child_source["line_start"], child_source["line_end"] + 1))
        for exclusion in bundle["exclusions"]:
            exact_keys(exclusion, {
                "id", "file", "line_start", "column_start", "line_end", "column_end",
                "text_exact", "text_sha256", "reason", "rationale", "legacy_claim_ids",
                "overlapping_legacy_claim_ids",
            }, f"{source_id}.exclusion")
            source = load_source(exclusion["file"])
            require(extract_exact(
                source, exclusion["line_start"], exclusion["column_start"],
                exclusion["line_end"], exclusion["column_end"],
            ) == exclusion["text_exact"], f"{source_id}: exclusion source mismatch")
            require(sha256_text(exclusion["text_exact"]) == exclusion["text_sha256"],
                    f"{source_id}: exclusion hash mismatch")
            require(exclusion["file"] == primary_effective["file"],
                    f"{source_id}: exclusion is not on the primary effective source")
            covered_lines.update(range(exclusion["line_start"], exclusion["line_end"] + 1))
        require(covered_lines == set(range(primary_effective["line_start"], primary_effective["line_end"] + 1)),
                f"{source_id}: assertion/exclusion source-line coverage is incomplete")

    for assertion in assertions:
        exact_keys(assertion, ASSERTION_FIELDS, f"assertion {assertion.get('id')}")
        require(assertion["bundle_id"] in bundle_by_id, f"{assertion['id']}: unknown bundle")
        require(assertion["source_record_id"] == bundle_by_id[assertion["bundle_id"]]["source_record_id"],
                f"{assertion['id']}: source-record mismatch")
        require(assertion["kind"] in ASSERTION_KINDS, f"{assertion['id']}: invalid kind")
        expected_id = stable_id(
            "AST-", "host-docs-p1-material-assertion-v1",
            assertion["source_record_id"], assertion["assertion_key"],
        )
        require(assertion["id"] == expected_id, f"{assertion['id']}: unstable assertion ID")
        require(assertion["text_exact"] and sha256_text(assertion["text_exact"]) == assertion["text_sha256"],
                f"{assertion['id']}: exact text hash mismatch")
        binding = assertion["source_binding"]
        exact_keys(binding, {
            "id", "file", "line_start", "column_start", "line_end", "column_end",
            "source_type", "source_file_sha256", "source_span_sha256", "heading_path",
            "heading_path_state", "local_context", "block_type",
        }, f"{assertion['id']}.source")
        source = load_source(binding["file"])
        require(source.sha256 == binding["source_file_sha256"], f"{assertion['id']}: source file changed")
        exact = extract_exact(
            source, binding["line_start"], binding["column_start"],
            binding["line_end"], binding["column_end"],
        )
        require(exact == assertion["text_exact"] and sha256_text(exact) == binding["source_span_sha256"],
                f"{assertion['id']}: exact bounded source mismatch")
        require(binding["heading_path"] == list(source.heading_paths[binding["line_start"] - 1]),
                f"{assertion['id']}: heading path mismatch")
        require(assertion["execution_unit_effect"] == EXECUTION_UNIT_EFFECT
                and assertion["status"] == "UNVALIDATED" and assertion["attempt_ids"] == [],
                f"{assertion['id']}: assertion overclaims execution")
        require(assertion["source_alignment_disposition"] is None,
                f"{assertion['id']}: alignment result was invented")
        validate_authority_boundary(assertion["authority_boundary"], f"{assertion['id']}.authority", with_refs=False)
        validate_planned_method(assertion["planned_method"], f"{assertion['id']}.method")
        raw_occ = assertion["raw_occurrence"]
        require(raw_occ["source_binding_id"] == binding["id"], f"{assertion['id']}: raw occurrence mismatch")
        require(raw_occ["id"] not in all_raw_ids, f"{assertion['id']}: duplicate raw occurrence ID")
        all_raw_ids.add(raw_occ["id"])
        rendered_ids = {item["id"] for item in assertion["rendered_occurrences"]}
        require(rendered_ids and not rendered_ids.intersection(all_rendered_ids),
                f"{assertion['id']}: duplicate/no rendered occurrences")
        all_rendered_ids.update(rendered_ids)
        require(assertion["context_bindings"], f"{assertion['id']}: no target context")
        for context in assertion["context_bindings"]:
            exact_keys(context, {
                "id", "raw_occurrence_id", "rendered_occurrence_id", "route", "procedure_id",
                "branch_id", "step_ids", "procedure_field", "binding_basis",
                "authority_boundary", "planned_method", "semantic_record",
            }, f"{assertion['id']}.context")
            require(context["id"] not in all_context_ids, f"{assertion['id']}: duplicate context ID")
            all_context_ids.add(context["id"])
            require(context["raw_occurrence_id"] == raw_occ["id"]
                    and context["rendered_occurrence_id"] in rendered_ids,
                    f"{assertion['id']}: context occurrence mismatch")
            procedure = maps["procedure_by_id"].get(context["procedure_id"])
            require(procedure is not None and procedure["page_id"] == bundle_by_id[assertion["bundle_id"]]["page_id"],
                    f"{assertion['id']}: wrong procedure owner")
            if context["branch_id"] is not None:
                require(maps["branch_by_id"].get(context["branch_id"], (None,))[0] == context["procedure_id"],
                        f"{assertion['id']}: wrong branch owner")
            for step_id in context["step_ids"]:
                owner = maps["step_by_id"].get(step_id)
                require(owner is not None and owner[0] == context["procedure_id"]
                        and owner[1] == context["branch_id"],
                        f"{assertion['id']}: wrong step owner")
            validate_authority_boundary(
                context["authority_boundary"], f"{assertion['id']}.context.authority", with_refs=True
            )
            validate_planned_method(context["planned_method"], f"{assertion['id']}.context.method")
            semantic = context["semantic_record"]
            require(semantic["id"] not in all_semantic_ids, f"{assertion['id']}: semantic result shared")
            all_semantic_ids.add(semantic["id"])
            validate_semantic(semantic, f"{assertion['id']}.semantic")
            if semantic["status"] == "PASS":
                boundary = context["authority_boundary"]
                require(boundary["state"] == "CONFIRMED"
                        and isinstance(boundary["confirmed_source_identity"], str)
                        and boundary["confirmed_source_identity"],
                        f"{assertion['id']}: semantic PASS lacks confirmed applicable authority")

    require(set(assertion_by_id) == {item for bundle in bundles for item in bundle["assertion_ids"]},
            "bundle/assertion sets do not reconcile")
    counts = candidate["counts"]
    require(counts["discovery_bundles"] == 104
            and counts["atomic_assertions"] == len(assertions)
            and counts["raw_occurrences"] == len(all_raw_ids)
            and counts["rendered_occurrences"] == len(all_rendered_ids)
            and counts["target_context_bindings"] == len(all_context_ids)
            and counts["semantic_records"] == len(all_semantic_ids),
            "candidate counts do not reconcile")
    require(counts["semantic_statuses"] == {"UNVALIDATED": len(all_semantic_ids)},
            "semantic status count overclaims")
    require(counts["semantic_scores"] == {"unassessed_null": len(all_semantic_ids)},
            "semantic score count overclaims")
    require(counts["source_alignment_dispositions"] == {
        "bundle_pending_null": 104,
        "bundle_structured": 0,
        "assertion_pending_null": len(assertions),
        "assertion_structured": 0,
    },
            "source alignment disposition count differs")
    require(counts["source_hash_coverage"] == {
        "bundle_discovery_bindings_verified": 104,
        "effective_bindings_verified": sum(len(item["effective_source_bindings"]) for item in bundles),
        "atomic_assertion_spans_verified": len(assertions),
        "bundles_with_one_or_more_assertions": 104,
    }, "source hash coverage count differs")
    require(counts["unresolved_blocker_classes"] == len(candidate["unresolved_blockers"]) == 6,
            "blocker-class count differs")
    plan_value = copy.deepcopy(candidate)
    integrity = plan_value.pop("integrity")
    require(integrity["plan_sha256"] == sha256_bytes(canonical_bytes(plan_value)),
            "candidate plan digest mismatch")


def make_truth_table_projection() -> list[dict[str, Any]]:
    return [
        {"status": "UNVALIDATED", "allowed_scores": [None], "evidence": "empty", "rationale": "null"},
        {"status": "PASS", "allowed_scores": [3], "evidence": "nonempty", "rationale": "nonempty", "finding_class": "EXACTLY_SUPPORTED"},
        {"status": "FAIL", "allowed_scores": [1, 2], "evidence": "nonempty", "rationale": "nonempty", "finding_classes": ["NO_SUPPORT", "PARTIAL_INCORRECT_OR_BROKEN"]},
        {"status": "BLOCKED", "allowed_scores": [None], "evidence": "nonempty", "rationale": "nonempty", "finding_class": "AUTHORITY_ACCESS_OR_SAFETY_BLOCKER"},
        {"status": "NOT_APPLICABLE", "allowed_scores": [None], "evidence": "nonempty_with_authorized_decision", "rationale": "nonempty", "finding_class": "AUTHORIZED_NOT_APPLICABLE"},
        {"status": "STALE", "allowed_scores": [None], "evidence": "nonempty", "rationale": "nonempty", "finding_class": "STALE_SOURCE_AUTHORITY_OR_EVIDENCE"},
    ]


def build_candidate(
    baseline: dict[str, Any], raw: dict[str, Any], reconcile: dict[str, Any]
) -> dict[str, Any]:
    maps = topology_maps(baseline)
    raw_by_id = {item["id"]: item for item in raw["gaps"]}
    material = sorted(
        (item for item in reconcile["reconciliation"] if item["classification"] == "ADD_MATERIAL_CLAIM"),
        key=lambda item: item["id"],
    )
    require(len(material) == 104 and len({item["id"] for item in material}) == 104,
            "reconciliation material denominator is not 104")
    bundles: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    for record in material:
        require(record["id"] in raw_by_id, f"{record['id']}: missing raw gap")
        require(record["execution_unit_effect"] == EXECUTION_UNIT_EFFECT,
                f"{record['id']}: input creates executable unit")
        bundle, children = build_bundle_and_assertions(record, raw_by_id[record["id"]], baseline, maps)
        bundles.append(bundle)
        assertions.extend(children)

    bundles.sort(key=lambda item: item["id"])
    assertions.sort(key=lambda item: item["id"])
    raw_occurrences = len(assertions)
    rendered_count = sum(len(item["rendered_occurrences"]) for item in assertions)
    contexts = [context for item in assertions for context in item["context_bindings"]]
    kinds = dict(sorted(Counter(item["kind"] for item in assertions).items()))
    source_review_states = dict(sorted(Counter(item["source_review_state"]["state"] for item in bundles).items()))
    material_defects = [item for item in material if item["source_span_review"]["state"] != "EXACT_SOURCE_SPAN"]
    all_defects = [item for item in reconcile["reconciliation"] if item["source_span_review"]["state"] != "EXACT_SOURCE_SPAN"]
    canonical_alignment = Counter(item["source_alignment"] for item in baseline["claims"])
    alignment_review_required = (
        canonical_alignment["CROSS_SECTION_REVIEW_REQUIRED"]
        + canonical_alignment["SECTION_ONLY_REVIEW_REQUIRED"]
        + canonical_alignment["SPAN_ONLY_REVIEW_REQUIRED"]
    )
    exclusions = [item for bundle in bundles for item in bundle["exclusions"]]
    candidate: dict[str, Any] = {
        "schema_version": "host-docs-p1-atomic-semantic-candidate/1.0",
        "record_type": "HOST_DOCS_P1_ATOMIC_SEMANTIC_CANDIDATE",
        "state": "DRAFT_NOT_FROZEN",
        "mode": "LOCAL_STATIC_SOURCE_RECONCILIATION_ONLY",
        "created_at": baseline["created_at"],
        "execution_performed": False,
        "browser_or_rendered_execution_performed": False,
        "human_acceptance": "NOT_DECIDED",
        "source_identity": {
            "target": copy.deepcopy(EXPECTED_TARGET),
            "baseline_id": baseline["baseline_id"],
            "inputs": copy.deepcopy(EXPECTED_INPUT_SHA256),
            "prepared_by": "Codex atomic semantic reconciler",
            "independence_limit": "The same agent constructed and self-tested this isolated candidate; independent human review remains required.",
            "created_at_basis": "The deterministic created_at value is inherited from the exact canonical P1 draft; it is not a claim-execution timestamp.",
            "rejected_input_disposition": "The rejected claim builder/candidate are hash-pinned for provenance only; their bundle-level scoring schema and results are not imported.",
        },
        "topology_denominators": {
            "pages": 39,
            "procedures": 82,
            "branches": 193,
            "steps": 454,
            "new_executable_test_units": 0,
        },
        "method": {
            "parent_model": "Every ADD_MATERIAL_CLAIM record remains one unscored discovery bundle.",
            "assertion_model": "Exact authored Markdown semantic blocks are selected; unusually broad prose alone may split at exact sentence boundaries.",
            "context_model": "Each procedure/branch/rendered context has a distinct semantic record; results are never shared across contexts.",
            "exclusion_model": "Markdown structure, non-rendered comments, context-only lead-ins, and exact legacy semantic duplicates are explicitly retained with rationale.",
            "execution_boundary": "Atomic semantic records add no executable test unit and cannot directly carry runtime attempts.",
        },
        "semantic_truth_table": make_truth_table_projection(),
        "source_alignment_disposition_schema": {
            "initial_value": None,
            "object_fields": ["decision", "evidence_refs", "reviewed_at", "reviewer", "role"],
            "allowed_decisions": ["APPROVED_CROSS_SECTION_ROLE", "APPROVED_SHARED_FRAGMENT", "CORRECTED_TO_EXACT"],
            "rule": "A non-null value requires an independent reviewer, role, UTC timestamp, and nonempty evidence refs; raw source-review state strings are forbidden.",
        },
        "counts": {
            "discovery_bundles": len(bundles),
            "atomic_assertions": len(assertions),
            "raw_occurrences": raw_occurrences,
            "rendered_occurrences": rendered_count,
            "target_context_bindings": len(contexts),
            "semantic_records": len(contexts),
            "assertions_by_kind": kinds,
            "semantic_statuses": {"UNVALIDATED": len(contexts)},
            "semantic_scores": {"unassessed_null": len(contexts)},
            "source_review_states": source_review_states,
            "source_alignment_dispositions": {
                "bundle_pending_null": len(bundles),
                "bundle_structured": 0,
                "assertion_pending_null": len(assertions),
                "assertion_structured": 0,
            },
            "source_hash_coverage": {
                "bundle_discovery_bindings_verified": len(bundles),
                "effective_bindings_verified": sum(len(item["effective_source_bindings"]) for item in bundles),
                "atomic_assertion_spans_verified": len(assertions),
                "bundles_with_one_or_more_assertions": sum(bool(item["assertion_ids"]) for item in bundles),
            },
            "recorded_exclusions": len(exclusions),
            "exact_legacy_duplicate_exclusions": sum(item["reason"] == "EXACT_LEGACY_SEMANTIC_DUPLICATE" for item in exclusions),
            "new_executable_test_units": 0,
            "unresolved_blocker_classes": 6,
        },
        "discovery_bundles": bundles,
        "atomic_assertions": assertions,
        "unresolved_blockers": [
            {
                "id": "ATOMIC-BLOCK-MATERIAL-SOURCE-REVIEW",
                "class": "SOURCE_OR_TARGET_DEFECT",
                "count": len(material_defects),
                "source_record_ids": sorted(item["id"] for item in material_defects),
                "effect": "The exact source-review finding remains open; no affected assertion can PASS or be used to freeze P1 until independently dispositioned.",
            },
            {
                "id": "ATOMIC-BLOCK-OTHER-RECONCILIATION-DEFECTS",
                "class": "SOURCE_OR_TARGET_DEFECT_OUTSIDE_MATERIAL_ASSERTION_LAYER",
                "count": len(all_defects) - len(material_defects),
                "source_record_ids": sorted(
                    item["id"] for item in all_defects if item["id"] not in {entry["id"] for entry in material_defects}
                ),
                "effect": "These reconciled defects belong to procedure requirements or dispositions and remain P1 blockers outside this isolated candidate.",
            },
            {
                "id": "ATOMIC-BLOCK-CANONICAL-SOURCE-ALIGNMENT",
                "class": "INDEPENDENT_SOURCE_ALIGNMENT_REVIEW_PENDING",
                "count": alignment_review_required,
                "claim_states": {
                    "CROSS_SECTION_REVIEW_REQUIRED": canonical_alignment["CROSS_SECTION_REVIEW_REQUIRED"],
                    "SECTION_ONLY_REVIEW_REQUIRED": canonical_alignment["SECTION_ONLY_REVIEW_REQUIRED"],
                    "SPAN_ONLY_REVIEW_REQUIRED": canonical_alignment["SPAN_ONLY_REVIEW_REQUIRED"],
                },
                "effect": "Structured source_alignment_disposition remains null; these 113 canonical legacy occurrences require independent review before P1 freeze.",
            },
            {
                "id": "ATOMIC-BLOCK-DEFECT-ISSUE-LINKS",
                "class": "DURABLE_ISSUE_LINKS_PENDING",
                "count": len(all_defects),
                "source_record_ids": sorted(item["id"] for item in all_defects),
                "effect": "All 17 identified source/target defects still need durable issue IDs before a frozen package can expose closure, correction, and retest history.",
            },
            {
                "id": "ATOMIC-BLOCK-RENDERED-CONTEXT",
                "class": "RENDERED_CONTEXT_REVIEW_PENDING",
                "count": rendered_count,
                "effect": "Rendered occurrences are inventoried but not browser-reviewed; all semantic records remain UNVALIDATED with null score.",
            },
            {
                "id": "ATOMIC-BLOCK-AUTHORITY",
                "class": "PENDING_OWNER",
                "count": len(assertions),
                "effect": "Every material assertion requires a bounded confirmed authority source or owner decision before semantic PASS.",
            },
        ],
    }
    plan_value = copy.deepcopy(candidate)
    candidate["integrity"] = {
        "plan_sha256": sha256_bytes(canonical_bytes(plan_value)),
        "deterministic_serialization": "UTF-8_JSON_SORTED_KEYS_INDENT_2_LF",
    }
    return candidate


def preflight(
    baseline: dict[str, Any], baseline_bytes: bytes,
    raw: dict[str, Any], raw_bytes: bytes,
    reconcile: dict[str, Any], reconcile_bytes: bytes,
    claim_review: dict[str, Any], claim_review_bytes: bytes,
    goal_audit: dict[str, Any], goal_audit_bytes: bytes,
    rejected_builder_bytes: bytes, rejected_candidate_bytes: bytes,
) -> None:
    actual = {
        "canonical_baseline": sha256_bytes(baseline_bytes),
        "raw_claim_gap_audit": sha256_bytes(raw_bytes),
        "independent_gap_reconciliation": sha256_bytes(reconcile_bytes),
        "claim_schema_review": sha256_bytes(claim_review_bytes),
        "goal_schema_audit": sha256_bytes(goal_audit_bytes),
        "rejected_claim_integration_builder": sha256_bytes(rejected_builder_bytes),
        "rejected_claim_integration_candidate": sha256_bytes(rejected_candidate_bytes),
    }
    require(actual == EXPECTED_INPUT_SHA256, f"governing input pin mismatch: {actual}")
    require(raw.get("target") == EXPECTED_TARGET and reconcile.get("target") == EXPECTED_TARGET,
            "raw/reconciliation target pin mismatch")
    require(baseline["source_identity"]["docs_target_revision"] == EXPECTED_TARGET["docs_head"]
            and baseline["source_identity"]["repository_tree_at_assembly"] == EXPECTED_TARGET["docs_tree"],
            "canonical source identity mismatch")
    require(baseline["state"] == "DRAFT_NOT_FROZEN" and baseline["freeze"]["state"] == "NOT_FROZEN",
            "canonical P1 is no longer an unfrozen draft")
    require(claim_review.get("verdict") == "DO_NOT_INTEGRATE_UNTIL_ATOMIC_ASSERTIONS_AND_SCHEMA_CONFLICTS_ARE_RESOLVED",
            "claim review verdict changed")
    require(goal_audit.get("verdict", {}).get("p1_freeze") == "NO_GO",
            "goal schema audit verdict changed")
    require(reconcile["counts"]["classification"] == {
        "ABSORB_IN_PROCEDURE_FIELD": 67,
        "ADD_MATERIAL_CLAIM": 104,
        "DUPLICATE": 5,
        "LEGACY_EQUIVALENT": 1,
    }, "reconciliation classification denominator changed")
    require(reconcile["counts"]["new_executable_test_units"] == 0,
            "reconciliation creates executable units")
    topology_maps(baseline)


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    baseline, baseline_bytes = load_json(CANONICAL_PATH)
    raw, raw_bytes = load_json(RAW_PATH)
    reconcile, reconcile_bytes = load_json(RECONCILE_PATH)
    claim_review, claim_review_bytes = load_json(CLAIM_REVIEW_PATH)
    goal_audit, goal_audit_bytes = load_json(GOAL_AUDIT_PATH)
    rejected_builder_bytes = REJECTED_BUILDER_PATH.read_bytes()
    rejected_candidate_bytes = REJECTED_CANDIDATE_PATH.read_bytes()
    preflight(
        baseline, baseline_bytes, raw, raw_bytes, reconcile, reconcile_bytes,
        claim_review, claim_review_bytes, goal_audit, goal_audit_bytes,
        rejected_builder_bytes, rejected_candidate_bytes,
    )
    return baseline, raw, reconcile


def expect_rejected(
    name: str,
    candidate: dict[str, Any],
    mutate: Callable[[dict[str, Any]], None],
    baseline: dict[str, Any], raw: dict[str, Any], reconcile: dict[str, Any],
) -> None:
    value = copy.deepcopy(candidate)
    mutate(value)
    try:
        validate_candidate(value, baseline, raw, reconcile)
    except AtomicCandidateError:
        return
    raise AtomicCandidateError(f"negative self-test did not reject mutation: {name}")


def reseal(value: dict[str, Any]) -> None:
    plan = copy.deepcopy(value)
    plan.pop("integrity", None)
    value["integrity"] = {
        "plan_sha256": sha256_bytes(canonical_bytes(plan)),
        "deterministic_serialization": "UTF-8_JSON_SORTED_KEYS_INDENT_2_LF",
    }


def run_self_tests(
    candidate: dict[str, Any], baseline: dict[str, Any], raw: dict[str, Any], reconcile: dict[str, Any]
) -> int:
    validate_candidate(candidate, baseline, raw, reconcile)
    truth_table_positive = [
        initial_semantic_record("SEM-positive-unvalidated"),
        {
            **initial_semantic_record("SEM-positive-pass"),
            "status": "PASS", "score": 3, "rationale": "supported",
            "finding_class": "EXACTLY_SUPPORTED", "evidence_refs": ["E-PASS"],
        },
        {
            **initial_semantic_record("SEM-positive-fail-one"),
            "status": "FAIL", "score": 1, "rationale": "unsupported",
            "finding_class": "NO_SUPPORT", "evidence_refs": ["E-FAIL-1"],
        },
        {
            **initial_semantic_record("SEM-positive-fail-two"),
            "status": "FAIL", "score": 2, "rationale": "partial",
            "finding_class": "PARTIAL_INCORRECT_OR_BROKEN", "evidence_refs": ["E-FAIL-2"],
        },
        {
            **initial_semantic_record("SEM-positive-blocked"),
            "status": "BLOCKED", "score": None, "rationale": "authority pending",
            "finding_class": "AUTHORITY_ACCESS_OR_SAFETY_BLOCKER", "evidence_refs": ["E-BLOCK"],
        },
        {
            **initial_semantic_record("SEM-positive-na"),
            "status": "NOT_APPLICABLE", "score": None, "rationale": "authorized exclusion",
            "finding_class": "AUTHORIZED_NOT_APPLICABLE", "evidence_refs": ["E-NA"],
            "not_applicable_decision_ref": "DECISION-NA",
        },
        {
            **initial_semantic_record("SEM-positive-stale"),
            "status": "STALE", "score": None, "rationale": "source changed",
            "finding_class": "STALE_SOURCE_AUTHORITY_OR_EVIDENCE", "evidence_refs": ["E-STALE"],
        },
    ]
    for index, record in enumerate(truth_table_positive):
        validate_semantic(record, f"truth-table-positive[{index}]")
    tests: list[tuple[str, Callable[[dict[str, Any]], None]]] = []

    def semantic_mutator(**changes: Any) -> Callable[[dict[str, Any]], None]:
        def mutate(value: dict[str, Any]) -> None:
            record = value["atomic_assertions"][0]["context_bindings"][0]["semantic_record"]
            record.update(changes)
            reseal(value)
        return mutate

    tests.extend([
        ("PASS_SCORE_2", semantic_mutator(status="PASS", score=2, rationale="x", finding_class="EXACTLY_SUPPORTED", evidence_refs=["E"])),
        ("FAIL_SCORE_3", semantic_mutator(status="FAIL", score=3, rationale="x", finding_class="PARTIAL_INCORRECT_OR_BROKEN", evidence_refs=["E"])),
        ("BLOCKED_WITH_SCORE", semantic_mutator(status="BLOCKED", score=1, rationale="x", finding_class="AUTHORITY_ACCESS_OR_SAFETY_BLOCKER", evidence_refs=["E"])),
        ("SCORE_ZERO", semantic_mutator(score=0)),
        ("PASS_WITHOUT_EVIDENCE", semantic_mutator(status="PASS", score=3, rationale="x", finding_class="EXACTLY_SUPPORTED", evidence_refs=[])),
        ("FAIL_WITHOUT_RATIONALE", semantic_mutator(status="FAIL", score=1, rationale=None, finding_class="NO_SUPPORT", evidence_refs=["E"])),
        ("NA_WITHOUT_DECISION", semantic_mutator(status="NOT_APPLICABLE", score=None, rationale="x", finding_class="AUTHORIZED_NOT_APPLICABLE", evidence_refs=["E"])),
        ("STALE_WITHOUT_EVIDENCE", semantic_mutator(status="STALE", score=None, rationale="x", finding_class="STALE_SOURCE_AUTHORITY_OR_EVIDENCE", evidence_refs=[])),
        ("UNVALIDATED_WITH_RATIONALE", semantic_mutator(rationale="invented")),
    ])

    def add_bundle_score(value: dict[str, Any]) -> None:
        value["discovery_bundles"][0]["semantic_assessment"] = initial_semantic_record("SEM-illegal")
        reseal(value)

    def drop_assertion(value: dict[str, Any]) -> None:
        assertion = value["atomic_assertions"].pop()
        for bundle in value["discovery_bundles"]:
            if assertion["id"] in bundle["assertion_ids"]:
                bundle["assertion_ids"].remove(assertion["id"])
                break
        value["counts"]["atomic_assertions"] -= 1
        reseal(value)

    def add_executable_unit(value: dict[str, Any]) -> None:
        value["topology_denominators"]["steps"] += 1
        value["topology_denominators"]["new_executable_test_units"] = 1
        reseal(value)

    def mutate_text(value: dict[str, Any]) -> None:
        value["atomic_assertions"][0]["text_exact"] += " invented"
        reseal(value)

    def overload_alignment(value: dict[str, Any]) -> None:
        value["discovery_bundles"][0]["source_alignment_disposition"] = "EXACT_SOURCE_SPAN"
        reseal(value)

    def share_semantic(value: dict[str, Any]) -> None:
        first = value["atomic_assertions"][0]["context_bindings"][0]["semantic_record"]["id"]
        target = next(
            item for item in value["atomic_assertions"]
            if item["context_bindings"] and item["context_bindings"][0]["semantic_record"]["id"] != first
        )
        target["context_bindings"][0]["semantic_record"]["id"] = first
        reseal(value)

    def wrong_step_owner(value: dict[str, Any]) -> None:
        context = next(
            context for assertion in value["atomic_assertions"]
            for context in assertion["context_bindings"] if context["step_ids"]
        )
        wrong = next(
            step_id for procedure in baseline["procedures"] for branch in procedure["branches"]
            for step_id in [branch["steps"][0]["id"]]
            if procedure["id"] != context["procedure_id"]
        )
        context["step_ids"] = [wrong]
        reseal(value)

    def mutate_source_hash(value: dict[str, Any]) -> None:
        value["atomic_assertions"][0]["source_binding"]["source_file_sha256"] = "0" * 64
        reseal(value)

    def remove_context(value: dict[str, Any]) -> None:
        context = value["atomic_assertions"][0]["context_bindings"].pop()
        value["counts"]["target_context_bindings"] -= 1
        value["counts"]["semantic_records"] -= 1
        value["counts"]["semantic_statuses"]["UNVALIDATED"] -= 1
        value["counts"]["semantic_scores"]["unassessed_null"] -= 1
        if not value["atomic_assertions"][0]["context_bindings"]:
            pass
        reseal(value)

    def invent_pass_status(value: dict[str, Any]) -> None:
        value["atomic_assertions"][0]["status"] = "PASS"
        reseal(value)

    def pass_with_pending_authority(value: dict[str, Any]) -> None:
        record = value["atomic_assertions"][0]["context_bindings"][0]["semantic_record"]
        record.update({
            "status": "PASS",
            "score": 3,
            "rationale": "shape is otherwise valid",
            "finding_class": "EXACTLY_SUPPORTED",
            "evidence_refs": ["E-PASS"],
        })
        reseal(value)

    def expose_private_path(value: dict[str, Any]) -> None:
        value["source_identity"]["prepared_by"] = "/private/tmp/reconciler"
        reseal(value)

    def drop_source_exclusion(value: dict[str, Any]) -> None:
        bundle = next(item for item in value["discovery_bundles"] if item["exclusions"])
        bundle["exclusions"].pop()
        value["counts"]["recorded_exclusions"] -= 1
        reseal(value)

    tests.extend([
        ("BUNDLE_LEVEL_SCORE", add_bundle_score),
        ("DROP_ASSERTION", drop_assertion),
        ("ADD_EXECUTABLE_UNIT", add_executable_unit),
        ("MUTATE_EXACT_TEXT", mutate_text),
        ("OVERLOAD_ALIGNMENT_DISPOSITION", overload_alignment),
        ("SHARE_SEMANTIC_RESULT", share_semantic),
        ("WRONG_STEP_OWNER", wrong_step_owner),
        ("MUTATE_SOURCE_HASH", mutate_source_hash),
        ("REMOVE_CONTEXT", remove_context),
        ("ASSERTION_PASS_WITHOUT_EXECUTION", invent_pass_status),
        ("SEMANTIC_PASS_WITH_PENDING_AUTHORITY", pass_with_pending_authority),
        ("EXPOSE_PRIVATE_PATH", expose_private_path),
        ("DROP_SOURCE_EXCLUSION", drop_source_exclusion),
    ])

    for name, mutate in tests:
        expect_rejected(name, candidate, mutate, baseline, raw, reconcile)

    rebuilt = build_candidate(baseline, raw, reconcile)
    require(canonical_bytes(rebuilt, pretty=True) == canonical_bytes(candidate, pretty=True),
            "deterministic rebuild differs")
    return 1 + len(truth_table_positive) + len(tests) + 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", type=Path, help="validate an existing candidate instead of writing")
    parser.add_argument("--self-test", action="store_true", help="run fail-closed mutation tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        baseline, raw, reconcile = load_inputs()
        candidate = build_candidate(baseline, raw, reconcile)
        validate_candidate(candidate, baseline, raw, reconcile)
        if args.check:
            existing, existing_bytes = load_json(args.check)
            validate_candidate(existing, baseline, raw, reconcile)
            expected_bytes = canonical_bytes(candidate, pretty=True)
            require(existing_bytes == expected_bytes, f"{args.check}: bytes differ from deterministic rebuild")
            tests = run_self_tests(existing, baseline, raw, reconcile) if args.self_test else 0
            print(json.dumps({
                "result": "PASS",
                "mode": "check",
                "path": str(args.check),
                "sha256": sha256_bytes(existing_bytes),
                "bundles": existing["counts"]["discovery_bundles"],
                "assertions": existing["counts"]["atomic_assertions"],
                "contexts": existing["counts"]["target_context_bindings"],
                "semantic_records": existing["counts"]["semantic_records"],
                "self_tests": tests,
            }, sort_keys=True))
            return 0
        output_bytes = canonical_bytes(candidate, pretty=True)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output_bytes)
        tests = run_self_tests(candidate, baseline, raw, reconcile) if args.self_test else 0
        print(json.dumps({
            "result": "PASS",
            "mode": "build",
            "path": str(args.output),
            "sha256": sha256_bytes(output_bytes),
            "bundles": candidate["counts"]["discovery_bundles"],
            "assertions": candidate["counts"]["atomic_assertions"],
            "contexts": candidate["counts"]["target_context_bindings"],
            "semantic_records": candidate["counts"]["semantic_records"],
            "self_tests": tests,
        }, sort_keys=True))
        return 0
    except (AtomicCandidateError, FileNotFoundError, PermissionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
