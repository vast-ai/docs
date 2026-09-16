#!/usr/bin/env python3
"""Assemble and validate the Host Docs Procedure Baseline P1.

The three partition files are temporary human-review inputs. The assembled JSON is the
single canonical baseline. ``--check`` validates that canonical file directly and does
not require the temporary partitions.

This script performs no documented Host procedure, network request, credentialed action,
or live test. It reads repository sources and frozen inventory records only.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ALLOWED_STATUSES = {
    "UNVALIDATED",
    "PASS",
    "FAIL",
    "BLOCKED",
    "NOT_APPLICABLE",
    "STALE",
}
ALLOWED_AUTHORITY_STATES = {
    "CONFIRMED",
    "PENDING_OWNER",
    "ADVISORY",
    "NOT_IDENTIFIED",
    "CONTRADICTED",
}
ALLOWED_BASELINE_STATES = {"DRAFT_NOT_FROZEN", "FROZEN_P1"}
ALLOWED_FREEZE_STATES = {"NOT_FROZEN", "FROZEN"}
ALLOWED_BRANCH_MODEL_STATES = {
    "LINEAR_SINGLE_BRANCH",
    "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED",
    "SEQUENCE",
    "ALL_OF",
    "ONE_OF",
    "CONDITIONAL",
    "MIXED_TYPED_GRAPH",
}
ALLOWED_ALIGNMENT_DECISIONS = {
    "APPROVED_SHARED_FRAGMENT",
    "APPROVED_CROSS_SECTION_ROLE",
    "CORRECTED_TO_EXACT",
}
ALLOWED_HEADING_DECISIONS = {
    "APPROVED_EQUIVALENT_HEADING",
    "CORRECTED_TO_EXACT",
}
ALLOWED_BRANCH_REVIEW_DECISIONS = {
    "APPROVED_BRANCH_MODEL",
    "CORRECTED_AND_APPROVED",
}
ALLOWED_BRANCH_GROUP_TYPES = {
    "ONE_OF",
    "ALL_OF",
    "CONDITIONAL",
    "CONDITIONAL_ALL_APPLICABLE",
    "CONDITIONAL_ONE_OR_MORE",
    "OPTIONAL_ONE_OF",
    "FAILURE_ONLY",
    "ONE_OF_WITH_FALLBACK",
    "OUTCOME",
}
ALLOWED_BRANCH_EDGE_RELATIONS = {"BEFORE", "ON_FAILURE_RETRY", "HANDOFF"}
EXPECTED_UNIQUE_BY_KIND = {
    "command": 176,
    "behavior-claim": 203,
    "error": 77,
    "threshold": 18,
}
EXPECTED_OCCURRENCES_BY_KIND = {
    "command": 203,
    "behavior-claim": 204,
    "error": 104,
    "threshold": 18,
}
EXPECTED_OCCURRENCES_BY_SOURCE = {
    "authored": 418,
    "generated-self-test": 69,
    "generated-cli-sdk": 42,
}
ALLOWED_PRIMARY_TREATMENTS = {
    "required-step",
    "prerequisite",
    "checkpoint",
    "cleanup",
    "branch",
    "template",
    "config",
    "output-error",
    "formula-example",
    "generated-reference",
    "duplicate-shared",
    "non-executable-claim",
}
IMPORT_RE = re.compile(
    r"^\s*import\s+\w+\s+from\s+['\"](?P<path>/snippets/[^'\"]+)['\"]\s*;?",
    re.MULTILINE,
)
TITLE_RE = re.compile(r"^title:\s*[\"']?(.*?)[\"']?\s*$", re.MULTILINE)
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
HEX64_RE = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{64}(?![0-9A-Fa-f])")
IPV6_CANDIDATE_RE = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])"
)
TARGET_COORDINATE_RE = re.compile(
    r"\b(?:machine|offer|instance|account|host|wan|ssh|target)[ _-]?(?:id|ip|address)?\s*[:=#]\s*[0-9]{3,}\b",
    re.IGNORECASE,
)
PAGE_INPUT_FIELDS = {
    "id",
    "route",
    "file",
    "source_kind",
    "disposition",
    "goals",
    "imports",
    "procedure_ids",
    "page_claim_ids",
    "status",
    "_partition",
}
PROCEDURE_INPUT_FIELDS = {
    "id",
    "page_id",
    "unit_type",
    "title",
    "goal",
    "vv_kind",
    "authority_state",
    "status",
    "prerequisites",
    "representative_context",
    "access_classes",
    "safety_constraints",
    "expected_final_observables",
    "failure_behavior",
    "limitations",
    "cleanup",
    "branches",
    "_partition",
}
BRANCH_INPUT_FIELDS = {"id", "condition", "status", "steps"}
STEP_INPUT_FIELDS = {
    "id",
    "role",
    "required",
    "status",
    "source_sections",
    "source_lines",
    "instruction_summary",
    "dependencies",
    "expected_observables",
    "failure_behavior",
}

# The first-pass partitions used compact composite labels for fourteen source
# ranges.  Those labels were useful notes, but they are not literal headings and
# therefore cannot satisfy the freeze-time source-context contract.  Normalize
# only these reviewed records, and fail closed if either the step ID or its
# expected first-pass value drifts.
STEP_SOURCE_SECTION_CORRECTIONS: dict[
    str, tuple[tuple[str, ...], tuple[str, ...]]
] = {
    "API-P01-workflows-s01": (
        ("Common Host Workflows / Day-To-Day Host Usage",),
        ("Common Host Workflows", "Day-To-Day Host Usage"),
    ),
    "COM-E01-join-s01": (
        ("Introduction / Joining the host Discord channels",),
        ("Introduction", "Joining the host Discord channels"),
    ),
    "FAQ-C01-routes-s01": (
        ("Introduction through Support Boundary",),
        (
            "Introduction",
            "Getting Started",
            "Install And Machine Health",
            "Network, Self-Test, And Verification",
            "Pricing, Payouts, And Operations",
            "Support Boundary",
        ),
    ),
    "GLO-C01-terms-s01": (
        ("Auto Sort through Verification / verified",),
        (
            "Auto Sort",
            "CGNAT",
            "Datacenter status / Secure Cloud",
            "Deverified",
            "Direct ports (`direct_port_count`)",
            "DLPerf",
            "DPH",
            "Instance",
            "Interruptible rental",
            "kaalia",
            "Machines tab",
            "Min GPU / `min_chunk`",
            "NAT hairpinning",
            "Offer",
            "Offer end date / rental end date",
            "On-demand rental",
            "Reliability",
            "Rental contract",
            "Reserved rental",
            "Self-test",
            "Unlist vs. delete",
            "Verification / verified",
        ),
    ),
    "GLO-C01-storage-s01": (
        ("Volume offer / XFS prjquota",),
        ("Volume offer", "XFS `prjquota`"),
    ),
    "MET-E01-dashboard-s01": (
        ("Access / Dashboard Views",),
        ("Access", "Dashboard Views"),
    ),
    "OPT-C01-price-bid-s01": (
        ("Price / Interruptible Minimum Bid",),
        ("Price", "Interruptible Minimum Bid"),
    ),
    "OPT-C01-sustain-s01": (
        ("Keep The Listing Competitive / Quick Reference",),
        ("Keep The Listing Competitive", "Quick Reference"),
    ),
    "PRICE-C01-main-s02": (
        ("Listing Controls / Starting Workflow",),
        ("Listing Controls", "Starting Workflow"),
    ),
    "SRCH-E01-direct-s01": (
        ("Introduction / Check the machine directly",),
        ("Introduction", "Check the machine directly"),
    ),
    "ST-E01-normal-s05": (
        ("What Self-Test Checks / Run The Test",),
        ("What Self-Test Checks", "Run The Test"),
    ),
    "STR-C02-preflight-s01": (
        ("Preflight Checks / Direct Ports And Port Mapping / Bandwidth Formula",),
        ("Preflight Checks", "Direct Ports And Port Mapping", "Bandwidth Formula"),
    ),
    "VER-C01-model-s01": (
        ("How Verification Works / Main Factors",),
        ("How Verification Works", "Main Factors"),
    ),
    "VER-C01-timing-support-s01": (
        ("How Long Can Verification Take? / Can Support Verify My Machine?",),
        ("How Long Can Verification Take?", "Can Support Verify My Machine?"),
    ),
}
MAPPING_INPUT_FIELDS = {
    "legacy_item_id",
    "location_index",
    "file",
    "section",
    "line_start",
    "line_end",
    "primary_treatment",
    "page_id",
    "procedure_id",
    "branch_id",
    "step_id",
    "rationale",
    "status",
    "occurrence_id",
    "claim_id",
    "legacy_kind",
    "legacy_text",
    "_partition",
}
UNCERTAINTY_INPUT_FIELDS = {
    "id",
    "scope",
    "question",
    "description",
    "impact",
    "status",
}
BASELINE_IDENTITY_FIELDS = (
    "schema_version",
    "record_type",
    "state",
    "operating_mode",
    "source_identity",
    "scope",
    "authority_sources",
    "pages",
    "procedures",
    "supporting_routes",
    "fragments",
    "support_contracts",
    "claims",
    "legacy_crosswalk",
    "uncertainties",
    "reconciliation",
)
PLAN_MUTABLE_KEYS = {
    "status",
    "attempt_ids",
    "issue_ids",
    "correction_ids",
    "retest_ids",
    "evidence_refs",
    "semantic_assessment",
    "approval_state",
    "gate_evaluation",
}
BASELINE_TOP_LEVEL_FIELDS = {
    "schema_version",
    "record_type",
    "baseline_id",
    "plan_baseline_sha256",
    "state",
    "operating_mode",
    "created_at",
    "source_identity",
    "scope",
    "status_vocabulary",
    "authority_state_vocabulary",
    "authority_sources",
    "pages",
    "procedures",
    "supporting_routes",
    "fragments",
    "support_contracts",
    "claims",
    "legacy_crosswalk",
    "uncertainties",
    "reconciliation",
    "freeze",
    "execution_readiness",
    "completion_and_acceptance",
}
FORBIDDEN_RESTRICTED_KEYS = {
    "api_key",
    "client_api_key",
    "host_api_key",
    "secret",
    "password",
    "token",
    "private_key",
    "raw_target",
    "ssh_target",
    "host_ip",
    "wan_ip",
    "machine_id",
    "offer_id",
    "instance_id",
    "machine_identifier",
    "offer_identifier",
    "instance_identifier",
    "account_identifier",
    "target_identifier",
}

PAGE_OUTPUT_FIELDS = {
    "id", "partition_page_id", "partition", "route", "navigation_group",
    "source_file", "source_sha256", "title", "intended_host_goals", "source_kind",
    "authorship", "disposition", "disposition_source_label", "imports",
    "actionable_sections", "procedure_ids", "claim_ids", "authority_refs",
    "rendered_context", "status",
}
PROCEDURE_OUTPUT_FIELDS = {
    "id", "page_id", "unit_type", "title", "goal", "vv_kind", "authority_state",
    "prerequisites", "representative_context", "access_classes", "safety_constraints",
    "expected_final_observables", "failure_behavior", "limitations", "cleanup",
    "branches", "authority_assertion", "authority_refs", "test_basis",
    "authorized_environment", "evidence_plan", "evidence_sensitivity",
    "public_redaction_rules", "claim_ids", "attempt_ids", "issue_ids",
    "correction_ids", "retest_ids", "status", "branch_execution_model",
    "source_context",
}
BRANCH_OUTPUT_FIELDS = {
    "id", "condition", "status", "steps", "access_override", "execution_gate",
}
STEP_OUTPUT_FIELDS = {
    "id", "role", "required", "status", "source_sections", "source_lines",
    "instruction_summary", "dependencies", "expected_observables", "failure_behavior",
    "claim_ids", "executable_template", "parameters", "cleanup_required",
    "source_context_validation", "source_carriers", "execution_form_state",
}
CLAIM_OUTPUT_FIELDS = {
    "id", "occurrence_id", "legacy_item_id", "legacy_location_index", "kind", "text",
    "source", "page_id", "procedure_id", "branch_id", "step_id",
    "supporting_route_id", "fragment_id", "primary_treatment", "source_alignment",
    "source_alignment_disposition", "raw_context", "rendered_context_refs",
    "authority_refs", "authority_state", "claim_limit", "test_basis",
    "expected_observables", "planned_method", "status", "attempt_ids", "issue_ids",
    "semantic_assessment",
}
CROSSWALK_OUTPUT_FIELDS = {
    "occurrence_id", "legacy_item_id", "legacy_location_index", "legacy_kind",
    "legacy_status", "source", "claim_id", "primary_treatment", "source_alignment",
    "source_alignment_disposition", "page_id", "procedure_id", "branch_id", "step_id",
    "supporting_route_id", "fragment_id", "rendered_context_refs", "rationale", "status",
}
SUPPORTING_OUTPUT_FIELDS = {
    "id", "route", "title", "kind", "source_file", "source_sha256", "fragment_id",
    "parent_page_id", "generator_contract", "support_contract_id", "claim_ids", "status",
}
FRAGMENT_OUTPUT_FIELDS = {
    "id", "kind", "source_file", "source_sha256", "generator_contract",
    "rendered_route_ids", "claim_ids", "status",
}
SUPPORT_CONTRACT_OUTPUT_FIELDS = {
    "id", "kind", "fragment_id", "rendered_context_id", "rendered_source_file",
    "source_file", "import_path", "expected_observables", "planned_method",
    "authority_refs", "status", "attempt_ids", "evidence_refs", "issue_ids",
}
AUTHORITY_OUTPUT_FIELDS = {
    "id", "type", "path", "sha256", "authority_state", "claim_limit", "evidence_status",
}
UNCERTAINTY_OUTPUT_FIELDS = {
    "id", "partition", "status", "scope", "question", "description", "impact",
}


class BaselineError(RuntimeError):
    """A deterministic assembly or validation error."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise BaselineError(f"{path}: expected a JSON object")
    return value


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def immutable_plan_value(value: Any) -> Any:
    """Remove append-only result state while retaining frozen plan definitions."""

    if isinstance(value, dict):
        return {
            key: immutable_plan_value(item)
            for key, item in value.items()
            if key not in PLAN_MUTABLE_KEYS
        }
    if isinstance(value, list):
        return [immutable_plan_value(item) for item in value]
    return value


