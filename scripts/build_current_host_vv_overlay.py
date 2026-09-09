#!/usr/bin/env python3
"""Build the additive, current-source Host Docs review package.

This deliberately does not rewrite the frozen 7d V&V JSON triplet.  It uses
the historical package only as an auditable input for exact-source carry
forward; all changed/new prose is parsed from the current worktree.
"""

from __future__ import annotations

import argparse
import copy
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "verification/current-host-docs-review.json"
WORKLIST = REPO / "verification/current-host-docs-claim-worklist.md"
RUNTIME_REGISTER = REPO / "verification/current-runtime-operator-blockers.md"
OWNER_REGISTER = REPO / "verification/current-source-owner-blockers.md"
STATIC_EVIDENCE = REPO / "verification/evidence/2026-09-07-host-current-vv-attempt-01/current-static-checks.json"
TWO_DEFECT_STATIC_EVIDENCE = REPO / "verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/current-static-transition-checks-01.json"
CORRECTION_INPUT = REPO / "verification/current-host-claim-corrections.json"
EDITORIAL_INPUT = REPO / "verification/current-host-editorial-classifications.json"
LIVE_ADJUDICATION_INPUT = REPO / "verification/current-host-live-adjudications.json"
HISTORICAL_REVISION = "7d42a0d439f91e4dc2877104db807ec6fb975ce4"
CURRENT_REVISION = "bfa926c9421521767fa7411718bd31ea38b38528"
HISTORICAL_FILES = (
    "verification/host-docs-test-sets.json",
    "verification/host-docs-test-results.json",
    "verification/host-docs-command-scores.json",
)
STATUS = {"PASS", "FAIL", "BLOCKED", "UNVALIDATED", "STALE", "NOT_APPLICABLE"}
POLICY_RE = re.compile(
    r"\b(?:must|must not|should|should not|policy|agreement|contract|legal|tax|payout|payment|"
    r"billing|pricing|price|fee|prohibited|permitted|allowed|responsib|liable|security|privacy)\b",
    re.I,
)
RUNTIME_RE = re.compile(
    r"\b(?:run|create|delete|mount|attach|install|restart|reboot|rent|workload|network|port|gpu|"
    r"machine|instance|volume|appears|returns?|fails?|passes?)\b", re.I,
)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
IMPORT_RE = re.compile(
    r"^import\s+(?P<component>[A-Za-z][A-Za-z0-9_]*)\s+from\s+['\"](?P<path>/snippets/[A-Za-z0-9._/-]+\.mdx)['\"]\s*;?\s*$",
    re.M,
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    return digest(path.read_bytes())


def json_load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def git_tree() -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"{CURRENT_REVISION}^{{tree}}"], text=True
    ).strip()


def baseline_file_hash(source_file: str) -> str:
    """Return the exact bfa page blob identity for changed-page history."""
    return digest(subprocess.check_output(
        ["git", "-C", str(REPO), "show", f"{CURRENT_REVISION}:{source_file}"]
    ))


def line_hash(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"invalid source span {path}:{start}-{end}")
    return digest("\n".join(lines[start - 1:end]).encode())


def route_file(route: str) -> Path:
    relative = route.lstrip("/")
    candidates = (REPO / f"{relative}.mdx", REPO / relative / "index.mdx")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError(f"unresolved local route: {route}")


def host_navigation() -> list[str]:
    docs = json_load(REPO / "docs.json")
    tabs = docs.get("navigation", {}).get("tabs", [])
    host_tabs = [tab for tab in tabs if isinstance(tab, dict) and tab.get("tab") == "Host"]
    if len(host_tabs) != 1:
        raise ValueError("expected exactly one Host navigation tab")
    routes: list[str] = []

    def visit(items: list[Any]) -> None:
        for item in items:
            if isinstance(item, str):
                if not re.fullmatch(r"host/[A-Za-z0-9._/-]+", item):
                    raise ValueError(f"invalid Host route {item!r}")
                routes.append("/" + item)
            elif isinstance(item, dict) and isinstance(item.get("pages"), list):
                visit(item["pages"])
            else:
                raise ValueError("invalid Host navigation group")

    for group in host_tabs[0].get("groups", []):
        if not isinstance(group, dict) or not isinstance(group.get("pages"), list):
            raise ValueError("invalid Host navigation group")
        visit(group["pages"])
    if len(routes) != 44 or len(set(routes)) != 44:
        raise ValueError(f"expected 44 unique current Host routes, got {len(routes)}")
    return routes


