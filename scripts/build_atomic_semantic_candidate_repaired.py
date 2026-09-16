#!/usr/bin/env python3
"""Build and fail-closed validate the repaired Host Docs atomic-claim candidate.

This script deliberately does not alter Procedure Baseline P1.  It turns the 104
reconciled material-gap records into unscored discovery parents and exact-source
atomic semantic assertions.  Assertions are semantic assessment records only;
they never add procedures, branches, steps, commands, or runtime attempts.

This is a fresh correction of the independently rejected atomic candidate.  The
rejected builder and bytes are retained only as immutable provenance; they are
never imported as assertion or ownership data.  The builder is deterministic
for the pinned inputs.  It performs local source
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
INDEPENDENT_REVIEW_PATH = Path("/private/tmp/host-docs-p1-atomic-independent-review.json")
REPAIRED_TOPOLOGY_PATH = Path("/private/tmp/procedure-baseline-p1-topology-reviewer2-candidate.json")
GOAL_PATH = REPO / "HOST-DOCS-PROCEDURE-VV-GOAL.md"
VV_SKILL_PATH = Path("/Users/hanneszietsman/.codex-vast/skills/vv-evidence/SKILL.md")
REJECTED_BUILDER_PATH = REPO / "scripts/build_procedure_claim_integration.py"
REJECTED_CANDIDATE_PATH = Path("/private/tmp/procedure-baseline-p1-claims-candidate.json")
REJECTED_ATOMIC_BUILDER_PATH = REPO / "scripts/build_atomic_semantic_candidate.py"
REJECTED_ATOMIC_CANDIDATE_PATH = Path("/private/tmp/procedure-baseline-p1-atomic-claims-candidate.json")
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-atomic-claims-repaired-candidate.json")

EXPECTED_INPUT_SHA256 = {
    "canonical_baseline": "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912",
    "raw_claim_gap_audit": "0568cda70f237eb10823e75ce1deb3fef7873a658eb287266f3b52f03e494de1",
    "independent_gap_reconciliation": "a1ae714917f1da76bbd967a7f82d40117002dc636d81255e1132f61ef715566f",
    "claim_schema_review": "c3e3cd637c54c0bf8ca1ca1879a32ff97e122d916b9af94c95ec20a74828d743",
    "goal_schema_audit": "4aa7984dd7bac5abaa396ec9bdf14f90929fafcbe5015dca6788734387f1b090",
    "rejected_claim_integration_builder": "7ac1c24c1ed7f4702307aa6d2118942d030c0204961fab1e10a94e664e6b4ad4",
    "rejected_claim_integration_candidate": "51f51b18fd9833a3f0613dc3cc20cdcaa18cc3a1397e2fe10a54344849703ab8",
    "rejected_atomic_builder": "eb69fcd65524f53499379baafdd7134bee089e5951ef13f781720b338ce92fb5",
    "rejected_atomic_candidate": "a4e377f5c7709c9b69d3ad2d7c33d1b71bdba4310ac702332e485e3129d815af",
    "independent_atomic_review": "207e63a9bc09200d7aa66cd765b335e389879a4ffdf3adbea59831984d7f0c5f",
    "repaired_topology_candidate": "41f1c65bec8dd1e45d842884915bb117273c7ca018f41b3c3b6c3eb5fefa4599",
    "governing_goal": "25c0d0be320f7189d93aa69172e74e95aa27644a5d3f7afd580eb6c72eca8779",
    "vv_evidence_skill": "5c71f16cc25a52e62cb71cd01c9129e92cda8e971faa1d0779d712ef00e2e18d",
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
SEMANTIC_SCOPE = "ONE_ATOMIC_ASSERTION_ONE_PROCEDURE_AT_MOST_ONE_BRANCH_AND_STEP_PER_RENDERED_CONTEXT"
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
CLAUSE_CONNECTOR_RE = re.compile(
    r"(?P<html><br\s*/?>)|"
    r"(?P<semicolon>;\s+)|"
    r"(?P<contrast>,\s+(?:but|while|whereas)\s+)|"
    r"(?P<sequence>,\s+(?:then\s+)?(?=(?:run|runs|check|checks|confirm|confirms|verify|verifies|inspect|inspects|review|reviews|use|uses|keep|keeps|contact|contacts|open|opens|select|selects|set|sets|create|creates|remove|removes|restart|restarts|retry|retries|try|tries|look|looks|wait|waits|watch|watches|compare|compares|follow|follows|rent|rents|start|starts|poll|polls|report|reports|destroy|destroys|collect|collects)\b))|"
    r"(?P<coord>\s+(?:and|but)\s+(?=(?:you|it|this|these|they|each|the|a|an|Vast|hosts?|renters?|machines?|contracts?|billing|payout|verification|keep|keeps|remain|remains|use|uses|run|runs|check|checks|confirm|confirms|verify|verifies|inspect|inspects|review|reviews|contact|contacts|open|opens|select|selects|set|sets|create|creates|remove|removes|restart|restarts|wait|waits|watch|watches|compare|compares|follow|follows|rent|rents|start|starts|poll|polls|report|reports|destroy|destroys|collect|collects)\b))",
    flags=re.I,
)


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
    context_spans: tuple[tuple[int, int, int, int, str, str], ...] = ()
    decomposition_basis: str = "ONE_AUTHORED_DECISION_UNIT"


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
        source.heading_paths[start - 1], local_context, code_language, (),
        "ONE_LOGICAL_CODE_OR_AUTHORED_BLOCK",
    )


def offset_location(segment: Segment, offset: int, *, end: bool) -> tuple[int, int]:
    """Map a character offset in an exact segment back to one-based source coordinates."""
    line_starts = [0] + [match.end() for match in re.finditer("\n", segment.text_exact)]
    line_index = max(index for index, line_start in enumerate(line_starts) if line_start <= offset)
    relative = offset - line_starts[line_index]
    line_number = segment.line_start + line_index
    column = relative + (segment.column_start if line_index == 0 else 1)
    if end:
        column -= 1
    return line_number, column


def has_decision_signal(value: str) -> bool:
    normalized = normalize_prose(value).lower()
    return bool(
        re.search(r"\b(?:must|should|can|cannot|will|is|are|means|requires?|allows?|prevents?|"
                  r"run|runs|use|uses|keep|keeps|set|sets|select|selects|check|checks|confirm|confirms|"
                  r"verify|verifies|inspect|inspects|review|reviews|watch|watches|compare|compares|follow|follows|contact|contacts|open|opens|create|creates|remove|removes|"
                  r"restart|restarts|retry|retries|try|tries|look|looks|wait|waits|rent|rents|start|starts|poll|polls|report|reports|destroy|destroys|"
                  r"collect|collects|fails?|failed|passes?|passed|skipped|ignored|works?|supports?|depends?|shows?|points?|"
                  r"not|guaranteed|eligible|available|listed|charged|paid)\b", normalized)
        or re.search(r"\d", normalized)
        or "`" in value
    )


def decisional_segments(segment: Segment) -> tuple[list[Segment], list[tuple[int, int, int, int, str, str]]]:
    """Split prose/list text by decisional independence, retaining exact connectors.

    Sentence boundaries are always independent candidates.  Within a sentence,
    explicit semicolons, contrasting clauses, sequential imperatives, and coordinated
    clauses with their own decision signal split.  Connectives are structural context,
    never silently discarded.  Anaphoric children link to the exact prior clause.
    """
    if segment.block_type == "CODE_FORM":
        return [segment], []
    sentence_bounds = [0] + [match.end() for match in SENTENCE_BREAK_RE.finditer(segment.text_exact)] + [len(segment.text_exact)]
    raw_units: list[tuple[int, int, str]] = []
    connectors: list[tuple[int, int, str]] = []
    for sentence_left, sentence_right in zip(sentence_bounds, sentence_bounds[1:]):
        left = sentence_left
        while left < sentence_right and segment.text_exact[left].isspace():
            left += 1
        right = sentence_right
        while right > left and segment.text_exact[right - 1].isspace():
            right -= 1
        if left >= right:
            continue
        cursor = left
        for match in CLAUSE_CONNECTOR_RE.finditer(segment.text_exact, left, right):
            candidate_left = cursor
            candidate_right = match.start()
            following_left = match.end()
            following = segment.text_exact[following_left:right]
            current = segment.text_exact[candidate_left:candidate_right]
            if has_decision_signal(current) and has_decision_signal(following):
                while candidate_right > candidate_left and segment.text_exact[candidate_right - 1].isspace():
                    candidate_right -= 1
                if candidate_right > candidate_left:
                    raw_units.append((candidate_left, candidate_right, "DECISIONAL_CLAUSE"))
                connectors.append((match.start(), match.end(), "DECISIONAL_CONNECTOR"))
                cursor = following_left
        while cursor < right and segment.text_exact[cursor].isspace():
            cursor += 1
        if cursor < right:
            raw_units.append((cursor, right, "SENTENCE_OR_REMAINDER"))

    # Diagnostic/check lists with three or more comma-delimited dimensions are
    # independently decidable; split their exact items while keeping the lead as
    # linked context.  This intentionally does not split arbitrary noun lists.
    expanded_units: list[tuple[int, int, str]] = []
    enum_trigger = re.compile(
        r"^(?:(?:First|Then)\s+)?(?:check|confirm|inspect|review|compare|verify|look|collect|monitor|test)\b|"
        r"\b(?:requires?|depends\s+on|includes?|considers?|affected\s+by)\b",
        flags=re.I,
    )
    for unit_left, unit_right, basis in raw_units:
        unit_text = segment.text_exact[unit_left:unit_right]
        separators = list(re.finditer(r",\s+(?:(?:and|or)\s+)?", unit_text, flags=re.I))
        if enum_trigger.search(normalize_prose(unit_text)) and len(separators) >= 2:
            cursor = 0
            for separator in separators:
                right = separator.start()
                while right > cursor and unit_text[right - 1].isspace():
                    right -= 1
                if right > cursor:
                    expanded_units.append((unit_left + cursor, unit_left + right, "ENUMERATED_DECISION_ITEM"))
                connectors.append((unit_left + separator.start(), unit_left + separator.end(), "ENUMERATION_CONNECTOR"))
                cursor = separator.end()
            if cursor < len(unit_text):
                expanded_units.append((unit_left + cursor, unit_right, "ENUMERATED_DECISION_ITEM"))
        else:
            expanded_units.append((unit_left, unit_right, basis))
    raw_units = expanded_units

    output: list[Segment] = []
    prior_span: tuple[int, int, int, int, str, str] | None = None
    for left, right, basis in raw_units:
        text = segment.text_exact[left:right]
        if re.match(r"^(?:See|Read|Learn more)\s+\[", text.strip(), flags=re.I):
            start_line, start_col = offset_location(segment, left, end=False)
            end_line, end_col = offset_location(segment, right, end=True)
            connectors.append((left, right, "NAVIGATION_ONLY"))
            continue
        start_line, start_col = offset_location(segment, left, end=False)
        end_line, end_col = offset_location(segment, right, end=True)
        links = list(segment.context_spans)
        if prior_span and (basis == "ENUMERATED_DECISION_ITEM" or re.match(
            r"^(?:It|This|These|They|If it|If this|When it|Then|checks?|confirms?|verifies?|"
            r"inspects?|reviews?|uses?|keeps?|contacts?|opens?|selects?|sets?|creates?|removes?|"
            r"restarts?|waits?|rents?|starts?|polls?|reports?|destroys?|collects?)\b",
            text.strip(), flags=re.I,
        )):
            links.append(prior_span)
        child = Segment(
            start_line, start_col, end_line, end_col, text,
            "ATOMIC_DECISIONAL_CLAUSE", segment.heading_path, segment.local_context,
            segment.code_language, tuple(links), basis,
        )
        output.append(child)
        prior_span = (start_line, start_col, end_line, end_col, text, "ADJACENT_ANTECEDENT")

    exclusion_spans: list[tuple[int, int, int, int, str, str]] = []
    for left, right, reason in connectors:
        if left >= right:
            continue
        start_line, start_col = offset_location(segment, left, end=False)
        end_line, end_col = offset_location(segment, right, end=True)
        exclusion_spans.append((start_line, start_col, end_line, end_col, segment.text_exact[left:right], reason))
    return output or [segment], exclusion_spans


def markdown_cells(line: str) -> list[tuple[int, int, str]]:
    """Return trimmed Markdown-table cells as zero-based half-open exact spans."""
    delimiters: list[int] = []
    escaped = False
    in_code = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "`":
            in_code = not in_code
            continue
        if char == "|" and not in_code:
            delimiters.append(index)
    bounds = [-1] + delimiters + [len(line)]
    output: list[tuple[int, int, str]] = []
    for left, right in zip(bounds, bounds[1:]):
        cell_left, cell_right = left + 1, right
        while cell_left < cell_right and line[cell_left].isspace():
            cell_left += 1
        while cell_right > cell_left and line[cell_right - 1].isspace():
            cell_right -= 1
        if cell_left < cell_right:
            output.append((cell_left, cell_right, line[cell_left:cell_right]))
    return output


def classify_source_span(source: SourceFile, start: int, end: int) -> tuple[list[Segment], list[dict[str, Any]]]:
    """Return meaningful Markdown blocks and explicit structural exclusions."""
    require(1 <= start <= end <= len(source.lines), f"invalid effective source {source.path}:{start}-{end}")
    selected: list[Segment] = []
    excluded: list[dict[str, Any]] = []
    index = start
    local_context: str | None = None

    def exclude(
        line_start: int, line_end: int, reason: str, rationale: str,
        column_start: int | None = None, column_end: int | None = None,
    ) -> None:
        if column_start is None:
            column_start = 1
        if column_end is None:
            column_end = len(source.lines[line_end - 1])
        text = extract_exact(source, line_start, column_start, line_end, column_end)
        excluded.append({
            "line_start": line_start,
            "column_start": column_start,
            "line_end": line_end,
            "column_end": column_end,
            "text_exact": text,
            "text_sha256": sha256_text(text),
            "reason": reason,
            "rationale": rationale,
        })

    def exclude_decision_connectors(spans: list[tuple[int, int, int, int, str, str]]) -> None:
        for line_start, col_start, line_end, col_end, text, reason in spans:
            exclude(
                line_start, line_end, reason,
                "The exact connective or navigation fragment is retained as structural/context evidence and is not scored as a separate proposition.",
                col_start, col_end,
            )

    def exclude_table_residue(line_number: int, occupied: list[tuple[int, int]]) -> None:
        line_value = source.lines[line_number - 1]
        occupied_zero = [(left - 1, right) for left, right in occupied]
        cursor = 0
        while cursor < len(line_value):
            if line_value[cursor].isspace() or any(left <= cursor < right for left, right in occupied_zero):
                cursor += 1
                continue
            start_zero = cursor
            while (cursor < len(line_value) and not line_value[cursor].isspace()
                   and not any(left <= cursor < right for left, right in occupied_zero)):
                cursor += 1
            exclude(
                line_number, line_number, "TABLE_FORMATTING",
                "Markdown table delimiters are rendering structure, not a semantic claim.",
                start_zero + 1, cursor,
            )

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
            header_line = index
            header_cells = markdown_cells(line)
            exclude(index, index, "TABLE_HEADER_CONTEXT", "Column names are retained as table context; each data row is independently bounded.")
            exclude(index + 1, index + 1, "TABLE_SEPARATOR", "Markdown table delimiter carries no claim.")
            index += 2
            while index <= end:
                row = source.lines[index - 1]
                if not row.strip() or "|" not in row:
                    break
                cells = markdown_cells(row)
                if not cells:
                    exclude(index, index, "EMPTY_TABLE_ROW", "The row has no independently scorable cell text.")
                    index += 1
                    continue
                key = cells[0] if len(cells) > 1 else None
                assertion_cells = cells[1:] if key else cells
                occupied: list[tuple[int, int]] = []
                if key:
                    occupied.append((key[0] + 1, key[1]))
                    exclude(
                        index, index, "TABLE_ROW_KEY_CONTEXT",
                        "The row key identifies the subject for independently scored value cells.",
                        key[0] + 1, key[1],
                    )
                for cell_index, (left, right, cell_text) in enumerate(assertion_cells, start=1 if key else 0):
                    occupied.append((left + 1, right))
                    context_spans: list[tuple[int, int, int, int, str, str]] = []
                    if key:
                        context_spans.append((index, key[0] + 1, index, key[1], key[2], "TABLE_ROW_KEY"))
                    if cell_index < len(header_cells):
                        h_left, h_right, h_text = header_cells[cell_index]
                        context_spans.append((header_line, h_left + 1, header_line, h_right, h_text, "TABLE_COLUMN_HEADER"))
                    base = Segment(
                        index, left + 1, index, right, cell_text, "TABLE_CELL",
                        source.heading_paths[index - 1], local_context, None,
                        tuple(context_spans), "ONE_TABLE_VALUE_CELL",
                    )
                    pieces, connectors = decisional_segments(base)
                    selected.extend(pieces)
                    exclude_decision_connectors(connectors)
                exclude_table_residue(index, occupied)
                index += 1
            continue
        if TABLE_SEPARATOR_RE.match(line):
            exclude(index, index, "TABLE_SEPARATOR", "Markdown table delimiter carries no claim.")
            index += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3:
            cells = markdown_cells(line)
            if len(cells) <= 1:
                exclude(index, index, "TABLE_STRUCTURE_WITHOUT_VALUE", "No independently scorable value cell is present.")
                index += 1
                continue
            key = cells[0]
            occupied = [(key[0] + 1, key[1])]
            exclude(index, index, "TABLE_ROW_KEY_CONTEXT", "The row key identifies the subject for value cells.", key[0] + 1, key[1])
            for left, right, cell_text in cells[1:]:
                occupied.append((left + 1, right))
                base = Segment(
                    index, left + 1, index, right, cell_text, "TABLE_CELL",
                    source.heading_paths[index - 1], local_context, None,
                    ((index, key[0] + 1, index, key[1], key[2], "TABLE_ROW_KEY"),),
                    "ONE_TABLE_VALUE_CELL",
                )
                pieces, connectors = decisional_segments(base)
                selected.extend(pieces)
                exclude_decision_connectors(connectors)
            exclude_table_residue(index, occupied)
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
            item = whole_line_segment(source, item_start, item_end, "LIST_ITEM", local_context)
            prefix = re.match(r"^\s*(?:[-+*]|\d+[.)])\s+", item.text_exact)
            require(prefix is not None, f"{source.path}:{item_start}: list prefix parse failed")
            prefix_end = prefix.end()
            exclude(
                item_start, item_start, "LIST_MARKER",
                "The Markdown list marker is structure, not part of the user-facing proposition.",
                1, prefix_end,
            )
            start_line, start_col = offset_location(item, prefix_end, end=False)
            content = Segment(
                start_line, start_col, item.line_end, item.column_end,
                item.text_exact[prefix_end:], "LIST_ITEM_PROSE", item.heading_path,
                item.local_context, item.code_language, (), "ONE_LIST_ITEM_SOURCE_BLOCK",
            )
            pieces, connectors = decisional_segments(content)
            selected.extend(pieces)
            exclude_decision_connectors(connectors)
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
            pieces, connectors = decisional_segments(paragraph)
            selected.extend(pieces)
            exclude_decision_connectors(connectors)
        index = paragraph_end + 1

    # Recover adjacent antecedents across authored block boundaries (for example,
    # a separate "Then ..." list item) without merging their semantic results.
    linked_selected: list[Segment] = []
    prior_segment: Segment | None = None
    for segment in selected:
        context_spans = list(segment.context_spans)
        if (prior_segment is not None and not context_spans
                and re.match(r"^(?:It|This|These|They|If it|If this|When it|Then)\b",
                             segment.text_exact.strip(), flags=re.I)):
            context_spans.append((
                prior_segment.line_start, prior_segment.column_start,
                prior_segment.line_end, prior_segment.column_end,
                prior_segment.text_exact, "ADJACENT_ANTECEDENT",
            ))
            segment = Segment(
                segment.line_start, segment.column_start, segment.line_end, segment.column_end,
                segment.text_exact, segment.block_type, segment.heading_path, segment.local_context,
                segment.code_language, tuple(context_spans), segment.decomposition_basis,
            )
        linked_selected.append(segment)
        prior_segment = segment
    selected = linked_selected

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


def topology_maps(baseline: dict[str, Any], *, repaired: bool = False) -> dict[str, Any]:
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
    expected = (39, 97, 203, 468) if repaired else (39, 82, 193, 454)
    require((len(pages), len(procedures), len(branches), len(steps)) == expected,
            f"{'repaired' if repaired else 'canonical'} topology denominator changed")
    return {
        "page_by_id": page_by_id,
        "page_by_file": page_by_file,
        "procedure_by_id": procedure_by_id,
        "branch_by_id": branches,
        "step_by_id": steps,
        "fragment_by_file": fragments,
    }


def topology_remaps(repaired_topology: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    raw = repaired_topology["topology_candidate"]["id_remap"]
    return {
        kind: {item["old_id"]: sorted(item["new_ids"]) for item in raw[kind]}
        for kind in ("procedures", "branches", "steps")
    }


def stable_repaired_id(
    old_id: str | None, kind: str, repaired_maps: dict[str, Any],
    remaps: dict[str, dict[str, list[str]]],
) -> tuple[str | None, str, list[str]]:
    if old_id is None:
        return None, "NOT_APPLICABLE", []
    index = repaired_maps[{"procedures": "procedure_by_id", "branches": "branch_by_id", "steps": "step_by_id"}[kind]]
    if old_id in index:
        return old_id, "DIRECT_REPAIRED_TOPOLOGY_ID", []
    mapped = remaps[kind].get(old_id, [])
    if len(mapped) == 1 and mapped[0] in index:
        return mapped[0], "ONE_TO_ONE_REPAIRED_TOPOLOGY_REMAP", mapped
    return None, "REBASE_BLOCKED_AMBIGUOUS_OR_UNMAPPED", mapped


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


def exact_carrier_owners(
    segment: Segment, primary_file: str, repaired_maps: dict[str, Any],
) -> list[tuple[str, str, str, str]]:
    """Resolve exact owner steps from carrier source identity before coarse ranges."""
    needle = normalize_prose(segment.text_exact)
    owners: list[tuple[str, str, str, str]] = []
    if not needle:
        return owners
    for step_id, (procedure_id, branch_id, step) in repaired_maps["step_by_id"].items():
        for carrier in step.get("source_carriers", []):
            source = carrier.get("source", {})
            if source.get("file") != primary_file:
                continue
            if not (int(source.get("line_start", 0)) <= segment.line_start
                    and int(source.get("line_end", 0)) >= segment.line_end):
                continue
            carrier_text = normalize_prose(str(carrier.get("text", "")))
            if needle == carrier_text or (len(needle) >= 8 and needle in carrier_text):
                owners.append((procedure_id, branch_id, step_id, carrier["claim_id"]))
    return sorted(set(owners))


def assertion_target_contexts(
    assertion_id: str,
    record: dict[str, Any],
    segment: Segment,
    primary_file: str,
    raw_occurrence_id: str,
    rendered_occurrence_ids: dict[str, str],
    page: dict[str, Any],
    maps: dict[str, Any],
    repaired_maps: dict[str, Any],
    remaps: dict[str, dict[str, list[str]]],
    authority_boundary: dict[str, Any],
    planned_method: dict[str, str],
) -> list[dict[str, Any]]:
    target = record["target"]
    # One tuple is one independently statused owner.  There is never a list of steps.
    # (procedure, branch, step, basis, topology basis, source ids, carrier id, blockers)
    contexts: list[tuple[str, str | None, str | None, str, str, dict[str, Any], str | None, list[str]]] = []
    exact_owners = exact_carrier_owners(segment, primary_file, repaired_maps)
    if exact_owners:
        for procedure_id, branch_id, step_id, carrier_id in exact_owners:
            contexts.append((
                procedure_id, branch_id, step_id, "EXACT_STEP_SOURCE_CARRIER",
                "REPAIRED_TOPOLOGY_CANDIDATE", {"procedure_id": procedure_id, "branch_id": branch_id, "step_id": step_id},
                carrier_id, [],
            ))
    else:
        for old_procedure_id in sorted(target["procedure_ids"]):
            procedure_id, procedure_state, procedure_candidates = stable_repaired_id(
                old_procedure_id, "procedures", repaired_maps, remaps
            )
            blockers: list[str] = []
            topology_basis = "REPAIRED_TOPOLOGY_CANDIDATE"
            if procedure_id is None:
                procedure_id = old_procedure_id
                topology_basis = "CANONICAL_BASELINE_PENDING_REBASE"
                blockers.append("REBASE-PROCEDURE-" + old_procedure_id)

            old_steps = sorted(
                step_id for step_id in target["step_ids"]
                if maps["step_by_id"][step_id][0] == old_procedure_id
            )
            overlapping = [step_id for step_id in old_steps if step_overlaps(maps["step_by_id"][step_id][2], segment)]
            step_candidates = overlapping if overlapping else old_steps
            if len(step_candidates) == 1:
                old_step_id = step_candidates[0]
                old_branch_id = maps["step_by_id"][old_step_id][1]
                step_id, step_state, mapped_steps = stable_repaired_id(old_step_id, "steps", repaired_maps, remaps)
                branch_id, branch_state, mapped_branches = stable_repaired_id(old_branch_id, "branches", repaired_maps, remaps)
                if step_id is not None and branch_id is not None and topology_basis == "REPAIRED_TOPOLOGY_CANDIDATE":
                    owner = repaired_maps["step_by_id"][step_id]
                    require(owner[:2] == (procedure_id, branch_id), f"{record['id']}: stable remap owner mismatch")
                    contexts.append((
                        procedure_id, branch_id, step_id, "SINGLE_TARGET_STEP_OR_UNIQUE_SOURCE_OVERLAP",
                        topology_basis,
                        {"procedure_id": old_procedure_id, "branch_id": old_branch_id, "step_id": old_step_id},
                        None, blockers,
                    ))
                    continue
                blockers.extend([
                    "REBASE-BRANCH-" + old_branch_id if branch_id is None else "",
                    "REBASE-STEP-" + old_step_id if step_id is None else "",
                ])

            # Multiple/coarse steps are not guessed.  Retain an explicit branch-level
            # null step for each determinable target branch; otherwise procedure-level.
            old_branches = sorted(set(
                [maps["step_by_id"][step_id][1] for step_id in step_candidates]
                or [branch_id for branch_id in target["branch_ids"]
                    if maps["branch_by_id"][branch_id][0] == old_procedure_id]
            ))
            if not old_branches:
                contexts.append((
                    procedure_id, None, None, "PROCEDURE_LEVEL_NON_STEP_ASSERTION",
                    topology_basis,
                    {"procedure_id": old_procedure_id, "branch_id": None, "step_id": None},
                    None, sorted(set(item for item in blockers if item)),
                ))
                continue
            for old_branch_id in old_branches:
                branch_id, branch_state, branch_candidates = stable_repaired_id(
                    old_branch_id, "branches", repaired_maps, remaps
                )
                local_blockers = list(blockers)
                if branch_id is None or topology_basis != "REPAIRED_TOPOLOGY_CANDIDATE":
                    if topology_basis == "REPAIRED_TOPOLOGY_CANDIDATE":
                        # A stable procedure may still have an unresolved split branch;
                        # null the branch rather than mixing topology identities.
                        branch_id = None
                    else:
                        branch_id = old_branch_id
                    local_blockers.append("REBASE-BRANCH-" + old_branch_id)
                if len(step_candidates) > 1:
                    local_blockers.append("OWNER-STEP-" + record["id"] + "-" + old_branch_id)
                contexts.append((
                    procedure_id, branch_id, None,
                    "BRANCH_LEVEL_NULL_STEP_COARSE_OR_AMBIGUOUS_OWNER",
                    topology_basis,
                    {"procedure_id": old_procedure_id, "branch_id": old_branch_id, "step_id": None},
                    None, sorted(set(item for item in local_blockers if item)),
                ))

    require(contexts, f"{record['id']} / {assertion_id}: no target context")
    output = []
    for route in sorted(rendered_occurrence_ids):
        for procedure_id, branch_id, step_id, binding_basis, topology_basis, source_target_ids, carrier_id, blockers in contexts:
            owner_maps = repaired_maps if topology_basis == "REPAIRED_TOPOLOGY_CANDIDATE" else maps
            procedure = owner_maps["procedure_by_id"][procedure_id]
            refs = sorted(set(page.get("authority_refs", [])) | set(procedure.get("authority_refs", [])))
            context_id = stable_id(
                "CTX-", "host-docs-p1-assertion-context-v2", assertion_id, route,
                procedure_id, branch_id or "", step_id or "", target["procedure_field"], topology_basis,
            )
            semantic_id = stable_id("SEM-", "host-docs-p1-semantic-record-v2", context_id)
            output.append({
                "id": context_id,
                "raw_occurrence_id": raw_occurrence_id,
                "rendered_occurrence_id": rendered_occurrence_ids[route],
                "route": route,
                "procedure_id": procedure_id,
                "branch_id": branch_id,
                "step_id": step_id,
                "step_role": owner_maps["step_by_id"][step_id][2]["role"] if step_id else None,
                "procedure_field": target["procedure_field"],
                "binding_basis": binding_basis,
                "topology_basis": topology_basis,
                "source_target_ids": source_target_ids,
                "exact_source_carrier_claim_id": carrier_id,
                "rebase_blocker_ids": blockers,
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
        str(segment.line_start), str(segment.column_start), str(segment.line_end), str(segment.column_end),
        sha256_text(segment.text_exact),
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
        "decomposition_basis": segment.decomposition_basis,
        "context_source_bindings": [{
            "id": stable_id("CSRC-", "host-docs-p1-assertion-context-source-v2", assertion_id, *span),
            "file": source.path,
            "line_start": span[0],
            "column_start": span[1],
            "line_end": span[2],
            "column_end": span[3],
            "text_exact": span[4],
            "text_sha256": sha256_text(span[4]),
            "role": span[5],
        } for span in segment.context_spans],
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
    repaired_maps: dict[str, Any],
    remaps: dict[str, dict[str, list[str]]],
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
            page, maps, repaired_maps, remaps, authority_boundary, planned_method,
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
            "atomicity_rationale": "One exact source-bounded decisional clause, logical command form, or table value cell; surrounding labels/connectors are separately linked or excluded.",
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
            page, maps, repaired_maps, remaps, authority_boundary, planned_method,
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
            "column_start": item["column_start"],
            "line_end": item["line_end"],
            "column_end": item["column_end"],
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
            "unit": "ONE_INDEPENDENTLY_DECIDABLE_EXACT_SOURCE_CLAUSE_OR_LOGICAL_COMMAND",
            "sentence_tokenizer_for_every_sentence": False,
            "sentence_boundaries": "EVALUATED_AS_DECISIONAL_CANDIDATES; NAVIGATION_AND_CONTEXT_ONLY_FRAGMENTS_ARE_NOT SCORED",
            "table_rows": "ROW_KEY_AND_HEADERS_ARE_CONTEXT; EACH_VALUE_CELL_AND_INDEPENDENT_CLAUSE_IS_SEPARATE",
            "list_items": "LIST_MARKER_EXCLUDED; EACH_DECIDABLE_SENTENCE_OR_CLAUSE_IS_SEPARATE",
            "code_forms": "ONE_LOGICAL_SOURCE_FORM_PER_ASSERTION_WITH_CONTINUATIONS_GROUPED",
            "coordinated_prose": "SPLIT_WHEN_BOTH_SIDES_HAVE_INDEPENDENT_DECISION_SIGNALS; RETAIN_CONNECTOR_AND_ANTECEDENT LINKS",
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
        "truth_table_requirement_conflict", "counts", "discovery_bundles", "atomic_assertions",
        "owner_controls", "rebase_blockers", "provenance_reconciliation", "cross_artifact_blocker_index",
        "unresolved_blockers", "integrity",
    }, "candidate")
    require(candidate["schema_version"] == "host-docs-p1-atomic-semantic-candidate/2.0-repaired",
            "unexpected candidate schema")
    require(candidate["record_type"] == "HOST_DOCS_P1_ATOMIC_SEMANTIC_REPAIRED_CANDIDATE",
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
        "created_at_basis", "rejected_input_disposition", "builder", "governing_goal",
        "vv_evidence_skill", "independent_review", "repaired_topology",
    }, "candidate.source_identity")
    require(candidate["source_identity"]["inputs"] == EXPECTED_INPUT_SHA256,
            "candidate input pins differ")
    require(candidate["source_identity"]["target"] == EXPECTED_TARGET,
            "candidate target pin differs")
    require(candidate["source_identity"]["builder"] == {
        "artifact_ref": "scripts/build_atomic_semantic_candidate_repaired.py",
        "sha256": sha256_path(Path(__file__)),
    }, "candidate does not self-pin its current builder")
    require(candidate["source_identity"]["governing_goal"]["sha256"] == EXPECTED_INPUT_SHA256["governing_goal"]
            and candidate["source_identity"]["vv_evidence_skill"]["sha256"] == EXPECTED_INPUT_SHA256["vv_evidence_skill"]
            and candidate["source_identity"]["independent_review"]["sha256"] == EXPECTED_INPUT_SHA256["independent_atomic_review"]
            and candidate["source_identity"]["repaired_topology"]["sha256"] == EXPECTED_INPUT_SHA256["repaired_topology_candidate"],
            "candidate governing provenance pin mismatch")
    require(candidate["source_alignment_disposition_schema"] == {
        "initial_value": None,
        "object_fields": ["decision", "evidence_refs", "reviewed_at", "reviewer", "role"],
        "allowed_decisions": ["APPROVED_CROSS_SECTION_ROLE", "APPROVED_SHARED_FRAGMENT", "CORRECTED_TO_EXACT"],
        "rule": "A non-null value requires an independent reviewer, role, UTC timestamp, and nonempty evidence refs; raw source-review state strings are forbidden.",
    }, "source-alignment disposition schema differs from canonical reviewer contract")
    maps = topology_maps(baseline)
    repaired_topology, repaired_bytes = load_json(REPAIRED_TOPOLOGY_PATH)
    require(sha256_bytes(repaired_bytes) == EXPECTED_INPUT_SHA256["repaired_topology_candidate"],
            "repaired topology bytes changed")
    repaired_maps = topology_maps(repaired_topology, repaired=True)
    topology = candidate["topology_denominators"]
    require(topology == {
        "canonical": {"pages": 39, "procedures": 82, "branches": 193, "steps": 454},
        "repaired_candidate": {"pages": 39, "procedures": 97, "branches": 203, "steps": 468},
        "repaired_candidate_sha256": EXPECTED_INPUT_SHA256["repaired_topology_candidate"],
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
        claimed_positions: set[tuple[int, int]] = set()
        excluded_positions: set[tuple[int, int]] = set()

        def positions(line_start: int, column_start: int, line_end: int, column_end: int) -> set[tuple[int, int]]:
            output: set[tuple[int, int]] = set()
            for line_number in range(line_start, line_end + 1):
                first = column_start if line_number == line_start else 1
                last = column_end if line_number == line_end else len(load_source(primary_effective["file"]).lines[line_number - 1])
                output.update((line_number, column) for column in range(first, last + 1))
            return output
        for assertion_id in bundle["assertion_ids"]:
            child_source = assertion_by_id[assertion_id]["source_binding"]
            require(child_source["file"] == primary_effective["file"],
                    f"{source_id}: assertion is not bound to the primary effective source")
            require(primary_effective["line_start"] <= child_source["line_start"]
                    <= child_source["line_end"] <= primary_effective["line_end"],
                    f"{source_id}: assertion escapes its effective source span")
            covered_lines.update(range(child_source["line_start"], child_source["line_end"] + 1))
            child_positions = positions(
                child_source["line_start"], child_source["column_start"],
                child_source["line_end"], child_source["column_end"],
            )
            require(not claimed_positions.intersection(child_positions),
                    f"{source_id}: atomic assertion spans overlap")
            claimed_positions.update(child_positions)
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
            excluded_positions.update(positions(
                exclusion["line_start"], exclusion["column_start"],
                exclusion["line_end"], exclusion["column_end"],
            ))
        require(covered_lines == set(range(primary_effective["line_start"], primary_effective["line_end"] + 1)),
                f"{source_id}: assertion/exclusion source-line coverage is incomplete")
        primary_source = load_source(primary_effective["file"])
        required_positions = {
            (line_number, column)
            for line_number in range(primary_effective["line_start"], primary_effective["line_end"] + 1)
            for column, char in enumerate(primary_source.lines[line_number - 1], start=1)
            if not char.isspace()
        }
        require(required_positions <= claimed_positions | excluded_positions,
                f"{source_id}: non-whitespace source partition is incomplete")

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
            "heading_path_state", "local_context", "block_type", "decomposition_basis",
            "context_source_bindings",
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
        require(binding["block_type"] != "TABLE_ROW" and isinstance(binding["decomposition_basis"], str)
                and binding["decomposition_basis"], f"{assertion['id']}: under-decomposed source block")
        if binding["block_type"] != "CODE_FORM":
            probe = Segment(
                binding["line_start"], binding["column_start"], binding["line_end"], binding["column_end"],
                assertion["text_exact"], binding["block_type"], tuple(binding["heading_path"]),
                binding["local_context"], None, (), binding["decomposition_basis"],
            )
            probe_units, _ = decisional_segments(probe)
            require(len(probe_units) == 1, f"{assertion['id']}: multiple independent clauses remain bundled")
        for context_source in binding["context_source_bindings"]:
            exact_keys(context_source, {
                "id", "file", "line_start", "column_start", "line_end", "column_end",
                "text_exact", "text_sha256", "role",
            }, f"{assertion['id']}.context_source")
            context_file = load_source(context_source["file"])
            context_exact = extract_exact(
                context_file, context_source["line_start"], context_source["column_start"],
                context_source["line_end"], context_source["column_end"],
            )
            require(context_exact == context_source["text_exact"]
                    and sha256_text(context_exact) == context_source["text_sha256"],
                    f"{assertion['id']}: context source binding/hash mismatch")
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
                "branch_id", "step_id", "step_role", "procedure_field", "binding_basis",
                "topology_basis", "source_target_ids", "exact_source_carrier_claim_id",
                "rebase_blocker_ids",
                "authority_boundary", "planned_method", "semantic_record",
            }, f"{assertion['id']}.context")
            require(context["id"] not in all_context_ids, f"{assertion['id']}: duplicate context ID")
            all_context_ids.add(context["id"])
            require(context["raw_occurrence_id"] == raw_occ["id"]
                    and context["rendered_occurrence_id"] in rendered_ids,
                    f"{assertion['id']}: context occurrence mismatch")
            require(context["step_id"] is None or isinstance(context["step_id"], str),
                    f"{assertion['id']}: invalid singular step owner")
            require(context["topology_basis"] in {"REPAIRED_TOPOLOGY_CANDIDATE", "CANONICAL_BASELINE_PENDING_REBASE"},
                    f"{assertion['id']}: invalid topology basis")
            owner_maps = repaired_maps if context["topology_basis"] == "REPAIRED_TOPOLOGY_CANDIDATE" else maps
            procedure = owner_maps["procedure_by_id"].get(context["procedure_id"])
            require(procedure is not None and procedure["page_id"] == bundle_by_id[assertion["bundle_id"]]["page_id"],
                    f"{assertion['id']}: wrong procedure owner")
            if context["branch_id"] is not None:
                require(owner_maps["branch_by_id"].get(context["branch_id"], (None,))[0] == context["procedure_id"],
                        f"{assertion['id']}: wrong branch owner")
            if context["step_id"] is not None:
                owner = owner_maps["step_by_id"].get(context["step_id"])
                require(owner is not None and owner[0] == context["procedure_id"]
                        and owner[1] == context["branch_id"],
                        f"{assertion['id']}: wrong step owner")
                require(context["step_role"] == owner[2]["role"], f"{assertion['id']}: step role mismatch")
            else:
                require(context["step_role"] is None, f"{assertion['id']}: null step has a role")
            require(context["rebase_blocker_ids"] == sorted(set(context["rebase_blocker_ids"])),
                    f"{assertion['id']}: invalid rebase blocker IDs")
            if context["binding_basis"] == "EXACT_STEP_SOURCE_CARRIER":
                exact_owners = exact_carrier_owners(
                    Segment(
                        binding["line_start"], binding["column_start"], binding["line_end"], binding["column_end"],
                        assertion["text_exact"], binding["block_type"], tuple(binding["heading_path"]),
                        binding["local_context"], None, (), binding["decomposition_basis"],
                    ), binding["file"], repaired_maps,
                )
                require(any(owner[:3] == (context["procedure_id"], context["branch_id"], context["step_id"])
                            and owner[3] == context["exact_source_carrier_claim_id"] for owner in exact_owners),
                        f"{assertion['id']}: exact carrier owner cannot be reproduced")
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
        "context_source_bindings_verified": sum(
            len(item["source_binding"]["context_source_bindings"]) for item in assertions
        ),
    }, "source hash coverage count differs")
    require(counts["context_step_cardinality"]["more_than_one"] == 0
            and counts["context_step_cardinality"]["zero_null"]
                + counts["context_step_cardinality"]["one"] == len(all_context_ids)
            and counts["multi_step_semantic_records"] == 0,
            "multi-step semantic result scope is not closed")
    require(counts["whole_table_row_assertions"] == 0,
            "under-decomposed table row remains")
    require(counts["multi_sentence_assertions"] == 0
            and counts["anaphoric_assertions_without_context_link"] == 0
            and counts["html_breaks_remaining_inside_assertions"] == 0
            and counts["shared_semantic_record_ids"] == 0,
            "decisional decomposition/context-link population controls failed")
    require(counts["legacy_overlap_parent_records_preserved"] == 104
            and counts["rejected_exact_legacy_overlap_provenance_records"] == 80,
            "legacy-overlap provenance coverage differs")
    provenance = candidate["provenance_reconciliation"]
    require(provenance["rejected_atomic_candidate_sha256"] == EXPECTED_INPUT_SHA256["rejected_atomic_candidate"]
            and provenance["rejected_candidate_counts"] == {
                "discovery_bundles": 104, "atomic_assertions": 685,
                "recorded_exclusions": 923, "exact_legacy_duplicate_exclusions": 80,
            }
            and len(provenance["exact_legacy_overlap_records"]) == 80,
            "rejected legacy-overlap provenance reconciliation differs")
    provenance_ids: set[str] = set()
    for item in provenance["exact_legacy_overlap_records"]:
        require(item["id"] not in provenance_ids, "duplicate rejected exact-legacy provenance ID")
        provenance_ids.add(item["id"])
        source = load_source(item["file"])
        exact = extract_exact(
            source, item["line_start"], item["column_start"], item["line_end"], item["column_end"]
        )
        require(sha256_text(exact) == item["text_sha256"]
                and item["record_role"] == "REJECTED_CANDIDATE_PROVENANCE_ONLY_NOT_A_SEMANTIC_RESULT",
                "rejected exact-legacy source/hash provenance mismatch")
    owner_controls = candidate["owner_controls"]
    require(owner_controls["machine_errors_114_115_expected_step"] == "ERR-T02-B01-S02"
            and owner_controls["assertions"], "missing exact wrong-owner regression control")
    require(all(item["step_id"] == "ERR-T02-B01-S02"
                for item in owner_controls["assertions"]),
            "machine-errors lines 114/115 do not bind exclusively to exact owner ERR-T02-B01-S02")
    review_ids = [item["id"] for item in candidate["cross_artifact_blocker_index"]["independent_atomic_review_findings"]]
    schema_ids = [item["id"] for item in candidate["cross_artifact_blocker_index"]["goal_schema_audit_findings"]]
    require(review_ids == ["F-001", "F-002", "F-003", "F-004", "F-005", "F-006"]
            and schema_ids == [f"P1-SCHEMA-{index:03d}" for index in range(1, 10)]
            and candidate["cross_artifact_blocker_index"]["composition_allowed"] is False,
            "cross-artifact blocker coverage is incomplete")
    require(candidate["truth_table_requirement_conflict"]["id"] == "F-004"
            and candidate["truth_table_requirement_conflict"]["state"] == "OPEN_GOVERNING_REQUIREMENT_CONFLICT",
            "governing truth-table conflict is hidden")
    require(counts["unresolved_blocker_classes"] == len(candidate["unresolved_blockers"]) == 10,
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
    baseline: dict[str, Any], raw: dict[str, Any], reconcile: dict[str, Any],
    repaired_topology: dict[str, Any] | None = None,
    independent_review: dict[str, Any] | None = None,
    goal_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if repaired_topology is None:
        repaired_topology, _ = load_json(REPAIRED_TOPOLOGY_PATH)
    if independent_review is None:
        independent_review, _ = load_json(INDEPENDENT_REVIEW_PATH)
    if goal_audit is None:
        goal_audit, _ = load_json(GOAL_AUDIT_PATH)
    rejected_atomic, rejected_atomic_bytes = load_json(REJECTED_ATOMIC_CANDIDATE_PATH)
    require(sha256_bytes(rejected_atomic_bytes) == EXPECTED_INPUT_SHA256["rejected_atomic_candidate"],
            "rejected atomic provenance bytes changed")
    maps = topology_maps(baseline)
    repaired_maps = topology_maps(repaired_topology, repaired=True)
    remaps = topology_remaps(repaired_topology)
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
        bundle, children = build_bundle_and_assertions(
            record, raw_by_id[record["id"]], baseline, maps, repaired_maps, remaps
        )
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
    context_source_bindings = sum(
        len(item["source_binding"]["context_source_bindings"]) for item in assertions
    )
    context_topologies = Counter(context["topology_basis"] for context in contexts)
    step_cardinality = Counter("null" if context["step_id"] is None else "one" for context in contexts)
    rebase_contexts = [context for context in contexts if context["rebase_blocker_ids"]]
    ambiguous_remaps = [{
        "id": "REBASE-" + kind[:-1].upper() + "-" + old_id,
        "kind": kind[:-1].upper(),
        "old_id": old_id,
        "candidate_ids": new_ids,
        "state": "OPEN_UNINTEGRATED_BRANCH_PHASE_REBASE",
        "effect": "Atomic owner remains canonical or is nulled at the lower scope; no candidate owner is guessed.",
    } for kind in ("procedures", "branches", "steps")
      for old_id, new_ids in sorted(remaps[kind].items()) if len(new_ids) != 1]
    context_rebase_ids = sorted(set(
        blocker for context in rebase_contexts for blocker in context["rebase_blocker_ids"]
    ))
    review_findings = [{
        "id": finding["id"],
        "severity": finding["severity"],
        "title": finding["title"],
        "state": (
            "CORRECTED_IN_THIS_CANDIDATE_PENDING_INDEPENDENT_REVIEW"
            if finding["id"] in {"F-001", "F-002", "F-003", "F-005", "F-006"}
            else "OPEN_GOVERNING_REQUIREMENT_CONFLICT"
        ),
        "source_review_sha256": EXPECTED_INPUT_SHA256["independent_atomic_review"],
    } for finding in independent_review["findings"]]
    schema_findings = [{
        "id": finding["id"],
        "severity": finding["severity"],
        "title": finding["title"],
        "state": (
            "ATOMIC_CORRECTION_PENDING_INDEPENDENT_REVIEW"
            if finding["id"] == "P1-SCHEMA-001" else "OPEN_OUTSIDE_THIS_ISOLATED_ATOMIC_LAYER"
        ),
        "source_audit_sha256": EXPECTED_INPUT_SHA256["goal_schema_audit"],
    } for finding in goal_audit["findings"]]
    owner_control_assertions = []
    for assertion in assertions:
        if (assertion["source_binding"]["file"] != "host/machine-errors.mdx"
                or assertion["source_binding"]["line_start"] not in {114, 115}):
            continue
        observed_steps = sorted(set(
            context["step_id"] for context in assertion["context_bindings"] if context["step_id"]
        ))
        require(len(observed_steps) == 1, f"{assertion['id']}: wrong-owner control is not singular")
        owner_control_assertions.append({
            "assertion_id": assertion["id"],
            "source": f"{assertion['source_binding']['file']}:{assertion['source_binding']['line_start']}",
            "step_id": observed_steps[0],
        })
    rejected_exact_legacy = sorted([{
        "bundle_id": bundle["id"],
        "source_record_id": bundle["source_record_id"],
        "id": exclusion["id"],
        "file": exclusion["file"],
        "line_start": exclusion["line_start"],
        "column_start": exclusion["column_start"],
        "line_end": exclusion["line_end"],
        "column_end": exclusion["column_end"],
        "text_sha256": exclusion["text_sha256"],
        "legacy_claim_ids": exclusion["legacy_claim_ids"],
        "overlapping_legacy_claim_ids": exclusion["overlapping_legacy_claim_ids"],
        "record_role": "REJECTED_CANDIDATE_PROVENANCE_ONLY_NOT_A_SEMANTIC_RESULT",
    } for bundle in rejected_atomic["discovery_bundles"] for exclusion in bundle["exclusions"]
      if exclusion["reason"] == "EXACT_LEGACY_SEMANTIC_DUPLICATE"], key=lambda item: item["id"])
    require(len(rejected_exact_legacy) == 80, "rejected exact-legacy provenance denominator changed")
    candidate: dict[str, Any] = {
        "schema_version": "host-docs-p1-atomic-semantic-candidate/2.0-repaired",
        "record_type": "HOST_DOCS_P1_ATOMIC_SEMANTIC_REPAIRED_CANDIDATE",
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
            "builder": {
                "artifact_ref": "scripts/build_atomic_semantic_candidate_repaired.py",
                "sha256": sha256_path(Path(__file__)),
            },
            "governing_goal": {"artifact_ref": "HOST-DOCS-PROCEDURE-VV-GOAL.md", "sha256": EXPECTED_INPUT_SHA256["governing_goal"]},
            "vv_evidence_skill": {"artifact_ref": "vv-evidence/SKILL.md", "sha256": EXPECTED_INPUT_SHA256["vv_evidence_skill"]},
            "independent_review": {"artifact_ref": "host-docs-p1-atomic-independent-review.json", "sha256": EXPECTED_INPUT_SHA256["independent_atomic_review"], "verdict": independent_review["overall_verdict"]},
            "repaired_topology": {"artifact_ref": "procedure-baseline-p1-topology-reviewer2-candidate.json", "sha256": EXPECTED_INPUT_SHA256["repaired_topology_candidate"], "state": repaired_topology["state"]},
            "prepared_by": "Codex atomic semantic reconciler",
            "independence_limit": "The same agent constructed and self-tested this isolated candidate; independent human review remains required.",
            "created_at_basis": "The deterministic created_at value is inherited from the exact canonical P1 draft; it is not a claim-execution timestamp.",
            "rejected_input_disposition": "Both rejected claim-integration and rejected atomic builders/candidates are hash-pinned for provenance only; no rejected assertion, context, result, or owner record is imported.",
        },
        "topology_denominators": {
            "canonical": {"pages": 39, "procedures": 82, "branches": 193, "steps": 454},
            "repaired_candidate": {"pages": 39, "procedures": 97, "branches": 203, "steps": 468},
            "repaired_candidate_sha256": EXPECTED_INPUT_SHA256["repaired_topology_candidate"],
            "new_executable_test_units": 0,
        },
        "method": {
            "parent_model": "Every ADD_MATERIAL_CLAIM record remains one unscored discovery bundle.",
            "assertion_model": "Each exact source-bounded record contains one independently decidable prose clause, one table value-cell clause, or one logical code form; headings, row keys, antecedents, and connectors remain exact linked context/exclusions.",
            "context_model": "Each semantic record owns exactly one procedure, at most one branch, and zero or one true step in one rendered context. Multi-context assertions have separate records and no result sharing.",
            "exclusion_model": "Markdown structure, non-rendered comments, context-only lead-ins, and exact legacy semantic duplicates are explicitly retained with rationale.",
            "execution_boundary": "Atomic semantic records add no executable test unit and cannot directly carry runtime attempts.",
        },
        "semantic_truth_table": make_truth_table_projection(),
        "truth_table_requirement_conflict": {
            "id": "F-004",
            "state": "OPEN_GOVERNING_REQUIREMENT_CONFLICT",
            "current_candidate_rule": "UNVALIDATED_REQUIRES_NULL_SCORE_NULL_RATIONALE_EMPTY_EVIDENCE",
            "conflict": "Phase 10 forbids invented scores while success criterion 9 requires an UNVALIDATED 1-3 score and evidence-gap rationale.",
            "effect": "No semantic score is assigned and composition/freeze remains blocked pending an owner-approved goal correction.",
        },
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
                "context_source_bindings_verified": context_source_bindings,
            },
            "context_step_cardinality": {"zero_null": step_cardinality["null"], "one": step_cardinality["one"], "more_than_one": 0},
            "context_topology_basis": dict(sorted(context_topologies.items())),
            "contexts_with_rebase_blocker": len(rebase_contexts),
            "exact_source_carrier_contexts": sum(context["binding_basis"] == "EXACT_STEP_SOURCE_CARRIER" for context in contexts),
            "table_cell_assertions": sum(item["source_binding"]["block_type"] in {"TABLE_CELL", "ATOMIC_DECISIONAL_CLAUSE"} and bool(item["source_binding"]["context_source_bindings"]) for item in assertions),
            "whole_table_row_assertions": sum(item["source_binding"]["block_type"] == "TABLE_ROW" for item in assertions),
            "multi_sentence_assertions": sum(
                len(re.findall(r"[.!?](?:\s|$)", item["text_exact"])) > 1 for item in assertions
            ),
            "anaphoric_assertions_without_context_link": sum(
                bool(re.match(r"^(?:It|This|These|They|If it|If this|When it|Then)\b",
                              item["text_exact"].strip(), flags=re.I))
                and not item["source_binding"]["context_source_bindings"]
                for item in assertions
            ),
            "html_breaks_remaining_inside_assertions": sum(
                "<br" in item["text_exact"].lower() for item in assertions
            ),
            "shared_semantic_record_ids": 0,
            "multi_step_semantic_records": 0,
            "recorded_exclusions": len(exclusions),
            "exact_legacy_duplicate_exclusions": sum(item["reason"] == "EXACT_LEGACY_SEMANTIC_DUPLICATE" for item in exclusions),
            "rejected_exact_legacy_overlap_provenance_records": len(rejected_exact_legacy),
            "legacy_overlap_parent_records_preserved": sum("legacy_overlap" in item for item in bundles),
            "new_executable_test_units": 0,
            "independent_review_findings_indexed": len(review_findings),
            "goal_schema_findings_indexed": len(schema_findings),
            "unresolved_blocker_classes": 10,
        },
        "discovery_bundles": bundles,
        "atomic_assertions": assertions,
        "owner_controls": {
            "machine_errors_114_115_expected_step": "ERR-T02-B01-S02",
            "assertions": owner_control_assertions,
        },
        "rebase_blockers": {
            "ambiguous_topology_remaps": ambiguous_remaps,
            "context_blocker_ids": context_rebase_ids,
            "state": "OPEN_PENDING_BRANCH_PHASE_COMPOSITION",
        },
        "provenance_reconciliation": {
            "rejected_atomic_candidate_sha256": EXPECTED_INPUT_SHA256["rejected_atomic_candidate"],
            "rejected_candidate_counts": {
                "discovery_bundles": rejected_atomic["counts"]["discovery_bundles"],
                "atomic_assertions": rejected_atomic["counts"]["atomic_assertions"],
                "recorded_exclusions": rejected_atomic["counts"]["recorded_exclusions"],
                "exact_legacy_duplicate_exclusions": rejected_atomic["counts"]["exact_legacy_duplicate_exclusions"],
            },
            "exact_legacy_overlap_records": rejected_exact_legacy,
            "new_partition_exclusions": len(exclusions),
            "disposition": "The 80 rejected-candidate exact-legacy exclusions are retained only as source/hash/overlap provenance. Repaired assertions and exclusions are rebuilt from raw/reconciled source inputs.",
        },
        "cross_artifact_blocker_index": {
            "independent_atomic_review_findings": review_findings,
            "goal_schema_audit_findings": schema_findings,
            "complete_review_finding_id_coverage": True,
            "composition_allowed": False,
        },
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
            {
                "id": "ATOMIC-BLOCK-GOVERNING-TRUTH-TABLE-CONFLICT",
                "class": "GOVERNING_REQUIREMENT_CONFLICT",
                "count": 1,
                "finding_ids": ["F-004"],
                "effect": "An owner must resolve the UNVALIDATED score/rationale contradiction before composition or freeze.",
            },
            {
                "id": "ATOMIC-BLOCK-REBASE",
                "class": "UNINTEGRATED_BRANCH_PHASE_OR_OWNER_REBASE",
                "count": len(context_rebase_ids) + len(ambiguous_remaps),
                "blocker_ids": context_rebase_ids,
                "effect": "Ambiguous topology splits and coarse owner mappings remain explicitly null or canonical; no repaired owner is guessed.",
            },
            {
                "id": "ATOMIC-BLOCK-INDEPENDENT-REVIEW",
                "class": "REPAIRED_CANDIDATE_REQUIRES_FRESH_INDEPENDENT_REVIEW",
                "count": 1,
                "finding_ids": ["F-001", "F-002", "F-003", "F-005", "F-006", "P1-SCHEMA-001"],
                "effect": "Builder self-tests do not close the independent review findings.",
            },
            {
                "id": "ATOMIC-BLOCK-GOAL-SCHEMA",
                "class": "GOAL_SCHEMA_FINDINGS_OUTSIDE_ATOMIC_LAYER",
                "count": len(schema_findings) - 1,
                "finding_ids": [item["id"] for item in schema_findings if item["id"] != "P1-SCHEMA-001"],
                "effect": "The remaining schema findings are visible and remain open outside this isolated atomic candidate.",
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
    rejected_atomic_builder_bytes: bytes, rejected_atomic_candidate_bytes: bytes,
    independent_review: dict[str, Any], independent_review_bytes: bytes,
    repaired_topology: dict[str, Any], repaired_topology_bytes: bytes,
    goal_bytes: bytes, vv_skill_bytes: bytes,
) -> None:
    actual = {
        "canonical_baseline": sha256_bytes(baseline_bytes),
        "raw_claim_gap_audit": sha256_bytes(raw_bytes),
        "independent_gap_reconciliation": sha256_bytes(reconcile_bytes),
        "claim_schema_review": sha256_bytes(claim_review_bytes),
        "goal_schema_audit": sha256_bytes(goal_audit_bytes),
        "rejected_claim_integration_builder": sha256_bytes(rejected_builder_bytes),
        "rejected_claim_integration_candidate": sha256_bytes(rejected_candidate_bytes),
        "rejected_atomic_builder": sha256_bytes(rejected_atomic_builder_bytes),
        "rejected_atomic_candidate": sha256_bytes(rejected_atomic_candidate_bytes),
        "independent_atomic_review": sha256_bytes(independent_review_bytes),
        "repaired_topology_candidate": sha256_bytes(repaired_topology_bytes),
        "governing_goal": sha256_bytes(goal_bytes),
        "vv_evidence_skill": sha256_bytes(vv_skill_bytes),
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
    require(independent_review.get("overall_verdict") == "FAIL_NO_GO"
            and [item["id"] for item in independent_review.get("findings", [])]
            == ["F-001", "F-002", "F-003", "F-004", "F-005", "F-006"],
            "independent atomic review contract changed")
    require(repaired_topology.get("state") == "DRAFT_NOT_FROZEN",
            "repaired topology candidate unexpectedly changed state")
    require(reconcile["counts"]["classification"] == {
        "ABSORB_IN_PROCEDURE_FIELD": 67,
        "ADD_MATERIAL_CLAIM": 104,
        "DUPLICATE": 5,
        "LEGACY_EQUIVALENT": 1,
    }, "reconciliation classification denominator changed")
    require(reconcile["counts"]["new_executable_test_units"] == 0,
            "reconciliation creates executable units")
    topology_maps(baseline)
    topology_maps(repaired_topology, repaired=True)


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    baseline, baseline_bytes = load_json(CANONICAL_PATH)
    raw, raw_bytes = load_json(RAW_PATH)
    reconcile, reconcile_bytes = load_json(RECONCILE_PATH)
    claim_review, claim_review_bytes = load_json(CLAIM_REVIEW_PATH)
    goal_audit, goal_audit_bytes = load_json(GOAL_AUDIT_PATH)
    rejected_builder_bytes = REJECTED_BUILDER_PATH.read_bytes()
    rejected_candidate_bytes = REJECTED_CANDIDATE_PATH.read_bytes()
    rejected_atomic_builder_bytes = REJECTED_ATOMIC_BUILDER_PATH.read_bytes()
    rejected_atomic_candidate_bytes = REJECTED_ATOMIC_CANDIDATE_PATH.read_bytes()
    independent_review, independent_review_bytes = load_json(INDEPENDENT_REVIEW_PATH)
    repaired_topology, repaired_topology_bytes = load_json(REPAIRED_TOPOLOGY_PATH)
    goal_bytes = GOAL_PATH.read_bytes()
    vv_skill_bytes = VV_SKILL_PATH.read_bytes()
    preflight(
        baseline, baseline_bytes, raw, raw_bytes, reconcile, reconcile_bytes,
        claim_review, claim_review_bytes, goal_audit, goal_audit_bytes,
        rejected_builder_bytes, rejected_candidate_bytes,
        rejected_atomic_builder_bytes, rejected_atomic_candidate_bytes,
        independent_review, independent_review_bytes,
        repaired_topology, repaired_topology_bytes, goal_bytes, vv_skill_bytes,
    )
    return baseline, raw, reconcile, repaired_topology, independent_review, goal_audit


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
    parser_probe = Segment(
        1, 1, 1, 39, "Run the first check. Verify the result.",
        "PARAGRAPH", ("Probe",), None,
    )
    probe_units, _ = decisional_segments(parser_probe)
    require(len(probe_units) == 2, "decisional splitter accepted two independent sentences as one")
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
        value["topology_denominators"]["repaired_candidate"]["steps"] += 1
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
            for context in assertion["context_bindings"] if context["step_id"]
        )
        owner_source = (
            REPAIRED_TOPOLOGY_PATH if context["topology_basis"] == "REPAIRED_TOPOLOGY_CANDIDATE"
            else CANONICAL_PATH
        )
        owner_topology, _ = load_json(owner_source)
        wrong = next(
            step_id for procedure in owner_topology["procedures"] for branch in procedure["branches"]
            for step_id in [branch["steps"][0]["id"]]
            if procedure["id"] != context["procedure_id"]
        )
        context["step_id"] = wrong
        reseal(value)

    def multi_step_scope(value: dict[str, Any]) -> None:
        context = next(
            context for assertion in value["atomic_assertions"]
            for context in assertion["context_bindings"] if context["step_id"]
        )
        second = next(
            candidate for assertion in value["atomic_assertions"]
            for candidate in assertion["context_bindings"]
            if candidate["step_id"] and candidate["step_id"] != context["step_id"]
        )
        context["step_id"] = [context["step_id"], second["step_id"]]
        reseal(value)

    def cross_role_share(value: dict[str, Any]) -> None:
        contexts = [
            context for assertion in value["atomic_assertions"] for context in assertion["context_bindings"]
            if context["step_role"]
        ]
        first = contexts[0]
        second = next(item for item in contexts if item["step_role"] != first["step_role"])
        second["semantic_record"]["id"] = first["semantic_record"]["id"]
        reseal(value)

    def underdecomposed_clause(value: dict[str, Any]) -> None:
        assertion = next(
            item for item in value["atomic_assertions"]
            if item["source_binding"]["block_type"] != "CODE_FORM"
        )
        assertion["source_binding"]["block_type"] = "TABLE_ROW"
        reseal(value)

    def underdecomposed_table(value: dict[str, Any]) -> None:
        assertion = next(
            item for item in value["atomic_assertions"]
            if any(link["role"] == "TABLE_ROW_KEY" for link in item["source_binding"]["context_source_bindings"])
        )
        assertion["source_binding"]["block_type"] = "TABLE_ROW"
        reseal(value)

    def wrong_exact_command_owner(value: dict[str, Any]) -> None:
        assertion = next(
            item for item in value["atomic_assertions"]
            if item["source_binding"]["file"] == "host/machine-errors.mdx"
            and item["source_binding"]["line_start"] in {114, 115}
        )
        context = assertion["context_bindings"][0]
        context["step_id"] = "ERR-T02-B01-S01"
        context["step_role"] = "setup"
        context["exact_source_carrier_claim_id"] = None
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

    def drop_legacy_provenance(value: dict[str, Any]) -> None:
        value["provenance_reconciliation"]["exact_legacy_overlap_records"].pop()
        reseal(value)

    tests.extend([
        ("BUNDLE_LEVEL_SCORE", add_bundle_score),
        ("DROP_ASSERTION", drop_assertion),
        ("ADD_EXECUTABLE_UNIT", add_executable_unit),
        ("MUTATE_EXACT_TEXT", mutate_text),
        ("OVERLOAD_ALIGNMENT_DISPOSITION", overload_alignment),
        ("SHARE_SEMANTIC_RESULT", share_semantic),
        ("MULTI_STEP_SCOPE", multi_step_scope),
        ("CROSS_ROLE_RESULT_SHARING", cross_role_share),
        ("UNDERDECOMPOSED_INDEPENDENT_CLAUSES", underdecomposed_clause),
        ("UNDERDECOMPOSED_TABLE_ROW", underdecomposed_table),
        ("WRONG_STEP_OWNER", wrong_step_owner),
        ("WRONG_EXACT_COMMAND_OWNER_114_115", wrong_exact_command_owner),
        ("MUTATE_SOURCE_HASH", mutate_source_hash),
        ("REMOVE_CONTEXT", remove_context),
        ("ASSERTION_PASS_WITHOUT_EXECUTION", invent_pass_status),
        ("SEMANTIC_PASS_WITH_PENDING_AUTHORITY", pass_with_pending_authority),
        ("EXPOSE_PRIVATE_PATH", expose_private_path),
        ("DROP_SOURCE_EXCLUSION", drop_source_exclusion),
        ("DROP_LEGACY_OVERLAP_PROVENANCE", drop_legacy_provenance),
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
        baseline, raw, reconcile, repaired_topology, independent_review, goal_audit = load_inputs()
        candidate = build_candidate(
            baseline, raw, reconcile, repaired_topology, independent_review, goal_audit
        )
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