def restricted_key_paths(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}"
            if str(key).lower() in FORBIDDEN_RESTRICTED_KEYS and item not in (
                None,
                "",
                False,
                [],
                {},
            ):
                findings.append(path)
            findings.extend(restricted_key_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(restricted_key_paths(item, f"{prefix}[{index}]"))
    return findings


def require_exact_keys(
    record: Any,
    required: set[str],
    allowed: set[str],
    context: str,
    errors: list[str],
) -> None:
    if not isinstance(record, dict):
        errors.append(f"{context} must be an object")
        return
    missing = sorted(required - set(record))
    unknown = sorted(set(record) - allowed)
    if missing:
        errors.append(f"{context} missing required fields: {missing}")
    if unknown:
        errors.append(f"{context} has unknown fields: {unknown}")


def require_nonempty_text_list(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(f"{context} must be a nonempty list of nonempty strings")


def exact_source_stripped_projection(baseline: dict[str, Any]) -> dict[str, Any]:
    """Remove only byte-for-byte documentation text before privacy scanning.

    Source text remains integrity checked through source hashes, claims, and source
    carriers. All human-authored planning/result fields remain in this projection.
    """

    projection = copy.deepcopy(baseline)
    for claim in projection.get("claims", []):
        claim["text"] = "[EXACT_SOURCE_TEXT_STRIPPED]"
    for procedure in projection.get("procedures", []):
        for branch in procedure.get("branches", []):
            for step in branch.get("steps", []):
                step["source_carriers"] = []
    return projection


def sensitive_value_paths(
    value: Any,
    prefix: str = "$",
    field_name: str | None = None,
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            findings.extend(
                sensitive_value_paths(item, f"{prefix}.{key}", str(key))
            )
        return findings
    if isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(
                sensitive_value_paths(item, f"{prefix}[{index}]", field_name)
            )
        return findings
    if not isinstance(value, str):
        return findings
    if PRIVATE_KEY_RE.search(value) or IPV4_RE.search(value):
        findings.append(prefix)
    for candidate in IPV6_CANDIDATE_RE.findall(value):
        try:
            ipaddress.IPv6Address(candidate)
        except ValueError:
            continue
        findings.append(prefix)
        break
    digest_field = bool(field_name and (
        field_name.endswith("sha256")
        or field_name.endswith("fingerprint")
        or field_name in {"content_fingerprint", "plan_baseline_sha256"}
    ))
    if HEX64_RE.search(value) and not digest_field:
        findings.append(prefix)
    if TARGET_COORDINATE_RE.search(value):
        findings.append(prefix)
    return sorted(set(findings))


def is_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def valid_review_disposition(value: Any, allowed_decisions: set[str]) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "decision",
        "reviewer",
        "role",
        "reviewed_at",
        "evidence_refs",
    }:
        return False
    return (
        value.get("decision") in allowed_decisions
        and isinstance(value.get("reviewer"), str)
        and bool(value["reviewer"].strip())
        and isinstance(value.get("role"), str)
        and bool(value["role"].strip())
        and is_utc_timestamp(value.get("reviewed_at"))
        and isinstance(value.get("evidence_refs"), list)
        and bool(value["evidence_refs"])
        and all(isinstance(ref, str) and ref.strip() for ref in value["evidence_refs"])
    )


def validate_output_shapes(baseline: dict[str, Any]) -> list[str]:
    """Validate the closed P1 schema; unknown nested fields fail closed."""

    errors: list[str] = []
    source_identity = baseline.get("source_identity")
    require_exact_keys(
        source_identity,
        {
            "repository", "branch", "docs_target_revision", "repository_head_at_assembly",
            "repository_tree_at_assembly", "target_binding", "tracked_tree_clean_before_assembly",
            "docs_json_sha256", "legacy_inventory", "vv_evidence_skill", "partition_inputs",
        },
        {
            "repository", "branch", "docs_target_revision", "repository_head_at_assembly",
            "repository_tree_at_assembly", "target_binding", "tracked_tree_clean_before_assembly",
            "docs_json_sha256", "legacy_inventory", "vv_evidence_skill", "partition_inputs",
        },
        "source_identity",
        errors,
    )
    require_exact_keys(
        (source_identity or {}).get("legacy_inventory"),
        {"path", "sha256", "source_revision", "content_fingerprint"},
        {"path", "sha256", "source_revision", "content_fingerprint"},
        "source_identity.legacy_inventory",
        errors,
    )
    require_exact_keys(
        (source_identity or {}).get("vv_evidence_skill"),
        {"upstream_revision", "skill_sha256"},
        {"upstream_revision", "skill_sha256"},
        "source_identity.vv_evidence_skill",
        errors,
    )
    for pin in (source_identity or {}).get("partition_inputs", []):
        require_exact_keys(
            pin,
            {
                "partition", "path_role", "sha256", "pages", "procedures",
                "occurrence_mappings", "declared_source_revision",
                "declared_content_fingerprint", "declared_source_file_hashes",
                "source_pin_state",
            },
            {
                "partition", "path_role", "sha256", "pages", "procedures",
                "occurrence_mappings", "declared_source_revision",
                "declared_content_fingerprint", "declared_source_file_hashes",
                "source_pin_state",
            },
            f"partition pin {pin.get('partition')}",
            errors,
        )
    require_exact_keys(
        baseline.get("scope"),
        {
            "primary_routes", "primary_authored", "primary_generated_self_test",
            "supporting_cli_routes", "supporting_sdk_routes", "imported_fragments",
            "support_layer_contracts", "legacy_unique_items", "legacy_occurrences",
            "command_behavior_semantic_occurrences", "all_claims_require_semantic_assessment",
        },
        {
            "primary_routes", "primary_authored", "primary_generated_self_test",
            "supporting_cli_routes", "supporting_sdk_routes", "imported_fragments",
            "support_layer_contracts", "legacy_unique_items", "legacy_occurrences",
            "command_behavior_semantic_occurrences", "all_claims_require_semantic_assessment",
        },
        "scope",
        errors,
    )
    require_exact_keys(
        baseline.get("reconciliation"),
        {
            "pages", "procedures", "branches", "steps", "claims", "support_contracts",
            "legacy_crosswalk_rows", "unique_items_by_kind", "occurrences_by_kind",
            "occurrences_by_source_type", "source_alignment_counts",
            "step_heading_review_required", "first_pass", "independent_second_pass",
            "same_agent_limit",
        },
        {
            "pages", "procedures", "branches", "steps", "claims", "support_contracts",
            "legacy_crosswalk_rows", "unique_items_by_kind", "occurrences_by_kind",
            "occurrences_by_source_type", "source_alignment_counts",
            "step_heading_review_required", "first_pass", "independent_second_pass",
            "same_agent_limit",
        },
        "reconciliation",
        errors,
    )
    freeze = baseline.get("freeze")
    require_exact_keys(
        freeze,
        {
            "state", "author", "reconciler", "frozen_at", "target_alias",
            "restricted_target_record_in_git", "blocking_checks", "change_record",
        },
        {
            "state", "author", "reconciler", "frozen_at", "target_alias",
            "restricted_target_record_in_git", "blocking_checks", "change_record",
        },
        "freeze",
        errors,
    )
    for change in (freeze or {}).get("change_record", []):
        require_exact_keys(
            change,
            {"event", "predecessor", "disposition", "history_preserved"},
            {"event", "predecessor", "disposition", "history_preserved"},
            "freeze.change_record entry",
            errors,
        )
    require_exact_keys(
        baseline.get("execution_readiness"),
        {
            "new_live_execution_allowed", "local_read_only_inventory_work_allowed",
            "credentials_from_chat_allowed", "required_live_gates",
        },
        {
            "new_live_execution_allowed", "local_read_only_inventory_work_allowed",
            "credentials_from_chat_allowed", "required_live_gates",
        },
        "execution_readiness",
        errors,
    )
    completion = baseline.get("completion_and_acceptance")
    require_exact_keys(
        completion,
        {"evidence_package_complete", "target_acceptance_candidate", "human_acceptance"},
        {"evidence_package_complete", "target_acceptance_candidate", "human_acceptance"},
        "completion_and_acceptance",
        errors,
    )
    require_exact_keys(
        (completion or {}).get("human_acceptance"),
        {"owner", "role", "decision", "date", "conditions", "closure_evidence"},
        {"owner", "role", "decision", "date", "conditions", "closure_evidence"},
        "completion_and_acceptance.human_acceptance",
        errors,
    )
    for page in baseline.get("pages", []):
        context = f"page {page.get('id')}"
        require_exact_keys(page, PAGE_OUTPUT_FIELDS, PAGE_OUTPUT_FIELDS, context, errors)
        require_exact_keys(
            page.get("rendered_context"),
            {"route", "status", "evidence_refs"},
            {"route", "status", "evidence_refs"},
            f"{context}.rendered_context",
            errors,
        )
    for procedure in baseline.get("procedures", []):
        context = f"procedure {procedure.get('id')}"
        require_exact_keys(
            procedure,
            PROCEDURE_OUTPUT_FIELDS,
            PROCEDURE_OUTPUT_FIELDS,
            context,
            errors,
        )
        for field in (
            "prerequisites",
            "access_classes",
            "safety_constraints",
            "expected_final_observables",
            "failure_behavior",
            "limitations",
            "cleanup",
            "public_redaction_rules",
        ):
            require_nonempty_text_list(procedure.get(field), f"{context}.{field}", errors)
        if not isinstance(procedure.get("goal"), str) or not procedure.get("goal", "").strip():
            errors.append(f"{context}.goal must be nonempty")
        require_exact_keys(
            procedure.get("test_basis"),
            {"goal", "vv_kind", "claim_boundary"},
            {"goal", "vv_kind", "claim_boundary"},
            f"{context}.test_basis",
            errors,
        )
        require_exact_keys(
            procedure.get("authorized_environment"),
            {"access_classes", "approval_state", "target_alias"},
            {"access_classes", "approval_state", "target_alias"},
            f"{context}.authorized_environment",
            errors,
        )
        require_exact_keys(
            procedure.get("evidence_plan"),
            {"planned_method", "required_observations", "evidence_refs", "attempt_ids"},
            {"planned_method", "required_observations", "evidence_refs", "attempt_ids"},
            f"{context}.evidence_plan",
            errors,
        )
        require_exact_keys(
            procedure.get("source_context"),
            {"file", "headings", "line_start", "line_end", "rendered_route", "rendered_status"},
            {"file", "headings", "line_start", "line_end", "rendered_route", "rendered_status"},
            f"{context}.source_context",
            errors,
        )
        require_exact_keys(
            procedure.get("branch_execution_model"),
            {"state", "source_order", "ordered_edges", "alternative_groups", "pass_rule", "reconciler"},
            {"state", "source_order", "ordered_edges", "alternative_groups", "pass_rule", "reconciler"},
            f"{context}.branch_execution_model",
            errors,
        )
        for branch in procedure.get("branches", []):
            branch_context = f"branch {branch.get('id')}"
            require_exact_keys(
                branch, BRANCH_OUTPUT_FIELDS, BRANCH_OUTPUT_FIELDS, branch_context, errors
            )
            require_exact_keys(
                branch.get("execution_gate"),
                {"access_requirements", "safety_requirements", "unmet_gate_behavior", "gate_evaluation"},
                {"access_requirements", "safety_requirements", "unmet_gate_behavior", "gate_evaluation"},
                f"{branch_context}.execution_gate",
                errors,
            )
            require_exact_keys(
                branch.get("execution_gate", {}).get("gate_evaluation"),
                {"status", "blocker_class", "reason", "claim_impact", "attempt_id"},
                {"status", "blocker_class", "reason", "claim_impact", "attempt_id"},
                f"{branch_context}.gate_evaluation",
                errors,
            )
            for step in branch.get("steps", []):
                step_context = f"step {step.get('id')}"
                require_exact_keys(
                    step, STEP_OUTPUT_FIELDS, STEP_OUTPUT_FIELDS, step_context, errors
                )
                if not isinstance(step.get("instruction_summary"), str) or not step.get(
                    "instruction_summary", ""
                ).strip():
                    errors.append(f"{step_context}.instruction_summary must be nonempty")
                require_nonempty_text_list(
                    step.get("expected_observables"),
                    f"{step_context}.expected_observables",
                    errors,
                )
                require_nonempty_text_list(
                    step.get("failure_behavior"),
                    f"{step_context}.failure_behavior",
                    errors,
                )
                for span in step.get("source_lines", []):
                    require_exact_keys(
                        span,
                        {"start", "end"},
                        {"start", "end"},
                        f"{step_context}.source_span",
                        errors,
                    )
                require_exact_keys(
                    step.get("source_context_validation"),
                    {
                        "source_sha256", "span_bounds", "invalid_spans", "heading_match",
                        "unmatched_headings", "span_heading_matches", "reconciler_disposition",
                    },
                    {
                        "source_sha256", "span_bounds", "invalid_spans", "heading_match",
                        "unmatched_headings", "span_heading_matches", "reconciler_disposition",
                    },
                    f"{step_context}.source_context_validation",
                    errors,
                )
                for match in step.get("source_context_validation", {}).get(
                    "span_heading_matches", []
                ):
                    require_exact_keys(
                        match,
                        {"start", "end", "overlapping_headings"},
                        {"start", "end", "overlapping_headings"},
                        f"{step_context}.span_heading_match",
                        errors,
                    )
                for carrier in step.get("source_carriers", []):
                    require_exact_keys(
                        carrier,
                        {"claim_id", "kind", "text", "source"},
                        {"claim_id", "kind", "text", "source"},
                        f"{step_context}.source_carrier",
                        errors,
                    )
                    require_exact_keys(
                        carrier.get("source"),
                        {"file", "section", "line_start", "line_end", "source_type", "text_sha256"},
                        {"file", "section", "line_start", "line_end", "source_type", "text_sha256"},
                        f"{step_context}.source_carrier.source",
                        errors,
                    )
    for claim in baseline.get("claims", []):
        context = f"claim {claim.get('id')}"
        require_exact_keys(claim, CLAIM_OUTPUT_FIELDS, CLAIM_OUTPUT_FIELDS, context, errors)
        require_exact_keys(
            claim.get("source"),
            {"file", "section", "line_start", "line_end", "source_type", "text_sha256"},
            {"file", "section", "line_start", "line_end", "source_type", "text_sha256"},
            f"{context}.source",
            errors,
        )
        require_exact_keys(
            claim.get("raw_context"),
            {"section", "source_span"},
            {"section", "source_span"},
            f"{context}.raw_context",
            errors,
        )
        require_exact_keys(
            claim.get("semantic_assessment"),
            {"required", "status", "score", "rationale", "finding_class", "evidence_refs", "correction_id", "retest_id"},
            {"required", "status", "score", "rationale", "finding_class", "evidence_refs", "correction_id", "retest_id"},
            f"{context}.semantic_assessment",
            errors,
        )
        for rendered in claim.get("rendered_context_refs", []):
            require_exact_keys(
                rendered,
                {"route", "status"},
                {"route", "status"},
                f"{context}.rendered_context",
                errors,
            )
    for row in baseline.get("legacy_crosswalk", []):
        require_exact_keys(
            row,
            CROSSWALK_OUTPUT_FIELDS,
            CROSSWALK_OUTPUT_FIELDS,
            f"crosswalk {row.get('occurrence_id')}",
            errors,
        )
    for route in baseline.get("supporting_routes", []):
        context = f"supporting route {route.get('id')}"
        require_exact_keys(
            route, SUPPORTING_OUTPUT_FIELDS, SUPPORTING_OUTPUT_FIELDS, context, errors
        )
        require_exact_keys(
            route.get("generator_contract"),
            {"state", "planned_method"},
            {"state", "planned_method", "introduction_commit"},
            f"{context}.generator_contract",
            errors,
        )
    for fragment in baseline.get("fragments", []):
        context = f"fragment {fragment.get('id')}"
        require_exact_keys(fragment, FRAGMENT_OUTPUT_FIELDS, FRAGMENT_OUTPUT_FIELDS, context, errors)
        require_exact_keys(
            fragment.get("generator_contract"),
            {"state", "planned_method"},
            {"state", "planned_method"},
            f"{context}.generator_contract",
            errors,
        )
    for contract in baseline.get("support_contracts", []):
        require_exact_keys(
            contract,
            SUPPORT_CONTRACT_OUTPUT_FIELDS,
            SUPPORT_CONTRACT_OUTPUT_FIELDS,
            f"support contract {contract.get('id')}",
            errors,
        )
    for authority in baseline.get("authority_sources", []):
        require_exact_keys(
            authority,
            AUTHORITY_OUTPUT_FIELDS - {"evidence_status"},
            AUTHORITY_OUTPUT_FIELDS,
            f"authority source {authority.get('id')}",
            errors,
        )
    for uncertainty in baseline.get("uncertainties", []):
        require_exact_keys(
            uncertainty,
            {"id", "partition", "status", "scope"},
            UNCERTAINTY_OUTPUT_FIELDS,
            f"uncertainty {uncertainty.get('id')}",
            errors,
        )
        if not uncertainty.get("question") and not uncertainty.get("description"):
            errors.append(
                f"uncertainty {uncertainty.get('id')} lacks question or description"
            )
    return errors


def plan_identity_payload(baseline: dict[str, Any]) -> dict[str, Any]:
    return immutable_plan_value(
        {key: baseline[key] for key in BASELINE_IDENTITY_FIELDS}
    )


def repo_file(repo: Path, raw_path: str, allowed_prefixes: tuple[str, ...]) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise BaselineError(f"repository source path escapes allowed scope: {raw_path!r}")
    normalized = candidate.as_posix()
    if not normalized.endswith(".mdx") or not normalized.startswith(allowed_prefixes):
        raise BaselineError(f"repository source path is not allowlisted: {raw_path!r}")
    resolved_repo = repo.resolve()
    resolved = (repo / candidate).resolve()
    if resolved_repo not in resolved.parents:
        raise BaselineError(f"repository source path escapes repository: {raw_path!r}")
    return resolved


def reject_unknown_fields(record: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise BaselineError(f"{context}: unknown input fields {unknown}")


def reject_partition_sensitive_values(value: Any, context: str) -> None:
    """Fail closed on raw coordinates/key material in human-authored partition prose.

    Exact source carriers are added later from the frozen inventory and are not passed
    through this check, so documentation examples remain intact.
    """

    serialized = json.dumps(value, ensure_ascii=False)
    if IPV4_RE.search(serialized):
        raise BaselineError(f"{context}: partition prose contains a raw IPv4 address")
    if PRIVATE_KEY_RE.search(serialized):
        raise BaselineError(f"{context}: partition prose contains private-key material")


def without_exact_source_carriers(value: Any) -> Any:
    """Return the non-source evidence projection used by the privacy guard.

    ``source_carriers`` are reloaded byte-for-byte from the frozen documentation
    inventory. They may contain generic documented coordinates such as ``0.0.0.0``;
    those are source evidence, not human-authored target metadata.
    """

    if isinstance(value, dict):
        return {
            key: without_exact_source_carriers(item)
            for key, item in value.items()
            if key != "source_carriers"
        }
    if isinstance(value, list):
        return [without_exact_source_carriers(item) for item in value]
    return value


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_blob(repo: Path, revision: str, relative_path: str) -> bytes:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise BaselineError(f"Git object path escapes repository: {relative_path!r}")
    result = subprocess.run(
        ["git", "show", f"{revision}:{candidate.as_posix()}"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return result.stdout


def git_blob_sha256(repo: Path, revision: str, relative_path: str) -> str:
    return hashlib.sha256(git_blob(repo, revision, relative_path)).hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def canonical_page_id(route: str) -> str:
    return "PAGE-" + route.strip("/").replace("/", "-")


def supporting_route_id(route: str) -> str:
    return "ROUTE-" + route.strip("/").replace("/", "-")


def fragment_id(source_file: str) -> str:
    stem = source_file.removeprefix("snippets/").removesuffix(".mdx")
    return "FRAGMENT-" + stem.replace("/", "-")


def occurrence_id(item_id: str, location_index: int, location: dict[str, Any]) -> str:
    stable_tuple = "\0".join(
        [
            item_id,
            str(location_index),
            str(location.get("file", "")),
            str(location.get("section", "")),
        ]
    )
    return "OCC-" + sha256_text(stable_tuple)[:16]


def claim_id(item_id: str, location_index: int, location: dict[str, Any]) -> str:
    stable_tuple = "\0".join(
        [
            "host-docs-p1-claim-v1",
            item_id,
            str(location_index),
            str(location.get("file", "")),
            str(location.get("section", "")),
        ]
    )
    return "CLM-" + sha256_text(stable_tuple)[:16]


def title_for(path: Path) -> str:
    match = TITLE_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else path.stem.replace("-", " ").title()


def imports_for(path: Path) -> list[str]:
    return sorted({match.group("path").lstrip("/") for match in IMPORT_RE.finditer(
        path.read_text(encoding="utf-8")
    )})


def normalized_heading(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[`*_{}\[\]()]", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(value.split())


def declared_heading_components(value: str) -> list[str]:
    through_parts = re.split(r"\s+through\s+", value, maxsplit=1, flags=re.IGNORECASE)
    if len(through_parts) == 2:
        return [normalized_heading(part) for part in through_parts if normalized_heading(part)]
    return [
        normalized_heading(part)
        for part in value.split("/")
        if normalized_heading(part)
    ]


def source_context_validation(source_path: Path, step: dict[str, Any]) -> dict[str, Any]:
    lines = source_path.read_text(encoding="utf-8").splitlines()
    heading_records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading_records.append(
            {
                "line": line_number,
                "level": len(match.group(1)),
                "title": match.group(2),
                "normalized": normalized_heading(match.group(2)),
            }
        )
    for index, heading in enumerate(heading_records):
        end = len(lines)
        for later in heading_records[index + 1 :]:
            if int(later["level"]) <= int(heading["level"]):
                end = int(later["line"]) - 1
                break
        heading["end"] = end

    frontmatter_end = 0
    if lines and lines[0].strip() == "---":
        for line_number, line in enumerate(lines[1:], start=2):
            if line.strip() == "---":
                frontmatter_end = line_number
                break
    first_heading_line = int(heading_records[0]["line"]) if heading_records else len(lines) + 1
    introduction_start = frontmatter_end + 1 if frontmatter_end else 1
    if introduction_start < first_heading_line:
        heading_records.insert(
            0,
            {
                "line": introduction_start,
                "end": first_heading_line - 1,
                "level": 1,
                "title": "Introduction",
                "normalized": "introduction",
            },
        )
    invalid_spans: list[dict[str, Any]] = []
    for span in step.get("source_lines", []):
        start = span.get("start")
        end = span.get("end")
        if (
            not isinstance(start, int)
            or not isinstance(end, int)
            or start < 1
            or end < start
            or end > len(lines)
        ):
            invalid_spans.append(copy.deepcopy(span))
    span_heading_matches: list[dict[str, Any]] = []
    matched_components: set[str] = set()
    for span in step.get("source_lines", []):
        start = span.get("start")
        end = span.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        overlapping = [
            heading
            for heading in heading_records
            if int(heading["line"]) <= end and int(heading["end"]) >= start
        ]
        matched_components.update(str(heading["normalized"]) for heading in overlapping)
        span_heading_matches.append(
            {
                "start": start,
                "end": end,
                "overlapping_headings": [str(heading["title"]) for heading in overlapping],
            }
        )
    unmatched_headings: list[str] = []
    for section in step.get("source_sections", []):
        full_heading = normalized_heading(str(section))
        if not full_heading or full_heading not in matched_components:
            unmatched_headings.append(str(section))
    return {
        "source_sha256": sha256_path(source_path),
        "span_bounds": "PASS" if not invalid_spans else "FAIL",
        "invalid_spans": invalid_spans,
        "heading_match": "PASS" if not unmatched_headings else "REVIEW_REQUIRED",
        "unmatched_headings": unmatched_headings,
        "span_heading_matches": span_heading_matches,
        "reconciler_disposition": None,
    }


def computed_source_alignment(
    source: dict[str, Any],
    step: dict[str, Any] | None,
) -> str:
    if source.get("source_type") == "generated-cli-sdk":
        return "GENERATED_FRAGMENT_CONTEXT"
    if step is None:
        return "NON_STEP_TREATMENT"
    start = source.get("line_start")
    end = source.get("line_end")
    span_covers = isinstance(start, int) and isinstance(end, int) and any(
        isinstance(span.get("start"), int)
        and isinstance(span.get("end"), int)
        and int(span["start"]) <= start
        and int(span["end"]) >= end
        for span in step.get("source_lines", [])
    )
    section_matches = source.get("section") in step.get("source_sections", [])
    if span_covers and section_matches:
        return "EXACT_SECTION_AND_SPAN"
    if span_covers:
        return "SPAN_ONLY_REVIEW_REQUIRED"
    if section_matches:
        return "SECTION_ONLY_REVIEW_REQUIRED"
    return "CROSS_SECTION_REVIEW_REQUIRED"


def authority_state(raw: Any) -> str:
    text = str(raw or "").upper()
    if "CONTRADICT" in text:
        return "CONTRADICTED"
    if "ADVIS" in text:
        return "ADVISORY"
    if "PENDING" in text or "UNCONFIRMED" in text or "REQUIRED" in text:
        return "PENDING_OWNER"
    if "CONFIRMED" in text and "UNCONFIRMED" not in text:
        return "CONFIRMED"
    if text:
        # A source can be precisely identified while its runtime claim is still
        # unvalidated. The partition's original assertion remains visible separately.
        if "CANONICAL" in text or "SOURCE" in text or "DOCUMENTED" in text:
            return "PENDING_OWNER"
    return "NOT_IDENTIFIED"


def vv_kind(raw: Any) -> str:
    text = str(raw or "").lower()
    if "both" in text or ("verification" in text and "validation" in text):
        return "both"
    if "validation" in text:
        return "validation"
    return "verification"


def disposition(raw: Any, procedures: list[dict[str, Any]]) -> str:
    text = str(raw or "").lower()
    types = {str(proc.get("unit_type", "")).upper() for proc in procedures}
    if "generated" in text:
        return "generated-reference"
    if "parent" in text or "journey" in text or "orientation" in text:
        return "navigation/cross-page journey"
    if "policy" in text or "legal" in text:
        return "conceptual/policy"
    if "troubleshoot" in text:
        return "procedure-bearing"
    if "procedur" in text or types.intersection({"E", "T"}):
        return "procedure-bearing"
    if "concept" in text or "calculation" in text or types == {"C"}:
        return "conceptual/policy"
    if procedures:
        return "reference-only"
    return "no-actionable-instruction"


def host_navigation(docs_json: dict[str, Any]) -> tuple[list[str], list[str], list[str], dict[str, str]]:
    navigation = docs_json.get("navigation", {})
    tabs = navigation.get("tabs", [])
    host_tab = next((tab for tab in tabs if tab.get("tab") == "Host"), None)
    if not host_tab:
        raise BaselineError("docs.json: Host navigation tab not found")

    primary: list[str] = []
    cli_support: list[str] = []
    sdk_support: list[str] = []
    groups: dict[str, str] = {}
    for group in host_tab.get("groups", []):
        name = str(group.get("group", ""))
        pages = [str(page) for page in group.get("pages", [])]
        for route in pages:
            groups["/" + route] = name
        if name == "CLI":
            if "host/cli-api-sdk" not in pages:
                raise BaselineError("docs.json: CLI group does not contain host/cli-api-sdk")
            primary.append("/host/cli-api-sdk")
            cli_support.extend("/" + route for route in pages if route != "host/cli-api-sdk")
        elif name == "SDK":
            sdk_support.extend("/" + route for route in pages)
        else:
            primary.extend("/" + route for route in pages)
    return primary, cli_support, sdk_support, groups


def authority_refs_for(route: str) -> list[str]:
    refs = ["AUTH-REVIEW-TRACEABILITY"]
    if route in {
        "/host/supported-hardware",
        "/host/hardware-prep",
        "/host/account-hosting-agreement",
        "/host/account-security-for-hosts",
        "/host/installing-host-software",
        "/host/host-teams",
        "/host/machine-errors",
        "/host/network-ports",
        "/host/pricing-your-listing",
        "/host/market-metrics",
        "/host/optimization-guide",
        "/host/earning",
        "/host/payment",
        "/host/datacenter-status",
        "/host/guide-to-taxes",
    }:
        refs.append("AUTH-REVIEW-QUESTIONS")
    if route == "/host/self-test-reference":
        refs.append("AUTH-SELF-TEST-GENERATOR")
    if route == "/host/cli-api-sdk":
        refs.append("AUTH-CLI-REGISTRY-LEGACY")
    return refs


def evidence_plan(procedure: dict[str, Any]) -> dict[str, Any]:
    access = " ".join(str(item).lower() for item in procedure.get("access_classes", []))
    unit_type = str(procedure.get("unit_type", "")).upper()
    if unit_type == "P" or "delegated" in access:
        method = "Inspect cross-page order and require separately scoped child evidence."
    elif any(word in access for word in ("source", "conceptual", "legal", "policy", "formula")):
        method = "Inspect exact pinned source and obtain named owner confirmation where authority is pending."
    else:
        method = "Execute the applicable branch in documented order only after its access and safety gate is authorized."
    return {
        "planned_method": method,
        "required_observations": copy.deepcopy(procedure.get("expected_final_observables", [])),
        "evidence_refs": [],
        "attempt_ids": [],
    }


def normalize_partitions(
    repo: Path,
    partition_paths: list[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    raw_pages: list[dict[str, Any]] = []
    raw_procedures: list[dict[str, Any]] = []
    raw_mappings: list[dict[str, Any]] = []
    uncertainties: list[dict[str, Any]] = []
    partition_pins: list[dict[str, Any]] = []
    applied_source_section_corrections: set[str] = set()
    current_inventory = load_json(repo / "host-docs-verification-inventory.json")

    for path in partition_paths:
        partition = load_json(path)
        partition_name = str(
            partition.get("partition_id") or partition.get("partition") or path.stem
        )
        declared_revision = partition.get("source_revision")
        declared_fingerprint = partition.get("content_fingerprint")
        if declared_revision is not None and declared_revision != current_inventory.get("source_revision"):
            raise BaselineError(f"{partition_name}: declared source revision is stale")
        if declared_fingerprint is not None and declared_fingerprint != current_inventory.get("content_fingerprint"):
            raise BaselineError(f"{partition_name}: declared content fingerprint is stale")
        declared_file_hashes = partition.get("source_file_sha256") or {}
        if not isinstance(declared_file_hashes, dict):
            raise BaselineError(f"{partition_name}: source_file_sha256 must be an object")
        for source_file, declared_hash in declared_file_hashes.items():
            source_path = repo_file(repo, str(source_file), ("host/",))
            if not source_path.is_file() or sha256_path(source_path) != declared_hash:
                raise BaselineError(f"{partition_name}: declared source hash is stale for {source_file}")
        partition_pins.append(
            {
                "partition": partition_name,
                "path_role": "temporary-human-review-input",
                "sha256": sha256_path(path),
                "pages": len(partition.get("pages", [])),
                "procedures": len(partition.get("procedures", [])),
                "occurrence_mappings": len(partition.get("occurrence_mappings", [])),
                "declared_source_revision": declared_revision,
                "declared_content_fingerprint": declared_fingerprint,
                "declared_source_file_hashes": len(declared_file_hashes),
                "source_pin_state": (
                    "MATCHED"
                    if declared_revision is not None or declared_fingerprint is not None or declared_file_hashes
                    else "NOT_DECLARED_BASELINE_RECOMPUTED"
                ),
            }
        )
        for page in partition.get("pages", []):
            item = copy.deepcopy(page)
            item["_partition"] = partition_name
            reject_unknown_fields(item, PAGE_INPUT_FIELDS, f"{partition_name} page")
            reject_partition_sensitive_values(item, f"{partition_name} page")
            raw_pages.append(item)
        for procedure in partition.get("procedures", []):
            item = copy.deepcopy(procedure)
            item["_partition"] = partition_name
            reject_unknown_fields(
                item, PROCEDURE_INPUT_FIELDS, f"{partition_name} procedure"
            )
            for branch in item.get("branches", []):
                if "ordered_steps" in branch:
                    if "steps" in branch:
                        raise BaselineError(
                            f"{partition_name} procedure {item.get('id')} branch "
                            "declares both steps and ordered_steps"
                        )
                    branch["steps"] = branch.pop("ordered_steps")
                reject_unknown_fields(
                    branch,
                    BRANCH_INPUT_FIELDS,
                    f"{partition_name} procedure {item.get('id')} branch",
                )
                for step in branch.get("steps", []):
                    if isinstance(step.get("source_lines"), dict):
                        step["source_lines"] = [step["source_lines"]]
                    step_id = str(step.get("id", ""))
                    correction = STEP_SOURCE_SECTION_CORRECTIONS.get(step_id)
                    if correction is not None:
                        expected, replacement = correction
                        observed = tuple(str(value) for value in step.get("source_sections", []))
                        if observed != expected:
                            raise BaselineError(
                                f"{partition_name} step {step_id} source-section "
                                f"normalization precondition changed: {observed!r}"
                            )
                        if step_id in applied_source_section_corrections:
                            raise BaselineError(
                                f"duplicate source-section normalization target: {step_id}"
                            )
                        step["source_sections"] = list(replacement)
                        applied_source_section_corrections.add(step_id)
                    reject_unknown_fields(
                        step,
                        STEP_INPUT_FIELDS,
                        f"{partition_name} procedure {item.get('id')} step",
                    )
            reject_partition_sensitive_values(item, f"{partition_name} procedure")
            raw_procedures.append(item)
        for mapping in partition.get("occurrence_mappings", []):
            item = copy.deepcopy(mapping)
            item["_partition"] = partition_name
            reject_unknown_fields(item, MAPPING_INPUT_FIELDS, f"{partition_name} mapping")
            # Only the normalized treatment/rationale is copied. Legacy text and source
            # tuples are reloaded from the exact frozen inventory below.
            reject_partition_sensitive_values(
                {"rationale": item.get("rationale")}, f"{partition_name} mapping"
            )
            raw_mappings.append(item)
        for index, uncertainty in enumerate(partition.get("uncertainties", []), start=1):
            raw = copy.deepcopy(uncertainty)
            if "detail" in raw:
                if "description" in raw:
                    raise BaselineError(
                        f"{partition_name} uncertainty declares both detail and description"
                    )
                raw["description"] = raw.pop("detail")
            scoped_pages = raw.pop("pages", None)
            scoped_procedures = raw.pop("procedures", None)
            if scoped_pages is not None or scoped_procedures is not None:
                if "scope" in raw:
                    raise BaselineError(
                        f"{partition_name} uncertainty declares both scope and page/procedure scopes"
                    )
                raw["scope"] = {
                    "page_ids": copy.deepcopy(scoped_pages or []),
                    "procedure_ids": copy.deepcopy(scoped_procedures or []),
                }
            reject_unknown_fields(
                raw, UNCERTAINTY_INPUT_FIELDS, f"{partition_name} uncertainty"
            )
            reject_partition_sensitive_values(raw, f"{partition_name} uncertainty")
            raw_id = str(raw.pop("id", f"U-{index:03d}"))
            normalized_uncertainty = {
                key: copy.deepcopy(raw[key])
                for key in ("scope", "question", "description", "impact")
                if key in raw
            }
            uncertainties.append(
                {
                    "id": "UNC-" + re.sub(r"[^A-Za-z0-9]+", "-", partition_name).strip("-") + "-" + raw_id,
                    "partition": partition_name,
                    "status": "UNVALIDATED",
                    **normalized_uncertainty,
                }
            )

    missing_source_section_corrections = (
        set(STEP_SOURCE_SECTION_CORRECTIONS) - applied_source_section_corrections
    )
    if missing_source_section_corrections:
        raise BaselineError(
            "missing reviewed source-section normalization targets: "
            + ", ".join(sorted(missing_source_section_corrections))
        )

    page_id_map: dict[str, str] = {}
    pages: list[dict[str, Any]] = []
    procedures_by_old_page: dict[str, list[dict[str, Any]]] = {}
    for procedure in raw_procedures:
        procedures_by_old_page.setdefault(str(procedure.get("page_id")), []).append(procedure)

    for raw_page in raw_pages:
        route = str(raw_page.get("route", ""))
        if not route.startswith("/host/"):
            raise BaselineError(f"invalid primary page route: {route!r}")
        source_file = str(raw_page.get("file", route.lstrip("/") + ".mdx"))
        source_path = repo_file(repo, source_file, ("host/",))
        if not source_path.is_file():
            raise BaselineError(f"missing primary page source: {source_file}")
        old_id = str(raw_page.get("id"))
        new_id = canonical_page_id(route)
        if old_id in page_id_map:
            raise BaselineError(f"duplicate partition page ID: {old_id}")
        page_id_map[old_id] = new_id
        owned = procedures_by_old_page.get(old_id, [])
        page = {
            "id": new_id,
            "partition_page_id": old_id,
            "partition": raw_page.get("_partition"),
            "route": route,
            "navigation_group": None,
            "source_file": source_file,
            "source_sha256": sha256_path(source_path),
            "title": title_for(source_path),
            "intended_host_goals": copy.deepcopy(raw_page.get("goals", [])),
            "source_kind": raw_page.get("source_kind", "authored"),
            "authorship": (
                "generated"
                if "generated" in str(raw_page.get("source_kind", "authored")).lower()
                else "authored"
            ),
            "disposition": disposition(raw_page.get("disposition"), owned),
            "disposition_source_label": raw_page.get("disposition"),
            "imports": imports_for(source_path),
            "actionable_sections": sorted(
                {
                    section
                    for proc in owned
                    for branch in proc.get("branches", [])
                    for step in branch.get("steps", [])
                    for section in step.get("source_sections", [])
                }
            ),
            "procedure_ids": [str(proc.get("id")) for proc in owned],
            "claim_ids": [],
            "authority_refs": authority_refs_for(route),
            "rendered_context": {
                "route": route,
                "status": "UNVALIDATED",
                "evidence_refs": [],
            },
            "status": "UNVALIDATED",
        }
        pages.append(page)

    procedures: list[dict[str, Any]] = []
    for raw in raw_procedures:
        proc = {
            key: copy.deepcopy(raw[key])
            for key in PROCEDURE_INPUT_FIELDS - {"_partition"}
            if key in raw
        }
        old_page_id = str(proc.get("page_id"))
        if old_page_id not in page_id_map:
            raise BaselineError(f"procedure {proc.get('id')} references unknown page {old_page_id}")
        proc["page_id"] = page_id_map[old_page_id]
        proc["vv_kind"] = vv_kind(proc.get("vv_kind"))
        proc["authority_assertion"] = proc.get("authority_state")
        proc["authority_state"] = authority_state(proc.get("authority_state"))
        page_route = next(page["route"] for page in pages if page["id"] == proc["page_id"])
        proc["authority_refs"] = authority_refs_for(page_route)
        proc["test_basis"] = {
            "goal": proc.get("goal"),
            "vv_kind": proc["vv_kind"],
            "claim_boundary": copy.deepcopy(proc.get("limitations", [])),
        }
        proc["authorized_environment"] = {
            "access_classes": copy.deepcopy(proc.get("access_classes", [])),
            "approval_state": "NOT_AUTHORIZED_FOR_LIVE_EXECUTION",
            "target_alias": "HOST_VV_TARGET" if any(
                word in " ".join(str(item).lower() for item in proc.get("access_classes", []))
                for word in ("host", "wan", "paid", "client", "mutat", "destruct", "credential")
            ) else None,
        }
        proc["evidence_plan"] = evidence_plan(proc)
        access_text = " ".join(str(item).lower() for item in proc.get("access_classes", []))
        proc["evidence_sensitivity"] = (
            "restricted-or-sanitized"
            if any(word in access_text for word in ("secret", "credential", "log", "financial", "private", "paid"))
            else "public-sanitized"
        )
        proc["public_redaction_rules"] = [
            "Exclude credentials and unrestricted diagnostic output.",
            "Replace raw account, machine, offer, instance, network, and target identifiers with scoped aliases.",
        ]
        proc["claim_ids"] = []
        proc["attempt_ids"] = []
        proc["issue_ids"] = []
        proc["correction_ids"] = []
        proc["retest_ids"] = []
        proc["status"] = "UNVALIDATED"
        branch_ids_in_source_order = [
            str(branch.get("id")) for branch in proc.get("branches", [])
        ]
        proc["branch_execution_model"] = {
            "state": (
                "LINEAR_SINGLE_BRANCH"
                if len(branch_ids_in_source_order) == 1
                else "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED"
            ),
            "source_order": branch_ids_in_source_order,
            "ordered_edges": [],
            "alternative_groups": [],
            "pass_rule": (
                "All required steps and checkpoints in the single applicable branch must pass."
                if len(branch_ids_in_source_order) == 1
                else "No procedure PASS is allowed until an independent reconciler records which branches are ordered phases, alternatives, optional modifiers, or failure-only paths."
            ),
            "reconciler": None,
        }
        source_lines: list[int] = []
        source_sections: set[str] = set()
        procedure_source_file = next(
            page["source_file"] for page in pages if page["id"] == proc["page_id"]
        )
        procedure_source_path = repo_file(repo, procedure_source_file, ("host/",))
        for branch in proc.get("branches", []):
            branch["status"] = "UNVALIDATED"
            branch.setdefault("access_override", None)
            branch["execution_gate"] = {
                "access_requirements": copy.deepcopy(proc.get("access_classes", [])),
                "safety_requirements": copy.deepcopy(proc.get("safety_constraints", [])),
                "unmet_gate_behavior": "Create a NOT_EXECUTED attempt and mark only the affected branch/claims BLOCKED; continue independent safe work.",
                "gate_evaluation": {
                    "status": "UNVALIDATED",
                    "blocker_class": None,
                    "reason": None,
                    "claim_impact": [],
                    "attempt_id": None,
                },
            }
            for step in branch.get("steps", []):
                step["status"] = "UNVALIDATED"
                step.setdefault("claim_ids", [])
                step.setdefault("executable_template", None)
                step.setdefault("parameters", [])
                step.setdefault("cleanup_required", step.get("role") == "cleanup")
                step["source_context_validation"] = source_context_validation(
                    procedure_source_path, step
                )
                if step["source_context_validation"]["span_bounds"] != "PASS":
                    raise BaselineError(
                        f"step {step.get('id')} has an out-of-bounds source span"
                    )
                for section in step.get("source_sections", []):
                    source_sections.add(str(section))
                for span in step.get("source_lines", []):
                    if span.get("start") is not None:
                        source_lines.append(int(span["start"]))
                    if span.get("end") is not None:
                        source_lines.append(int(span["end"]))
        proc["source_context"] = {
            "file": procedure_source_file,
            "headings": sorted(source_sections),
            "line_start": min(source_lines) if source_lines else None,
            "line_end": max(source_lines) if source_lines else None,
            "rendered_route": page_route,
            "rendered_status": "UNVALIDATED",
        }
        procedures.append(proc)

    mappings: list[dict[str, Any]] = []
    for raw in raw_mappings:
        mapping = {
            key: copy.deepcopy(raw[key])
            for key in (
                "legacy_item_id",
                "location_index",
                "file",
                "section",
                "line_start",
                "line_end",
                "primary_treatment",
                "page_id",
                "procedure_id",
                "branch_id",
                "step_id",
                "rationale",
            )
            if key in raw
        }
        old_page_id = str(mapping.get("page_id"))
        if old_page_id not in page_id_map:
            raise BaselineError(
                f"mapping {mapping.get('legacy_item_id')}/{mapping.get('location_index')} references unknown page {old_page_id}"
            )
        mapping["page_id"] = page_id_map[old_page_id]
        mapping["status"] = "UNVALIDATED"
        mappings.append(mapping)

    pages.sort(key=lambda item: item["route"])
    procedures.sort(key=lambda item: item["id"])
    mappings.sort(key=lambda item: (item["legacy_item_id"], int(item["location_index"])))
    uncertainties.sort(key=lambda item: item["id"])
    return pages, procedures, mappings, uncertainties, partition_pins


def build_supporting_layers(
    repo: Path,
    cli_routes: list[str],
    sdk_routes: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    routes: list[dict[str, Any]] = []
    fragments: dict[str, dict[str, Any]] = {}
    contracts: list[dict[str, Any]] = []
    for route in [*cli_routes, *sdk_routes]:
        source_file = route.lstrip("/") + ".mdx"
        source_path = repo_file(repo, source_file, ("host/cli/", "host/sdk/"))
        imports = imports_for(source_path)
        if len(imports) != 1:
            raise BaselineError(f"{source_file}: expected exactly one snippet import, got {imports}")
        snippet = imports[0]
        snippet_path = repo_file(
            repo, snippet, ("snippets/host/cli/", "snippets/host/sdk/")
        )
        if not snippet_path.is_file():
            raise BaselineError(f"{source_file}: missing imported snippet {snippet}")
        route_id = supporting_route_id(route)
        frag_id = fragment_id(snippet)
        contract_id = "SUPPORT-CONTRACT-" + route.strip("/").replace("/", "-")
        routes.append(
            {
                "id": route_id,
                "route": route,
                "kind": "generated-cli-wrapper" if "/cli/" in route else "generated-sdk-wrapper",
                "source_file": source_file,
                "source_sha256": sha256_path(source_path),
                "title": title_for(source_path),
                "fragment_id": frag_id,
                "support_contract_id": contract_id,
                "parent_page_id": canonical_page_id("/host/cli-api-sdk"),
                "generator_contract": {
                    "state": "NO_CURRENT_LOCAL_GENERATOR_IDENTIFIED",
                    "introduction_commit": "5bbf124",
                    "planned_method": "Compare wrapper, snippet, current canonical CLI/SDK signature source, and rendered context.",
                },
                "claim_ids": [],
                "status": "UNVALIDATED",
            }
        )
        fragment = fragments.setdefault(
            frag_id,
            {
                "id": frag_id,
                "source_file": snippet,
                "source_sha256": sha256_path(snippet_path),
                "kind": "generated-cli-snippet" if "/cli/" in snippet else "generated-sdk-snippet",
                "rendered_route_ids": [],
                "claim_ids": [],
                "generator_contract": {
                    "state": "NO_CURRENT_LOCAL_GENERATOR_IDENTIFIED",
                    "planned_method": "Validate canonical source/signature and every rendered wrapper context.",
                },
                "status": "UNVALIDATED",
            },
        )
        fragment["rendered_route_ids"].append(route_id)
        contracts.append(
            {
                "id": contract_id,
                "kind": "wrapper-import-render-contract",
                "fragment_id": frag_id,
                "source_file": snippet,
                "rendered_context_id": route_id,
                "rendered_source_file": source_file,
                "import_path": "/" + snippet,
                "expected_observables": [
                    "The wrapper imports exactly the recorded snippet source.",
                    "The rendered page presents the source content in its intended CLI or SDK context.",
                    "The source/signature is current against its authoritative implementation target.",
                ],
                "planned_method": "Inspect the exact import edge, render the wrapper, and compare source/signature currentness.",
                "authority_refs": ["AUTH-CLI-REGISTRY-LEGACY"],
                "status": "UNVALIDATED",
                "attempt_ids": [],
                "evidence_refs": [],
                "issue_ids": [],
            }
        )

    notification_file = "snippets/notifications/channels.mdx"
    notification_path = repo_file(repo, notification_file, ("snippets/notifications/",))
    notification_id = fragment_id(notification_file)
    notification_page_file = "host/notifications.mdx"
    notification_page_path = repo_file(repo, notification_page_file, ("host/",))
    if notification_file not in imports_for(notification_page_path):
        raise BaselineError("Host Notifications does not import the recorded shared fragment")
    notification_contract_id = "SUPPORT-CONTRACT-host-notifications-channels"
    fragments[notification_id] = {
        "id": notification_id,
        "source_file": notification_file,
        "source_sha256": sha256_path(notification_path),
        "kind": "authored-shared-fragment",
        "rendered_route_ids": [canonical_page_id("/host/notifications")],
        "claim_ids": [],
        "generator_contract": {
            "state": "AUTHORED_SHARED_SOURCE",
            "planned_method": "Inspect the fragment once and validate its material rendered context on Host Notifications.",
        },
        "status": "UNVALIDATED",
    }
    contracts.append(
        {
            "id": notification_contract_id,
            "kind": "shared-fragment-render-contract",
            "fragment_id": notification_id,
            "source_file": notification_file,
            "rendered_context_id": canonical_page_id("/host/notifications"),
            "rendered_source_file": notification_page_file,
            "import_path": "/" + notification_file,
            "expected_observables": [
                "Host Notifications imports the exact shared channel fragment.",
                "The fragment renders coherently in the Host page context without changing its claim boundary.",
            ],
            "planned_method": "Inspect the exact import edge once at source and validate the rendered Host-page context.",
            "authority_refs": ["AUTH-REVIEW-TRACEABILITY"],
            "status": "UNVALIDATED",
            "attempt_ids": [],
            "evidence_refs": [],
            "issue_ids": [],
        }
    )
    routes.sort(key=lambda item: item["route"])
    result_fragments = sorted(fragments.values(), key=lambda item: item["source_file"])
    contracts.sort(key=lambda item: item["id"])
    return routes, result_fragments, contracts


def build_claims_and_crosswalk(
    inventory: dict[str, Any],
    pages: list[dict[str, Any]],
    procedures: list[dict[str, Any]],
    partition_mappings: list[dict[str, Any]],
    supporting_routes: list[dict[str, Any]],
    fragments: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    occurrence_lookup: dict[tuple[str, int], tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in inventory.get("items", []):
        for index, location in enumerate(item.get("locations", [])):
            key = (str(item["id"]), index)
            if key in occurrence_lookup:
                raise BaselineError(f"duplicate legacy occurrence key: {key}")
            occurrence_lookup[key] = (item, location)

    mappings: dict[tuple[str, int], dict[str, Any]] = {}
    for mapping in partition_mappings:
        key = (str(mapping.get("legacy_item_id")), int(mapping.get("location_index")))
        if key in mappings:
            raise BaselineError(f"duplicate partition mapping: {key}")
        if key not in occurrence_lookup:
            raise BaselineError(f"partition mapping does not exist in legacy inventory: {key}")
        item, location = occurrence_lookup[key]
        for field in ("file", "section", "line_start", "line_end"):
            if mapping.get(field) != location.get(field):
                raise BaselineError(
                    f"partition mapping {key} {field} mismatch: {mapping.get(field)!r} != {location.get(field)!r}"
                )
        if location.get("source_type") == "generated-cli-sdk":
            raise BaselineError(f"partition mapping unexpectedly owns generated CLI occurrence: {key}")
        mappings[key] = mapping

    generated_parent = canonical_page_id("/host/cli-api-sdk")
    for key, (item, location) in occurrence_lookup.items():
        if location.get("source_type") != "generated-cli-sdk":
            continue
        source_file = str(location["file"])
        route = "/host/cli/" + Path(source_file).stem
        route_id = supporting_route_id(route)
        frag_id = fragment_id(source_file)
        if not any(record["id"] == route_id for record in supporting_routes):
            raise BaselineError(f"legacy CLI occurrence {key} has no supporting wrapper {route_id}")
        mappings[key] = {
            "legacy_item_id": key[0],
            "location_index": key[1],
            "file": location.get("file"),
            "section": location.get("section"),
            "line_start": location.get("line_start"),
            "line_end": location.get("line_end"),
            "primary_treatment": "generated-reference",
            "page_id": generated_parent,
            "procedure_id": "API-P01",
            "branch_id": None,
            "step_id": None,
            "supporting_route_id": route_id,
            "fragment_id": frag_id,
            "rationale": "Generated CLI snippet is validated through its canonical source and wrapper/render contract, not as an independent end-to-end Host workflow.",
            "source_alignment": "GENERATED_FRAGMENT_CONTEXT",
            "source_alignment_disposition": None,
            "status": "UNVALIDATED",
        }

    missing = sorted(set(occurrence_lookup) - set(mappings))
    extra = sorted(set(mappings) - set(occurrence_lookup))
    if missing or extra:
        raise BaselineError(f"legacy occurrence mapping mismatch: missing={missing[:5]} extra={extra[:5]}")

    page_by_id = {page["id"]: page for page in pages}
    procedure_by_id = {procedure["id"]: procedure for procedure in procedures}
    branch_by_id: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    step_by_id: dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = {}
    for procedure in procedures:
        for branch in procedure.get("branches", []):
            branch_by_id[branch["id"]] = (procedure, branch)
            for step in branch.get("steps", []):
                step_by_id[step["id"]] = (procedure, branch, step)
    support_by_id = {route["id"]: route for route in supporting_routes}
    fragment_by_id = {fragment["id"]: fragment for fragment in fragments}

    claims: list[dict[str, Any]] = []
    crosswalk: list[dict[str, Any]] = []
    for key in sorted(occurrence_lookup):
        item, location = occurrence_lookup[key]
        mapping = mappings[key]
        claim = claim_id(key[0], key[1], location)
        occurrence = occurrence_id(key[0], key[1], location)
        page_id = mapping.get("page_id")
        procedure_id = mapping.get("procedure_id")
        branch_id = mapping.get("branch_id")
        step_id = mapping.get("step_id")
        if page_id not in page_by_id:
            raise BaselineError(f"mapping {key} references unknown page {page_id}")
        source_type = location.get("source_type")
        if source_type in {"authored", "generated-self-test"}:
            if location.get("file") != page_by_id[page_id].get("source_file"):
                raise BaselineError(
                    f"mapping {key} source/page mismatch: {location.get('file')} != {page_by_id[page_id].get('source_file')}"
                )
        if procedure_id is not None:
            if procedure_id not in procedure_by_id:
                raise BaselineError(f"mapping {key} references unknown procedure {procedure_id}")
            if procedure_by_id[procedure_id]["page_id"] != page_id:
                raise BaselineError(f"mapping {key} procedure/page mismatch")
        if branch_id is not None:
            if branch_id not in branch_by_id:
                raise BaselineError(f"mapping {key} references unknown branch {branch_id}")
            branch_procedure, _branch = branch_by_id[branch_id]
            if procedure_id is None or branch_procedure["id"] != procedure_id:
                raise BaselineError(f"mapping {key} branch/procedure ownership mismatch")
        if step_id is not None:
            if step_id not in step_by_id:
                raise BaselineError(f"mapping {key} references unknown step {step_id}")
            step_procedure, step_branch, step = step_by_id[step_id]
            if procedure_id is None or step_procedure["id"] != procedure_id:
                raise BaselineError(f"mapping {key} step/procedure ownership mismatch")
            if branch_id is None or step_branch["id"] != branch_id:
                raise BaselineError(f"mapping {key} step/branch ownership mismatch")
            mapping["source_alignment"] = computed_source_alignment(location, step)
            mapping["source_alignment_disposition"] = None
        elif source_type == "generated-cli-sdk":
            mapping["source_alignment"] = "GENERATED_FRAGMENT_CONTEXT"
            mapping["source_alignment_disposition"] = None
        else:
            mapping["source_alignment"] = "NON_STEP_TREATMENT"
            mapping["source_alignment_disposition"] = None

        rendered_refs = [{"route": page_by_id[page_id]["route"], "status": "UNVALIDATED"}]
        support_id = mapping.get("supporting_route_id")
        frag_id = mapping.get("fragment_id")
        if support_id:
            rendered_refs = [{"route": support_by_id[support_id]["route"], "status": "UNVALIDATED"}]
        expected: list[str] = []
        if step_id:
            expected = copy.deepcopy(step_by_id[step_id][2].get("expected_observables", []))
        elif procedure_id:
            expected = copy.deepcopy(procedure_by_id[procedure_id].get("expected_final_observables", []))
        refs = authority_refs_for(page_by_id[page_id]["route"])
        if frag_id and frag_id.startswith("FRAGMENT-host-cli-"):
            refs.append("AUTH-CLI-REGISTRY-LEGACY")
        inherited_authority = (
            procedure_by_id[procedure_id]["authority_state"]
            if procedure_id in procedure_by_id
            else "NOT_IDENTIFIED"
        )
        claim_record = {
            "id": claim,
            "occurrence_id": occurrence,
            "legacy_item_id": key[0],
            "legacy_location_index": key[1],
            "kind": item.get("kind"),
            "text": item.get("text"),
            "source": {
                "file": location.get("file"),
                "section": location.get("section"),
                "line_start": location.get("line_start"),
                "line_end": location.get("line_end"),
                "source_type": location.get("source_type"),
                "text_sha256": sha256_text(str(item.get("text", ""))),
            },
            "page_id": page_id,
            "procedure_id": procedure_id,
            "branch_id": branch_id,
            "step_id": step_id,
            "supporting_route_id": support_id,
            "fragment_id": frag_id,
            "primary_treatment": mapping.get("primary_treatment"),
            "source_alignment": mapping.get("source_alignment", "NON_STEP_TREATMENT"),
            "source_alignment_disposition": mapping.get("source_alignment_disposition"),
            "raw_context": {
                "section": location.get("section"),
                "source_span": [location.get("line_start"), location.get("line_end")],
            },
            "rendered_context_refs": rendered_refs,
            "authority_refs": sorted(set(refs)),
            "authority_state": inherited_authority,
            "claim_limit": mapping.get("rationale"),
            "test_basis": item.get("verification_method"),
            "expected_observables": expected,
            "planned_method": item.get("verification_method"),
            "status": "UNVALIDATED",
            "attempt_ids": [],
            "issue_ids": [],
            "semantic_assessment": {
                "required": True,
                "status": "UNVALIDATED",
                "score": None,
                "rationale": None,
                "finding_class": None,
                "evidence_refs": [],
                "correction_id": None,
                "retest_id": None,
            },
        }
        claims.append(claim_record)
        page_by_id[page_id]["claim_ids"].append(claim)
        if procedure_id:
            procedure_by_id[procedure_id]["claim_ids"].append(claim)
        if step_id:
            step_by_id[step_id][2]["claim_ids"].append(claim)
        if support_id:
            support_by_id[support_id]["claim_ids"].append(claim)
        if frag_id:
            fragment_by_id[frag_id]["claim_ids"].append(claim)
        crosswalk.append(
            {
                "occurrence_id": occurrence,
                "legacy_item_id": key[0],
                "legacy_location_index": key[1],
                "legacy_kind": item.get("kind"),
                "legacy_status": item.get("status"),
                "source": copy.deepcopy(claim_record["source"]),
                "claim_id": claim,
                "primary_treatment": mapping.get("primary_treatment"),
                "source_alignment": mapping.get("source_alignment", "NON_STEP_TREATMENT"),
                "source_alignment_disposition": mapping.get("source_alignment_disposition"),
                "page_id": page_id,
                "procedure_id": procedure_id,
                "branch_id": branch_id,
                "step_id": step_id,
                "supporting_route_id": support_id,
                "fragment_id": frag_id,
                "rendered_context_refs": rendered_refs,
                "rationale": mapping.get("rationale"),
                "status": "UNVALIDATED",
            }
        )

    claims.sort(key=lambda item: item["id"])
    crosswalk.sort(key=lambda item: item["occurrence_id"])
    claim_records_by_id = {claim["id"]: claim for claim in claims}
    for page in pages:
        page["claim_ids"] = sorted(set(page["claim_ids"]))
    for procedure in procedures:
        procedure["claim_ids"] = sorted(set(procedure["claim_ids"]))
        for branch in procedure.get("branches", []):
            for step in branch.get("steps", []):
                step["claim_ids"] = sorted(set(step["claim_ids"]))
                step["source_carriers"] = [
                    {
                        "claim_id": claim,
                        "kind": claim_records_by_id[claim]["kind"],
                        "text": claim_records_by_id[claim]["text"],
                        "source": copy.deepcopy(claim_records_by_id[claim]["source"]),
                    }
                    for claim in step["claim_ids"]
                ]
                if any(
                    carrier["kind"] == "command"
                    for carrier in step["source_carriers"]
                ):
                    step["execution_form_state"] = (
                        "UNVALIDATED_SAFE_PARAMETERIZATION_REQUIRED"
                    )
                else:
                    step["execution_form_state"] = "NOT_APPLICABLE_NON_COMMAND_STEP"
    for route in supporting_routes:
        route["claim_ids"] = sorted(set(route["claim_ids"]))
    for fragment in fragments:
        fragment["claim_ids"] = sorted(set(fragment["claim_ids"]))
    return claims, crosswalk


def authority_sources(repo: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": "AUTH-REVIEW-TRACEABILITY",
            "type": "repository-traceability-record",
            "path": "REVIEW-TRACEABILITY.md",
            "sha256": sha256_path(repo / "REVIEW-TRACEABILITY.md"),
            "authority_state": "ADVISORY",
            "claim_limit": "Maps Jira/runtime/document sources and unresolved review state; it does not itself prove runtime behavior.",
        },
        {
            "id": "AUTH-REVIEW-QUESTIONS",
            "type": "pending-owner-question-record",
            "path": "REVIEW-QUESTIONS.md",
            "sha256": sha256_path(repo / "REVIEW-QUESTIONS.md"),
            "authority_state": "PENDING_OWNER",
            "claim_limit": "Identifies named owner questions and publication gates; unanswered questions remain unresolved.",
        },
        {
            "id": "AUTH-SELF-TEST-GENERATOR",
            "type": "local-generator-contract",
            "path": "scripts/generate_self_test_reference.py",
            "sha256": sha256_path(repo / "scripts/generate_self_test_reference.py"),
            "authority_state": "CONFIRMED",
            "claim_limit": "Confirms the local generation contract only; current upstream inputs and runtime claims require freshness and execution evidence.",
        },
        {
            "id": "AUTH-CLI-REGISTRY-LEGACY",
            "type": "retained-static-registry-evidence",
            "path": "host-docs-cli-command-check.json",
            "sha256": sha256_path(repo / "host-docs-cli-command-check.json"),
            "authority_state": "CONFIRMED",
            "evidence_status": "STALE",
            "claim_limit": "Confirms static registry conformance only at its exact legacy CLI target; it does not prove current runtime behavior.",
        },
    ]


def assemble(
    repo: Path,
    partition_paths: list[Path],
    *,
    created_at: str | None = None,
) -> dict[str, Any]:
    docs_json = load_json(repo / "docs.json")
    primary_routes, cli_routes, sdk_routes, nav_groups = host_navigation(docs_json)
    pages, procedures, mappings, uncertainties, partition_pins = normalize_partitions(
        repo, partition_paths
    )
    discovered_page_routes = {page["route"] for page in pages}
    expected_page_routes = set(primary_routes)
    if discovered_page_routes != expected_page_routes:
        missing = sorted(expected_page_routes - discovered_page_routes)
        extra = sorted(discovered_page_routes - expected_page_routes)
        raise BaselineError(f"primary route mismatch: missing={missing} extra={extra}")
    for page in pages:
        page["navigation_group"] = nav_groups.get(page["route"])
    supporting_routes, fragments, support_contracts = build_supporting_layers(
        repo, cli_routes, sdk_routes
    )
    inventory = load_json(repo / "host-docs-verification-inventory.json")
    claims, crosswalk = build_claims_and_crosswalk(
        inventory, pages, procedures, mappings, supporting_routes, fragments
    )
    head = git(repo, "rev-parse", "HEAD")
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    branch = git(repo, "branch", "--show-current")
    tracked_status = git(repo, "status", "--porcelain", "--untracked-files=no")
    branches = sum(len(proc.get("branches", [])) for proc in procedures)
    steps = sum(
        len(branch_record.get("steps", []))
        for proc in procedures
        for branch_record in proc.get("branches", [])
    )
    source_alignment_counts: dict[str, int] = {}
    for row in crosswalk:
        alignment = str(row.get("source_alignment"))
        source_alignment_counts[alignment] = source_alignment_counts.get(alignment, 0) + 1
    heading_review_required = sum(
        1
        for procedure in procedures
        for branch_record in procedure.get("branches", [])
        for step in branch_record.get("steps", [])
        if step.get("source_context_validation", {}).get("heading_match") != "PASS"
    )
    baseline = {
        "schema_version": "1.0",
        "record_type": "host-docs-procedure-baseline",
        "baseline_id": None,
        "plan_baseline_sha256": None,
        "state": "DRAFT_NOT_FROZEN",
        "operating_mode": "PLAN_AND_EXECUTE",
        "created_at": created_at or utc_now(),
        "source_identity": {
            "repository": "vast-ai/docs",
            "branch": branch,
            "docs_target_revision": head,
            "repository_head_at_assembly": head,
            "repository_tree_at_assembly": tree,
            "target_binding": "Exact source-file and navigation hashes; later evidence-only commits do not silently retarget Host content.",
            "tracked_tree_clean_before_assembly": not bool(tracked_status),
            "docs_json_sha256": sha256_path(repo / "docs.json"),
            "legacy_inventory": {
                "path": "host-docs-verification-inventory.json",
                "sha256": sha256_path(repo / "host-docs-verification-inventory.json"),
                "source_revision": inventory.get("source_revision"),
                "content_fingerprint": inventory.get("content_fingerprint"),
            },
            "vv_evidence_skill": {
                "upstream_revision": "ab3c35b5bb7da41bc6bc3cbbefea6bc64c94c7b2",
                "skill_sha256": "5c71f16cc25a52e62cb71cd01c9129e92cda8e971faa1d0779d712ef00e2e18d",
            },
            "partition_inputs": partition_pins,
        },
        "scope": {
            "primary_routes": len(primary_routes),
            "primary_authored": 38,
            "primary_generated_self_test": 1,
            "supporting_cli_routes": len(cli_routes),
            "supporting_sdk_routes": len(sdk_routes),
            "imported_fragments": len(fragments),
            "support_layer_contracts": len(support_contracts),
            "legacy_unique_items": len(inventory.get("items", [])),
            "legacy_occurrences": len(crosswalk),
            "command_behavior_semantic_occurrences": sum(
                1 for claim in claims if claim["kind"] in {"command", "behavior-claim"}
            ),
            "all_claims_require_semantic_assessment": True,
        },
        "status_vocabulary": sorted(ALLOWED_STATUSES),
        "authority_state_vocabulary": sorted(ALLOWED_AUTHORITY_STATES),
        "authority_sources": authority_sources(repo),
        "pages": pages,
        "procedures": procedures,
        "supporting_routes": supporting_routes,
        "fragments": fragments,
        "support_contracts": support_contracts,
        "claims": claims,
        "legacy_crosswalk": crosswalk,
        "uncertainties": uncertainties,
        "reconciliation": {
            "pages": len(pages),
            "procedures": len(procedures),
            "branches": branches,
            "steps": steps,
            "claims": len(claims),
            "support_contracts": len(support_contracts),
            "legacy_crosswalk_rows": len(crosswalk),
            "unique_items_by_kind": EXPECTED_UNIQUE_BY_KIND,
            "occurrences_by_kind": EXPECTED_OCCURRENCES_BY_KIND,
            "occurrences_by_source_type": EXPECTED_OCCURRENCES_BY_SOURCE,
            "source_alignment_counts": source_alignment_counts,
            "step_heading_review_required": heading_review_required,
            "first_pass": "COMPLETE",
            "independent_second_pass": "PENDING",
            "same_agent_limit": "The primary assembler validates structure and exact coverage but does not replace independent grouping reconciliation.",
        },
        "freeze": {
            "state": "NOT_FROZEN",
            "author": "Codex primary agent",
            "reconciler": None,
            "frozen_at": None,
            "target_alias": "HOST_VV_TARGET",
            "restricted_target_record_in_git": False,
            "blocking_checks": [
                "Independent second-pass grouping and source reconciliation is pending.",
                "Rendered-context review is pending for every primary page and supporting wrapper context.",
                "Generator/source contract currentness remains pending where identified in uncertainties.",
                "Every source-alignment or unmatched-heading review item must receive an independent disposition.",
            ],
            "change_record": [
                {
                    "event": "SUPERSEDE_EXECUTION_MODEL",
                    "predecessor": "Baseline B command/occurrence execution model",
                    "disposition": "SUPERSEDED_FOR_EXECUTION_PLANNING",
                    "history_preserved": True,
                }
            ],
        },
        "execution_readiness": {
            "new_live_execution_allowed": False,
            "local_read_only_inventory_work_allowed": True,
            "credentials_from_chat_allowed": False,
            "required_live_gates": [
                "named safety approver and role",
                "operation-specific approved window and target scope",
                "restricted HOST_VV_TARGET record outside Git",
                "external client and confirmed-unused approved port",
                "numeric MAX_SPEND_USD and MAX_RUNTIME_MINUTES",
                "fresh rotated role-correct keys through secure non-chat injection",
                "cleanup authority and escalation contact",
            ],
        },
        "completion_and_acceptance": {
            "evidence_package_complete": False,
            "target_acceptance_candidate": False,
            "human_acceptance": {
                "owner": None,
                "role": None,
                "decision": "NOT_DECIDED",
                "date": None,
                "conditions": [],
                "closure_evidence": [],
            },
        },
    }
    identity_payload = plan_identity_payload(baseline)
    content_digest = sha256_text(
        json.dumps(identity_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )
    baseline["plan_baseline_sha256"] = content_digest
    baseline["baseline_id"] = f"P1-DRAFT-{head[:12]}-{content_digest[:12]}"
    return baseline


def duplicate_ids(records: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for record in records:
        record_id = str(record.get("id"))
        if record_id in seen:
            duplicates.append(record_id)
        seen.add(record_id)
    return sorted(set(duplicates))


def validate_against_repository(
    baseline: dict[str, Any], repo: Path
) -> list[str]:
    """Re-derive source identities so ``--check`` detects stale canonical data."""

    errors: list[str] = []
    source_identity = baseline.get("source_identity", {})
    partition_pins = source_identity.get("partition_inputs", [])
    if len(partition_pins) != 3:
        errors.append(f"expected three partition provenance pins, got {len(partition_pins)}")
    if sum(int(pin.get("pages", 0)) for pin in partition_pins) != 39:
        errors.append("partition provenance page totals do not equal 39")
    if sum(int(pin.get("procedures", 0)) for pin in partition_pins) != len(
        baseline.get("procedures", [])
    ):
        errors.append("partition provenance procedure totals do not match baseline")
    if sum(int(pin.get("occurrence_mappings", 0)) for pin in partition_pins) != 487:
        errors.append("partition provenance primary occurrence totals do not equal 487")
    for pin in partition_pins:
        if not re.fullmatch(r"[0-9a-f]{64}", str(pin.get("sha256", ""))):
            errors.append(f"partition provenance has invalid SHA-256: {pin.get('partition')}")
    target_revision = str(source_identity.get("docs_target_revision", ""))
    target_available = False
    if not re.fullmatch(r"[0-9a-f]{40}", target_revision):
        errors.append("docs target revision is missing or invalid")
    else:
        try:
            resolved_commit = git(repo, "rev-parse", target_revision + "^{commit}")
            if resolved_commit != target_revision:
                errors.append("docs target revision does not resolve to the exact pinned commit")
            else:
                target_available = True
        except subprocess.CalledProcessError:
            errors.append("docs target revision is not available in the repository")
    if source_identity.get("repository") != "vast-ai/docs":
        errors.append("source repository identity mismatch")
    pinned_branch = str(source_identity.get("branch", ""))
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", pinned_branch):
        errors.append("source branch metadata is missing or malformed")
    else:
        current_branch = git(repo, "branch", "--show-current")
        if current_branch and current_branch != pinned_branch:
            errors.append("current checkout branch differs from the assembly branch")
    if source_identity.get("repository_head_at_assembly") != target_revision:
        errors.append("assembly head and docs target revision must initially agree")
    if target_available:
        try:
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", target_revision, "HEAD"],
                cwd=repo,
                check=True,
                capture_output=True,
            )
            target_tree = git(repo, "rev-parse", target_revision + "^{tree}")
            if source_identity.get("repository_tree_at_assembly") != target_tree:
                errors.append("assembly tree does not match the exact docs target commit")
            target_docs_json_sha = git_blob_sha256(repo, target_revision, "docs.json")
            if source_identity.get("docs_json_sha256") != target_docs_json_sha:
                errors.append("docs.json hash is not bound to the exact target commit")
        except (subprocess.CalledProcessError, BaselineError):
            errors.append("docs target is not an ancestor or its tree/docs.json cannot be read")
    if source_identity.get("docs_json_sha256") != sha256_path(repo / "docs.json"):
        errors.append("current docs.json differs from the pinned target")
    legacy_pin = source_identity.get("legacy_inventory", {})
    inventory_path = repo / "host-docs-verification-inventory.json"
    if legacy_pin.get("sha256") != sha256_path(inventory_path):
        errors.append("current legacy inventory differs from the pinned target")
    if target_available:
        try:
            target_inventory_blob = git_blob(
                repo, target_revision, "host-docs-verification-inventory.json"
            )
            if legacy_pin.get("sha256") != hashlib.sha256(target_inventory_blob).hexdigest():
                errors.append("legacy inventory hash is not bound to the exact target commit")
            target_inventory = json.loads(target_inventory_blob.decode("utf-8"))
            if not isinstance(target_inventory, dict):
                raise ValueError("inventory is not an object")
            if legacy_pin.get("source_revision") != target_inventory.get("source_revision"):
                errors.append("legacy inventory source revision pin mismatch")
            if legacy_pin.get("content_fingerprint") != target_inventory.get(
                "content_fingerprint"
            ):
                errors.append("legacy inventory content fingerprint pin mismatch")
            for pin in partition_pins:
                declared_revision = pin.get("declared_source_revision")
                declared_fingerprint = pin.get("declared_content_fingerprint")
                if declared_revision is not None and declared_revision != target_inventory.get(
                    "source_revision"
                ):
                    errors.append(
                        f"partition source revision pin mismatch: {pin.get('partition')}"
                    )
                if declared_fingerprint is not None and declared_fingerprint != target_inventory.get(
                    "content_fingerprint"
                ):
                    errors.append(
                        f"partition content fingerprint pin mismatch: {pin.get('partition')}"
                    )
        except (subprocess.CalledProcessError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            errors.append("legacy inventory cannot be read from the exact target commit")
    expected_authority_paths = {
        "AUTH-REVIEW-TRACEABILITY": "REVIEW-TRACEABILITY.md",
        "AUTH-REVIEW-QUESTIONS": "REVIEW-QUESTIONS.md",
        "AUTH-SELF-TEST-GENERATOR": "scripts/generate_self_test_reference.py",
        "AUTH-CLI-REGISTRY-LEGACY": "host-docs-cli-command-check.json",
    }
    authority_by_id = {
        authority.get("id"): authority
        for authority in baseline.get("authority_sources", [])
    }
    if set(authority_by_id) != set(expected_authority_paths):
        errors.append("authority source population changed or is incomplete")
    for authority_id, relative_path in expected_authority_paths.items():
        record = authority_by_id.get(authority_id, {})
        source_path = (repo / relative_path).resolve()
        if repo.resolve() not in source_path.parents:
            errors.append(f"authority source escapes repository: {authority_id}")
            continue
        if record.get("path") != relative_path or not source_path.is_file():
            errors.append(f"authority source path mismatch: {authority_id}")
        elif record.get("sha256") != sha256_path(source_path):
            errors.append(f"authority source changed: {authority_id}")
        if target_available:
            try:
                if record.get("sha256") != git_blob_sha256(
                    repo, target_revision, relative_path
                ):
                    errors.append(
                        f"authority source is not bound to target commit: {authority_id}"
                    )
            except subprocess.CalledProcessError:
                errors.append(f"authority source is absent from target commit: {authority_id}")

    if target_available:
        try:
            docs_json = json.loads(git_blob(repo, target_revision, "docs.json").decode("utf-8"))
            if not isinstance(docs_json, dict):
                raise ValueError("docs.json is not an object")
        except (subprocess.CalledProcessError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            errors.append("target docs.json cannot be parsed")
            docs_json = load_json(repo / "docs.json")
    else:
        docs_json = load_json(repo / "docs.json")
    primary_routes, cli_routes, sdk_routes, _groups = host_navigation(docs_json)
    baseline_primary = {page.get("route") for page in baseline.get("pages", [])}
    if baseline_primary != set(primary_routes):
        errors.append("canonical primary route set no longer matches docs.json")
    baseline_cli = {
        route.get("route")
        for route in baseline.get("supporting_routes", [])
        if route.get("kind") == "generated-cli-wrapper"
    }
    baseline_sdk = {
        route.get("route")
        for route in baseline.get("supporting_routes", [])
        if route.get("kind") == "generated-sdk-wrapper"
    }
    if baseline_cli != set(cli_routes):
        errors.append("canonical CLI wrapper set no longer matches docs.json")
    if baseline_sdk != set(sdk_routes):
        errors.append("canonical SDK wrapper set no longer matches docs.json")

    for page in baseline.get("pages", []):
        try:
            source = repo_file(repo, str(page.get("source_file", "")), ("host/",))
        except BaselineError as error:
            errors.append(str(error))
            continue
        if not source.is_file() or page.get("source_sha256") != sha256_path(source):
            errors.append(f"primary page source changed or is missing: {page.get('id')}")
        elif page.get("imports") != imports_for(source):
            errors.append(f"primary page import set changed: {page.get('id')}")
        if target_available:
            try:
                if page.get("source_sha256") != git_blob_sha256(
                    repo, target_revision, str(page.get("source_file", ""))
                ):
                    errors.append(
                        f"primary page source is not bound to target commit: {page.get('id')}"
                    )
            except subprocess.CalledProcessError:
                errors.append(f"primary page source absent from target commit: {page.get('id')}")
    page_sources = {
        page.get("id"): repo_file(repo, str(page.get("source_file", "")), ("host/",))
        for page in baseline.get("pages", [])
        if isinstance(page.get("source_file"), str)
        and not Path(str(page.get("source_file"))).is_absolute()
        and ".." not in Path(str(page.get("source_file"))).parts
    }
    for procedure in baseline.get("procedures", []):
        source_path = page_sources.get(procedure.get("page_id"))
        if source_path is None or not source_path.is_file():
            continue
        for branch in procedure.get("branches", []):
            for step in branch.get("steps", []):
                current = source_context_validation(source_path, step)
                recorded = step.get("source_context_validation", {})
                for field in (
                    "source_sha256",
                    "span_bounds",
                    "invalid_spans",
                    "heading_match",
                    "unmatched_headings",
                    "span_heading_matches",
                ):
                    if recorded.get(field) != current.get(field):
                        errors.append(
                            f"step source context changed for {step.get('id')} field {field}"
                        )
                        break
    for route in baseline.get("supporting_routes", []):
        try:
            source = repo_file(
                repo,
                str(route.get("source_file", "")),
                ("host/cli/", "host/sdk/"),
            )
        except BaselineError as error:
            errors.append(str(error))
            continue
        if not source.is_file() or route.get("source_sha256") != sha256_path(source):
            errors.append(f"supporting route source changed or is missing: {route.get('id')}")
        else:
            imports = imports_for(source)
            fragment = next(
                (
                    item
                    for item in baseline.get("fragments", [])
                    if item.get("id") == route.get("fragment_id")
                ),
                None,
            )
            if fragment is None or imports != [fragment.get("source_file")]:
                errors.append(f"supporting route import contract changed: {route.get('id')}")
        if target_available:
            try:
                if route.get("source_sha256") != git_blob_sha256(
                    repo, target_revision, str(route.get("source_file", ""))
                ):
                    errors.append(
                        f"supporting route is not bound to target commit: {route.get('id')}"
                    )
            except subprocess.CalledProcessError:
                errors.append(f"supporting route absent from target commit: {route.get('id')}")
    for fragment in baseline.get("fragments", []):
        try:
            source = repo_file(
                repo,
                str(fragment.get("source_file", "")),
                ("snippets/host/cli/", "snippets/host/sdk/", "snippets/notifications/"),
            )
        except BaselineError as error:
            errors.append(str(error))
            continue
        if not source.is_file() or fragment.get("source_sha256") != sha256_path(source):
            errors.append(f"fragment source changed or is missing: {fragment.get('id')}")
        if target_available:
            try:
                if fragment.get("source_sha256") != git_blob_sha256(
                    repo, target_revision, str(fragment.get("source_file", ""))
                ):
                    errors.append(
                        f"fragment source is not bound to target commit: {fragment.get('id')}"
                    )
            except subprocess.CalledProcessError:
                errors.append(f"fragment source absent from target commit: {fragment.get('id')}")
    for contract in baseline.get("support_contracts", []):
        try:
            rendered_source = repo_file(
                repo,
                str(contract.get("rendered_source_file", "")),
                ("host/",),
            )
        except BaselineError as error:
            errors.append(str(error))
            continue
        expected_import = str(contract.get("source_file", ""))
        if expected_import not in imports_for(rendered_source):
            errors.append(f"support contract import edge changed: {contract.get('id')}")
        if contract.get("import_path") != "/" + expected_import:
            errors.append(f"support contract import path mismatch: {contract.get('id')}")

    inventory = load_json(inventory_path)
    current_occurrences: dict[tuple[str, int], tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in inventory.get("items", []):
        for location_index, location in enumerate(item.get("locations", [])):
            current_occurrences[(str(item.get("id")), location_index)] = (item, location)
    crosswalk_by_key = {
        (str(row.get("legacy_item_id")), int(row.get("legacy_location_index"))): row
        for row in baseline.get("legacy_crosswalk", [])
    }
    baseline_keys = {
        (str(claim.get("legacy_item_id")), int(claim.get("legacy_location_index")))
        for claim in baseline.get("claims", [])
    }
    if baseline_keys != set(current_occurrences):
        errors.append("canonical claim occurrence set no longer matches legacy inventory")
    for claim in baseline.get("claims", []):
        key = (str(claim.get("legacy_item_id")), int(claim.get("legacy_location_index")))
        current = current_occurrences.get(key)
        if not current:
            continue
        item, location = current
        row = crosswalk_by_key.get(key, {})
        if row.get("legacy_kind") != item.get("kind"):
            errors.append(f"legacy crosswalk kind changed for {claim.get('id')}")
        if row.get("legacy_status") != item.get("status"):
            errors.append(f"legacy crosswalk status changed for {claim.get('id')}")
        if claim.get("kind") != item.get("kind") or claim.get("text") != item.get("text"):
            errors.append(f"legacy item content changed for claim {claim.get('id')}")
        source = claim.get("source", {})
        for field in ("file", "section", "line_start", "line_end", "source_type"):
            if source.get(field) != location.get(field):
                errors.append(
                    f"legacy source tuple changed for claim {claim.get('id')} field {field}"
                )
                break
    return errors


def validate(baseline: dict[str, Any], repo: Path | None = None) -> list[str]:
    errors: list[str] = []
    unknown_top_level = sorted(set(baseline) - BASELINE_TOP_LEVEL_FIELDS)
    if unknown_top_level:
        errors.append(f"unknown baseline top-level fields: {unknown_top_level}")
    errors.extend(validate_output_shapes(baseline))
    restricted_paths = restricted_key_paths(baseline)
    if restricted_paths:
        errors.append(f"restricted raw fields are not allowed in canonical evidence: {restricted_paths[:5]}")
    sensitive_paths = sensitive_value_paths(exact_source_stripped_projection(baseline))
    if sensitive_paths:
        errors.append(
            "canonical non-source evidence contains restricted coordinates or key-like values: "
            + ", ".join(sensitive_paths[:5])
        )
    state = baseline.get("state")
    freeze_state = baseline.get("freeze", {}).get("state")
    if state not in ALLOWED_BASELINE_STATES:
        errors.append(f"invalid baseline lifecycle state: {state}")
    if freeze_state not in ALLOWED_FREEZE_STATES:
        errors.append(f"invalid freeze state: {freeze_state}")
    if (state, freeze_state) not in {
        ("DRAFT_NOT_FROZEN", "NOT_FROZEN"),
        ("FROZEN_P1", "FROZEN"),
    }:
        errors.append("baseline lifecycle state and freeze state are inconsistent")
    missing_identity_fields = [key for key in BASELINE_IDENTITY_FIELDS if key not in baseline]
    if missing_identity_fields:
        errors.append(f"baseline identity fields missing: {missing_identity_fields}")
    else:
        identity_payload = plan_identity_payload(baseline)
        computed_digest = sha256_text(
            json.dumps(
                identity_payload,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        if baseline.get("plan_baseline_sha256") != computed_digest:
            errors.append("plan baseline digest mismatch")
        target_revision = str(
            baseline.get("source_identity", {}).get("docs_target_revision", "")
        )
        id_label = "DRAFT" if state == "DRAFT_NOT_FROZEN" else "FROZEN"
        expected_id = f"P1-{id_label}-{target_revision[:12]}-{computed_digest[:12]}"
        if state in ALLOWED_BASELINE_STATES and baseline.get("baseline_id") != expected_id:
            errors.append("baseline ID does not match lifecycle state, content, and repository identity")
    pages = baseline.get("pages", [])
    procedures = baseline.get("procedures", [])
    supporting = baseline.get("supporting_routes", [])
    fragments = baseline.get("fragments", [])
    support_contracts = baseline.get("support_contracts", [])
    authority_records = baseline.get("authority_sources", [])
    claims = baseline.get("claims", [])
    crosswalk = baseline.get("legacy_crosswalk", [])
    for name, records in (
        ("page", pages),
        ("procedure", procedures),
        ("supporting route", supporting),
        ("fragment", fragments),
        ("support contract", support_contracts),
        ("authority source", authority_records),
        ("claim", claims),
        ("crosswalk occurrence", [{"id": row.get("occurrence_id")} for row in crosswalk]),
    ):
        duplicates = duplicate_ids(records)
        if duplicates:
            errors.append(f"duplicate {name} IDs: {duplicates[:5]}")

    if len(pages) != 39:
        errors.append(f"expected 39 primary pages, got {len(pages)}")
    authored = sum(1 for page in pages if page.get("authorship") == "authored")
    generated = sum(1 for page in pages if page.get("authorship") == "generated")
    if (authored, generated) != (38, 1):
        errors.append(f"expected primary authorship 38/1, got {authored}/{generated}")
    cli_support = sum(1 for route in supporting if route.get("kind") == "generated-cli-wrapper")
    sdk_support = sum(1 for route in supporting if route.get("kind") == "generated-sdk-wrapper")
    if (cli_support, sdk_support) != (18, 15):
        errors.append(f"expected supporting CLI/SDK 18/15, got {cli_support}/{sdk_support}")
    if len(fragments) != 34:
        errors.append(f"expected 34 imported fragments, got {len(fragments)}")
    if len(support_contracts) != 34:
        errors.append(f"expected 34 supporting-layer contracts, got {len(support_contracts)}")
    if len(claims) != 529 or len(crosswalk) != 529:
        errors.append(f"expected 529 claims/crosswalk rows, got {len(claims)}/{len(crosswalk)}")

    unique_by_kind: dict[str, set[str]] = {}
    occurrences_by_kind: dict[str, int] = {}
    occurrences_by_source: dict[str, int] = {}
    for claim in claims:
        kind = str(claim.get("kind"))
        unique_by_kind.setdefault(kind, set()).add(str(claim.get("legacy_item_id")))
        occurrences_by_kind[kind] = occurrences_by_kind.get(kind, 0) + 1
        source_type = str(claim.get("source", {}).get("source_type"))
        occurrences_by_source[source_type] = occurrences_by_source.get(source_type, 0) + 1
        if claim.get("status") not in ALLOWED_STATUSES:
            errors.append(f"claim {claim.get('id')} has invalid status {claim.get('status')}")
        if claim.get("authority_state") not in ALLOWED_AUTHORITY_STATES:
            errors.append(
                f"claim {claim.get('id')} has invalid authority state {claim.get('authority_state')}"
            )
        if not set(claim.get("authority_refs", [])).issubset(
            {record.get("id") for record in baseline.get("authority_sources", [])}
        ):
            errors.append(f"claim {claim.get('id')} has unknown authority references")
        semantic = claim.get("semantic_assessment", {})
        if semantic.get("required") is not True:
            errors.append(f"claim {claim.get('id')} is missing required semantic assessment")
        if semantic.get("score") not in (None, 1, 2, 3):
            errors.append(f"claim {claim.get('id')} has invalid semantic score")
        if semantic.get("status") not in ALLOWED_STATUSES:
            errors.append(f"claim {claim.get('id')} has invalid semantic status")
        for rendered in claim.get("rendered_context_refs", []):
            if rendered.get("status") not in ALLOWED_STATUSES:
                errors.append(f"claim {claim.get('id')} has invalid rendered-context status")
        source_location = claim.get("source", {})
        expected_claim_id = claim_id(
            str(claim.get("legacy_item_id")),
            int(claim.get("legacy_location_index")),
            source_location,
        )
        expected_occurrence_id = occurrence_id(
            str(claim.get("legacy_item_id")),
            int(claim.get("legacy_location_index")),
            source_location,
        )
        if claim.get("id") != expected_claim_id or claim.get("occurrence_id") != expected_occurrence_id:
            errors.append(f"claim {claim.get('id')} has unstable or forged identity")
    actual_unique = {key: len(value) for key, value in unique_by_kind.items()}
    if actual_unique != EXPECTED_UNIQUE_BY_KIND:
        errors.append(f"unique-kind counts mismatch: {actual_unique}")
    if occurrences_by_kind != EXPECTED_OCCURRENCES_BY_KIND:
        errors.append(f"occurrence-kind counts mismatch: {occurrences_by_kind}")
    if occurrences_by_source != EXPECTED_OCCURRENCES_BY_SOURCE:
        errors.append(f"occurrence-source counts mismatch: {occurrences_by_source}")
    semantic_command_behavior = sum(
        count for kind, count in occurrences_by_kind.items() if kind in {"command", "behavior-claim"}
    )
    if semantic_command_behavior != 407:
        errors.append(f"expected 407 command/behavior occurrences, got {semantic_command_behavior}")

    page_ids = {page.get("id") for page in pages}
    page_by_id = {page.get("id"): page for page in pages}
    procedure_ids = {procedure.get("id") for procedure in procedures}
    procedure_by_id = {procedure.get("id"): procedure for procedure in procedures}
    supporting_ids = {route.get("id") for route in supporting}
    supporting_by_id = {route.get("id"): route for route in supporting}
    fragment_ids = {fragment.get("id") for fragment in fragments}
    fragment_by_id = {fragment.get("id"): fragment for fragment in fragments}
    support_contract_ids = {contract.get("id") for contract in support_contracts}
    support_contract_contexts = {
        contract.get("rendered_context_id") for contract in support_contracts
    }
    expected_support_contexts = supporting_ids | {
        canonical_page_id("/host/notifications")
    }
    if support_contract_contexts != expected_support_contexts:
        errors.append("support contracts do not exactly cover all wrapper and notification contexts")
    authority_ids = {record.get("id") for record in authority_records}
    for authority in authority_records:
        if authority.get("authority_state") not in ALLOWED_AUTHORITY_STATES:
            errors.append(f"authority source {authority.get('id')} has invalid authority state")
    branch_ids: set[str] = set()
    step_ids: set[str] = set()
    heading_review_required = 0
    branch_owner: dict[str, str] = {}
    step_owner: dict[str, tuple[str, str, dict[str, Any]]] = {}
    claim_ids = {claim.get("id") for claim in claims}
    claim_by_id = {claim.get("id"): claim for claim in claims}
    expected_page_claims: dict[Any, set[Any]] = {page_id: set() for page_id in page_ids}
    expected_page_procedures: dict[Any, set[Any]] = {page_id: set() for page_id in page_ids}
    expected_procedure_claims: dict[Any, set[Any]] = {
        procedure_id: set() for procedure_id in procedure_ids
    }
    expected_supporting_claims: dict[Any, set[Any]] = {
        route_id: set() for route_id in supporting_ids
    }
    expected_fragment_claims: dict[Any, set[Any]] = {
        fragment_id_value: set() for fragment_id_value in fragment_ids
    }
    expected_step_claims: dict[Any, set[Any]] = {}
    for claim in claims:
        expected_page_claims.setdefault(claim.get("page_id"), set()).add(claim.get("id"))
        if claim.get("procedure_id") is not None:
            expected_procedure_claims.setdefault(claim.get("procedure_id"), set()).add(
                claim.get("id")
            )
        if claim.get("supporting_route_id") is not None:
            expected_supporting_claims.setdefault(claim.get("supporting_route_id"), set()).add(
                claim.get("id")
            )
        if claim.get("fragment_id") is not None:
            expected_fragment_claims.setdefault(claim.get("fragment_id"), set()).add(
                claim.get("id")
            )
        if claim.get("step_id") is not None:
            expected_step_claims.setdefault(claim.get("step_id"), set()).add(claim.get("id"))
    for procedure in procedures:
        expected_page_procedures.setdefault(procedure.get("page_id"), set()).add(
            procedure.get("id")
        )
    for page in pages:
        if page.get("id") != canonical_page_id(str(page.get("route", ""))):
            errors.append(f"page {page.get('id')} ID does not match route")
        if page.get("status") not in ALLOWED_STATUSES:
            errors.append(f"page {page.get('id')} has invalid status")
        if page.get("rendered_context", {}).get("status") not in ALLOWED_STATUSES:
            errors.append(f"page {page.get('id')} has invalid rendered-context status")
        unknown = set(page.get("procedure_ids", [])) - procedure_ids
        if unknown:
            errors.append(f"page {page.get('id')} has unknown procedures: {sorted(unknown)}")
        if set(page.get("procedure_ids", [])) != expected_page_procedures.get(
            page.get("id"), set()
        ):
            errors.append(f"page {page.get('id')} procedure reverse index mismatch")
        unknown_claims = set(page.get("claim_ids", [])) - claim_ids
        if unknown_claims:
            errors.append(f"page {page.get('id')} has unknown claims")
        if set(page.get("claim_ids", [])) != expected_page_claims.get(page.get("id"), set()):
            errors.append(f"page {page.get('id')} claim reverse index mismatch")
        if not set(page.get("authority_refs", [])).issubset(authority_ids):
            errors.append(f"page {page.get('id')} has unknown authority references")
    for procedure in procedures:
        if procedure.get("page_id") not in page_ids:
            errors.append(f"procedure {procedure.get('id')} references unknown page")
        if procedure.get("status") not in ALLOWED_STATUSES:
            errors.append(f"procedure {procedure.get('id')} has invalid status")
        if procedure.get("source_context", {}).get("rendered_status") not in ALLOWED_STATUSES:
            errors.append(f"procedure {procedure.get('id')} has invalid rendered-context status")
        if procedure.get("authority_state") not in ALLOWED_AUTHORITY_STATES:
            errors.append(f"procedure {procedure.get('id')} has invalid authority state")
        if set(procedure.get("claim_ids", [])) != expected_procedure_claims.get(
            procedure.get("id"), set()
        ):
            errors.append(f"procedure {procedure.get('id')} claim reverse index mismatch")
        if not set(procedure.get("authority_refs", [])).issubset(authority_ids):
            errors.append(f"procedure {procedure.get('id')} has unknown authority references")
        branches = procedure.get("branches", [])
        if not branches:
            errors.append(f"procedure {procedure.get('id')} has no branch")
        branch_model = procedure.get("branch_execution_model", {})
        local_branch_order = [str(branch.get("id")) for branch in branches]
        local_branch_ids = set(local_branch_order)
        if branch_model.get("source_order") != local_branch_order:
            errors.append(
                f"procedure {procedure.get('id')} branch model source order is not exact"
            )
        model_state = branch_model.get("state")
        if model_state not in ALLOWED_BRANCH_MODEL_STATES:
            errors.append(f"procedure {procedure.get('id')} has invalid branch model state")
        if not isinstance(branch_model.get("pass_rule"), str) or not branch_model.get(
            "pass_rule", ""
        ).strip():
            errors.append(f"procedure {procedure.get('id')} lacks a branch pass rule")
        modeled_branch_ids: set[str] = set()
        for edge in branch_model.get("ordered_edges", []):
            require_exact_keys(
                edge,
                {"from_branch", "to_branch", "relation"},
                {"from_branch", "to_branch", "relation"},
                f"procedure {procedure.get('id')} branch edge",
                errors,
            )
            from_branch = edge.get("from_branch")
            to_branch = edge.get("to_branch")
            if (
                from_branch not in local_branch_ids
                or to_branch not in local_branch_ids
                or from_branch == to_branch
                or edge.get("relation") not in ALLOWED_BRANCH_EDGE_RELATIONS
            ):
                errors.append(f"procedure {procedure.get('id')} has invalid ordered branch edge")
            modeled_branch_ids.update(
                branch_id_value
                for branch_id_value in (from_branch, to_branch)
                if branch_id_value in local_branch_ids
            )
        group_ids: set[str] = set()
        for group in branch_model.get("alternative_groups", []):
            require_exact_keys(
                group,
                {"id", "type", "branch_ids"},
                {"id", "type", "branch_ids", "label", "parent_branch", "fallback_branch"},
                f"procedure {procedure.get('id')} branch group",
                errors,
            )
            if group.get("id") in group_ids:
                errors.append(f"procedure {procedure.get('id')} has duplicate branch group ID")
            group_ids.add(str(group.get("id")))
            group_branches = group.get("branch_ids", [])
            if (
                group.get("type") not in ALLOWED_BRANCH_GROUP_TYPES
                or not isinstance(group_branches, list)
                or not group_branches
                or len(set(group_branches)) != len(group_branches)
                or not set(group_branches).issubset(local_branch_ids)
            ):
                errors.append(f"procedure {procedure.get('id')} has invalid branch group")
            modeled_branch_ids.update(
                branch_id_value
                for branch_id_value in group_branches
                if branch_id_value in local_branch_ids
            )
            for field in ("parent_branch", "fallback_branch"):
                if group.get(field) is not None and group.get(field) not in local_branch_ids:
                    errors.append(
                        f"procedure {procedure.get('id')} branch group has invalid {field}"
                    )
        if model_state == "LINEAR_SINGLE_BRANCH" and len(local_branch_order) != 1:
            errors.append(f"procedure {procedure.get('id')} falsely claims a single branch")
        if model_state == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED" and len(
            local_branch_order
        ) <= 1:
            errors.append(f"procedure {procedure.get('id')} falsely claims unresolved multi-branch state")
        if freeze_state == "FROZEN":
            if model_state == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED":
                errors.append(f"frozen procedure {procedure.get('id')} has unresolved branch semantics")
            if len(local_branch_order) > 1 and modeled_branch_ids != local_branch_ids:
                errors.append(
                    f"frozen procedure {procedure.get('id')} branch model is not exhaustive"
                )
            if not valid_review_disposition(
                branch_model.get("reconciler"), ALLOWED_BRANCH_REVIEW_DECISIONS
            ):
                errors.append(
                    f"frozen procedure {procedure.get('id')} lacks branch-model reviewer provenance"
                )
        for branch in branches:
            branch_id_value = str(branch.get("id"))
            if branch_id_value in branch_ids:
                errors.append(f"duplicate branch ID: {branch_id_value}")
            branch_ids.add(branch_id_value)
            branch_owner[branch_id_value] = str(procedure.get("id"))
            if branch.get("status") not in ALLOWED_STATUSES:
                errors.append(f"branch {branch_id_value} has invalid status")
            gate_evaluation = branch.get("execution_gate", {}).get(
                "gate_evaluation", {}
            )
            if gate_evaluation.get("status") not in ALLOWED_STATUSES:
                errors.append(f"branch {branch_id_value} has invalid gate status")
            if not branch.get("execution_gate", {}).get("unmet_gate_behavior"):
                errors.append(f"branch {branch_id_value} lacks unmet-gate behavior")
            steps = branch.get("steps", [])
            if not steps:
                errors.append(f"branch {branch_id_value} has no steps")
            for step in steps:
                step_id_value = str(step.get("id"))
                if step_id_value in step_ids:
                    errors.append(f"duplicate step ID: {step_id_value}")
                step_ids.add(step_id_value)
                step_owner[step_id_value] = (
                    str(procedure.get("id")),
                    branch_id_value,
                    step,
                )
                if step.get("status") not in ALLOWED_STATUSES:
                    errors.append(f"step {step_id_value} has invalid status")
                if not step.get("source_sections") or not step.get("source_lines"):
                    errors.append(f"step {step_id_value} lacks source context")
                source_validation = step.get("source_context_validation", {})
                if source_validation.get("span_bounds") != "PASS":
                    errors.append(f"step {step_id_value} has invalid source-span validation")
                if source_validation.get("heading_match") != "PASS":
                    heading_review_required += 1
                    if freeze_state == "FROZEN" and not valid_review_disposition(
                        source_validation.get("reconciler_disposition"),
                        ALLOWED_HEADING_DECISIONS,
                    ):
                        errors.append(
                            f"frozen step {step_id_value} lacks heading reconciler disposition"
                        )
                if set(step.get("claim_ids", [])) != expected_step_claims.get(
                    step_id_value, set()
                ):
                    errors.append(f"step {step_id_value} claim reverse index mismatch")
                source_carrier_ids = {
                    carrier.get("claim_id")
                    for carrier in step.get("source_carriers", [])
                }
                if source_carrier_ids != set(step.get("claim_ids", [])):
                    errors.append(f"step {step_id_value} exact source-carrier set mismatch")
                for carrier in step.get("source_carriers", []):
                    canonical_claim = claim_by_id.get(carrier.get("claim_id"), {})
                    if (
                        carrier.get("kind") != canonical_claim.get("kind")
                        or carrier.get("text") != canonical_claim.get("text")
                        or carrier.get("source") != canonical_claim.get("source")
                    ):
                        errors.append(f"step {step_id_value} source carrier differs from claim")
                        break

    for procedure in procedures:
        procedure_id = str(procedure.get("id"))
        for branch in procedure.get("branches", []):
            for step in branch.get("steps", []):
                step_id_value = str(step.get("id"))
                if step.get("role") not in {"setup", "action", "checkpoint", "cleanup"}:
                    errors.append(f"step {step_id_value} has invalid role {step.get('role')}")
                if not isinstance(step.get("required"), bool):
                    errors.append(f"step {step_id_value} required flag is not boolean")
                for dependency in step.get("dependencies", []):
                    if dependency not in step_owner:
                        errors.append(f"step {step_id_value} has unknown dependency {dependency}")
                    elif step_owner[dependency][0] != procedure_id:
                        errors.append(f"step {step_id_value} has cross-procedure dependency {dependency}")

    for route in supporting:
        route_id = route.get("id")
        if route_id != supporting_route_id(str(route.get("route", ""))):
            errors.append(f"supporting route {route_id} ID does not match route")
        fragment_id_value = route.get("fragment_id")
        if route.get("parent_page_id") not in page_ids:
            errors.append(f"supporting route {route_id} references unknown parent page")
        if fragment_id_value not in fragment_ids:
            errors.append(f"supporting route {route_id} references unknown fragment")
        elif route_id not in fragment_by_id[fragment_id_value].get("rendered_route_ids", []):
            errors.append(f"supporting route {route_id} missing from fragment render contexts")
        if set(route.get("claim_ids", [])) != expected_supporting_claims.get(route_id, set()):
            errors.append(f"supporting route {route_id} claim reverse index mismatch")
        if route.get("support_contract_id") not in support_contract_ids:
            errors.append(f"supporting route {route_id} has no valid support contract")
        if route.get("status") not in ALLOWED_STATUSES:
            errors.append(f"supporting route {route_id} has invalid status")
    for fragment in fragments:
        fragment_id_value = fragment.get("id")
        if set(fragment.get("claim_ids", [])) != expected_fragment_claims.get(
            fragment_id_value, set()
        ):
            errors.append(f"fragment {fragment_id_value} claim reverse index mismatch")
        for rendered_id in fragment.get("rendered_route_ids", []):
            if rendered_id not in supporting_ids and rendered_id not in page_ids:
                errors.append(
                    f"fragment {fragment_id_value} has unknown rendered context {rendered_id}"
                )
        if fragment.get("status") not in ALLOWED_STATUSES:
            errors.append(f"fragment {fragment_id_value} has invalid status")
    for contract in support_contracts:
        contract_id = contract.get("id")
        fragment_id_value = contract.get("fragment_id")
        rendered_context_id = contract.get("rendered_context_id")
        if fragment_id_value not in fragment_ids:
            errors.append(f"support contract {contract_id} references unknown fragment")
        if rendered_context_id not in supporting_ids and rendered_context_id not in page_ids:
            errors.append(f"support contract {contract_id} has unknown rendered context")
        if fragment_id_value in fragment_by_id and rendered_context_id not in fragment_by_id[
            fragment_id_value
        ].get("rendered_route_ids", []):
            errors.append(f"support contract {contract_id} is absent from fragment reverse edge")
        if not contract.get("expected_observables") or not contract.get("planned_method"):
            errors.append(f"support contract {contract_id} lacks expectations/method")
        if not set(contract.get("authority_refs", [])).issubset(authority_ids):
            errors.append(f"support contract {contract_id} has unknown authority references")
        if contract.get("status") not in ALLOWED_STATUSES:
            errors.append(f"support contract {contract_id} has invalid status")

    if set(baseline.get("status_vocabulary", [])) != ALLOWED_STATUSES:
        errors.append("status vocabulary does not match governing V&V statuses")
    if set(baseline.get("authority_state_vocabulary", [])) != ALLOWED_AUTHORITY_STATES:
        errors.append("authority-state vocabulary does not match governing values")
    scope = baseline.get("scope", {})
    expected_scope_counts = {
        "primary_routes": len(pages),
        "primary_authored": authored,
        "primary_generated_self_test": generated,
        "supporting_cli_routes": cli_support,
        "supporting_sdk_routes": sdk_support,
        "imported_fragments": len(fragments),
        "support_layer_contracts": len(support_contracts),
        "legacy_unique_items": len({claim.get("legacy_item_id") for claim in claims}),
        "legacy_occurrences": len(claims),
        "command_behavior_semantic_occurrences": semantic_command_behavior,
    }
    for field, expected in expected_scope_counts.items():
        if scope.get(field) != expected:
            errors.append(f"scope summary mismatch for {field}: {scope.get(field)} != {expected}")
    if scope.get("all_claims_require_semantic_assessment") is not True:
        errors.append("scope must state that all in-scope claims require semantic assessment")
    reconciliation = baseline.get("reconciliation", {})
    expected_reconciliation = {
        "pages": len(pages),
        "procedures": len(procedures),
        "branches": len(branch_ids),
        "steps": len(step_ids),
        "claims": len(claims),
        "legacy_crosswalk_rows": len(crosswalk),
        "support_contracts": len(support_contracts),
    }
    for field, expected in expected_reconciliation.items():
        if reconciliation.get(field) != expected:
            errors.append(
                f"reconciliation summary mismatch for {field}: {reconciliation.get(field)} != {expected}"
            )
    if reconciliation.get("step_heading_review_required") != heading_review_required:
        errors.append("reconciliation unmatched-heading count does not match steps")

    crosswalk_claims = {row.get("claim_id") for row in crosswalk}
    if crosswalk_claims != claim_ids:
        errors.append("crosswalk claim IDs do not exactly match canonical claim IDs")
    source_alignment_counts: dict[str, int] = {}
    for row in crosswalk:
        row_page = row.get("page_id")
        row_procedure = row.get("procedure_id")
        row_branch = row.get("branch_id")
        row_step = row.get("step_id")
        if row.get("page_id") not in page_ids:
            errors.append(f"crosswalk {row.get('occurrence_id')} references unknown page")
        if row_procedure is not None and row_procedure not in procedure_ids:
            errors.append(f"crosswalk {row.get('occurrence_id')} references unknown procedure")
        elif row_procedure is not None and procedure_by_id[row_procedure].get("page_id") != row_page:
            errors.append(f"crosswalk {row.get('occurrence_id')} procedure/page ownership mismatch")
        if row_branch is not None and row_branch not in branch_ids:
            errors.append(f"crosswalk {row.get('occurrence_id')} references unknown branch")
        elif row_branch is not None and branch_owner[row_branch] != row_procedure:
            errors.append(f"crosswalk {row.get('occurrence_id')} branch/procedure ownership mismatch")
        if row_step is not None and row_step not in step_ids:
            errors.append(f"crosswalk {row.get('occurrence_id')} references unknown step")
        elif row_step is not None:
            owner_procedure, owner_branch, _step = step_owner[row_step]
            if owner_procedure != row_procedure or owner_branch != row_branch:
                errors.append(f"crosswalk {row.get('occurrence_id')} step ownership mismatch")
        source = row.get("source", {})
        if source.get("source_type") in {"authored", "generated-self-test"}:
            page = page_by_id.get(row_page, {})
            if source.get("file") != page.get("source_file"):
                errors.append(f"crosswalk {row.get('occurrence_id')} source/page mismatch")
        if not row.get("primary_treatment") or not row.get("rationale"):
            errors.append(f"crosswalk {row.get('occurrence_id')} lacks treatment/rationale")
        if row.get("status") not in ALLOWED_STATUSES:
            errors.append(f"crosswalk {row.get('occurrence_id')} has invalid status")
        if row.get("primary_treatment") not in ALLOWED_PRIMARY_TREATMENTS:
            errors.append(f"crosswalk {row.get('occurrence_id')} has invalid treatment")
        alignment = str(row.get("source_alignment"))
        source_alignment_counts[alignment] = source_alignment_counts.get(alignment, 0) + 1
        if alignment not in {
            "EXACT_SECTION_AND_SPAN",
            "SPAN_ONLY_REVIEW_REQUIRED",
            "SECTION_ONLY_REVIEW_REQUIRED",
            "CROSS_SECTION_REVIEW_REQUIRED",
            "NON_STEP_TREATMENT",
            "GENERATED_FRAGMENT_CONTEXT",
        }:
            errors.append(f"crosswalk {row.get('occurrence_id')} has invalid source alignment")
        owner_step = step_owner.get(row_step, (None, None, None))[2] if row_step else None
        expected_alignment = computed_source_alignment(source, owner_step)
        if alignment != expected_alignment:
            errors.append(
                f"crosswalk {row.get('occurrence_id')} source alignment is not recomputed from its source and step"
            )
        if freeze_state == "FROZEN" and alignment.endswith(
            "REVIEW_REQUIRED"
        ) and not valid_review_disposition(
            row.get("source_alignment_disposition"), ALLOWED_ALIGNMENT_DECISIONS
        ):
            errors.append(
                f"frozen crosswalk {row.get('occurrence_id')} lacks reconciler source-alignment disposition"
            )
        claim = claim_by_id.get(row.get("claim_id"), {})
        for field in (
            "occurrence_id",
            "legacy_item_id",
            "legacy_location_index",
            "page_id",
            "procedure_id",
            "branch_id",
            "step_id",
            "supporting_route_id",
            "fragment_id",
            "primary_treatment",
            "source_alignment",
        ):
            claim_field = "legacy_location_index" if field == "legacy_location_index" else field
            if row.get(field) != claim.get(claim_field):
                errors.append(
                    f"crosswalk {row.get('occurrence_id')} differs from claim for {field}"
                )
                break
        canonical_projection = {
            "occurrence_id": claim.get("occurrence_id"),
            "legacy_item_id": claim.get("legacy_item_id"),
            "legacy_location_index": claim.get("legacy_location_index"),
            "legacy_kind": claim.get("kind"),
            "source": claim.get("source"),
            "claim_id": claim.get("id"),
            "primary_treatment": claim.get("primary_treatment"),
            "source_alignment": claim.get("source_alignment"),
            "source_alignment_disposition": claim.get("source_alignment_disposition"),
            "page_id": claim.get("page_id"),
            "procedure_id": claim.get("procedure_id"),
            "branch_id": claim.get("branch_id"),
            "step_id": claim.get("step_id"),
            "supporting_route_id": claim.get("supporting_route_id"),
            "fragment_id": claim.get("fragment_id"),
            "rendered_context_refs": claim.get("rendered_context_refs"),
            "rationale": claim.get("claim_limit"),
            "status": claim.get("status"),
        }
        for field, expected_value in canonical_projection.items():
            if row.get(field) != expected_value:
                errors.append(
                    f"crosswalk {row.get('occurrence_id')} is not a canonical claim projection for {field}"
                )
                break
        support_id = row.get("supporting_route_id")
        fragment_id_value = row.get("fragment_id")
        if support_id is not None:
            if support_id not in supporting_ids:
                errors.append(f"crosswalk {row.get('occurrence_id')} has unknown supporting route")
            elif supporting_by_id[support_id].get("fragment_id") != fragment_id_value:
                errors.append(f"crosswalk {row.get('occurrence_id')} support/fragment mismatch")

    if reconciliation.get("source_alignment_counts") != source_alignment_counts:
        errors.append("reconciliation source-alignment counts do not match crosswalk")

    for uncertainty in baseline.get("uncertainties", []):
        if uncertainty.get("status") not in ALLOWED_STATUSES:
            errors.append(f"uncertainty {uncertainty.get('id')} has invalid status")

    if baseline.get("state") == "DRAFT_NOT_FROZEN":
        draft_statuses: list[tuple[str, Any]] = []
        for page in pages:
            draft_statuses.extend(
                [
                    (str(page.get("id")), page.get("status")),
                    (
                        f"{page.get('id')}.rendered_context",
                        page.get("rendered_context", {}).get("status"),
                    ),
                ]
            )
        for procedure in procedures:
            draft_statuses.extend(
                [
                    (str(procedure.get("id")), procedure.get("status")),
                    (
                        f"{procedure.get('id')}.rendered_context",
                        procedure.get("source_context", {}).get("rendered_status"),
                    ),
                ]
            )
            for branch in procedure.get("branches", []):
                draft_statuses.append((str(branch.get("id")), branch.get("status")))
                draft_statuses.append(
                    (
                        f"{branch.get('id')}.execution_gate",
                        branch.get("execution_gate", {})
                        .get("gate_evaluation", {})
                        .get("status"),
                    )
                )
                for step in branch.get("steps", []):
                    draft_statuses.append((str(step.get("id")), step.get("status")))
        for collection in (supporting, fragments, support_contracts, claims, crosswalk):
            for record in collection:
                record_id = record.get("id") or record.get("occurrence_id")
                draft_statuses.append((str(record_id), record.get("status")))
        for claim in claims:
            draft_statuses.append(
                (
                    f"{claim.get('id')}.semantic",
                    claim.get("semantic_assessment", {}).get("status"),
                )
            )
            for rendered in claim.get("rendered_context_refs", []):
                draft_statuses.append(
                    (f"{claim.get('id')}.rendered_context", rendered.get("status"))
                )
        for uncertainty in baseline.get("uncertainties", []):
            draft_statuses.append((str(uncertainty.get("id")), uncertainty.get("status")))
        invalid_draft_statuses = [
            f"{record_id}={status}"
            for record_id, status in draft_statuses
            if status != "UNVALIDATED"
        ]
        if invalid_draft_statuses:
            errors.append(
                "draft baseline result records must all be UNVALIDATED: "
                + ", ".join(invalid_draft_statuses[:5])
            )
    freeze = baseline.get("freeze", {})
    if freeze.get("target_alias") != "HOST_VV_TARGET":
        errors.append("freeze target must use HOST_VV_TARGET alias only")
    if freeze.get("restricted_target_record_in_git") is not False:
        errors.append("restricted target record must remain outside Git")
    completion = baseline.get("completion_and_acceptance", {})
    acceptance = completion.get("human_acceptance", {})
    if completion.get("evidence_package_complete") is not False:
        errors.append("P1 baseline cannot claim evidence-package completion")
    if completion.get("target_acceptance_candidate") is not False:
        errors.append("P1 baseline cannot claim target-acceptance candidacy")
    if acceptance != {
        "owner": None,
        "role": None,
        "decision": "NOT_DECIDED",
        "date": None,
        "conditions": [],
        "closure_evidence": [],
    }:
        errors.append("P1 baseline must keep human acceptance explicitly undecided")
    readiness = baseline.get("execution_readiness", {})
    if readiness.get("new_live_execution_allowed") is not False:
        errors.append("P1 baseline cannot itself authorize new live execution")
    if readiness.get("local_read_only_inventory_work_allowed") is not True:
        errors.append("P1 baseline must preserve safe local inventory continuation")
    if readiness.get("credentials_from_chat_allowed") is not False:
        errors.append("credentials supplied through chat must remain prohibited")
    if state == "DRAFT_NOT_FROZEN":
        if freeze.get("reconciler") is not None or freeze.get("frozen_at") is not None:
            errors.append("draft baseline cannot contain frozen reviewer metadata")
        if baseline.get("reconciliation", {}).get("independent_second_pass") != "PENDING":
            errors.append("draft baseline independent second pass must remain PENDING")
    if state == "FROZEN_P1":
        reconciler = freeze.get("reconciler")
        if not isinstance(reconciler, dict) or set(reconciler) != {
            "reviewer", "role", "reviewed_at", "evidence_refs"
        }:
            errors.append("frozen baseline lacks structured independent reconciler provenance")
        elif (
            not isinstance(reconciler.get("reviewer"), str)
            or not reconciler["reviewer"].strip()
            or not isinstance(reconciler.get("role"), str)
            or not reconciler["role"].strip()
            or not is_utc_timestamp(reconciler.get("reviewed_at"))
            or not isinstance(reconciler.get("evidence_refs"), list)
            or not reconciler["evidence_refs"]
        ):
            errors.append("frozen baseline independent reconciler provenance is incomplete")
        if not is_utc_timestamp(freeze.get("frozen_at")):
            errors.append("frozen baseline lacks a valid UTC freeze timestamp")
        if baseline.get("reconciliation", {}).get("independent_second_pass") != "COMPLETE":
            errors.append("frozen baseline independent second pass is not COMPLETE")
        if freeze.get("blocking_checks"):
            errors.append("frozen baseline retains unresolved freeze blockers")
        unresolved_forms = [
            step.get("id")
            for procedure in procedures
            for branch in procedure.get("branches", [])
            for step in branch.get("steps", [])
            if step.get("execution_form_state")
            == "UNVALIDATED_SAFE_PARAMETERIZATION_REQUIRED"
        ]
        if unresolved_forms:
            errors.append(
                "frozen baseline retains unresolved safe executable forms: "
                + ", ".join(str(item) for item in unresolved_forms[:5])
            )
        unreviewed_pages = [
            page.get("id")
            for page in pages
            if page.get("rendered_context", {}).get("status") in {"UNVALIDATED", "STALE"}
            or not page.get("rendered_context", {}).get("evidence_refs")
        ]
        if unreviewed_pages:
            errors.append(
                "frozen baseline has unreviewed primary rendered contexts: "
                + ", ".join(str(item) for item in unreviewed_pages[:5])
            )
        unreviewed_support = [
            contract.get("id")
            for contract in support_contracts
            if contract.get("status") in {"UNVALIDATED", "STALE"}
            or not contract.get("evidence_refs")
        ]
        if unreviewed_support:
            errors.append(
                "frozen baseline has unreviewed support/render contracts: "
                + ", ".join(str(item) for item in unreviewed_support[:5])
            )
    if repo is not None:
        errors.extend(validate_against_repository(baseline, repo))
    return errors


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        # Dicts are frequently constructed from explicitly validated field sets.
        # Python randomizes set iteration between processes, so sorting keys at
        # the serialization boundary is required for byte-identical replay.
        json.dump(value, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="verification/procedure-baseline-p1.json",
        help="Canonical baseline path relative to the repository",
    )
    parser.add_argument(
        "--partition",
        action="append",
        type=Path,
        help="Temporary partition JSON; repeat three times when assembling",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the existing canonical baseline without rewriting it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(__file__).resolve().parent.parent
    output = (repo / args.output).resolve()
    verification_root = (repo / "verification").resolve()
    if verification_root not in output.parents or output.suffix != ".json":
        raise BaselineError("--output must be a .json file contained under verification/")
    if args.check:
        if args.partition:
            raise BaselineError("--check does not accept --partition")
        baseline = load_json(output)
    else:
        if not args.partition or len(args.partition) != 3:
            raise BaselineError("assembly requires exactly three --partition inputs")
        preserved_created_at: str | None = None
        if output.is_file():
            previous = load_json(output)
            previous_identity = previous.get("source_identity", {})
            current_head = git(repo, "rev-parse", "HEAD")
            if (
                previous.get("record_type") == "host-docs-procedure-baseline"
                and previous_identity.get("docs_target_revision") == current_head
                and is_utc_timestamp(previous.get("created_at"))
            ):
                preserved_created_at = str(previous["created_at"])
        baseline = assemble(
            repo,
            [path.resolve() for path in args.partition],
            created_at=preserved_created_at,
        )
    errors = validate(baseline, repo)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if not args.check:
        write_json(output, baseline)
    print(
        json.dumps(
            {
                "status": "PASS",
                "mode": "check" if args.check else "assemble",
                "baseline": str(output),
                "state": baseline.get("state"),
                "pages": len(baseline.get("pages", [])),
                "procedures": len(baseline.get("procedures", [])),
                "branches": baseline.get("reconciliation", {}).get("branches"),
                "steps": baseline.get("reconciliation", {}).get("steps"),
                "claims": len(baseline.get("claims", [])),
                "crosswalk": len(baseline.get("legacy_crosswalk", [])),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BaselineError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