def title_and_headings(path: Path) -> tuple[str, list[tuple[int, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    frontmatter_title: str | None = None
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            match = re.match(r"^title:\s*[\"']?(.+?)[\"']?\s*$", line)
            if match:
                frontmatter_title = match.group(1)
                break
    headings: list[tuple[int, str]] = []
    for number, line in enumerate(lines, 1):
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append((number, re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(1))))
    return (frontmatter_title or headings[0][1] if headings else path.stem.replace("-", " ").title(), headings)


def heading_for(headings: list[tuple[int, str]], line: int) -> str:
    selected = "Introduction"
    for start, title in headings:
        if start > line:
            break
        selected = title
    return selected


def dependencies(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    result: list[dict[str, Any]] = []
    for match in IMPORT_RE.finditer(text):
        component, source_file = match.group("component"), match.group("path").lstrip("/")
        source = REPO / source_file
        if not source.is_file():
            raise ValueError(f"missing rendered dependency {source_file}")
        use = re.compile(rf"^\s*<{re.escape(component)}\s*/>\s*$", re.M)
        uses = list(use.finditer(text))
        if len(uses) != 1:
            raise ValueError(f"expected one rendered use of {component} in {path}")
        result.append({
            "component": component, "source_file": source_file, "source_sha256": file_digest(source),
            "import_line": text.count("\n", 0, match.start()) + 1,
            "insertion_line": text.count("\n", 0, uses[0].start()) + 1,
        })
    return sorted(result, key=lambda item: (item["insertion_line"], item["component"]))


def current_span(source_file: str, start: int, end: int) -> dict[str, Any]:
    return {"source_file": source_file, "start": start, "end": end,
            "text_sha256": line_hash(REPO / source_file, start, end)}


def multi_span_hash(source_file: str, spans: list[dict[str, int]]) -> str:
    lines = (REPO / source_file).read_text(encoding="utf-8").splitlines()
    return digest("\n".join("\n".join(lines[item["start"] - 1:item["end"]]) for item in spans).encode())


def heading_ids(path: Path) -> set[str]:
    _title, headings = title_and_headings(path)
    explicit = set(re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", path.read_text(encoding="utf-8")))
    generated = {re.sub(r"[^a-z0-9]+", "-", title.casefold().replace("&", " and ")).strip("-") for _line, title in headings}
    return generated | explicit


def resolve_local_href(source_file: str, href: str) -> bool:
    if not href.startswith(("/", "#")):
        return False
    target, _sep, fragment = href.partition("#")
    if target:
        try:
            destination = route_file(target.rstrip("/"))
        except ValueError:
            return False
    else:
        destination = REPO / source_file
    return not fragment or fragment in heading_ids(destination)


def require_local_links(source_file: str, spans: list[tuple[int, int]]) -> None:
    """Perform the retained repository-local route/fragment check for a span."""
    lines = (REPO / source_file).read_text(encoding="utf-8").splitlines()
    for start, end in spans:
        for href in LINK_RE.findall("\n".join(lines[start - 1:end])):
            if not resolve_local_href(source_file, href):
                raise ValueError(f"unresolved local navigation {source_file}:{start}-{end} -> {href}")


def historical_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return tuple(json_load(REPO / item) for item in HISTORICAL_FILES)  # type: ignore[return-value]


def apply_claim_corrections(claims: list[dict[str, Any]], source_file: str) -> list[dict[str, Any]]:
    """Apply a hash-bound editorial input without granting it product proof."""
    if not CORRECTION_INPUT.is_file():
        return []
    data = json_load(CORRECTION_INPUT)
    if data.get("schema_version") != "1.1" or data.get("artifact_type") != "CURRENT_HOST_CLAIM_CORRECTION_INPUT":
        raise ValueError("unsupported current claim correction input")
    summaries: list[dict[str, Any]] = []
    for correction in data.get("corrections", []):
        if correction.get("source_file") != source_file:
            continue
        spans = correction["source_spans"]
        # The original identity is checked against the declared bfa baseline,
        # while replacement wording is checked against the live current file.
        baseline = subprocess.check_output(["git", "-C", str(REPO), "show", f"{CURRENT_REVISION}:{source_file}"])
        if digest(baseline) != correction["original_file_sha256"]:
            raise ValueError(f"correction baseline file hash mismatch: {correction['id']}")
        baseline_lines = baseline.decode("utf-8").splitlines()
        original = "\n".join("\n".join(baseline_lines[item["start"] - 1:item["end"]]) for item in spans)
        if digest(original.encode()) != correction["original_sha256"] or original != correction["original_text"]:
            raise ValueError(f"correction baseline span mismatch: {correction['id']}")
        live = "\n".join("\n".join((REPO / source_file).read_text(encoding="utf-8").splitlines()[item["start"] - 1:item["end"]]) for item in spans)
        if live != correction["replacement_text"]:
            raise ValueError(f"correction replacement mismatch: {correction['id']}")
        target = next((claim for claim in claims if claim["spans"] == [current_span(source_file, item["start"], item["end"]) for item in spans]), None)
        if target is None:
            raise ValueError(f"correction literal claim missing: {correction['id']}")
        target.update({
            "id": correction["id"], "text": live, "headings": [correction["heading"]],
            "status": correction["status"], "classification": correction["taxonomy_override"],
            "owner_role": "Network or API source owner",
            "rationale": correction["root_retest"]["initial_failure"], "next_action": correction["next_action"],
            "evidence_refs": [{"id": correction["id"], "role": "CURRENT_CORRECTION_RETEST",
                               "limit": correction["root_retest"]["evidence_limits"],
                               "artifact_ref": "verification/current-host-claim-corrections.json"}],
            "source_refs": [{"repository": item["repository"], "revision": item["revision"], "path": item["path"],
                             "locator": item["locator"], "source_kind": "PARTIAL_STATIC_SOURCE"}
                            for item in correction["evidence_partial_bindings"]],
            "history": {"baseline_claim_id": f"{correction['id']}-BASELINE", "baseline_source_text_sha256": correction["original_sha256"],
                        "carry_decision": "NO_HISTORICAL_PASS_TRANSFER" if target["coverage_state"] == "CHANGED" else "NOT_CARRIED_NEW",
                        "reason": correction["root_retest"]["retest"]},
        })
        summaries.append({"id": correction["id"], "scope": "current-claim-correction",
                          "history": f"bfa source span SHA-256 {correction['original_sha256']}.",
                          "current": f"Current spans {', '.join(f'{item['start']}-{item['end']}' for item in spans)} are {correction['status']}.",
                          "reason": correction["root_retest"]["retest"]})
    return summaries


def historical_by_route(sets: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    pages = {page["route"]: page for page in sets["pages"]}
    claims: dict[str, list[dict[str, Any]]] = {}
    for claim in sets["material_claims"]:
        claims.setdefault(claim["scope"]["route"], []).append(claim)
    return pages, claims


def page_is_exact(page: dict[str, Any], source_file: str, source_hash: str, deps: list[dict[str, Any]]) -> bool:
    if page.get("source_file") != source_file or page.get("source_sha256") != source_hash:
        return False
    old = [{key: value for key, value in item.items() if key in {"component", "source_file", "source_sha256", "import_line", "insertion_line"}}
           for item in page.get("rendered_dependencies", [])]
    return old == deps


def local_navigation(source_file: str, text: str) -> bool:
    links = LINK_RE.findall(text)
    return bool(links) and all(resolve_local_href(source_file, link) for link in links) and not re.sub(
        r"(?<!!)\[[^\]]+\]\([^)]+\)[,.;\s]*", "", text).strip()


def classify_literal(source_file: str, text: str) -> tuple[str, list[str], str, str, str | None, list[dict[str, Any]], list[dict[str, Any]]]:
    """Return conservative current-only classification; documentation proves nothing itself."""
    if local_navigation(source_file, text):
        return (
            "NAVIGATION_CONTRACT", ["REPOSITORY_STATIC_CHECK"], "Host Docs information-architecture owner", "PASS",
            "Every literal local route in this occurrence resolves inside the current repository.", None,
            [{"id": "EV-CURRENT-LOCAL-NAVIGATION-01", "role": "CURRENT_STATIC_RETEST",
              "limit": "Route/fragment existence only; linked-page semantics are not validated.",
              "artifact_ref": STATIC_EVIDENCE.relative_to(REPO).as_posix()}],
            [{"repository": "vast-ai/docs", "revision": CURRENT_REVISION, "path": "docs.json",
              "locator": "current local route declaration", "source_kind": "ROUTE_CONFIGURATION"}],
        )
    # Dashboard/view vocabulary on Market Metrics is descriptive UI prose, not
    # a financial-policy assertion merely because it says "price" or "market".
    market_ui = source_file == "host/market-metrics.mdx" and bool(re.search(r"\b(?:dashboard|view|chart|table|filter)\b", text, re.I))
    verification_gate = source_file == "host/disable-ssh-password-login.mdx" and "will not pass verification" in text.casefold()
    # Do not turn ordinary technical "should"/security/pricing vocabulary into
    # a Finance/Legal citation failure.  This current delta has one known
    # owner-governed tax assertion; ambiguous material remains UNVALIDATED.
    policy = (
        source_file == "host/guide-to-taxes.mdx"
        and bool(re.search(r"\b(?:VAT|tax|collect|remit|reporting threshold)\b", text, re.I))
    ) and not market_ui
    runtime = bool(RUNTIME_RE.search(text))
    lanes = (["ACCOUNTABLE_OWNER_CONFIRMATION", "AUTHORITATIVE_DOCUMENTATION_CITATION"] if policy else [])
    if runtime:
        lanes.extend(["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"])
    if verification_gate:
        lanes = list(dict.fromkeys(["CANONICAL_IMPLEMENTATION_SOURCE", "ACCOUNTABLE_OWNER_CONFIRMATION", *lanes]))
    if not lanes:
        lanes = ["CANONICAL_IMPLEMENTATION_SOURCE"]
    owner = "Product, Finance, and Legal owner" if policy else "Verification enforcement and Product policy owner" if verification_gate else "Host implementation source owner"
    status = "FAIL" if policy and not re.search(r"https://(?:cloud\.)?vast\.ai/(?:host/agreement|terms)", text) else "UNVALIDATED"
    rationale = (
        "The literal owner-governed statement has no authoritative citation in this exact current occurrence."
        if status == "FAIL" else
        "No current claim-suitable source, runtime observation, or accountable-owner decision is bound to this literal occurrence."
    )
    action = ("Obtain an exact authoritative source or dated owner decision; then bind a focused retest."
              if status == "FAIL" else
              "Bind an exact canonical source, authorized runtime observation, or accountable-owner decision before changing status.")
    return ("POLICY_OR_COMMERCIAL" if policy else "RUNTIME_BEHAVIOR" if runtime else "IMPLEMENTATION_OR_CONCEPT",
            lanes, owner, status, rationale, action, [], [])


def literal_blocks(route: str, source_file: str) -> list[dict[str, Any]]:
    """Extract literal source blocks without historical line-number exceptions."""
    path = REPO / source_file
    lines = path.read_text(encoding="utf-8").splitlines()
    _title, headings = title_and_headings(path)
    blocks: list[tuple[int, int, str]] = []
    paragraph: list[tuple[int, str]] = []
    fence: tuple[int, list[str]] | None = None
    comment_end: str | None = None
    frontmatter = bool(lines and lines[0].strip() == "---")

    def flush() -> None:
        if paragraph:
            start, end = paragraph[0][0], paragraph[-1][0]
            text = "\n".join(value for _line, value in paragraph).strip()
            if text and not text.startswith(("import ", "export ")):
                blocks.append((start, end, text))
            paragraph.clear()

    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if frontmatter:
            if line_number > 1 and stripped == "---":
                frontmatter = False
            continue
        if comment_end is not None:
            flush()
            if comment_end in line:
                if line.split(comment_end, 1)[1].strip():
                    raise ValueError(f"mixed comment/rendered line requires explicit parsing in {source_file}:{line_number}")
                comment_end = None
            continue
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            if fence is None:
                flush(); fence = (line_number, [line])
            else:
                start, values = fence; values.append(line); blocks.append((start, line_number, "\n".join(values))); fence = None
            continue
        if fence is not None:
            fence[1].append(line)
            continue
        # MDX comments are non-rendered authoring metadata.  Preserve their
        # line positions by skipping rather than deleting them before spans.
        if stripped.startswith(("{/*", "<!--")):
            flush()
            closing = "*/}" if stripped.startswith("{/*") else "-->"
            if closing not in stripped:
                comment_end = closing
            elif stripped.split(closing, 1)[1].strip():
                raise ValueError(f"mixed comment/rendered line requires explicit parsing in {source_file}:{line_number}")
            continue
        if re.match(r"^#{1,6}\s+", line) or not stripped:
            flush(); continue
        if re.fullmatch(r"(?:-{3,}|\*{3,}|_{3,})", stripped) or re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", stripped):
            flush(); continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush()
            if re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", stripped):
                continue
            if line_number < len(lines) and re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", lines[line_number].strip()):
                continue
            blocks.append((line_number, line_number, line)); continue
        if re.match(r"^(?:[-*+] |\d+[.)] )", stripped):
            flush(); blocks.append((line_number, line_number, line)); continue
        if re.fullmatch(r"</?[A-Za-z][^>]*>", stripped):
            flush(); continue
        paragraph.append((line_number, line))
    flush()
    if fence is not None:
        raise ValueError(f"unterminated fenced block in {source_file}")
    if comment_end is not None:
        raise ValueError(f"unterminated authoring comment in {source_file}")

    records: list[dict[str, Any]] = []
    for start, end, text in blocks:
        raw_hash = line_hash(path, start, end)
        classification, lanes, owner, status, rationale, action, evidence, refs = classify_literal(source_file, text)
        claim_id = "CUR-" + digest(f"{route}\0{source_file}\0{start}\0{end}\0{raw_hash}".encode())[:16]
        records.append({
            "id": claim_id, "text": text, "headings": [heading_for(headings, start)],
            "spans": [current_span(source_file, start, end)], "status": status,
            "required_evidence_types": lanes, "owner_role": owner, "rationale": rationale,
            "next_action": action, "evidence_refs": evidence, "source_refs": refs,
            "history": {"baseline_claim_id": None, "baseline_source_text_sha256": None,
                        "carry_decision": "NOT_CARRIED_NEW", "reason": "No exact historical page-source identity exists."},
            "classification": classification, "coverage_state": "NEW",
        })
        if classification == "NAVIGATION_CONTRACT":
            records[-1]["rationale"] = "Current repository-local route structure was inspected and every literal local navigation destination resolves."
            records[-1]["next_action"] = "No further action for this bounded local route/fragment existence check; linked-page semantics remain out of scope."
            records[-1]["history"]["carry_decision"] = "CURRENT_STATIC_RETEST"
    return records


def historical_evidence_refs(results: dict[str, Any], evidence_ids: list[str], limitations: list[str]) -> list[dict[str, Any]]:
    """Bind each historical evidence id to its retained, narrow artifact."""
    attempts = {item["attempt_id"]: item for item in results["attempts"]}
    bindings: dict[str, dict[str, Any]] = {}
    for category in ("material_claim_results", "support_layer_results", "procedure_results", "command_results"):
        for item in results[category]:
            evidence_id = item.get("evidence_id")
            if evidence_id in evidence_ids:
                if evidence_id in bindings:
                    raise ValueError(f"duplicate historical evidence binding: {evidence_id}")
                bindings[evidence_id] = item
    missing = set(evidence_ids) - set(bindings)
    if missing:
        raise ValueError(f"unmapped historical evidence ids: {sorted(missing)}")
    limit = " ".join(limitations) or "Historical evidence limits are recorded by the bound result."
    refs = []
    for evidence_id in evidence_ids:
        binding = bindings[evidence_id]
        attempt = attempts.get(binding["attempt_id"])
        if attempt is None:
            raise ValueError(f"missing historical attempt: {binding['attempt_id']}")
        artifact = binding.get("evidence_ref") or attempt.get("evidence_ref")
        if not isinstance(artifact, str) or not artifact.startswith("verification/evidence/"):
            raise ValueError(f"missing retained artifact: {evidence_id}")
        refs.append({"id": evidence_id, "role": "HISTORICAL_CARRY_FORWARD_EXACT_SOURCE",
                     "limit": limit, "artifact_ref": artifact})
    return refs


def translated_historical_claim(claim: dict[str, Any], coverage: str, results: dict[str, Any]) -> dict[str, Any]:
    scope = claim["scope"]
    source_file = scope["source_file"]
    if multi_span_hash(source_file, scope["source_spans"]) != scope["source_text_sha256"]:
        raise ValueError(f"historical claim source span mismatch: {claim['claim_id']}")
    spans = [current_span(source_file, item["start"], item["end"]) for item in scope["source_spans"]]
    lines = (REPO / source_file).read_text(encoding="utf-8").splitlines()
    literal = "\n".join("\n".join(lines[item["start"] - 1:item["end"]]) for item in scope["source_spans"])
    source_refs = claim["authority"].get("source_refs", [])
    current = claim["current"]
    return {
        "id": claim["claim_id"], "text": literal, "headings": [scope["heading"]],
        "spans": spans, "status": current["status"],
        "required_evidence_types": claim["evidence_requirement"]["types"],
        "owner_role": claim["authority"].get("unresolved_owner_role") or "Bound historical source owner",
        "rationale": current.get("rationale") or "Exact current primary/rendered source and literal source-span hashes match the frozen historical package; status is carried only for this unchanged wording.",
        "next_action": claim.get("next_action") or "No additional current action is recorded for this exact-source historical carry-forward.",
        "evidence_refs": historical_evidence_refs(results, current.get("evidence_ids", []), current.get("limitations", [])),
        "source_refs": source_refs,
        "history": {"baseline_claim_id": claim["claim_id"], "baseline_source_text_sha256": scope["source_text_sha256"],
                    "carry_decision": "CARRIED_FORWARD_EXACT_SOURCE", "reason": "Full page/dependency and literal span hashes match."},
        "classification": claim["claim"]["kind"], "coverage_state": coverage,
    }


def apply_editorial_classifications(claims: list[dict[str, Any]]) -> None:
    """Correct only independently reviewed, exact hash-bound non-product rows."""
    by_id = {claim["id"]: claim for claim in claims}
    for item in json_load(EDITORIAL_INPUT)["classifications"]:
        claim = by_id.get(item["id"])
        if claim is None:
            continue
        expected_span = current_span(item["source_file"], item["start"], item["end"])
        if claim["text"] != item["literal"] or digest(claim["text"].encode()) != item["literal_sha256"] or claim["spans"] != [expected_span]:
            raise ValueError(f"stale exact editorial classification: {item['id']}")
        nav = item["class"] == "NAVIGATION_CONTRACT"
        if nav:
            require_local_links(item["source_file"], [(item["start"], item["end"])])
        claim.update({
            "classification": item["class"], "status": "PASS" if nav else "NOT_APPLICABLE",
            "required_evidence_types": item["required_evidence_types"], "owner_role": "Documentation maintainer",
            "rationale": item["reason_old_classification_wrong"] + (" Current local destinations resolve." if nav else ""),
            "next_action": "No operator or source-owner action for this exact navigation/editorial occurrence; linked product claims retain their own evidence requirements.",
            "source_refs": [],
            "evidence_refs": [{"id": item["id"], "role": "CURRENT_TAXONOMY_RETEST",
                "limit": "Exact literal classification only; no product behavior or owner approval implied.",
                "artifact_ref": EDITORIAL_INPUT.relative_to(REPO).as_posix()}] + ([{
                "id": "EV-CURRENT-LOCAL-NAVIGATION-01", "role": "CURRENT_STATIC_RETEST",
                "limit": "Local destination existence only, not linked-page semantics.",
                "artifact_ref": STATIC_EVIDENCE.relative_to(REPO).as_posix()}] if nav else []),
            "history": {**claim["history"], "carry_decision": "CURRENT_STATIC_RETEST",
                "reason": "The frozen historical disposition remains unchanged; this exact current occurrence received a narrow taxonomy correction."},
        })


def _exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValueError(f"invalid {label} keys")


def apply_live_endpoint_adjudications(pages: list[dict[str, Any]]) -> None:
    """Apply only registry-approved direct API checks to atomic endpoint rows.

    The registry is intentionally narrower than a general live-evidence importer:
    a HTTP 200 by itself cannot promote a claim, and CLI execution is excluded.
    """
    data = json_load(LIVE_ADJUDICATION_INPUT)
    _exact_keys(data, {"schema_version", "artifact_type", "purpose", "baseline", "artifact", "adjudications"}, "live adjudication input")
    if data["schema_version"] != "1.0" or data["artifact_type"] != "CURRENT_HOST_LIVE_ENDPOINT_ADJUDICATION_INPUT":
        raise ValueError("unsupported live adjudication input")
    _exact_keys(data["baseline"], {"current_package_sha256", "source_revision"}, "live adjudication baseline")
    if data["baseline"]["source_revision"] != CURRENT_REVISION or not re.fullmatch(r"[a-f0-9]{64}", data["baseline"]["current_package_sha256"]):
        raise ValueError("invalid live adjudication baseline")
    _exact_keys(data["artifact"], {"path", "sha256"}, "live adjudication artifact")
    artifact_ref = data["artifact"]["path"]
    if not isinstance(artifact_ref, str) or not re.fullmatch(r"verification/evidence/2026-09-08-host-live-readonly-attempt-01/[a-z0-9-]+\.json", artifact_ref):
        raise ValueError("invalid live adjudication artifact path")
    artifact_path = REPO / artifact_ref
    if not artifact_path.is_file() or artifact_path.is_symlink() or file_digest(artifact_path) != data["artifact"]["sha256"]:
        raise ValueError("live adjudication artifact digest mismatch")
    observation = json_load(artifact_path)
    if observation.get("method") != "Direct API GET, not CLI execution" or not re.fullmatch(r"[a-f0-9]{40}", observation.get("source_revision", "")):
        raise ValueError("live adjudication is not a direct API observation")
    source_files = {(item.get("repository"), item.get("path")): item for item in observation.get("source_files", [])}
    schemas = {item.get("path"): item for item in observation.get("schemas", [])}
    requests = observation.get("requests")
    if not isinstance(requests, list):
        raise ValueError("missing live adjudication requests")
    claims = {claim["id"]: (page, claim) for page in pages for claim in page["claims"]}
    seen: set[str] = set()
    expected_ids = {"CUR-a5b27de02fca3c9a", "CUR-6c8062ab1c766957", "CUR-2de1188bec6c9f72"}
    if not isinstance(data["adjudications"], list) or {item.get("claim_id") for item in data["adjudications"]} != expected_ids:
        raise ValueError("live adjudication target set is not exact")
    for item in data["adjudications"]:
        _exact_keys(item, {"id", "claim_id", "route", "source_file", "span", "literal", "literal_sha256", "prior_status",
                           "required_evidence_types", "endpoint", "description", "source_binding", "request_index", "request_query", "expected_shape", "limitations"}, "live adjudication")
        claim_id = item["claim_id"]
        if claim_id in seen or claim_id not in expected_ids or claim_id not in claims:
            raise ValueError("duplicate or unknown live adjudication claim")
        seen.add(claim_id)
        page, claim = claims[claim_id]
        _exact_keys(item["span"], {"start", "end", "text_sha256"}, "live adjudication span")
        expected_span = current_span(item["source_file"], item["span"]["start"], item["span"]["end"])
        if (page["route"] != item["route"] or page["source_file"] != item["source_file"] or
                claim["spans"] != [expected_span] or item["span"]["text_sha256"] != expected_span["text_sha256"] or claim["text"] != item["literal"] or
                digest(claim["text"].encode()) != item["literal_sha256"] or claim["status"] != item["prior_status"] or
                item["prior_status"] != "UNVALIDATED" or claim["required_evidence_types"] != item["required_evidence_types"] or
                item["required_evidence_types"] != ["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"]):
            raise ValueError("live adjudication claim identity or lanes mismatch")
        literal = re.fullmatch(r"\| `GET (?P<endpoint>/api/v0/metrics/gpu/(?:current|history|locations)/)` \| (?P<description>[^|]+) \|", claim["text"])
        if not literal or literal["endpoint"] != item["endpoint"] or literal["description"] != item["description"]:
            raise ValueError("live adjudication is not an atomic endpoint description")
        _exact_keys(item["source_binding"], {"client_path", "client_sha256", "openapi_path", "openapi_sha256"}, "live adjudication source binding")
        client = source_files.get(("vast-ai/vast-cli", item["source_binding"]["client_path"]))
        schema = schemas.get(item["source_binding"]["openapi_path"])
        if (not client or client.get("sha256") != item["source_binding"]["client_sha256"] or client.get("path_status") != "" or
                not schema or schema.get("sha256") != item["source_binding"]["openapi_sha256"] or
                item["source_binding"]["openapi_path"] == item["source_file"]):
            raise ValueError("live adjudication source binding mismatch")
        schema_blob = subprocess.check_output(["git", "-C", str(REPO), "cat-file", "blob",
            f"{CURRENT_REVISION}:{item['source_binding']['openapi_path']}"])
        if digest(schema_blob) != item["source_binding"]["openapi_sha256"]:
            raise ValueError("live adjudication pinned OpenAPI blob mismatch")
        if not isinstance(item["request_index"], int) or item["request_index"] < 0 or item["request_index"] >= len(requests) or not isinstance(item["request_query"], str):
            raise ValueError("invalid live adjudication request index")
        request = requests[item["request_index"]]
        parsed = urlparse(request.get("url", ""))
        _exact_keys(item["expected_shape"], {"root_fields", "boolean_field", "required_sections"}, "live adjudication expected shape")
        if (request.get("claim_id") != claim_id or request.get("method") != "GET" or parsed.scheme != "https" or
                parsed.netloc != "console.vast.ai" or parsed.path != item["endpoint"] or parsed.params or parsed.query != item["request_query"] or parsed.fragment or request.get("http_status") != 200 or
                request.get("success") is not True or request.get("json_parsed") is not True or request.get("shape_ok") is not True or
                request.get("status") != "PASS" or request.get("needs_machine") is not None or
                request.get("root_fields") != item["expected_shape"]["root_fields"] or
                request.get(item["expected_shape"]["boolean_field"]) is not True or
                not set(item["expected_shape"]["required_sections"]).issubset(set(request.get("sample_sections", [])))):
            raise ValueError("live adjudication request does not satisfy endpoint predicate")
        claim.update({
            "status": "PASS",
            "rationale": "Exact canonical API-client and OpenAPI bindings match a retained direct GET with the claim-specific successful response shape.",
            "next_action": "No further action for this exact endpoint-description observation. Keep broader market, cadence, finance, filter, CLI, Host, and renter claims separately reviewed.",
            "evidence_refs": [{"id": item["id"], "role": "CURRENT_LIVE_ENDPOINT_ADJUDICATION", "limit": item["limitations"], "artifact_ref": artifact_ref}],
            "source_refs": [
                {"repository": "vast-ai/vast-cli", "revision": observation["source_revision"], "path": item["source_binding"]["client_path"],
                 "locator": f"API client binding for {item['endpoint']}", "source_kind": "CANONICAL_API_CLIENT_SOURCE"},
                {"repository": "vast-ai/docs", "revision": CURRENT_REVISION, "path": item["source_binding"]["openapi_path"],
                 "locator": f"OpenAPI contract for {item['endpoint']}", "source_kind": "OPENAPI_SOURCE"},
            ],
            "history": {**claim["history"], "carry_decision": "CURRENT_LIVE_ENDPOINT_ADJUDICATION",
                        "reason": claim["history"]["reason"] + " Current direct endpoint adjudication is separately bound; no historical PASS was transferred."},
        })


def span_union(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in items]


def nodes_for_set(page: dict[str, Any], test_set: dict[str, Any], coverage: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    set_id = test_set["test_set_id"]
    source_file = page["source_file"]
    context = test_set["source_context"]
    set_spans = [current_span(source_file, context["line_start"], context["line_end"])] if coverage == "UNCHANGED_EXACT" else []
    nodes.append(node("TEST_SET", set_id, None, True, source_file, context.get("headings", []), set_spans,
                      test_set["execution_status"], coverage, set_id))
    for branch in test_set["branches"]:
        branch_id = branch["branch_id"]
        branch_spans = [] if coverage != "UNCHANGED_EXACT" else span_union(
            current_span(source_file, span["start"], span["end"])
            for step in branch["steps"] for span in step["source_lines"])
        nodes.append(node("BRANCH", branch_id, set_id, True, source_file, [], branch_spans,
                          branch["execution_status"], coverage, branch_id))
        for step in branch["steps"]:
            step_id = step["step_id"]
            spans = [current_span(source_file, span["start"], span["end"])
                     for span in step["source_lines"]] if coverage == "UNCHANGED_EXACT" else []
            nodes.append(node("STEP", step_id, branch_id, bool(step["required"]), source_file,
                              step["source_sections"], spans, step["execution_status"], coverage, step_id))
            for command in step["commands"]:
                source = command["source"]
                command_spans = [current_span(source["file"], source["line_start"], source["line_end"])] if coverage == "UNCHANGED_EXACT" else []
                nodes.append(node("COMMAND", command["command_id"], step_id, True, source["file"],
                                  [source["section"]], command_spans, command["execution_status"], coverage,
                                  command["command_id"]))
    return nodes


def procedure_nodes(page: dict[str, Any], coverage: str) -> list[dict[str, Any]]:
    return [node for test_set in page.get("test_sets", []) for node in nodes_for_set(page, test_set, coverage)]


def node(kind: str, identifier: str, parent: str | None, required: bool, source_file: str,
         headings: list[str], spans: list[dict[str, Any]], status: str, coverage: str, baseline_target: str) -> dict[str, Any]:
    carried = coverage == "UNCHANGED_EXACT"
    return {
        "kind": kind, "id": identifier, "parent_id": parent, "required": required,
        "source_file": source_file, "headings": headings, "spans": spans,
        "status": status if carried else "STALE", "coverage_state": coverage,
        "limits": ["Historical procedure node retained for traceability; no execution is represented by this current mapping."] if not carried else
                  ["Exact source identity carry-forward only; no new runtime execution occurred."],
        "next_action": "No additional current action is recorded for this exact-source historical carry-forward." if carried else "Map this historical procedure node to current literal wording and retain a focused current result before using it as validation.",
        "history": {"baseline_level": kind, "baseline_target": {"id": baseline_target},
                    "baseline_status": status, "carry_decision": "CARRIED_FORWARD_EXACT_SOURCE" if carried else "NOT_CARRIED_SOURCE_CHANGED"},
    }


def current_section_procedure(route: str, source_file: str, coverage: str) -> dict[str, Any]:
    _title, headings = title_and_headings(REPO / source_file)
    lines = (REPO / source_file).read_text(encoding="utf-8").splitlines()
    nodes = []
    for index, (start, heading) in enumerate(headings):
        end = (headings[index + 1][0] - 1) if index + 1 < len(headings) else len(lines)
        nodes.append({
            "kind": "CURRENT_HEADING_CHECK", "id": f"CUR-{Path(source_file).stem}-H{index + 1:02d}",
            "parent_id": None, "required": True, "source_file": source_file, "headings": [heading],
            "spans": [current_span(source_file, start, end)], "status": "UNVALIDATED", "coverage_state": coverage,
            "limits": ["Current source inventory only; no Host, API, credentialed, paid, privileged, or mutating behavior was executed."],
            "next_action": "Bind exact source, owner, or authorized runtime evidence for claims in this section.",
            "history": {"baseline_level": None, "baseline_target": None, "baseline_status": None,
                        "carry_decision": "NOT_CARRIED_NEW" if coverage == "NEW" else "NOT_CARRIED_SOURCE_CHANGED"},
        })
    return {"id": f"CUR-{Path(source_file).stem}-ORDERED-SECTIONS", "title": "Current ordered section review",
            "coverage_state": coverage, "status": "UNVALIDATED", "headings": [item[1] for item in headings],
            "spans": [current_span(source_file, start, (headings[index + 1][0] - 1) if index + 1 < len(headings) else len(lines)) for index, (start, _heading) in enumerate(headings)],
            "limits": ["Source-only ordered review, not product or runtime validation."],
            "history": {"baseline_test_set_id": None if coverage == "NEW" else f"CUR-{Path(source_file).stem}-BASELINE-PAGE", "carry_decision": "NOT_CARRIED_NEW" if coverage == "NEW" else "NOT_CARRIED_SOURCE_CHANGED", "reason": "New current Host page." if coverage == "NEW" else "Changed current page requires source-level review."},
            "nodes": nodes}


def support_layers() -> list[dict[str, Any]]:
    layers: list[dict[str, Any]] = []
    for layer, root, central, count in (
        ("CLI", REPO / "host/cli", "cli/reference", 18),
        ("SDK", REPO / "host/sdk", "sdk/python/reference", 15),
    ):
        wrappers = sorted(root.glob("*.mdx"))
        if len(wrappers) != count:
            raise ValueError(f"expected {count} {layer} wrappers")
        for wrapper in wrappers:
            text = wrapper.read_text(encoding="utf-8")
            match = IMPORT_RE.search(text)
            if match is None:
                raise ValueError(f"missing support fragment import in {wrapper}")
            fragment = REPO / match.group("path").lstrip("/")
            central_file = REPO / central / wrapper.name
            if not fragment.is_file() or not central_file.is_file():
                raise ValueError(f"missing support source for {wrapper}")
            changed = wrapper.name in {"list-machines.mdx", "defrag-machines.mdx", "schedule-maint.mdx", "show-machine.mdx", "show-machines.mdx", "show-maints.mdx"}
            layers.append({
                "support_id": f"SUPPORT-{layer}-{wrapper.stem}", "layer": layer,
                "route": f"/host/{layer.lower()}/{wrapper.stem}", "source_file": wrapper.relative_to(REPO).as_posix(),
                "source_sha256": file_digest(wrapper), "fragment_file": fragment.relative_to(REPO).as_posix(),
                "fragment_sha256": file_digest(fragment), "central_reference_file": central_file.relative_to(REPO).as_posix(),
                "central_reference_route": f"/{central}/{wrapper.stem}", "central_reference_sha256": file_digest(central_file),
                "classification": "CENTRAL_REFERENCE_SUPPORT_LAYER", "workflow": False, "status": "PASS",
                "coverage_state": "CHANGED" if changed else "UNCHANGED_EXACT",
                "evidence_refs": [{"id": "EV-CURRENT-SUPPORT-STRUCTURE-01", "role": "CURRENT_STATIC_SUPPORT_STRUCTURE",
                                   "limit": "Wrapper/import/fragment/central-reference structure only; no command runtime or Host workflow behavior.",
                                   "artifact_ref": STATIC_EVIDENCE.relative_to(REPO).as_posix()}],
                "claim_limit": "Support structure only; this is not an independent Host workflow or runtime result.",
            })
    return layers


def worklist(package: dict[str, Any]) -> tuple[str, str, str]:
    pairs = [(page, claim) for page in package["pages"] for claim in page["claims"]]
    unresolved = [(page, claim) for page, claim in pairs if claim["status"] not in {"PASS", "NOT_APPLICABLE"}]
    table = ["# Current Host Docs claim worklist", "", "Current-source claims requiring proof or correction. Historical evidence is carried only where exact source identity is recorded.", "",
             f"Current dispositions: {len(pairs)} occurrences ({sum(c['status'] == 'PASS' for _, c in pairs)} PASS, {sum(c['status'] == 'NOT_APPLICABLE' for _, c in pairs)} editorial NOT_APPLICABLE, {len(unresolved)} requiring review or evidence). Most dispositions are automated or exact historical carry-forward; this package records no invented manual completion.", ""]
    for page in package["pages"]:
        page_claims = [claim for candidate, claim in unresolved if candidate["route"] == page["route"]]
        if not page_claims:
            continue
        table.extend([f"## [{page['title']}](http://127.0.0.1:4000{page['route']})", ""])
        for claim in page_claims:
            heading = claim["headings"][0] if claim["headings"] else "Introduction"
            anchor = "" if heading == "Introduction" else "#" + re.sub(r"[^a-z0-9]+", "-", heading.casefold()).strip("-")
            quote = claim["text"].replace("\n", " ")
            proof = ", ".join(item.replace("_", " ").title() for item in claim["required_evidence_types"])
            refs = "; ".join(
                f"[{item['id']}]({Path(item['artifact_ref']).relative_to('verification').as_posix()}) — {item['limit']}"
                for item in claim["evidence_refs"]
            ) or "No retained proof"
            table.extend([f"### [{heading}](http://127.0.0.1:4000{page['route']}{anchor}) — `{claim['id']}`", "",
                          f"**Status:** {claim['status']}", "", f"**Literal source text:** {quote}", "",
                          f"**Required proof:** {proof}", "", f"**Existing proof / limit:** {refs}", "",
                          f"**Owner:** {claim['owner_role']}", "", f"**Next:** {claim['next_action']}", ""])
    runtime = ["# Current runtime/operator blockers", "", "Only claims requiring an authorized runtime or UI observation are listed. Status headings are dispositions, not a claim that every row is blocked.", ""]
    owners = ["# Current source-owner blockers", "", "Claims requiring source or accountable-owner evidence are listed. Status headings are dispositions, not a claim that every row is blocked.", ""]
    for status in ("BLOCKED", "FAIL", "UNVALIDATED"):
        runtime_rows: list[str] = []
        owner_rows: list[str] = []
        for page, claim in unresolved:
            if claim["status"] != status:
                continue
            quote = claim["text"].replace("\n", " ")
            heading = claim["headings"][0] if claim["headings"] else "Introduction"
            anchor = "" if heading == "Introduction" else "#" + re.sub(r"[^a-z0-9]+", "-", heading.casefold()).strip("-")
            row = f"- [{page['title']} — {heading}](http://127.0.0.1:4000{page['route']}{anchor}) — `{claim['id']}` — “{quote}” — **Owner:** {claim['owner_role']}. **Required:** {', '.join(claim['required_evidence_types'])}. **Next:** {claim['next_action']}"
            if "RUNTIME_OR_UI_OBSERVATION" in claim["required_evidence_types"]:
                runtime_rows.append(row)
            if any(item in claim["required_evidence_types"] for item in ("CANONICAL_IMPLEMENTATION_SOURCE", "ACCOUNTABLE_OWNER_CONFIRMATION", "AUTHORITATIVE_DOCUMENTATION_CITATION")):
                owner_rows.append(row)
        if runtime_rows:
            runtime.extend([f"## {status}", *runtime_rows, ""])
        if owner_rows:
            owners.extend([f"## {status}", *owner_rows, ""])
    return "\n".join(table).rstrip() + "\n", "\n".join(runtime).rstrip() + "\n", "\n".join(owners).rstrip() + "\n"


def static_evidence(package: dict[str, Any]) -> dict[str, Any]:
    """Retain only deterministic repository-local structural checks."""
    nav: list[dict[str, Any]] = []
    for page in package["pages"]:
        source_file = page["source_file"]
        for href in LINK_RE.findall((REPO / source_file).read_text(encoding="utf-8")):
            if href.startswith(("/", "#")):
                nav.append({"source_file": source_file, "source_sha256": page["source_sha256"], "href": href,
                            "result": "PASS" if resolve_local_href(source_file, href) else "FAIL"})
    volume = next(page for page in package["pages"] if page["route"] == "/host/volume-offers")
    volume_checks: list[dict[str, Any]] = []
    for start, end in ((101, 109), (111, 118)):
        for href in LINK_RE.findall("\n".join((REPO / volume["source_file"]).read_text(encoding="utf-8").splitlines()[start - 1:end])):
            volume_checks.append({"source_file": volume["source_file"], "source_sha256": volume["source_sha256"],
                                  "span": [start, end], "href": href, "result": "PASS" if resolve_local_href(volume["source_file"], href) else "FAIL"})
    support = [{"support_id": row["support_id"], "wrapper": {"path": row["source_file"], "sha256": row["source_sha256"]},
                "fragment": {"path": row["fragment_file"], "sha256": row["fragment_sha256"]},
                "central_reference": {"path": row["central_reference_file"], "sha256": row["central_reference_sha256"]}, "result": "PASS"}
               for row in package["support_layers"]]
    return {"schema_version": "1.0", "record_type": "HOST_DOCS_CURRENT_STATIC_CHECKS", "generated_at": package["generated_at"],
            "method": "Deterministic repository-local route/fragment resolution and wrapper/import/central-reference structural inspection.",
            "limits": "No Host, API, credentialed, paid, privileged, mutating, linked-page semantic, or runtime behavior was exercised.",
            "checks": [
                {"id": "EV-CURRENT-LOCAL-NAVIGATION-01", "result": "PASS" if all(item["result"] == "PASS" for item in nav) else "FAIL", "hrefs": nav},
                {"id": "EV-CURRENT-SUPPORT-STRUCTURE-01", "result": "PASS", "layers": support},
                {"id": "EV-CURRENT-VOL-C35-NAVIGATION-01", "result": "PASS" if all(item["result"] == "PASS" for item in volume_checks) else "FAIL", "hrefs": volume_checks},
            ]}


def _build_with_transition_projection() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    historical_sets, historical_results, _historical_scores = historical_inputs()
    old_pages, old_claims = historical_by_route(historical_sets)
    pages: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []
    correction_summaries: list[dict[str, Any]] = []
    for route in host_navigation():
        source = route_file(route)
        source_file = source.relative_to(REPO).as_posix()
        source_hash = file_digest(source)
        title, _headings = title_and_headings(source)
        deps = dependencies(source)
        old = old_pages.get(route)
        coverage = "NEW" if old is None else "UNCHANGED_EXACT" if page_is_exact(old, source_file, source_hash, deps) else "CHANGED"
        manifest.append({"kind": "PRIMARY", "route": route, "path": source_file, "sha256": source_hash})
        for dep in deps:
            manifest.append({"kind": "RENDERED_DEPENDENCY", "route": route, "path": dep["source_file"], "sha256": dep["source_sha256"]})
        if coverage == "UNCHANGED_EXACT":
            claims = [translated_historical_claim(claim, coverage, historical_results) for claim in old_claims.get(route, [])]
            apply_editorial_classifications(claims)
            if route == "/host/volume-offers":
                require_local_links(source_file, [(101, 109), (111, 118)])
                target = next(claim for claim in claims if claim["id"] == "VOL-C35")
                composite_spans = [current_span(source_file, 101, 109), current_span(source_file, 111, 118)]
                lines = (REPO / source_file).read_text(encoding="utf-8").splitlines()
                target.update({"headings": ["Command Map", "Related Pages"],
                               "spans": composite_spans,
                               "text": "\n".join("\n".join(lines[span["start"] - 1:span["end"]]) for span in composite_spans),
                               "status": "UNVALIDATED", "rationale": "The expanded source scope includes Command Map instructions as well as Related Pages. The retained navigation retest passes for destinations only; it does not establish command semantics.",
                               "required_evidence_types": ["CANONICAL_IMPLEMENTATION_SOURCE"],
                               "owner_role": "Volumes backend/API implementation source owner",
                               "next_action": "The nine pinned CLI dispatches have been inspected. Supply the backend endpoint implementation for ownership, publication, attachment and deletion eligibility/persistence; the client does not establish these effects. Keep navigation and client-dispatch proof separate from backend semantics.",
                               "evidence_refs": [{"id": "EV-CURRENT-VOL-C35-NAVIGATION-01", "role": "CURRENT_STATIC_RETEST",
                                                  "limit": "Current local route/fragment existence only; linked semantics remain outside this result.",
                                                  "artifact_ref": STATIC_EVIDENCE.relative_to(REPO).as_posix()},
                                                 {"id": "EV-CURRENT-VOLUME-COMMAND-MAP-SOURCE-01", "role": "PARTIAL_CLIENT_SOURCE_INSPECTION",
                                                  "limit": "Nine pinned CLI dispatches inspected; backend ownership, publication, attachment, deletion and persistence remain unproven.",
                                                  "artifact_ref": "verification/evidence/2026-09-07-host-current-vv-attempt-01/volume-command-map-source-inspection.md"}],
                               "history": {"baseline_claim_id": "VOL-C35", "baseline_source_text_sha256": target["history"]["baseline_source_text_sha256"],
                                           "carry_decision": "CURRENT_STATIC_RETEST", "reason": "Current static retest expands the narrow historical Related Pages scope to include Command Map."}})
            procedures = [{"id": item["test_set_id"], "title": item["title"], "coverage_state": coverage,
                           "status": item["execution_status"], "headings": item["source_context"]["headings"],
                           "spans": [current_span(source_file, item["source_context"]["line_start"], item["source_context"]["line_end"])],
                           "limits": ["Exact current source identity carry-forward only; no new execution."],
                           "history": {"baseline_test_set_id": item["test_set_id"], "carry_decision": "CARRIED_FORWARD_EXACT_SOURCE", "reason": "Full page and rendered dependency hashes match."},
                           "nodes": nodes_for_set(old, item, coverage)} for item in old["test_sets"]]
        else:
            claims = literal_blocks(route, source_file)
            # Imported MDX contributes rendered reader-facing prose.  Parse it
            # from its current bytes under the rendering Host route; never use
            # historical line maps as a substitute.
            for dependency in deps:
                claims.extend(literal_blocks(route, dependency["source_file"]))
            for claim in claims:
                claim["coverage_state"] = coverage
                claim["history"]["carry_decision"] = "NO_HISTORICAL_PASS_TRANSFER" if coverage == "CHANGED" else "NOT_CARRIED_NEW"
                if coverage == "CHANGED":
                    claim["history"].update({"baseline_claim_id": f"BASELINE-PAGE-{Path(source_file).stem.upper().replace('-', '_')}",
                                             "baseline_source_text_sha256": baseline_file_hash(source_file),
                                             "reason": "Current source differs from the frozen historical page; no historical PASS transfers to this literal."})
                else:
                    claim["history"]["reason"] = "No historical page exists."
            correction_summaries.extend(apply_claim_corrections(claims, source_file))
            procedures = ([{"id": item["test_set_id"], "title": item["title"], "coverage_state": coverage, "status": "STALE",
                            "headings": item["source_context"]["headings"], "spans": [],
                            "limits": ["Historical procedure retained only; changed current source is not validated by it."],
                            "history": {"baseline_test_set_id": item["test_set_id"], "carry_decision": "NOT_CARRIED_SOURCE_CHANGED", "reason": "Current page source differs."},
                            "nodes": nodes_for_set(old, item, coverage)} for item in old["test_sets"]] if old else [])
            procedures.append(current_section_procedure(route, source_file, coverage))
        pages.append({"route": route, "title": title, "source_file": source_file, "source_sha256": source_hash,
                      "dependencies": deps, "coverage_state": coverage, "claims": claims, "procedures": procedures})
    apply_live_endpoint_adjudications(pages)
    product_spec = importlib.util.spec_from_file_location("current_host_product_publications",
        Path(__file__).with_name("current_host_product_publications.py"))
    product_module = importlib.util.module_from_spec(product_spec)
    product_spec.loader.exec_module(product_module)
    correction_summaries.append(product_module.apply_product_publications(pages, REPO))
    readonly_spec = importlib.util.spec_from_file_location("current_host_readonly_adjudications",
        Path(__file__).with_name("current_host_readonly_adjudications.py"))
    readonly_module = importlib.util.module_from_spec(readonly_spec)
    readonly_spec.loader.exec_module(readonly_module)
    correction_summaries.extend(readonly_module.apply_current_host_readonly_adjudications(pages, REPO))
    # The two historical FAIL records are preserved in their immutable registry.
    # Replacing them is an exact source transition, not another fail adjudication
    # against the already-edited current page.
    transition_spec = importlib.util.spec_from_file_location("current_two_defect_transition",
        Path(__file__).with_name("current_two_defect_transition.py"))
    transition_module = importlib.util.module_from_spec(transition_spec)
    transition_spec.loader.exec_module(transition_module)
    correction_summaries.extend(transition_module.apply_current_two_defect_transition(pages, REPO))
    postinstall_spec = importlib.util.spec_from_file_location("current_h100x4_direct_postinstall_adjudications",
        Path(__file__).with_name("current_h100x4_direct_postinstall_adjudications.py"))
    postinstall_module = importlib.util.module_from_spec(postinstall_spec)
    postinstall_spec.loader.exec_module(postinstall_module)
    correction_summaries.extend(postinstall_module.apply_current_h100x4_direct_postinstall_adjudications(pages, REPO))
    # The two-defect registry is sealed against this exact pre-connection
    # projection.  Retain it only for its own output check; the public model
    # below receives the connection binding last.
    transition_output_pages = copy.deepcopy(pages)
    # This intentionally runs last: every connection entry pins the full
    # already-adjudicated claim from the two-defect, rental, and postinstall
    # layers, so it cannot silently replace an earlier result.
    connection_spec = importlib.util.spec_from_file_location("current_host_connection_adjudications",
        Path(__file__).with_name("current_host_connection_adjudications.py"))
    connection_module = importlib.util.module_from_spec(connection_spec)
    connection_spec.loader.exec_module(connection_module)
    correction_summaries.extend(connection_module.apply_current_host_connection_adjudications(pages, REPO))
    support = support_layers()
    for item in support:
        for kind, key in (("SUPPORT_WRAPPER", "source_file"), ("SUPPORT_FRAGMENT", "fragment_file"), ("CENTRAL_REFERENCE", "central_reference_file")):
            manifest.append({"kind": kind, "route": item["route"], "path": item[key], "sha256": item[key.replace("file", "sha256")]})
    if len({(item["kind"], item["route"], item["path"]) for item in manifest}) != len(manifest):
        raise ValueError("duplicate current source manifest record")
    claims = [claim for page in pages for claim in page["claims"]]
    procedures = [procedure for page in pages for procedure in page["procedures"]]
    nodes = [node for procedure in procedures for node in procedure["nodes"]]
    package = {
        "schema_version": "1.0", "record_type": "HOST_DOCS_CURRENT_REVIEW",
        # Stable source-derived timestamp keeps --check deterministic.  It is
        # a package identity marker, not a claim that a runtime check ran then.
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": {"repository": "vast-ai/docs", "revision": CURRENT_REVISION, "tree": git_tree(),
                   "primary_route_count": 44, "cli_support_layer_count": 18, "sdk_support_layer_count": 15,
                   "source_manifest": sorted(manifest, key=lambda item: (item["kind"], item["route"], item["path"]))},
        "history": {"source_revision": HISTORICAL_REVISION,
                    "packages": [{"path": item, "sha256": file_digest(REPO / item)} for item in HISTORICAL_FILES]},
        "pages": pages, "support_layers": support,
        "counts": {"primary_pages": len(pages), "cli_support_layers": sum(item["layer"] == "CLI" for item in support),
                   "sdk_support_layers": sum(item["layer"] == "SDK" for item in support), "total_host_routes": len(pages), "total_reviewed_layers": len(pages) + len(support),
                   "claims": len(claims), "procedures": len(procedures), "procedure_nodes": len(nodes), "support_layers": len(support),
                   "claim_statuses": dict(sorted(Counter(item["status"] for item in claims).items())),
                   "page_coverage_states": dict(sorted(Counter(item["coverage_state"] for item in pages).items()))},
        "corrections": [
            {"id": "VOL-C35-CURRENT-COMPOSITE-SCOPE", "scope": "/host/volume-offers", "history": "Frozen historical VOL-C35 scope was Related Pages lines 111-118 only.",
             "current": "Source scope now includes Command Map lines 101-109 and Related Pages lines 111-118. Destination checks PASS; the expanded command-semantics claim is UNVALIDATED.",
             "reason": "The historical narrow span and its status remain frozen. Expanding the current source binding must not turn passing navigation checks into proof of command semantics."},
            {"id": "SELFTEST-REFERENCE-FLAG-TYPOGRAPHY", "scope": "/host/self-test-reference", "history": "Prior generated rows lacked code-token markup for --ignore-requirements and --debugging.",
             "current": "Current generated rows are source lines 155 and 198; retained generator and rendered-DOM retests show both tokens as code.",
             "reason": "Current rendered-source typography retest confirms the two flags are marked as code; no runtime self-test behavior is implied."},
            *correction_summaries,
        ],
    }
    return package, transition_output_pages


def build() -> dict[str, Any]:
    """Return the public review-package dictionary expected by existing users.

    The transition projection is an internal output-only snapshot: it must not
    change this established builder API or leak into the public JSON package.
    """
    package, _ = _build_with_transition_projection()
    return package


def outputs() -> dict[Path, bytes]:
    package, transition_output_pages = _build_with_transition_projection()
    # Do not churn an evidence timestamp when the complete review identity is
    # unchanged.  A changed package receives its actual UTC generation time.
    if OUT.is_file():
        try:
            previous = json_load(OUT)
            prior_time = previous.get("generated_at")
            if isinstance(prior_time, str):
                package["generated_at"] = prior_time
                if previous != package:
                    package["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    # Historical entries retain their frozen results artifact.  Current static
    # entries bind the exact retained local check instead of an invented label.
    for page in package["pages"]:
        for claim in page["claims"]:
            for evidence in claim["evidence_refs"]:
                evidence.setdefault("artifact_ref", (
                    "verification/host-docs-test-results.json"
                    if evidence["role"] == "HISTORICAL_CARRY_FORWARD_EXACT_SOURCE"
                    else "verification/current-host-docs-review.json"
                ))
    for support in package["support_layers"]:
        for evidence in support["evidence_refs"]:
            evidence.setdefault("artifact_ref", "verification/current-host-docs-review.json")
    worklist_md, runtime_md, owner_md = worklist(package)
    static_record = static_evidence(package)
    frozen_static_bytes: bytes | None = None
    if STATIC_EVIDENCE.is_file():
        prior_static = json_load(STATIC_EVIDENCE)
        static_record["generated_at"] = prior_static.get("generated_at")
        if prior_static != static_record:
            # Keep the historical attempt byte-identical and emit the current
            # inspection under this correction attempt instead of relabelling
            # the historical result as current.
            frozen_static_bytes = STATIC_EVIDENCE.read_bytes()
    transition_spec = importlib.util.spec_from_file_location("current_two_defect_transition_output",
        Path(__file__).with_name("current_two_defect_transition.py"))
    transition_module = importlib.util.module_from_spec(transition_spec)
    transition_spec.loader.exec_module(transition_module)
    transition_static_record = static_evidence(package)
    if TWO_DEFECT_STATIC_EVIDENCE.is_file():
        prior_transition_static = json_load(TWO_DEFECT_STATIC_EVIDENCE)
        # Package/evidence metadata may change without changing this static
        # navigation/support inspection.  Freeze its original timestamp before
        # comparison, while rejecting a changed inspection body.
        transition_static_record["generated_at"] = prior_transition_static.get("generated_at")
        if transition_static_record != prior_transition_static:
            raise ValueError("Two-defect static evidence differs: create a new attempt, do not overwrite history")
    two_defect_static_bytes = (json.dumps(transition_static_record, indent=2, ensure_ascii=False) + "\n").encode()
    return {OUT: (json.dumps(package, indent=2, ensure_ascii=False) + "\n").encode(), WORKLIST: worklist_md.encode(),
            RUNTIME_REGISTER: runtime_md.encode(), OWNER_REGISTER: owner_md.encode(),
            STATIC_EVIDENCE: frozen_static_bytes or (json.dumps(static_record, indent=2, ensure_ascii=False) + "\n").encode(),
            TWO_DEFECT_STATIC_EVIDENCE: two_defect_static_bytes,
            REPO / transition_module.REGISTRY: transition_module.output_bytes(transition_output_pages, REPO)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    stale = [path.relative_to(REPO).as_posix() for path, value in expected.items() if not path.is_file() or path.read_bytes() != value]
    if args.check:
        if stale:
            raise SystemExit("stale current Host review output: " + ", ".join(stale))
        print("PASS: current Host review package covers 44 primary routes and 33 support layers.")
        return 0
    for path, value in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
    print("WROTE: current Host review package, worklist, and blocker registers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
