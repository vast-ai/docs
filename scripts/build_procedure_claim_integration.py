#!/usr/bin/env python3
"""Build an isolated Host Docs P1 raw-claim integration candidate.

This is deliberately not the canonical assembler.  It consumes the exact reviewed
P1 baseline and the two pinned reconciliation inputs, writes only a caller-selected
candidate (default: /private/tmp), and never executes documentation, network, Host,
credentialed, mutating, destructive, or paid operations.

The output is deterministic JSON.  ``--check`` validates an already-built candidate
against the pinned canonical baseline and repository sources without reading either
temporary reconciliation input.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import ipaddress
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[1]
CANONICAL_PATH = REPO / "verification/procedure-baseline-p1.json"
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-claims-candidate.json")
DESIGN_PATH = Path("/private/tmp/host-docs-p1-claim-integration-design.json")
RAW_PATH = Path("/private/tmp/host-docs-p1-raw-claim-gaps.json")
RECONCILE_PATH = Path("/private/tmp/host-docs-p1-gap-reconcile.json")

EXPECTED_CANONICAL_SHA256 = "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912"
EXPECTED_DESIGN_SHA256 = "696bada4e212297d7916c5f31ecfb3d2cff7cd06708031f7722cd8e32b7da5ca"
EXPECTED_RAW_SHA256 = "0568cda70f237eb10823e75ce1deb3fef7873a658eb287266f3b52f03e494de1"
EXPECTED_RECONCILE_SHA256 = "a1ae714917f1da76bbd967a7f82d40117002dc636d81255e1132f61ef715566f"
EXPECTED_SOURCE_RECORD_SET_SHA256 = "5e00a026aa50f7f9a97266bfc190125cca12d75291abc4f32e507089b8889fbf"
EXPECTED_CLASSIFICATION_MAP_SHA256 = "0f831c8a34bd5569a1ca606959049d4f95fba39d1e4bda0e8748208c45e97cc2"
EXPECTED_DEFECT_SOURCE_SET_SHA256 = "9abe61295d319b72c9ece30ceaf0cacfe543ad3ae13e05a00f354e74ec3f80fc"

EXPECTED_TOPOLOGY = {"pages": 39, "procedures": 82, "branches": 193, "steps": 454}
EXPECTED_CLASSIFICATIONS = {
    "ADD_MATERIAL_CLAIM": 104,
    "ABSORB_IN_PROCEDURE_FIELD": 67,
    "DUPLICATE": 5,
    "LEGACY_EQUIVALENT": 1,
}
EXPECTED_SOURCE_SPLIT = {
    ("PROPOSED_GAP", "ADD_MATERIAL_CLAIM"): 104,
    ("PROPOSED_GAP", "ABSORB_IN_PROCEDURE_FIELD"): 63,
    ("COVERED_OR_AMBIGUOUS", "ABSORB_IN_PROCEDURE_FIELD"): 4,
    ("COVERED_OR_AMBIGUOUS", "DUPLICATE"): 5,
    ("COVERED_OR_AMBIGUOUS", "LEGACY_EQUIVALENT"): 1,
}
EXPECTED_LEGACY_UNIQUE = {
    "command": 176,
    "behavior-claim": 203,
    "error": 77,
    "threshold": 18,
}
EXPECTED_LEGACY_OCCURRENCES = {
    "command": 203,
    "behavior-claim": 204,
    "error": 104,
    "threshold": 18,
}
EXPECTED_LEGACY_SOURCE_TYPES = {
    "authored": 418,
    "generated-self-test": 69,
    "generated-cli-sdk": 42,
}

RAW_TOP_FIELDS = {
    "audit_id", "audit_state", "counts", "covered_or_ambiguous",
    "execution_performed", "gaps", "generated_at", "human_acceptance",
    "limitations", "method", "mode", "pages", "procedure_partition_inputs_seen",
    "schema_version", "scope", "target",
}
RAW_GAP_FIELDS = {
    "authority", "claim_summary", "file", "gap_confidence", "heading",
    "human_acceptance", "id", "kind", "legacy_disposition", "line_end",
    "line_start", "overlapping_legacy_occurrences", "page_id",
    "proposed_treatment", "route", "source_text_exact", "validation_method",
    "vv_status", "why_material",
}
RAW_AMBIGUOUS_FIELDS = {
    "disposition", "file", "id", "legacy_item_ids", "line_end", "line_start", "note",
}
RAW_PAGE_FIELDS = {
    "covered_or_ambiguous_ids", "disposition", "file", "human_acceptance",
    "legacy_occurrence_count", "line_count", "material_gap_count",
    "material_gap_ids", "page_id", "procedure_ids", "route", "source_sha256",
    "vv_status",
}
RECONCILE_TOP_FIELDS = {
    "audit_id", "audit_state", "counts", "execution_performed", "generated_at",
    "human_acceptance", "inputs", "limitations", "method", "mode",
    "p1_freeze_decision", "prepared_by", "reconciliation", "schema_version", "target",
}
RECONCILE_RECORD_FIELDS = {
    "authority_state", "classification", "duplicate_of", "execution_unit_effect",
    "human_acceptance", "id", "legacy_overlap", "original_disposition",
    "original_kind", "original_summary", "rationale", "source", "source_set",
    "source_span_review", "target", "vv_status",
}
RECONCILE_SOURCE_FIELDS = {
    "exact_text_match", "file", "line_end", "line_start", "source_text_sha256",
}
RECONCILE_REVIEW_FIELDS = {
    "state", "overclaim", "note", "corrected_summary", "corrected_sources",
}
CORRECTED_SOURCE_FIELDS = {"file", "line_start", "line_end", "role"}
RECONCILE_TARGET_FIELDS = {
    "procedure_ids", "branch_ids", "step_ids", "procedure_field", "missing_draft_targets",
}
LEGACY_OVERLAP_FIELDS = {"item_ids", "same_span_occurrence_count", "treatment"}
TARGET_FIELDS = {
    "docs_head", "docs_tree", "legacy_inventory_source_revision",
    "legacy_content_fingerprint", "legacy_inventory_sha256",
}

PLAN_MUTABLE_KEYS = {
    "status", "attempt_ids", "issue_ids", "correction_ids", "retest_ids",
    "evidence_refs", "semantic_assessment", "approval_state", "gate_evaluation",
}
BASELINE_IDENTITY_FIELDS = (
    "schema_version", "record_type", "state", "operating_mode", "source_identity",
    "scope", "authority_sources", "pages", "procedures", "supporting_routes",
    "fragments", "support_contracts", "claims", "legacy_crosswalk", "uncertainties",
    "reconciliation",
)

ALLOWED_SOURCE_ROLES = {
    "PRIMARY_CLAIM_SOURCE", "PROCEDURE_CONTEXT_SOURCE",
    "RECONCILIATION_DISPOSITION_SOURCE", "IMPORT_AND_RENDERED_CONTEXT",
    "IMPORTED_CLAIM_SOURCE",
}
INTEGRATION_CORRECTION_STATES = {
    "PARTIAL_OVERCLAIM", "SPAN_TOO_SHORT", "INFERRED_OPERATION_CLASS",
    "WRONG_SOURCE_CARRIER", "MULTI_PROCEDURE_TARGET", "WRONG_PROCEDURE_TARGET",
    "NON_STANDALONE_TEMPLATE", "PARTIAL_LEGACY_SEMANTIC_COVERAGE",
}
SOURCE_OR_EXECUTION_DEFECT_STATES = {
    "APPLICABILITY_CONFLICT", "BROKEN_FOREGROUND_ORDERING",
    "INCOMPLETE_PROCESS_CLEANUP", "CURRENT_COMMAND_AND_IMAGE_CONFLICT",
    "SOURCE_CONTRADICTION", "STALE_EXAMPLE", "STALE_GENERATED_CONTRACT",
    "UNSAFE_TARGET_EXPANSION",
}
FORBIDDEN_KEYS = {
    "api_key", "client_api_key", "host_api_key", "secret", "password", "token",
    "private_key", "ssh_key", "machine_ip", "wan_ip", "account_identifier",
}
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")


class IntegrationError(RuntimeError):
    """The candidate cannot be safely or deterministically constructed."""


def canonical_json(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    else:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return text.encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegrationError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise IntegrationError(f"{path}: top level must be an object")
    return value, data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegrationError(message)


def exact_keys(value: Any, fields: set[str], context: str, *, optional: set[str] | None = None) -> None:
    require(isinstance(value, dict), f"{context}: expected object")
    optional = optional or set()
    unknown = set(value) - fields
    missing = fields - optional - set(value)
    require(not unknown, f"{context}: unknown fields {sorted(unknown)}")
    require(not missing, f"{context}: missing fields {sorted(missing)}")


def stable_id(prefix: str, namespace: str, source_record_id: str) -> str:
    digest = hashlib.sha256((namespace + "\0" + source_record_id).encode("utf-8")).hexdigest()
    return prefix + digest[:16]


def source_binding_id(source_record_id: str, role: str, file: str, start: int, end: int) -> str:
    basis = source_record_id + "\0" + role + "\0" + file + "\0" + str(start) + "\0" + str(end)
    return stable_id("SRC-", "host-docs-p1-source-binding-v1", basis)


def material_claim_id(source_record_id: str) -> str:
    return stable_id("CLM-", "host-docs-p1-material-claim-v1", source_record_id)


def requirement_id(source_record_id: str) -> str:
    return stable_id("PRQ-", "host-docs-p1-procedure-requirement-v1", source_record_id)


def disposition_id(source_record_id: str) -> str:
    return stable_id("DSP-", "host-docs-p1-reconciliation-disposition-v1", source_record_id)


def defect_id(source_record_id: str) -> str:
    return stable_id("DFG-", "host-docs-p1-source-target-defect-v1", source_record_id)


def immutable_plan_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: immutable_plan_value(item)
            for key, item in value.items()
            if key not in PLAN_MUTABLE_KEYS
        }
    if isinstance(value, list):
        return [immutable_plan_value(item) for item in value]
    return value


def plan_digest(baseline: dict[str, Any]) -> str:
    payload = immutable_plan_value({key: baseline[key] for key in BASELINE_IDENTITY_FIELDS})
    return sha256_bytes(canonical_json(payload))


def repo_source_path(raw: str) -> Path:
    candidate = Path(raw)
    require(not candidate.is_absolute() and ".." not in candidate.parts,
            f"source path escapes repository: {raw!r}")
    normalized = candidate.as_posix()
    require(normalized.endswith(".mdx") and normalized.startswith(("host/", "snippets/")),
            f"source path is not allowlisted: {raw!r}")
    resolved = (REPO / candidate).resolve()
    require(REPO.resolve() in resolved.parents, f"source path escapes repository: {raw!r}")
    require(resolved.is_file(), f"source file does not exist: {raw!r}")
    return resolved


def normalized_span(file: str, start: int, end: int) -> tuple[str, str, str]:
    require(isinstance(start, int) and isinstance(end, int) and 1 <= start <= end,
            f"invalid 1-based source span {file}:{start}-{end}")
    path = repo_source_path(file)
    data = path.read_bytes()
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise IntegrationError(f"source is not UTF-8: {file}") from exc
    require(end <= len(lines), f"source span exceeds {file}: {start}-{end}/{len(lines)}")
    span = "\n".join(lines[start - 1:end])
    return span, sha256_bytes(data), sha256_bytes(span.encode("utf-8"))


def semantic_assessment() -> dict[str, Any]:
    return {
        "required": True,
        "scope": "SOURCE_AUTHORITY_PROCEDURE_AND_RENDERED_CONTEXT",
        "status": "UNVALIDATED",
        "score": None,
        "rationale": None,
        "finding_class": None,
        "evidence_refs": [],
        "correction_id": None,
        "retest_id": None,
    }


def topology_maps(baseline: dict[str, Any]) -> dict[str, Any]:
    pages = baseline.get("pages", [])
    procedures = baseline.get("procedures", [])
    require(len(pages) == 39 and len(procedures) == 82, "canonical topology is not 39 pages / 82 procedures")
    page_by_id = {page["id"]: page for page in pages}
    page_by_file = {page["source_file"]: page for page in pages}
    require(len(page_by_id) == len(pages) == len(page_by_file), "page IDs/source files are not unique")
    procedure_by_id = {proc["id"]: proc for proc in procedures}
    require(len(procedure_by_id) == len(procedures), "procedure IDs are not unique")
    branch_by_id: dict[str, tuple[str, dict[str, Any]]] = {}
    step_by_id: dict[str, tuple[str, str, dict[str, Any]]] = {}
    for proc in procedures:
        require(proc.get("page_id") in page_by_id, f"procedure {proc.get('id')} has unknown page")
        for branch in proc.get("branches", []):
            bid = branch["id"]
            require(bid not in branch_by_id, f"duplicate branch ID: {bid}")
            branch_by_id[bid] = (proc["id"], branch)
            for step in branch.get("steps", []):
                sid = step["id"]
                require(sid not in step_by_id, f"duplicate step ID: {sid}")
                step_by_id[sid] = (proc["id"], bid, step)
    require(len(branch_by_id) == 193 and len(step_by_id) == 454,
            f"canonical topology is not 193 branches / 454 steps: {len(branch_by_id)}/{len(step_by_id)}")
    fragments = {fragment["id"]: fragment for fragment in baseline.get("fragments", [])}
    fragment_by_file = {fragment["source_file"]: fragment for fragment in fragments.values()}
    supporting = {route["id"]: route for route in baseline.get("supporting_routes", [])}
    return {
        "page_by_id": page_by_id,
        "page_by_file": page_by_file,
        "procedure_by_id": procedure_by_id,
        "branch_by_id": branch_by_id,
        "step_by_id": step_by_id,
        "fragments": fragments,
        "fragment_by_file": fragment_by_file,
        "supporting": supporting,
    }


def topology_signature(baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "pages": sorted(page["id"] for page in baseline.get("pages", [])),
        "procedures": sorted(proc["id"] for proc in baseline.get("procedures", [])),
        "branches": sorted(
            (proc["id"], branch["id"])
            for proc in baseline.get("procedures", [])
            for branch in proc.get("branches", [])
        ),
        "steps": sorted(
            (proc["id"], branch["id"], step["id"])
            for proc in baseline.get("procedures", [])
            for branch in proc.get("branches", [])
            for step in branch.get("steps", [])
        ),
    }


def validate_input_schemas(raw: dict[str, Any], reconcile: dict[str, Any]) -> None:
    exact_keys(raw, RAW_TOP_FIELDS, "raw audit")
    exact_keys(reconcile, RECONCILE_TOP_FIELDS, "independent reconciliation")
    require(raw["schema_version"] == "1.0-draft", "unexpected raw-audit schema")
    require(reconcile["schema_version"] == "host-docs-p1-gap-reconcile/1.0",
            "unexpected reconciliation schema")
    raw_execution = raw["execution_performed"]
    require(isinstance(raw_execution, dict) and raw_execution
            and all(value is False for value in raw_execution.values())
            and reconcile["execution_performed"] is False,
            "input incorrectly claims execution")
    require(raw["human_acceptance"] == "NOT_DECIDED" and reconcile["human_acceptance"] == "NOT_DECIDED",
            "input incorrectly claims acceptance")
    exact_keys(raw["target"], TARGET_FIELDS, "raw target")
    exact_keys(reconcile["target"], TARGET_FIELDS, "reconciliation target")
    for index, record in enumerate(raw["gaps"]):
        exact_keys(record, RAW_GAP_FIELDS, f"raw gap[{index}]")
        exact_keys(record["authority"], {"state", "suggested_references", "claim_limit"},
                   f"raw gap[{index}].authority")
        exact_keys(record["validation_method"], {"semantic", "runtime", "source"},
                   f"raw gap[{index}].validation_method")
        exact_keys(record["proposed_treatment"], {"scope", "procedure_id", "branch_id", "step_id", "instruction"},
                   f"raw gap[{index}].proposed_treatment")
    for index, record in enumerate(raw["covered_or_ambiguous"]):
        exact_keys(record, RAW_AMBIGUOUS_FIELDS, f"raw covered[{index}]")
    for index, page in enumerate(raw["pages"]):
        exact_keys(page, RAW_PAGE_FIELDS, f"raw page[{index}]")
    for index, record in enumerate(reconcile["reconciliation"]):
        exact_keys(record, RECONCILE_RECORD_FIELDS, f"reconciliation[{index}]")
        exact_keys(record["source"], RECONCILE_SOURCE_FIELDS, f"reconciliation[{index}].source")
        exact_keys(record["source_span_review"], RECONCILE_REVIEW_FIELDS,
                   f"reconciliation[{index}].source_span_review",
                   optional={"corrected_summary", "corrected_sources"})
        for corrected in record["source_span_review"].get("corrected_sources", []):
            exact_keys(corrected, CORRECTED_SOURCE_FIELDS,
                       f"reconciliation[{index}].corrected_source")
        exact_keys(record["target"], RECONCILE_TARGET_FIELDS, f"reconciliation[{index}].target")
        exact_keys(record["legacy_overlap"], LEGACY_OVERLAP_FIELDS,
                   f"reconciliation[{index}].legacy_overlap")


def preflight_inputs(
    baseline: dict[str, Any], baseline_bytes: bytes,
    design: dict[str, Any], design_bytes: bytes,
    raw: dict[str, Any], raw_bytes: bytes,
    reconcile: dict[str, Any], reconcile_bytes: bytes,
) -> None:
    require(sha256_bytes(baseline_bytes) == EXPECTED_CANONICAL_SHA256,
            "canonical baseline changed; abort and explicitly rebaseline this isolated integration")
    require(sha256_bytes(design_bytes) == EXPECTED_DESIGN_SHA256, "claim-integration design hash mismatch")
    require(sha256_bytes(raw_bytes) == EXPECTED_RAW_SHA256, "raw gap-audit hash mismatch")
    require(sha256_bytes(reconcile_bytes) == EXPECTED_RECONCILE_SHA256,
            "independent reconciliation hash mismatch")
    validate_input_schemas(raw, reconcile)
    require(design.get("design_id") == "HOST-DOCS-P1-RAW-CLAIM-INTEGRATION-DESIGN",
            "unexpected integration design")
    require(design.get("expected_counts", {}).get("claims", {}).get("canonical_claims_total") == 633,
            "design count contract changed")
    require(raw["target"] == reconcile["target"], "raw/reconciliation target identity differs")
    source_identity = baseline["source_identity"]
    target = raw["target"]
    require(target["docs_head"] == source_identity["docs_target_revision"], "docs head pin mismatch")
    require(target["docs_tree"] == source_identity["repository_tree_at_assembly"], "docs tree pin mismatch")
    legacy = source_identity["legacy_inventory"]
    require(target["legacy_inventory_source_revision"] == legacy["source_revision"],
            "legacy inventory revision pin mismatch")
    require(target["legacy_content_fingerprint"] == legacy["content_fingerprint"],
            "legacy fingerprint pin mismatch")
    require(target["legacy_inventory_sha256"] == legacy["sha256"] == sha256_path(REPO / legacy["path"]),
            "legacy inventory hash pin mismatch")
    require(reconcile["inputs"]["raw_gap_audit"]["sha256"] == EXPECTED_RAW_SHA256,
            "reconciliation does not pin the supplied raw audit")
    require(reconcile["counts"]["new_executable_test_units"] == 0,
            "reconciliation attempts to create executable units")
    require(baseline["state"] == "DRAFT_NOT_FROZEN", "canonical baseline is not a draft")
    require(baseline["completion_and_acceptance"]["human_acceptance"]["decision"] == "NOT_DECIDED",
            "canonical baseline already carries an acceptance decision")
    require(plan_digest(baseline) == baseline["plan_baseline_sha256"],
            "canonical baseline plan identity is invalid")
    topology_maps(baseline)


def reconcile_inputs(
    raw: dict[str, Any], reconcile: dict[str, Any], maps: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    raw_records = list(raw["gaps"]) + list(raw["covered_or_ambiguous"])
    raw_by_id = {record["id"]: record for record in raw_records}
    reconciled_by_id = {record["id"]: record for record in reconcile["reconciliation"]}
    require(len(raw_records) == len(raw_by_id) == 177, "raw source IDs are not 177 unique records")
    require(len(reconcile["reconciliation"]) == len(reconciled_by_id) == 177,
            "reconciled IDs are not 177 unique records")
    require(set(raw_by_id) == set(reconciled_by_id), "raw/reconciled source-ID sets differ")
    classifications = Counter(record["classification"] for record in reconciled_by_id.values())
    require(dict(classifications) == EXPECTED_CLASSIFICATIONS,
            f"classification counts differ: {dict(classifications)}")
    split = Counter((record["source_set"], record["classification"])
                    for record in reconciled_by_id.values())
    require(dict(split) == EXPECTED_SOURCE_SPLIT, f"source/classification split differs: {dict(split)}")
    non_exact = {record["id"] for record in reconciled_by_id.values()
                 if record["source_span_review"]["state"] != "EXACT_SOURCE_SPAN"}
    require(len(non_exact) == 17, f"expected 17 defect-source records, found {len(non_exact)}")
    raw_page_by_file = {page["file"]: page for page in raw["pages"]}
    require(len(raw_page_by_file) == len(raw["pages"]) == 39, "raw page inventory is not 39 unique files")
    for page in raw["pages"]:
        _, full_hash, _ = normalized_span(page["file"], 1, page["line_count"])
        require(full_hash == page["source_sha256"], f"raw page source hash stale: {page['file']}")
        canonical_page = maps["page_by_file"].get(page["file"])
        require(canonical_page is not None, f"raw page is not canonical: {page['file']}")
        require(canonical_page["route"] == page["route"], f"raw page route differs: {page['file']}")
        require(canonical_page["source_sha256"] == full_hash, f"baseline page hash differs: {page['file']}")
    for source_id, record in reconciled_by_id.items():
        raw_record = raw_by_id[source_id]
        source = record["source"]
        require(source["file"] == raw_record["file"] and source["line_start"] == raw_record["line_start"]
                and source["line_end"] == raw_record["line_end"],
                f"{source_id}: raw/reconciled source binding differs")
        span, _, span_hash = normalized_span(source["file"], source["line_start"], source["line_end"])
        require(span_hash == source["source_text_sha256"], f"{source_id}: reconciled source span is stale")
        if source_id.startswith("GAP-"):
            require(span == raw_record["source_text_exact"], f"{source_id}: raw exact source text is stale")
            require(record["original_kind"] == raw_record["kind"]
                    and record["original_summary"] == raw_record["claim_summary"]
                    and record["original_disposition"] == raw_record["legacy_disposition"],
                    f"{source_id}: reconciled raw semantics differ")
            require(record["source_set"] == "PROPOSED_GAP", f"{source_id}: wrong source set")
        else:
            require(record["source_set"] == "COVERED_OR_AMBIGUOUS", f"{source_id}: wrong source set")
            require(record["original_summary"] is None and record["original_kind"] is None,
                    f"{source_id}: ambiguous record invented summary/kind")
        require(record["execution_unit_effect"] == "NO_NEW_EXECUTABLE_TEST_UNIT",
                f"{source_id}: attempts to create executable test unit")
        require(record["vv_status"] == "UNVALIDATED" and record["human_acceptance"] == "NOT_DECIDED",
                f"{source_id}: invalid draft result state")
        require(not record["target"]["missing_draft_targets"], f"{source_id}: unresolved draft targets")
        validate_target_record(record, maps, source["file"])
    return raw_by_id, reconciled_by_id


def validate_target_record(record: dict[str, Any], maps: dict[str, Any], source_file: str) -> None:
    target = record["target"]
    proc_ids = target["procedure_ids"]
    require(proc_ids and len(proc_ids) == len(set(proc_ids)), f"{record['id']}: invalid procedure targets")
    source_page = maps["page_by_file"].get(source_file)
    require(source_page is not None, f"{record['id']}: discovery source is not a primary Host page")
    for proc_id in proc_ids:
        proc = maps["procedure_by_id"].get(proc_id)
        require(proc is not None, f"{record['id']}: unknown procedure {proc_id}")
        require(proc["page_id"] == source_page["id"], f"{record['id']}: cross-page procedure target {proc_id}")
    branch_ids = target["branch_ids"]
    step_ids = target["step_ids"]
    require(len(branch_ids) == len(set(branch_ids)) and len(step_ids) == len(set(step_ids)),
            f"{record['id']}: duplicate branch/step target")
    for branch_id in branch_ids:
        owner = maps["branch_by_id"].get(branch_id)
        require(owner is not None and owner[0] in proc_ids,
                f"{record['id']}: branch target has wrong owner {branch_id}")
    for step_id in step_ids:
        owner = maps["step_by_id"].get(step_id)
        require(owner is not None and owner[0] in proc_ids,
                f"{record['id']}: step target has wrong owner {step_id}")
        require(owner[1] in branch_ids,
                f"{record['id']}: step owner branch is absent from target {step_id}")


def source_type_for(file: str) -> str:
    if file == "host/self-test-reference.mdx":
        return "generated-self-test"
    if file.startswith("snippets/"):
        return "authored-shared-fragment"
    return "authored"


def build_source_binding(
    source_record_id: str, source: dict[str, Any], role: str, maps: dict[str, Any],
    rendered_routes: list[str], *, primary_for_claim: bool,
) -> dict[str, Any]:
    require(role in ALLOWED_SOURCE_ROLES, f"{source_record_id}: invalid source role {role}")
    file = source["file"]
    start = source["line_start"]
    end = source["line_end"]
    _, full_hash, span_hash = normalized_span(file, start, end)
    page = maps["page_by_file"].get(file)
    fragment = maps["fragment_by_file"].get(file)
    require(page is not None or fragment is not None,
            f"{source_record_id}: source has no page/fragment owner: {file}")
    if page is not None:
        require(page["source_sha256"] == full_hash, f"{source_record_id}: page source hash differs")
    if fragment is not None:
        require(fragment["source_sha256"] == full_hash, f"{source_record_id}: fragment source hash differs")
    return {
        "id": source_binding_id(source_record_id, role, file, start, end),
        "role": role,
        "primary_for_claim": primary_for_claim,
        "file": file,
        "line_start": start,
        "line_end": end,
        "source_type": source_type_for(file),
        "source_file_sha256": full_hash,
        "source_span_sha256": span_hash,
        "page_id": page["id"] if page else None,
        "fragment_id": fragment["id"] if fragment else None,
        "rendered_context_refs": sorted(set(rendered_routes)),
    }


def normalized_sources(
    record: dict[str, Any], classification: str, maps: dict[str, Any], rendered_routes: list[str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ordinary_role = {
        "ADD_MATERIAL_CLAIM": "PRIMARY_CLAIM_SOURCE",
        "ABSORB_IN_PROCEDURE_FIELD": "PROCEDURE_CONTEXT_SOURCE",
        "DUPLICATE": "RECONCILIATION_DISPOSITION_SOURCE",
        "LEGACY_EQUIVALENT": "RECONCILIATION_DISPOSITION_SOURCE",
    }[classification]
    corrected = record["source_span_review"].get("corrected_sources", [])
    discovery = build_source_binding(
        record["id"], record["source"], ordinary_role, maps, rendered_routes,
        primary_for_claim=(classification == "ADD_MATERIAL_CLAIM" and not corrected),
    )
    if not corrected:
        return discovery, [copy.deepcopy(discovery)]
    effective: list[dict[str, Any]] = []
    for source in corrected:
        raw_role = source["role"]
        role = "PRIMARY_CLAIM_SOURCE" if raw_role == "FULL_CLAIM_SOURCE" else raw_role
        primary = role in {"PRIMARY_CLAIM_SOURCE", "IMPORTED_CLAIM_SOURCE"}
        effective.append(build_source_binding(
            record["id"], source, role, maps, rendered_routes,
            primary_for_claim=(classification == "ADD_MATERIAL_CLAIM" and primary),
        ))
    effective.sort(key=lambda item: item["id"])
    return discovery, effective


def target_bindings(record: dict[str, Any], maps: dict[str, Any]) -> list[dict[str, Any]]:
    target = record["target"]
    output: list[dict[str, Any]] = []
    for proc_id in sorted(target["procedure_ids"]):
        branch_ids = sorted(bid for bid in target["branch_ids"] if maps["branch_by_id"][bid][0] == proc_id)
        step_ids = sorted(sid for sid in target["step_ids"] if maps["step_by_id"][sid][0] == proc_id)
        output.append({
            "procedure_id": proc_id,
            "branch_ids": branch_ids,
            "step_ids": step_ids,
            "procedure_field": target["procedure_field"],
        })
    return output


def authority_refs_for(record: dict[str, Any], maps: dict[str, Any], page_id: str) -> list[str]:
    refs = set(maps["page_by_id"][page_id].get("authority_refs", []))
    for proc_id in record["target"]["procedure_ids"]:
        refs.update(maps["procedure_by_id"][proc_id].get("authority_refs", []))
    return sorted(refs)


def source_projection(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "file": binding["file"],
        "line_start": binding["line_start"],
        "line_end": binding["line_end"],
        "source_type": binding["source_type"],
        "source_file_sha256": binding["source_file_sha256"],
        "source_span_sha256": binding["source_span_sha256"],
    }


def make_material_claim(
    record: dict[str, Any], raw_record: dict[str, Any], maps: dict[str, Any]
) -> dict[str, Any]:
    page = maps["page_by_file"][record["source"]["file"]]
    rendered_routes = [page["route"]]
    discovery, effective = normalized_sources(record, record["classification"], maps, rendered_routes)
    primary = [binding for binding in effective if binding["primary_for_claim"]]
    require(len(primary) == 1, f"{record['id']}: material claim must have one primary source")
    fragment_ids = sorted({binding["fragment_id"] for binding in effective if binding["fragment_id"]})
    require(len(fragment_ids) <= 1, f"{record['id']}: multiple fragment owners are unsupported")
    corrected_summary = record["source_span_review"].get("corrected_summary")
    authority = raw_record["authority"]
    boundary_note = record["source_span_review"]["note"]
    return {
        "id": material_claim_id(record["id"]),
        "origin": "RECONCILED_MATERIAL",
        "source_record_id": record["id"],
        "source_set": record["source_set"],
        "reconciliation_classification": "ADD_MATERIAL_CLAIM",
        "occurrence_id": None,
        "legacy_item_id": None,
        "legacy_location_index": None,
        "kind": record["original_kind"],
        "text": corrected_summary or record["original_summary"],
        "source": source_projection(primary[0]),
        "source_bindings": effective,
        "discovery_source_binding": discovery,
        "page_id": page["id"],
        "procedure_id": None,
        "branch_id": None,
        "step_id": None,
        "target_bindings": target_bindings(record, maps),
        "supporting_route_id": None,
        "fragment_id": fragment_ids[0] if fragment_ids else None,
        "primary_treatment": "non-executable-claim",
        "source_alignment": "RECONCILED_RAW_SOURCE",
        "source_alignment_disposition": record["source_span_review"]["state"],
        "raw_context": {
            "original_summary": record["original_summary"],
            "original_disposition": record["original_disposition"],
            "source_span_review": copy.deepcopy(record["source_span_review"]),
            "discovery_span": {
                "file": record["source"]["file"],
                "line_start": record["source"]["line_start"],
                "line_end": record["source"]["line_end"],
                "source_span_sha256": record["source"]["source_text_sha256"],
            },
        },
        "rendered_context_refs": [
            {"route": route, "status": "UNVALIDATED", "evidence_refs": []}
            for route in rendered_routes
        ],
        "legacy_overlap": copy.deepcopy(record["legacy_overlap"]),
        "execution_unit_effect": "NO_NEW_EXECUTABLE_TEST_UNIT",
        "authority_refs": authority_refs_for(record, maps, page["id"]),
        "authority_state": "PENDING_OWNER",
        "authority_resolution": {
            "candidate_sources": copy.deepcopy(authority["suggested_references"]),
            "claim_limit": authority["claim_limit"],
            "current_mdx_is_authority_for_own_truth": False,
        },
        "claim_limit": record["rationale"] + " Source-boundary review: " + boundary_note,
        "test_basis": copy.deepcopy(raw_record["validation_method"]),
        "expected_observables": [
            "Pinned authority and claim-suitable evidence support exactly this bounded statement in every named target context."
        ],
        "planned_method": copy.deepcopy(raw_record["validation_method"]),
        "status": "UNVALIDATED",
        "attempt_ids": [],
        "issue_ids": [],
        "reconciliation_disposition_ids": [],
        "defect_flag_ids": [],
        "semantic_assessment": semantic_assessment(),
    }


def default_requirement_test_basis() -> dict[str, str]:
    return {
        "source": "Inspect the pinned repository source and rendered Host context.",
        "semantic": "Evaluate this requirement through its existing target procedure, branch, and ordered steps.",
        "runtime": "Any runtime result must come only from claim-suitable attempts on the existing target execution units.",
    }


def make_requirement(
    record: dict[str, Any], raw_record: dict[str, Any], maps: dict[str, Any]
) -> dict[str, Any]:
    page = maps["page_by_file"][record["source"]["file"]]
    discovery, effective = normalized_sources(record, record["classification"], maps, [page["route"]])
    proc_ids = sorted(record["target"]["procedure_ids"])
    summary = (record["source_span_review"].get("corrected_summary")
               or record["original_summary"] or raw_record.get("note"))
    return {
        "id": requirement_id(record["id"]),
        "source_record_id": record["id"],
        "source_set": record["source_set"],
        "reconciliation_classification": "ABSORB_IN_PROCEDURE_FIELD",
        "storage_procedure_id": proc_ids[0],
        "requirement_kind": record["original_kind"],
        "requirement_summary": summary,
        "source_bindings": effective,
        "discovery_source_binding": discovery,
        "source_span_review": copy.deepcopy(record["source_span_review"]),
        "target_bindings": target_bindings(record, maps),
        "field_target": record["target"]["procedure_field"],
        "integration_effect": "AUGMENTS_EXISTING_PROCEDURE_TEST_BASIS_ONLY",
        "execution_unit_effect": "NO_NEW_EXECUTABLE_TEST_UNIT",
        "legacy_overlap": copy.deepcopy(record["legacy_overlap"]),
        "authority_effect": "NOT_CHANGED_BY_THIS_RECONCILIATION",
        "authority_refs": authority_refs_for(record, maps, page["id"]),
        "test_basis": copy.deepcopy(raw_record.get("validation_method", default_requirement_test_basis())),
        "runtime_result_source": "TARGET_PROCEDURE_BRANCH_STEP_ATTEMPTS_ONLY",
        "reconciliation_disposition_ids": [],
        "defect_flag_ids": [],
        "semantic_assessment": semantic_assessment(),
    }


def legacy_equivalent_resolution(
    record: dict[str, Any], baseline: dict[str, Any]
) -> tuple[list[str], list[str]]:
    item_ids = record["legacy_overlap"]["item_ids"]
    require(item_ids == ["com-7fa3c4e802"],
            f"{record['id']}: unexpected legacy-equivalent item set")
    source = record["source"]
    candidates = [
        claim for claim in baseline["claims"]
        if claim.get("legacy_item_id") in item_ids
        and claim.get("source", {}).get("file") == source["file"]
        and int(claim.get("source", {}).get("line_start", 0)) >= source["line_start"]
        and int(claim.get("source", {}).get("line_end", 0)) <= source["line_end"]
    ]
    require(len(candidates) == 1,
            f"{record['id']}: legacy equivalent must resolve to exactly one claim, found {len(candidates)}")
    claim = candidates[0]
    rows = [row for row in baseline["legacy_crosswalk"] if row["claim_id"] == claim["id"]]
    require(len(rows) == 1, f"{record['id']}: legacy equivalent crosswalk is not one-to-one")
    return [claim["id"]], [rows[0]["occurrence_id"]]


def make_disposition(
    record: dict[str, Any], maps: dict[str, Any], baseline: dict[str, Any],
    canonical_id_by_source: dict[str, str],
) -> dict[str, Any]:
    page = maps["page_by_file"][record["source"]["file"]]
    discovery, effective = normalized_sources(record, record["classification"], maps, [page["route"]])
    require(len(effective) == 1 and effective[0]["id"] == discovery["id"],
            f"{record['id']}: metadata disposition unexpectedly has corrected sources")
    canonical_targets: list[str] = []
    equivalent_claims: list[str] = []
    equivalent_occurrences: list[str] = []
    if record["classification"] == "DUPLICATE":
        canonical_targets = sorted(canonical_id_by_source[source_id] for source_id in record["duplicate_of"])
    else:
        equivalent_claims, equivalent_occurrences = legacy_equivalent_resolution(record, baseline)
    return {
        "id": disposition_id(record["id"]),
        "source_record_id": record["id"],
        "classification": record["classification"],
        "source_binding": discovery,
        "source_span_review": copy.deepcopy(record["source_span_review"]),
        "duplicate_of_source_record_ids": sorted(record["duplicate_of"]),
        "canonical_target_refs": canonical_targets,
        "equivalent_legacy_item_ids": sorted(record["legacy_overlap"]["item_ids"])
            if record["classification"] == "LEGACY_EQUIVALENT" else [],
        "equivalent_legacy_claim_ids": equivalent_claims,
        "equivalent_legacy_occurrence_ids": equivalent_occurrences,
        "effect": "NO_NEW_CLAIM_REQUIREMENT_OR_EXECUTABLE_UNIT",
        "rationale": record["rationale"],
        "defect_flag_ids": [],
    }


def defect_category(state: str) -> tuple[str, str]:
    if state in INTEGRATION_CORRECTION_STATES:
        return (
            "INTEGRATION_CORRECTION",
            "May enter a frozen inventory only after the corrected binding, target, or treatment is structurally proven; it blocks affected PASS until the semantic assessment accounts for it.",
        )
    require(state in SOURCE_OR_EXECUTION_DEFECT_STATES,
            f"unclassified defect state: {state}")
    return (
        "SOURCE_OR_EXECUTION_DEFECT",
        "Blocks affected PASS and related unsafe or live execution until correction, linked evidence, and claim-suitable retest or an authorized risk decision.",
    )


def make_defect_flag(
    record: dict[str, Any], affected_type: str, affected_id: str,
    effective_binding_ids: list[str],
) -> dict[str, Any]:
    state = record["source_span_review"]["state"]
    category, gate = defect_category(state)
    return {
        "id": defect_id(record["id"]),
        "source_record_id": record["id"],
        "finding_class": state,
        "overclaim": record["source_span_review"]["overclaim"],
        "note": record["source_span_review"]["note"],
        "corrected_summary": record["source_span_review"].get("corrected_summary"),
        "effective_source_binding_ids": sorted(effective_binding_ids),
        "affected_item_refs": [{"type": affected_type, "id": affected_id}],
        "category": category,
        "gate_effect": gate,
        "issue_ids": [],
        "correction_ids": [],
        "retest_ids": [],
    }


def add_empty_reverse_indexes(baseline: dict[str, Any]) -> None:
    for page in baseline["pages"]:
        page["procedure_requirement_ids"] = []
    for proc in baseline["procedures"]:
        proc["claim_ids"] = []
        test_basis = proc.setdefault("test_basis", {})
        test_basis["reconciled_procedure_requirement_ids"] = []
        test_basis["reconciled_procedure_requirements"] = []
        for branch in proc["branches"]:
            branch["claim_ids"] = []
            branch["procedure_requirement_ids"] = []
            for step in branch["steps"]:
                step["claim_ids"] = []
                step["procedure_requirement_ids"] = []
    for fragment in baseline["fragments"]:
        fragment["claim_ids"] = []
    for route in baseline["supporting_routes"]:
        route["claim_ids"] = []


def rebuild_reverse_indexes(
    baseline: dict[str, Any], requirements: list[dict[str, Any]], maps: dict[str, Any]
) -> None:
    add_empty_reverse_indexes(baseline)
    # Rebuild maps because the candidate is a deep copy and reverse fields were reset.
    maps = topology_maps(baseline)
    page_claims: dict[str, set[str]] = defaultdict(set)
    proc_claims: dict[str, set[str]] = defaultdict(set)
    branch_claims: dict[str, set[str]] = defaultdict(set)
    step_claims: dict[str, set[str]] = defaultdict(set)
    fragment_claims: dict[str, set[str]] = defaultdict(set)
    route_claims: dict[str, set[str]] = defaultdict(set)
    for claim in baseline["claims"]:
        cid = claim["id"]
        if claim["origin"] == "LEGACY_OCCURRENCE":
            page_claims[claim["page_id"]].add(cid)
            if claim.get("procedure_id"):
                proc_claims[claim["procedure_id"]].add(cid)
            if claim.get("branch_id"):
                branch_claims[claim["branch_id"]].add(cid)
            if claim.get("step_id"):
                step_claims[claim["step_id"]].add(cid)
            if claim.get("fragment_id"):
                fragment_claims[claim["fragment_id"]].add(cid)
            if claim.get("supporting_route_id"):
                route_claims[claim["supporting_route_id"]].add(cid)
        else:
            page_claims[claim["page_id"]].add(cid)
            for target in claim["target_bindings"]:
                proc_claims[target["procedure_id"]].add(cid)
                for branch_id in target["branch_ids"]:
                    branch_claims[branch_id].add(cid)
                for step_id in target["step_ids"]:
                    step_claims[step_id].add(cid)
            for binding in claim["source_bindings"]:
                if binding["fragment_id"]:
                    fragment_claims[binding["fragment_id"]].add(cid)
    for page in baseline["pages"]:
        page["claim_ids"] = sorted(page_claims[page["id"]])
    for proc in baseline["procedures"]:
        proc["claim_ids"] = sorted(proc_claims[proc["id"]])
        for branch in proc["branches"]:
            branch["claim_ids"] = sorted(branch_claims[branch["id"]])
            for step in branch["steps"]:
                step["claim_ids"] = sorted(step_claims[step["id"]])
    for fragment in baseline["fragments"]:
        fragment["claim_ids"] = sorted(fragment_claims[fragment["id"]])
    for route in baseline["supporting_routes"]:
        route["claim_ids"] = sorted(route_claims[route["id"]])

    page_requirements: dict[str, set[str]] = defaultdict(set)
    proc_requirements: dict[str, set[str]] = defaultdict(set)
    branch_requirements: dict[str, set[str]] = defaultdict(set)
    step_requirements: dict[str, set[str]] = defaultdict(set)
    for requirement in requirements:
        rid = requirement["id"]
        storage = maps["procedure_by_id"][requirement["storage_procedure_id"]]
        storage["test_basis"]["reconciled_procedure_requirements"].append(requirement)
        for target in requirement["target_bindings"]:
            proc_id = target["procedure_id"]
            page_id = maps["procedure_by_id"][proc_id]["page_id"]
            page_requirements[page_id].add(rid)
            proc_requirements[proc_id].add(rid)
            for branch_id in target["branch_ids"]:
                branch_requirements[branch_id].add(rid)
            for step_id in target["step_ids"]:
                step_requirements[step_id].add(rid)
    for page in baseline["pages"]:
        page["procedure_requirement_ids"] = sorted(page_requirements[page["id"]])
    for proc in baseline["procedures"]:
        proc["test_basis"]["reconciled_procedure_requirement_ids"] = sorted(proc_requirements[proc["id"]])
        proc["test_basis"]["reconciled_procedure_requirements"].sort(key=lambda item: item["id"])
        for branch in proc["branches"]:
            branch["procedure_requirement_ids"] = sorted(branch_requirements[branch["id"]])
            for step in branch["steps"]:
                step["procedure_requirement_ids"] = sorted(step_requirements[step["id"]])


def attach_reconciliation_links(
    baseline: dict[str, Any], requirements: list[dict[str, Any]],
    dispositions: list[dict[str, Any]], defects: list[dict[str, Any]],
) -> None:
    claim_by_id = {claim["id"]: claim for claim in baseline["claims"]}
    requirement_by_id = {item["id"]: item for item in requirements}
    disposition_by_id = {item["id"]: item for item in dispositions}
    row_by_occurrence = {row["occurrence_id"]: row for row in baseline["legacy_crosswalk"]}
    for claim in baseline["claims"]:
        claim.setdefault("reconciliation_disposition_ids", [])
        claim.setdefault("defect_flag_ids", [])
    for row in baseline["legacy_crosswalk"]:
        row["reconciliation_disposition_ids"] = []
    for disposition in dispositions:
        did = disposition["id"]
        for target_id in disposition["canonical_target_refs"]:
            target = claim_by_id.get(target_id) or requirement_by_id.get(target_id)
            require(target is not None, f"{did}: unknown duplicate target {target_id}")
            target["reconciliation_disposition_ids"].append(did)
        for claim_id in disposition["equivalent_legacy_claim_ids"]:
            claim_by_id[claim_id]["reconciliation_disposition_ids"].append(did)
        for occurrence_id in disposition["equivalent_legacy_occurrence_ids"]:
            row_by_occurrence[occurrence_id]["reconciliation_disposition_ids"].append(did)
    for defect in defects:
        did = defect["id"]
        for ref in defect["affected_item_refs"]:
            item = (claim_by_id.get(ref["id"]) or requirement_by_id.get(ref["id"])
                    or disposition_by_id.get(ref["id"]))
            require(item is not None, f"{did}: unknown affected item {ref['id']}")
            item["defect_flag_ids"].append(did)
    for claim in baseline["claims"]:
        claim["reconciliation_disposition_ids"] = sorted(set(claim["reconciliation_disposition_ids"]))
        claim["defect_flag_ids"] = sorted(set(claim["defect_flag_ids"]))
    for requirement in requirements:
        requirement["reconciliation_disposition_ids"] = sorted(set(requirement["reconciliation_disposition_ids"]))
        requirement["defect_flag_ids"] = sorted(set(requirement["defect_flag_ids"]))
    for disposition in dispositions:
        disposition["defect_flag_ids"] = sorted(set(disposition["defect_flag_ids"]))
    for row in baseline["legacy_crosswalk"]:
        row["reconciliation_disposition_ids"] = sorted(set(row["reconciliation_disposition_ids"]))


def build_candidate(
    base: dict[str, Any], base_bytes: bytes, design: dict[str, Any],
    raw: dict[str, Any], reconcile: dict[str, Any],
) -> dict[str, Any]:
    candidate = copy.deepcopy(base)
    maps = topology_maps(candidate)
    raw_by_id, reconciled_by_id = reconcile_inputs(raw, reconcile, maps)
    original_topology = topology_signature(candidate)

    for claim in candidate["claims"]:
        claim["origin"] = "LEGACY_OCCURRENCE"
        claim["reconciliation_disposition_ids"] = []
        claim["defect_flag_ids"] = []

    material_claims: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    canonical_id_by_source: dict[str, str] = {}
    for source_id in sorted(reconciled_by_id):
        record = reconciled_by_id[source_id]
        if record["classification"] == "ADD_MATERIAL_CLAIM":
            item = make_material_claim(record, raw_by_id[source_id], maps)
            material_claims.append(item)
            canonical_id_by_source[source_id] = item["id"]
        elif record["classification"] == "ABSORB_IN_PROCEDURE_FIELD":
            item = make_requirement(record, raw_by_id[source_id], maps)
            requirements.append(item)
            canonical_id_by_source[source_id] = item["id"]
    material_claims.sort(key=lambda item: item["id"])
    requirements.sort(key=lambda item: item["id"])
    candidate["claims"].extend(material_claims)
    candidate["claims"].sort(key=lambda item: item["id"])

    dispositions = [
        make_disposition(record, maps, candidate, canonical_id_by_source)
        for source_id, record in sorted(reconciled_by_id.items())
        if record["classification"] in {"DUPLICATE", "LEGACY_EQUIVALENT"}
    ]
    dispositions.sort(key=lambda item: item["id"])

    item_by_source: dict[str, tuple[str, dict[str, Any]]] = {}
    for claim in material_claims:
        item_by_source[claim["source_record_id"]] = ("MATERIAL_CLAIM", claim)
    for requirement in requirements:
        item_by_source[requirement["source_record_id"]] = ("PROCEDURE_REQUIREMENT", requirement)
    for disposition in dispositions:
        item_by_source[disposition["source_record_id"]] = ("RECONCILIATION_DISPOSITION", disposition)
    defects: list[dict[str, Any]] = []
    for source_id, record in sorted(reconciled_by_id.items()):
        if record["source_span_review"]["state"] == "EXACT_SOURCE_SPAN":
            continue
        item_type, item = item_by_source[source_id]
        if item_type == "RECONCILIATION_DISPOSITION":
            binding_ids = [item["source_binding"]["id"]]
        else:
            binding_ids = [binding["id"] for binding in item["source_bindings"]]
        defects.append(make_defect_flag(record, item_type, item["id"], binding_ids))
    defects.sort(key=lambda item: item["id"])

    rebuild_reverse_indexes(candidate, requirements, maps)
    attach_reconciliation_links(candidate, requirements, dispositions, defects)
    require(topology_signature(candidate) == original_topology, "claim integration changed topology")

    target = copy.deepcopy(raw["target"])
    input_pins = {
        "design": {
            "design_id": design["design_id"],
            "schema_version": design["schema_version"],
            "sha256": EXPECTED_DESIGN_SHA256,
            "path_role": "PINNED_TEMPORARY_ASSEMBLY_INPUT_NOT_RUNTIME_DEPENDENCY",
        },
        "raw_gap_audit": {
            "audit_id": raw["audit_id"],
            "schema_version": raw["schema_version"],
            "sha256": EXPECTED_RAW_SHA256,
            "target": target,
            "path_role": "PINNED_TEMPORARY_ASSEMBLY_INPUT_NOT_RUNTIME_DEPENDENCY",
        },
        "independent_reconciliation": {
            "audit_id": reconcile["audit_id"],
            "schema_version": reconcile["schema_version"],
            "sha256": EXPECTED_RECONCILE_SHA256,
            "prepared_by": reconcile["prepared_by"],
            "target": copy.deepcopy(reconcile["target"]),
            "path_role": "PINNED_TEMPORARY_ASSEMBLY_INPUT_NOT_RUNTIME_DEPENDENCY",
        },
        "canonical_baseline": {
            "sha256": sha256_bytes(base_bytes),
            "baseline_id": base["baseline_id"],
            "plan_baseline_sha256": base["plan_baseline_sha256"],
            "path_role": "CANONICAL_INPUT_READ_ONLY_NOT_OVERWRITTEN",
        },
    }
    candidate["source_identity"]["raw_gap_integration_inputs"] = copy.deepcopy(input_pins)
    candidate["schema_version"] = "1.1"
    candidate["scope"].update({
        "legacy_occurrence_claims": 529,
        "reconciled_material_claims": 104,
        "canonical_claims": 633,
        "embedded_procedure_requirements": 67,
        "semantic_assessment_records": 700,
        "raw_gap_source_records_accounted_for": 177,
    })
    source_alignment_counts = Counter(row["source_alignment"] for row in candidate["legacy_crosswalk"])
    integration_counts = {
        "source_records_accounted_for": 177,
        "material_claims": 104,
        "embedded_requirements": 67,
        "duplicate_dispositions": 5,
        "legacy_equivalent_dispositions": 1,
        "total_dispositions": 6,
        "defect_flags": 17,
        "semantic_assessment_records": 700,
        "effective_source_bindings": sum(len(item["source_bindings"])
                                         for item in material_claims + requirements)
                                     + len(dispositions),
        "discovery_source_bindings": 177,
        "new_procedures": 0,
        "new_branches": 0,
        "new_steps": 0,
        "new_executable_test_units": 0,
    }
    candidate["reconciliation"].update({
        "pages": 39,
        "procedures": 82,
        "branches": 193,
        "steps": 454,
        "claims": 633,
        "legacy_claims": 529,
        "reconciled_material_claims": 104,
        "embedded_procedure_requirements": 67,
        "semantic_assessment_records": 700,
        "legacy_crosswalk_rows": 529,
        "unique_items_by_kind": copy.deepcopy(EXPECTED_LEGACY_UNIQUE),
        "occurrences_by_kind": copy.deepcopy(EXPECTED_LEGACY_OCCURRENCES),
        "occurrences_by_source_type": copy.deepcopy(EXPECTED_LEGACY_SOURCE_TYPES),
        "source_alignment_counts": dict(sorted(source_alignment_counts.items())),
        "raw_gap_integration": {
            "input_pins": copy.deepcopy(input_pins),
            "counts": integration_counts,
            "dispositions": dispositions,
            "defect_flags": defects,
            "integration_method": {
                "normalization_version": "host-docs-p1-raw-claim-integration-v1",
                "executable_unit": "page -> procedure -> applicable branch -> ordered step",
                "claims_are_not_executable_units": True,
                "absorbed_requirements_augment_existing_test_basis_only": True,
                "metadata_dispositions_create_no_semantic_or_execution_result": True,
                "current_mdx_is_not_authority_for_own_truth": True,
                "execution_performed": False,
            },
            "new_executable_test_units": 0,
        },
    })
    candidate["plan_baseline_sha256"] = None
    candidate["baseline_id"] = None
    digest = plan_digest(candidate)
    candidate["plan_baseline_sha256"] = digest
    head = candidate["source_identity"]["docs_target_revision"]
    candidate["baseline_id"] = f"P1-DRAFT-{head[:12]}-{digest[:12]}"
    return candidate


SOURCE_BINDING_FIELDS = {
    "id", "role", "primary_for_claim", "file", "line_start", "line_end",
    "source_type", "source_file_sha256", "source_span_sha256", "page_id",
    "fragment_id", "rendered_context_refs",
}
TARGET_BINDING_FIELDS = {"procedure_id", "branch_ids", "step_ids", "procedure_field"}
SEMANTIC_FIELDS = {
    "required", "scope", "status", "score", "rationale", "finding_class",
    "evidence_refs", "correction_id", "retest_id",
}
MATERIAL_CLAIM_FIELDS = {
    "id", "origin", "source_record_id", "source_set", "reconciliation_classification",
    "occurrence_id", "legacy_item_id", "legacy_location_index", "kind", "text", "source",
    "source_bindings", "discovery_source_binding", "page_id", "procedure_id", "branch_id",
    "step_id", "target_bindings", "supporting_route_id", "fragment_id", "primary_treatment",
    "source_alignment", "source_alignment_disposition", "raw_context",
    "rendered_context_refs", "legacy_overlap", "execution_unit_effect", "authority_refs",
    "authority_state", "authority_resolution", "claim_limit", "test_basis",
    "expected_observables", "planned_method", "status", "attempt_ids", "issue_ids",
    "reconciliation_disposition_ids", "defect_flag_ids", "semantic_assessment",
}
REQUIREMENT_FIELDS = {
    "id", "source_record_id", "source_set", "reconciliation_classification",
    "storage_procedure_id", "requirement_kind", "requirement_summary", "source_bindings",
    "discovery_source_binding", "source_span_review", "target_bindings", "field_target",
    "integration_effect", "execution_unit_effect", "legacy_overlap", "authority_effect",
    "authority_refs", "test_basis", "runtime_result_source", "reconciliation_disposition_ids",
    "defect_flag_ids", "semantic_assessment",
}
DISPOSITION_FIELDS = {
    "id", "source_record_id", "classification", "source_binding", "source_span_review",
    "duplicate_of_source_record_ids", "canonical_target_refs", "equivalent_legacy_item_ids",
    "equivalent_legacy_claim_ids", "equivalent_legacy_occurrence_ids", "effect", "rationale",
    "defect_flag_ids",
}
DEFECT_FIELDS = {
    "id", "source_record_id", "finding_class", "overclaim", "note", "corrected_summary",
    "effective_source_binding_ids", "affected_item_refs", "category", "gate_effect",
    "issue_ids", "correction_ids", "retest_ids",
}


def flatten_requirements(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        requirement
        for proc in candidate["procedures"]
        for requirement in proc.get("test_basis", {}).get("reconciled_procedure_requirements", [])
    ]


def validate_semantic(value: Any, context: str) -> None:
    exact_keys(value, SEMANTIC_FIELDS, context)
    require(value["required"] is True, f"{context}: assessment must be required")
    require(value["scope"] == "SOURCE_AUTHORITY_PROCEDURE_AND_RENDERED_CONTEXT",
            f"{context}: wrong semantic scope")
    status = value["status"]
    score = value["score"]
    require(status in {"UNVALIDATED", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE", "STALE"},
            f"{context}: invalid semantic status")
    if status == "PASS":
        require(score == 3 and isinstance(value["rationale"], str) and value["rationale"].strip()
                and value["evidence_refs"], f"{context}: PASS does not satisfy score/evidence gate")
    if score in {1, 2}:
        require(status == "FAIL", f"{context}: score 1/2 must be FAIL")
        expected = "NO_SUPPORT" if score == 1 else "PARTIAL_INCORRECT_BROKEN"
        require(value["finding_class"] == expected, f"{context}: score finding class differs")
    if status == "UNVALIDATED":
        require(score is None and value["rationale"] is None and not value["evidence_refs"],
                f"{context}: UNVALIDATED carries result evidence")


def validate_source_binding(
    binding: dict[str, Any], source_record_id: str, maps: dict[str, Any], context: str
) -> None:
    exact_keys(binding, SOURCE_BINDING_FIELDS, context)
    require(binding["role"] in ALLOWED_SOURCE_ROLES, f"{context}: invalid role")
    expected_id = source_binding_id(
        source_record_id, binding["role"], binding["file"],
        binding["line_start"], binding["line_end"],
    )
    require(binding["id"] == expected_id, f"{context}: unstable source-binding ID")
    _, full_hash, span_hash = normalized_span(
        binding["file"], binding["line_start"], binding["line_end"]
    )
    require(binding["source_file_sha256"] == full_hash, f"{context}: stale full-file hash")
    require(binding["source_span_sha256"] == span_hash, f"{context}: stale source-span hash")
    page = maps["page_by_file"].get(binding["file"])
    fragment = maps["fragment_by_file"].get(binding["file"])
    require(binding["page_id"] == (page["id"] if page else None), f"{context}: wrong page owner")
    require(binding["fragment_id"] == (fragment["id"] if fragment else None),
            f"{context}: wrong fragment owner")
    require(binding["source_type"] == source_type_for(binding["file"]),
            f"{context}: wrong source type")
    valid_routes = {page["route"] for page in maps["page_by_id"].values()}
    require(binding["rendered_context_refs"] == sorted(set(binding["rendered_context_refs"])),
            f"{context}: rendered refs are not sorted unique")
    require(bool(binding["rendered_context_refs"])
            and set(binding["rendered_context_refs"]).issubset(valid_routes),
            f"{context}: invalid rendered primary Host route")


def validate_target_bindings(
    bindings: Any, source_record_id: str, maps: dict[str, Any], page_id: str,
    context: str,
) -> None:
    require(isinstance(bindings, list) and bindings, f"{context}: target bindings missing")
    proc_ids: list[str] = []
    for index, binding in enumerate(bindings):
        exact_keys(binding, TARGET_BINDING_FIELDS, f"{context}[{index}]")
        proc_id = binding["procedure_id"]
        proc = maps["procedure_by_id"].get(proc_id)
        require(proc is not None and proc["page_id"] == page_id,
                f"{context}: wrong target procedure/page {proc_id}")
        proc_ids.append(proc_id)
        require(binding["branch_ids"] == sorted(set(binding["branch_ids"])),
                f"{context}: branch IDs not sorted unique")
        require(binding["step_ids"] == sorted(set(binding["step_ids"])),
                f"{context}: step IDs not sorted unique")
        for branch_id in binding["branch_ids"]:
            require(maps["branch_by_id"].get(branch_id, (None,))[0] == proc_id,
                    f"{context}: branch ownership differs")
        for step_id in binding["step_ids"]:
            owner = maps["step_by_id"].get(step_id)
            require(owner is not None and owner[0] == proc_id,
                    f"{context}: step ownership differs")
            require(owner[1] in binding["branch_ids"],
                    f"{context}: step owner branch absent")
        require(isinstance(binding["procedure_field"], str) and binding["procedure_field"],
                f"{context}: procedure field missing")
    require(proc_ids == sorted(set(proc_ids)), f"{context}: procedure IDs not sorted unique")
    if source_record_id == "GAP-ERR-002":
        require(proc_ids == ["ERR-T01", "ERR-T02"], "GAP-ERR-002 lost a target procedure")
    if source_record_id == "GAP-FLT-003":
        require(proc_ids == ["FLT-E04", "FLT-E05"], "GAP-FLT-003 lost a target procedure")


def validate_special_source_corrections(
    item_by_source: dict[str, dict[str, Any]], maps: dict[str, Any]
) -> None:
    string_item = item_by_source["GAP-STR-009"]
    sources = string_item["source_bindings"]
    require(len(sources) == 1 and sources[0]["file"] == "host/self-test-reference.mdx"
            and sources[0]["line_start"] == 237 and sources[0]["line_end"] == 250,
            "GAP-STR-009 does not retain corrected 237-250 effective span")
    require(string_item["discovery_source_binding"]["line_end"] == 247,
            "GAP-STR-009 original discovery defect was hidden")
    notification = item_by_source["GAP-NOT-002"]
    roles = {(source["file"], source["role"], source["primary_for_claim"])
             for source in notification["source_bindings"]}
    require(roles == {
        ("host/notifications.mdx", "IMPORT_AND_RENDERED_CONTEXT", False),
        ("snippets/notifications/channels.mdx", "IMPORTED_CLAIM_SOURCE", True),
    }, "GAP-NOT-002 does not preserve import plus fragment semantics")
    page = maps["page_by_file"]["host/notifications.mdx"]
    require("snippets/notifications/channels.mdx" in page.get("imports", []),
            "notifications Host page no longer imports the claim fragment")
    fragment = maps["fragment_by_file"]["snippets/notifications/channels.mdx"]
    require(page["id"] in fragment["rendered_route_ids"],
            "notifications fragment no longer renders on its Host page")


def expected_reverse_indexes(
    candidate: dict[str, Any], requirements: list[dict[str, Any]]
) -> dict[str, dict[str, set[str]]]:
    result: dict[str, dict[str, set[str]]] = {
        key: defaultdict(set) for key in (
            "page_claims", "proc_claims", "branch_claims", "step_claims",
            "fragment_claims", "route_claims", "page_requirements",
            "proc_requirements", "branch_requirements", "step_requirements",
        )
    }
    for claim in candidate["claims"]:
        cid = claim["id"]
        result["page_claims"][claim["page_id"]].add(cid)
        if claim["origin"] == "LEGACY_OCCURRENCE":
            if claim.get("procedure_id"):
                result["proc_claims"][claim["procedure_id"]].add(cid)
            if claim.get("branch_id"):
                result["branch_claims"][claim["branch_id"]].add(cid)
            if claim.get("step_id"):
                result["step_claims"][claim["step_id"]].add(cid)
            if claim.get("fragment_id"):
                result["fragment_claims"][claim["fragment_id"]].add(cid)
            if claim.get("supporting_route_id"):
                result["route_claims"][claim["supporting_route_id"]].add(cid)
        else:
            for target in claim["target_bindings"]:
                result["proc_claims"][target["procedure_id"]].add(cid)
                for branch_id in target["branch_ids"]:
                    result["branch_claims"][branch_id].add(cid)
                for step_id in target["step_ids"]:
                    result["step_claims"][step_id].add(cid)
            for binding in claim["source_bindings"]:
                if binding["fragment_id"]:
                    result["fragment_claims"][binding["fragment_id"]].add(cid)
    maps = topology_maps(candidate)
    for requirement in requirements:
        rid = requirement["id"]
        for target in requirement["target_bindings"]:
            proc_id = target["procedure_id"]
            result["proc_requirements"][proc_id].add(rid)
            result["page_requirements"][maps["procedure_by_id"][proc_id]["page_id"]].add(rid)
            for branch_id in target["branch_ids"]:
                result["branch_requirements"][branch_id].add(rid)
            for step_id in target["step_ids"]:
                result["step_requirements"][step_id].add(rid)
    return result


def privacy_projection(candidate: dict[str, Any]) -> dict[str, Any]:
    projection = copy.deepcopy(candidate)
    for claim in projection["claims"]:
        claim["text"] = "[SOURCE_TEXT_STRIPPED]"
    for proc in projection["procedures"]:
        for branch in proc["branches"]:
            for step in branch["steps"]:
                step["source_carriers"] = []
    return projection


def privacy_findings(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}"
            if str(key).lower() in FORBIDDEN_KEYS and item not in (None, "", False, [], {}):
                findings.append(child + ":restricted-key")
            findings.extend(privacy_findings(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(privacy_findings(item, f"{prefix}[{index}]") )
    elif isinstance(value, str):
        if "/private/tmp" in value:
            findings.append(prefix + ":temporary-absolute-path")
        if PRIVATE_KEY_RE.search(value):
            findings.append(prefix + ":private-key")
        for match in IPV4_RE.findall(value):
            try:
                ipaddress.IPv4Address(match)
            except ValueError:
                continue
            findings.append(prefix + ":raw-ipv4")
    return findings


def validate_candidate(
    candidate: dict[str, Any], base: dict[str, Any], base_bytes: bytes
) -> dict[str, Any]:
    require(sha256_bytes(base_bytes) == EXPECTED_CANONICAL_SHA256,
            "canonical baseline no longer matches the integration pin")
    require(plan_digest(base) == base["plan_baseline_sha256"],
            "canonical baseline plan identity is invalid")
    require(candidate.get("schema_version") == "1.1", "candidate schema must be 1.1")
    require(candidate.get("record_type") == base.get("record_type"), "candidate record type changed")
    require(candidate.get("state") == "DRAFT_NOT_FROZEN", "candidate is not a draft")
    require(topology_signature(candidate) == topology_signature(base),
            "candidate changed page/procedure/branch/step topology")
    maps = topology_maps(candidate)

    integration = candidate.get("reconciliation", {}).get("raw_gap_integration")
    require(isinstance(integration, dict), "candidate lacks raw-gap integration metadata")
    pins = integration.get("input_pins", {})
    source_pins = candidate.get("source_identity", {}).get("raw_gap_integration_inputs")
    require(pins == source_pins, "input-pin copies differ")
    require(pins.get("design", {}).get("sha256") == EXPECTED_DESIGN_SHA256,
            "embedded design pin differs")
    require(pins.get("raw_gap_audit", {}).get("sha256") == EXPECTED_RAW_SHA256,
            "embedded raw-audit pin differs")
    require(pins.get("independent_reconciliation", {}).get("sha256") == EXPECTED_RECONCILE_SHA256,
            "embedded reconciliation pin differs")
    require(pins.get("canonical_baseline", {}).get("sha256") == EXPECTED_CANONICAL_SHA256,
            "embedded canonical baseline pin differs")
    require(pins["canonical_baseline"]["baseline_id"] == base["baseline_id"]
            and pins["canonical_baseline"]["plan_baseline_sha256"] == base["plan_baseline_sha256"],
            "embedded canonical plan identity differs")
    target = pins["raw_gap_audit"]["target"]
    require(target == pins["independent_reconciliation"]["target"], "embedded input targets differ")
    require(target["docs_head"] == base["source_identity"]["docs_target_revision"]
            and target["docs_tree"] == base["source_identity"]["repository_tree_at_assembly"],
            "embedded input target does not match canonical docs target")
    legacy_identity = base["source_identity"]["legacy_inventory"]
    require(target["legacy_inventory_sha256"] == legacy_identity["sha256"]
            and target["legacy_inventory_source_revision"] == legacy_identity["source_revision"]
            and target["legacy_content_fingerprint"] == legacy_identity["content_fingerprint"],
            "embedded legacy target does not match canonical identity")
    for pin in pins.values():
        require("path" not in pin, "candidate embeds an input filesystem path")

    claims = candidate.get("claims", [])
    legacy_claims = [claim for claim in claims if claim.get("origin") == "LEGACY_OCCURRENCE"]
    material_claims = [claim for claim in claims if claim.get("origin") == "RECONCILED_MATERIAL"]
    require(len(claims) == 633 and len(legacy_claims) == 529 and len(material_claims) == 104,
            f"claim origin counts differ: {len(claims)}/{len(legacy_claims)}/{len(material_claims)}")
    require(len({claim["id"] for claim in claims}) == 633, "claim IDs are not unique")
    base_claims = {claim["id"]: claim for claim in base["claims"]}
    require(set(base_claims) == {claim["id"] for claim in legacy_claims},
            "legacy claim set differs from canonical 529")
    for claim in legacy_claims:
        projection = copy.deepcopy(claim)
        require(projection.pop("origin") == "LEGACY_OCCURRENCE", "legacy claim origin differs")
        projection.pop("reconciliation_disposition_ids")
        projection.pop("defect_flag_ids")
        require(projection == base_claims[claim["id"]], f"legacy claim changed: {claim['id']}")

    crosswalk = candidate.get("legacy_crosswalk", [])
    require(len(crosswalk) == 529 and len({row["occurrence_id"] for row in crosswalk}) == 529,
            "legacy crosswalk is not 529 unique rows")
    require({row["claim_id"] for row in crosswalk} == {claim["id"] for claim in legacy_claims},
            "crosswalk does not exactly cover legacy claims")
    base_rows = {row["occurrence_id"]: row for row in base["legacy_crosswalk"]}
    for row in crosswalk:
        projection = copy.deepcopy(row)
        projection.pop("reconciliation_disposition_ids")
        require(projection == base_rows.get(row["occurrence_id"]),
                f"legacy crosswalk row changed: {row['occurrence_id']}")
    unique_kinds: dict[str, set[str]] = defaultdict(set)
    occurrence_kinds: Counter[str] = Counter()
    source_types: Counter[str] = Counter()
    for claim in legacy_claims:
        unique_kinds[claim["kind"]].add(claim["legacy_item_id"])
        occurrence_kinds[claim["kind"]] += 1
        source_types[claim["source"]["source_type"]] += 1
    require({key: len(value) for key, value in unique_kinds.items()} == EXPECTED_LEGACY_UNIQUE,
            "legacy unique-kind denominator drifted")
    require(dict(occurrence_kinds) == EXPECTED_LEGACY_OCCURRENCES,
            "legacy occurrence-kind denominator drifted")
    require(dict(source_types) == EXPECTED_LEGACY_SOURCE_TYPES,
            "legacy source-type denominator drifted")

    requirements = flatten_requirements(candidate)
    require(len(requirements) == 67 and len({item["id"] for item in requirements}) == 67,
            "embedded requirements are not 67 unique physical records")
    dispositions = integration.get("dispositions", [])
    defects = integration.get("defect_flags", [])
    require(len(dispositions) == 6 and len({item["id"] for item in dispositions}) == 6,
            "metadata dispositions are not 6 unique records")
    require(Counter(item["classification"] for item in dispositions)
            == Counter({"DUPLICATE": 5, "LEGACY_EQUIVALENT": 1}),
            "metadata disposition split differs")
    require(len(defects) == 17 and len({item["id"] for item in defects}) == 17,
            "defect flags are not 17 unique records")

    item_by_source: dict[str, dict[str, Any]] = {}
    item_type_by_source: dict[str, str] = {}
    authority_source_ids = {source["id"] for source in candidate["authority_sources"]}
    for claim in material_claims:
        exact_keys(claim, MATERIAL_CLAIM_FIELDS, f"material claim {claim.get('id')}")
        source_id = claim["source_record_id"]
        require(claim["id"] == material_claim_id(source_id), f"{source_id}: unstable material claim ID")
        require(claim["reconciliation_classification"] == "ADD_MATERIAL_CLAIM"
                and claim["source_set"] == "PROPOSED_GAP",
                f"{source_id}: wrong material destination")
        require(claim["occurrence_id"] is None and claim["legacy_item_id"] is None
                and claim["legacy_location_index"] is None,
                f"{source_id}: material claim has legacy identity")
        require(claim["procedure_id"] is None and claim["branch_id"] is None
                and claim["step_id"] is None and claim["supporting_route_id"] is None,
                f"{source_id}: material claim became a direct execution unit")
        require(claim["primary_treatment"] == "non-executable-claim"
                and claim["execution_unit_effect"] == "NO_NEW_EXECUTABLE_TEST_UNIT",
                f"{source_id}: material claim has executable effect")
        require(claim["authority_state"] == "PENDING_OWNER", f"{source_id}: authority was promoted")
        require(claim["status"] == "UNVALIDATED" and not claim["attempt_ids"] and not claim["issue_ids"],
                f"{source_id}: material claim carries a result")
        validate_semantic(claim["semantic_assessment"], f"material claim {source_id}.semantic")
        validate_target_bindings(claim["target_bindings"], source_id, maps, claim["page_id"],
                                 f"material claim {source_id}.targets")
        require(claim["rendered_context_refs"] and all(
            ref.get("status") == "UNVALIDATED" and not ref.get("evidence_refs")
            for ref in claim["rendered_context_refs"]
        ), f"{source_id}: rendered context carries a result")
        for binding in claim["source_bindings"]:
            validate_source_binding(binding, source_id, maps, f"material claim {source_id}.source")
        validate_source_binding(claim["discovery_source_binding"], source_id, maps,
                                f"material claim {source_id}.discovery")
        require(sum(bool(binding["primary_for_claim"]) for binding in claim["source_bindings"]) == 1,
                f"{source_id}: material claim lacks one effective primary source")
        primary = next(binding for binding in claim["source_bindings"] if binding["primary_for_claim"])
        require(claim["source"] == source_projection(primary),
                f"{source_id}: compatibility source is not the effective primary binding")
        fragment_ids = sorted({binding["fragment_id"] for binding in claim["source_bindings"]
                               if binding["fragment_id"]})
        require(claim["fragment_id"] == (fragment_ids[0] if fragment_ids else None),
                f"{source_id}: fragment ownership projection differs")
        require(set(claim["authority_refs"]).issubset(authority_source_ids),
                f"{source_id}: unknown authority reference")
        require(claim["authority_resolution"]["current_mdx_is_authority_for_own_truth"] is False,
                f"{source_id}: current prose was promoted to authority")
        discovery_span = claim["raw_context"]["discovery_span"]
        require(discovery_span["source_span_sha256"]
                == claim["discovery_source_binding"]["source_span_sha256"],
                f"{source_id}: discovery source projection differs")
        item_by_source[source_id] = claim
        item_type_by_source[source_id] = "MATERIAL_CLAIM"

    for requirement in requirements:
        exact_keys(requirement, REQUIREMENT_FIELDS, f"requirement {requirement.get('id')}")
        source_id = requirement["source_record_id"]
        require(requirement["id"] == requirement_id(source_id), f"{source_id}: unstable requirement ID")
        require(requirement["reconciliation_classification"] == "ABSORB_IN_PROCEDURE_FIELD",
                f"{source_id}: wrong requirement destination")
        require(requirement["storage_procedure_id"]
                == min(target["procedure_id"] for target in requirement["target_bindings"]),
                f"{source_id}: nondeterministic requirement storage")
        require(requirement["integration_effect"] == "AUGMENTS_EXISTING_PROCEDURE_TEST_BASIS_ONLY"
                and requirement["execution_unit_effect"] == "NO_NEW_EXECUTABLE_TEST_UNIT"
                and requirement["runtime_result_source"] == "TARGET_PROCEDURE_BRANCH_STEP_ATTEMPTS_ONLY",
                f"{source_id}: requirement creates independent execution/result state")
        page_id = maps["procedure_by_id"][requirement["target_bindings"][0]["procedure_id"]]["page_id"]
        validate_target_bindings(requirement["target_bindings"], source_id, maps, page_id,
                                 f"requirement {source_id}.targets")
        validate_semantic(requirement["semantic_assessment"], f"requirement {source_id}.semantic")
        for binding in requirement["source_bindings"]:
            validate_source_binding(binding, source_id, maps, f"requirement {source_id}.source")
        require(bool(requirement["source_bindings"]), f"{source_id}: requirement has no effective source")
        validate_source_binding(requirement["discovery_source_binding"], source_id, maps,
                                f"requirement {source_id}.discovery")
        require(set(requirement["authority_refs"]).issubset(authority_source_ids),
                f"{source_id}: unknown requirement authority reference")
        item_by_source[source_id] = requirement
        item_type_by_source[source_id] = "PROCEDURE_REQUIREMENT"

    for disposition in dispositions:
        exact_keys(disposition, DISPOSITION_FIELDS, f"disposition {disposition.get('id')}")
        source_id = disposition["source_record_id"]
        require(disposition["id"] == disposition_id(source_id), f"{source_id}: unstable disposition ID")
        validate_source_binding(disposition["source_binding"], source_id, maps,
                                f"disposition {source_id}.source")
        require(disposition["effect"] == "NO_NEW_CLAIM_REQUIREMENT_OR_EXECUTABLE_UNIT",
                f"{source_id}: disposition has semantic/executable effect")
        item_by_source[source_id] = disposition
        item_type_by_source[source_id] = "RECONCILIATION_DISPOSITION"
    require(len(item_by_source) == 177, "177 source records are not uniquely accounted for")
    require(Counter(item_type_by_source.values()) == Counter({
        "MATERIAL_CLAIM": 104, "PROCEDURE_REQUIREMENT": 67,
        "RECONCILIATION_DISPOSITION": 6,
    }), "source-record destinations differ")
    source_record_digest = sha256_bytes(canonical_json(sorted(item_by_source)))
    require(source_record_digest == EXPECTED_SOURCE_RECORD_SET_SHA256,
            "canonical 177 source-record ID set differs from the pinned reconciliation")
    classification_projection = []
    for source_id in sorted(item_by_source):
        item = item_by_source[source_id]
        if item_type_by_source[source_id] == "MATERIAL_CLAIM":
            classification = "ADD_MATERIAL_CLAIM"
            source_set = item["source_set"]
        elif item_type_by_source[source_id] == "PROCEDURE_REQUIREMENT":
            classification = "ABSORB_IN_PROCEDURE_FIELD"
            source_set = item["source_set"]
        else:
            classification = item["classification"]
            source_set = "COVERED_OR_AMBIGUOUS"
        classification_projection.append({
            "id": source_id, "classification": classification, "source_set": source_set,
        })
    require(sha256_bytes(canonical_json(classification_projection))
            == EXPECTED_CLASSIFICATION_MAP_SHA256,
            "source-record classification map differs from the pinned reconciliation")
    validate_special_source_corrections(item_by_source, maps)

    # Metadata resolution and exact reverse annotations.
    claim_by_id = {claim["id"]: claim for claim in claims}
    requirement_by_id = {item["id"]: item for item in requirements}
    disposition_by_id = {item["id"]: item for item in dispositions}
    row_by_occurrence = {row["occurrence_id"]: row for row in crosswalk}
    expected_item_dispositions: dict[str, set[str]] = defaultdict(set)
    expected_row_dispositions: dict[str, set[str]] = defaultdict(set)
    for disposition in dispositions:
        did = disposition["id"]
        if disposition["classification"] == "DUPLICATE":
            expected_targets = sorted(
                item_by_source[source_id]["id"]
                for source_id in disposition["duplicate_of_source_record_ids"]
            )
            require(disposition["canonical_target_refs"] == expected_targets,
                    f"{disposition['source_record_id']}: duplicate resolution differs")
            require(not disposition["equivalent_legacy_claim_ids"]
                    and not disposition["equivalent_legacy_occurrence_ids"],
                    f"{disposition['source_record_id']}: duplicate has legacy-equivalent links")
            for target_id in expected_targets:
                expected_item_dispositions[target_id].add(did)
        else:
            require(disposition["source_record_id"] == "AMB-PRICE-001"
                    and disposition["equivalent_legacy_item_ids"] == ["com-7fa3c4e802"],
                    "legacy-equivalent disposition differs")
            require(len(disposition["equivalent_legacy_claim_ids"]) == 1
                    and len(disposition["equivalent_legacy_occurrence_ids"]) == 1,
                    "legacy-equivalent disposition is not one-to-one")
            cid = disposition["equivalent_legacy_claim_ids"][0]
            oid = disposition["equivalent_legacy_occurrence_ids"][0]
            require(claim_by_id[cid]["legacy_item_id"] == "com-7fa3c4e802"
                    and row_by_occurrence[oid]["claim_id"] == cid,
                    "legacy-equivalent disposition points to the wrong occurrence")
            expected_item_dispositions[cid].add(did)
            expected_row_dispositions[oid].add(did)
    for item in claims + requirements:
        require(set(item.get("reconciliation_disposition_ids", []))
                == expected_item_dispositions[item["id"]],
                f"{item['id']}: disposition reverse link differs")
    for row in crosswalk:
        require(set(row["reconciliation_disposition_ids"])
                == expected_row_dispositions[row["occurrence_id"]],
                f"{row['occurrence_id']}: disposition reverse link differs")

    source_review_by_id = {
        source_id: (
            item["raw_context"]["source_span_review"]
            if item_type_by_source[source_id] == "MATERIAL_CLAIM"
            else item["source_span_review"]
        )
        for source_id, item in item_by_source.items()
    }
    expected_defect_sources = {
        source_id for source_id, review in source_review_by_id.items()
        if review["state"] != "EXACT_SOURCE_SPAN"
    }
    require(len(expected_defect_sources) == 17
            and {item["source_record_id"] for item in defects} == expected_defect_sources,
            "defect predicate/source set differs")
    require(sha256_bytes(canonical_json(sorted(expected_defect_sources)))
            == EXPECTED_DEFECT_SOURCE_SET_SHA256,
            "defect source-record set differs from the pinned reconciliation")
    expected_item_defects: dict[str, set[str]] = defaultdict(set)
    for defect in defects:
        exact_keys(defect, DEFECT_FIELDS, f"defect {defect.get('id')}")
        source_id = defect["source_record_id"]
        require(defect["id"] == defect_id(source_id), f"{source_id}: unstable defect ID")
        review = source_review_by_id[source_id]
        category, gate = defect_category(review["state"])
        require(defect["finding_class"] == review["state"]
                and defect["overclaim"] == review["overclaim"]
                and defect["note"] == review["note"]
                and defect["corrected_summary"] == review.get("corrected_summary")
                and defect["category"] == category and defect["gate_effect"] == gate,
                f"{source_id}: defect content differs from immutable planning finding")
        item = item_by_source[source_id]
        expected_ref = {"type": item_type_by_source[source_id], "id": item["id"]}
        require(defect["affected_item_refs"] == [expected_ref],
                f"{source_id}: defect affected-item link differs")
        expected_bindings = ([item["source_binding"]["id"]]
                             if item_type_by_source[source_id] == "RECONCILIATION_DISPOSITION"
                             else sorted(binding["id"] for binding in item["source_bindings"]))
        require(defect["effective_source_binding_ids"] == expected_bindings,
                f"{source_id}: defect source-binding links differ")
        expected_item_defects[item["id"]].add(defect["id"])
    for item in claims + requirements + dispositions:
        require(set(item.get("defect_flag_ids", [])) == expected_item_defects[item["id"]],
                f"{item['id']}: defect reverse link differs")

    expected = expected_reverse_indexes(candidate, requirements)
    for page in candidate["pages"]:
        require(set(page["claim_ids"]) == expected["page_claims"][page["id"]],
                f"page {page['id']}: claim reverse index differs")
        require(set(page["procedure_requirement_ids"]) == expected["page_requirements"][page["id"]],
                f"page {page['id']}: requirement reverse index differs")
    for proc in candidate["procedures"]:
        require(set(proc["claim_ids"]) == expected["proc_claims"][proc["id"]],
                f"procedure {proc['id']}: claim reverse index differs")
        test_basis = proc["test_basis"]
        require(set(test_basis["reconciled_procedure_requirement_ids"])
                == expected["proc_requirements"][proc["id"]],
                f"procedure {proc['id']}: requirement reverse index differs")
        for item in test_basis["reconciled_procedure_requirements"]:
            require(item["storage_procedure_id"] == proc["id"],
                    f"requirement {item['id']}: physically stored under wrong procedure")
        for branch in proc["branches"]:
            require(set(branch["claim_ids"]) == expected["branch_claims"][branch["id"]],
                    f"branch {branch['id']}: claim reverse index differs")
            require(set(branch["procedure_requirement_ids"])
                    == expected["branch_requirements"][branch["id"]],
                    f"branch {branch['id']}: requirement reverse index differs")
            for step in branch["steps"]:
                require(set(step["claim_ids"]) == expected["step_claims"][step["id"]],
                        f"step {step['id']}: claim reverse index differs")
                require(set(step["procedure_requirement_ids"])
                        == expected["step_requirements"][step["id"]],
                        f"step {step['id']}: requirement reverse index differs")
                expected_carriers = {
                    claim["id"] for claim in legacy_claims if claim.get("step_id") == step["id"]
                }
                actual_carriers = {carrier["claim_id"] for carrier in step["source_carriers"]}
                require(actual_carriers == expected_carriers,
                        f"step {step['id']}: source carriers are not exact legacy direct claims")
    for fragment in candidate["fragments"]:
        require(set(fragment["claim_ids"]) == expected["fragment_claims"][fragment["id"]],
                f"fragment {fragment['id']}: claim reverse index differs")
    for route in candidate["supporting_routes"]:
        require(set(route["claim_ids"]) == expected["route_claims"][route["id"]],
                f"supporting route {route['id']}: claim reverse index differs")

    counts = integration.get("counts", {})
    actual_effective_bindings = sum(
        len(item["source_bindings"])
        for item in material_claims + requirements
    ) + len(dispositions)
    actual_discovery_bindings = len(material_claims) + len(requirements) + len(dispositions)
    require(actual_effective_bindings == 178 and actual_discovery_bindings == 177,
            "actual effective/discovery source-binding counts differ")
    expected_counts = {
        "source_records_accounted_for": 177,
        "material_claims": 104,
        "embedded_requirements": 67,
        "duplicate_dispositions": 5,
        "legacy_equivalent_dispositions": 1,
        "total_dispositions": 6,
        "defect_flags": 17,
        "semantic_assessment_records": 700,
        "effective_source_bindings": 178,
        "discovery_source_bindings": 177,
        "new_procedures": 0,
        "new_branches": 0,
        "new_steps": 0,
        "new_executable_test_units": 0,
    }
    require(counts == expected_counts, f"integration counts differ: {counts}")
    require(candidate["scope"]["legacy_occurrence_claims"] == 529
            and candidate["scope"]["reconciled_material_claims"] == 104
            and candidate["scope"]["canonical_claims"] == 633
            and candidate["scope"]["embedded_procedure_requirements"] == 67
            and candidate["scope"]["semantic_assessment_records"] == 700,
            "scope counts differ")
    require(candidate["reconciliation"]["claims"] == 633
            and candidate["reconciliation"]["legacy_claims"] == 529
            and candidate["reconciliation"]["embedded_procedure_requirements"] == 67
            and candidate["reconciliation"]["semantic_assessment_records"] == 700
            and candidate["reconciliation"]["legacy_crosswalk_rows"] == 529,
            "reconciliation counts differ")
    require(candidate["reconciliation"]["unique_items_by_kind"] == EXPECTED_LEGACY_UNIQUE
            and candidate["reconciliation"]["occurrences_by_kind"] == EXPECTED_LEGACY_OCCURRENCES
            and candidate["reconciliation"]["occurrences_by_source_type"] == EXPECTED_LEGACY_SOURCE_TYPES,
            "reported legacy denominator counts differ")
    require(candidate["completion_and_acceptance"]["human_acceptance"]["decision"] == "NOT_DECIDED",
            "candidate claims human acceptance")
    require(integration["new_executable_test_units"] == 0
            and integration["integration_method"]["execution_performed"] is False,
            "candidate claims or permits integration execution")
    findings = privacy_findings(privacy_projection(candidate))
    require(not findings, f"candidate privacy/restricted-metadata findings: {findings[:10]}")
    digest = plan_digest(candidate)
    require(candidate["plan_baseline_sha256"] == digest, "candidate plan digest is forged or stale")
    expected_baseline_id = (
        "P1-DRAFT-" + candidate["source_identity"]["docs_target_revision"][:12]
        + "-" + digest[:12]
    )
    require(candidate["baseline_id"] == expected_baseline_id, "candidate baseline ID differs from plan digest")
    return {
        "pages": 39,
        "procedures": 82,
        "branches": 193,
        "steps": 454,
        "legacy_claims": 529,
        "material_claims": 104,
        "claims": 633,
        "legacy_crosswalk_rows": 529,
        "embedded_requirements": 67,
        "dispositions": 6,
        "defect_flags": 17,
        "semantic_assessments": 700,
        "effective_source_bindings": 178,
        "discovery_source_bindings": 177,
        "new_executable_test_units": 0,
        "plan_baseline_sha256": digest,
        "baseline_id": expected_baseline_id,
    }


def refresh_plan_identity(candidate: dict[str, Any]) -> None:
    digest = plan_digest(candidate)
    candidate["plan_baseline_sha256"] = digest
    candidate["baseline_id"] = (
        "P1-DRAFT-" + candidate["source_identity"]["docs_target_revision"][:12]
        + "-" + digest[:12]
    )


def material_for(candidate: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(claim for claim in candidate["claims"] if claim.get("source_record_id") == source_id)


def requirement_for(candidate: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(item for item in flatten_requirements(candidate) if item["source_record_id"] == source_id)


def disposition_for(candidate: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(item for item in candidate["reconciliation"]["raw_gap_integration"]["dispositions"]
                if item["source_record_id"] == source_id)


def defect_for(candidate: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(item for item in candidate["reconciliation"]["raw_gap_integration"]["defect_flags"]
                if item["source_record_id"] == source_id)


def run_adversarial_tests(
    candidate: dict[str, Any], base: dict[str, Any], base_bytes: bytes
) -> dict[str, Any]:
    """Run the design's 30 adversarial checks without modifying repository sources."""

    def ait001(value: dict[str, Any]) -> None:
        row = copy.deepcopy(value["legacy_crosswalk"][0])
        row["occurrence_id"] = "OCC-adversarial-530"
        value["legacy_crosswalk"].append(row)

    def ait002(value: dict[str, Any]) -> None:
        legacy_index = next(i for i, item in enumerate(value["claims"])
                            if item["origin"] == "LEGACY_OCCURRENCE")
        value["claims"].pop(legacy_index)
        replacement = copy.deepcopy(next(item for item in value["claims"]
                                         if item["origin"] == "RECONCILED_MATERIAL"))
        replacement["source_record_id"] = "GAP-ADVERSARIAL-REPLACEMENT"
        replacement["id"] = material_claim_id(replacement["source_record_id"])
        value["claims"].append(replacement)

    def ait003(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["legacy_item_id"] = "com-forged"

    def ait004(value: dict[str, Any]) -> None:
        original = material_for(value, "GAP-ERR-002")
        split = copy.deepcopy(original)
        split["source_record_id"] = "GAP-ERR-002-SPLIT"
        split["id"] = material_claim_id(split["source_record_id"])
        split["target_bindings"] = split["target_bindings"][:1]
        value["claims"].append(split)

    def ait005(value: dict[str, Any]) -> None:
        item = copy.deepcopy(requirement_for(value, "GAP-FLT-003"))
        target_proc = next(proc for proc in value["procedures"] if proc["id"] == "FLT-E05")
        target_proc["test_basis"]["reconciled_procedure_requirements"].append(item)

    def ait006(value: dict[str, Any]) -> None:
        material_for(value, "GAP-ERR-002")["target_bindings"] = [
            material_for(value, "GAP-ERR-002")["target_bindings"][0]
        ]

    def ait007(value: dict[str, Any]) -> None:
        item = material_for(value, "GAP-ERR-002")
        wrong = next(
            branch["id"] for proc in value["procedures"] if proc["id"] != "ERR-T01"
            for branch in proc["branches"]
        )
        item["target_bindings"][0]["branch_ids"] = [wrong]

    def ait008(value: dict[str, Any]) -> None:
        target = material_for(value, "GAP-ERR-002")["target_bindings"][0]
        target["branch_ids"] = target["branch_ids"][1:]

    def ait009(value: dict[str, Any]) -> None:
        item = material_for(value, "GAP-HOV-001")
        proc_id = item["target_bindings"][0]["procedure_id"]
        proc = next(proc for proc in value["procedures"] if proc["id"] == proc_id)
        proc["claim_ids"].remove(item["id"])

    def ait010(value: dict[str, Any]) -> None:
        item = material_for(value, "GAP-ERR-002")
        step_id = item["target_bindings"][0]["step_ids"][0]
        step = next(step for proc in value["procedures"] for branch in proc["branches"]
                    for step in branch["steps"] if step["id"] == step_id)
        step["source_carriers"].append({
            "claim_id": item["id"], "kind": item["kind"], "text": item["text"],
            "source": copy.deepcopy(item["source"]),
        })

    def ait011(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["id"] = "CLM-0000000000000000"

    def ait012(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["source_bindings"][0]["source_span_sha256"] = "0" * 64

    def ait013(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["source_bindings"][0]["source_file_sha256"] = "0" * 64

    def ait014(value: dict[str, Any]) -> None:
        item = material_for(value, "GAP-STR-009")
        discovery = copy.deepcopy(item["discovery_source_binding"])
        discovery["primary_for_claim"] = True
        item["source_bindings"] = [discovery]

    def ait015(value: dict[str, Any]) -> None:
        item = material_for(value, "GAP-NOT-002")
        host_only = next(copy.deepcopy(source) for source in item["source_bindings"]
                         if source["file"] == "host/notifications.mdx")
        host_only["primary_for_claim"] = True
        item["source_bindings"] = [host_only]

    def ait016(value: dict[str, Any]) -> None:
        source_id = "AMB-HDL-001"
        clone = copy.deepcopy(material_for(value, "GAP-HOV-001"))
        clone["source_record_id"] = source_id
        clone["id"] = material_claim_id(source_id)
        value["claims"].append(clone)

    def ait017(value: dict[str, Any]) -> None:
        item = disposition_for(value, "AMB-ERR-001")
        item["canonical_target_refs"] = item["canonical_target_refs"][:1]

    def ait018(value: dict[str, Any]) -> None:
        item = disposition_for(value, "AMB-PRICE-001")
        item["equivalent_legacy_claim_ids"] = []
        item["equivalent_legacy_occurrence_ids"] = []

    def ait019(value: dict[str, Any]) -> None:
        value["reconciliation"]["raw_gap_integration"]["defect_flags"].pop()

    def ait020(value: dict[str, Any]) -> None:
        semantic = material_for(value, "GAP-HOV-001")["semantic_assessment"]
        semantic.update({"status": "PASS", "score": 2, "rationale": "forged", "evidence_refs": ["forged"]})

    def ait021(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["status"] = "PASS"

    def ait022(value: dict[str, Any]) -> None:
        requirement_for(value, "GAP-HOV-002")["attempt_ids"] = ["ATT-forged"]

    def ait023(value: dict[str, Any]) -> None:
        proc = copy.deepcopy(value["procedures"][0])
        proc["id"] = "ADV-E99"
        proc["branches"] = []
        value["procedures"].append(proc)

    def ait024(value: dict[str, Any]) -> None:
        value["reconciliation"]["raw_gap_integration"]["integration_method"]["forged_target"] = "192.0.2.10"

    def ait025(value: dict[str, Any]) -> None:
        for pin_root in (
            value["reconciliation"]["raw_gap_integration"]["input_pins"],
            value["source_identity"]["raw_gap_integration_inputs"],
        ):
            pin_root["raw_gap_audit"]["target"]["docs_tree"] = "0" * 40
            pin_root["independent_reconciliation"]["target"]["docs_tree"] = "0" * 40

    def ait026(value: dict[str, Any]) -> None:
        for pin_root in (
            value["reconciliation"]["raw_gap_integration"]["input_pins"],
            value["source_identity"]["raw_gap_integration_inputs"],
        ):
            pin_root["raw_gap_audit"]["sha256"] = "0" * 64

    def ait028(value: dict[str, Any]) -> None:
        value["reconciliation"]["unique_items_by_kind"]["command"] = 177

    def ait029(value: dict[str, Any]) -> None:
        value["reconciliation"]["semantic_assessment_records"] = 633

    def ait030(value: dict[str, Any]) -> None:
        material_for(value, "GAP-HOV-001")["claim_limit"] += " forged"

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("AIT-001", ait001), ("AIT-002", ait002), ("AIT-003", ait003),
        ("AIT-004", ait004), ("AIT-005", ait005), ("AIT-006", ait006),
        ("AIT-007", ait007), ("AIT-008", ait008), ("AIT-009", ait009),
        ("AIT-010", ait010), ("AIT-011", ait011), ("AIT-012", ait012),
        ("AIT-013", ait013), ("AIT-014", ait014), ("AIT-015", ait015),
        ("AIT-016", ait016), ("AIT-017", ait017), ("AIT-018", ait018),
        ("AIT-019", ait019), ("AIT-020", ait020), ("AIT-021", ait021),
        ("AIT-022", ait022), ("AIT-023", ait023), ("AIT-024", ait024),
        ("AIT-025", ait025), ("AIT-026", ait026),
        ("AIT-028", ait028), ("AIT-029", ait029), ("AIT-030", ait030),
    ]
    results: list[dict[str, str]] = []
    for test_id, mutation in mutations:
        value = copy.deepcopy(candidate)
        mutation(value)
        if test_id != "AIT-030":
            refresh_plan_identity(value)
        try:
            validate_candidate(value, base, base_bytes)
        except (IntegrationError, KeyError, TypeError, ValueError) as exc:
            results.append({"id": test_id, "result": "PASS_REJECTED", "observation": str(exc)[:240]})
        else:
            raise IntegrationError(f"{test_id}: adversarial mutation was incorrectly accepted")
    # AIT-027 proves validation has no dependency on the two temporary inputs: this
    # call receives only the embedded candidate, canonical baseline, and repository.
    validate_candidate(candidate, base, base_bytes)
    results.append({
        "id": "AIT-027",
        "result": "PASS_ACCEPTED_NO_TEMP_INPUTS",
        "observation": "candidate validation used no raw-gap or reconciliation temporary input",
    })
    results.sort(key=lambda item: item["id"])
    require(len(results) == 30 and all(item["result"].startswith("PASS") for item in results),
            "adversarial suite did not pass all 30 design tests")
    return {"passed": 30, "failed": 0, "results": results}


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    require(path.resolve() == DEFAULT_OUTPUT.resolve(),
            f"isolated builder may write only {DEFAULT_OUTPUT}")
    data = canonical_json(value, pretty=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def load_canonical() -> tuple[dict[str, Any], bytes]:
    baseline, data = load_json_bytes(CANONICAL_PATH)
    require(sha256_bytes(data) == EXPECTED_CANONICAL_SHA256,
            "canonical baseline changed; abort and restart from an explicitly reviewed snapshot")
    return baseline, data


def build_from_pinned_inputs() -> tuple[dict[str, Any], dict[str, Any], bytes]:
    baseline, baseline_bytes = load_canonical()
    design, design_bytes = load_json_bytes(DESIGN_PATH)
    raw, raw_bytes = load_json_bytes(RAW_PATH)
    reconcile, reconcile_bytes = load_json_bytes(RECONCILE_PATH)
    preflight_inputs(
        baseline, baseline_bytes, design, design_bytes,
        raw, raw_bytes, reconcile, reconcile_bytes,
    )
    candidate = build_candidate(baseline, baseline_bytes, design, raw, reconcile)
    return candidate, baseline, baseline_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"candidate output (must be {DEFAULT_OUTPUT})")
    parser.add_argument("--check", type=Path,
                        help="validate an existing candidate without temporary reconciliation inputs")
    parser.add_argument("--self-test", action="store_true",
                        help="run the 30 design adversarial checks after validation")
    args = parser.parse_args(argv)
    try:
        baseline, baseline_bytes = load_canonical()
        if args.check:
            candidate, _ = load_json_bytes(args.check)
        else:
            candidate, baseline, baseline_bytes = build_from_pinned_inputs()
        summary = validate_candidate(candidate, baseline, baseline_bytes)
        if args.self_test:
            summary["adversarial_tests"] = run_adversarial_tests(candidate, baseline, baseline_bytes)
        if not args.check:
            write_atomic(args.output, candidate)
            summary["output"] = str(args.output)
            summary["output_sha256"] = sha256_bytes(canonical_json(candidate, pretty=True))
        else:
            summary["checked"] = str(args.check)
            summary["checked_sha256"] = sha256_path(args.check)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except (IntegrationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
