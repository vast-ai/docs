#!/usr/bin/env python3
"""Build an isolated Host Docs P1 topology-correction candidate.

This builder is deliberately planning-only.  It reads the pinned canonical P1 draft
and the independently reviewed topology inputs, applies the normalized topology
changes to a derivative candidate, and writes only the requested temporary JSON.
It never changes the canonical baseline and never invokes a documented, Host, WAN,
credentialed, or paid command.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parent.parent
CANONICAL_PATH = REPO / "verification/procedure-baseline-p1.json"
GOAL_PATH = REPO / "HOST-DOCS-PROCEDURE-VV-GOAL.md"
ASSEMBLER_PATH = REPO / "scripts/assemble_procedure_baseline.py"
SKILL_PATH = Path("/Users/hanneszietsman/.codex-vast/skills/vv-evidence/SKILL.md")
REVIEW_PATH = Path("/private/tmp/host-docs-p1-topology-review.json")
REJECTED_MANIFEST_PATH = Path("/private/tmp/host-docs-p1-topology-corrections.json")
FULL_RECONCILE_PATH = Path("/private/tmp/host-docs-p1-full-reconcile.json")
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-topology-candidate.json")

EXPECTED_HASHES = {
    "canonical_baseline_sha256": "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912",
    "governing_goal_sha256": "25c0d0be320f7189d93aa69172e74e95aa27644a5d3f7afd580eb6c72eca8779",
    "vv_evidence_skill_sha256": "5c71f16cc25a52e62cb71cd01c9129e92cda8e971faa1d0779d712ef00e2e18d",
    "canonical_assembler_sha256": "3973798b7cab49c103b8daeeb63a8075fa986a782a9b89ddedba919cfaaa8502",
    "independent_topology_review_sha256": "2c9ed4f8418d7cc600623708521fa63cf4df2d7f448a31896d399815fd2027f5",
    "rejected_manifest_sha256": "14c1aa7206382ba724cf9ca937c7d3b9cb72980a36b7aa8e8ce11bc8f9da6d1b",
    "full_reconcile_sha256": "5d2a4aa65bb0ef16894d6e65304de60c30b0aa544c2da48c54660b70f976b88c",
}

ALLOWED_STATUSES = {
    "UNVALIDATED",
    "PASS",
    "FAIL",
    "BLOCKED",
    "NOT_APPLICABLE",
    "STALE",
}
ALLOWED_MODEL_STATES = {
    "LINEAR_SINGLE_BRANCH",
    "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED",
    "SEQUENCE",
    "ALL_OF",
    "ONE_OF",
    "CONDITIONAL",
    "MIXED_TYPED_GRAPH",
}
ALLOWED_GROUP_TYPES = {
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
ALLOWED_EDGE_RELATIONS = {"BEFORE", "HANDOFF", "ON_FAILURE_RETRY"}
ALLOWED_OUTCOME_CLASSES = {
    "APPLICABLE_SUCCESS_PATH",
    "CONDITIONAL_SUCCESS_PATH",
    "DELEGATED_PATH",
    "DIAGNOSTIC_ONLY",
    "FAILURE_ONLY_DIAGNOSTIC",
    "NEGATIVE_FIT_OUTCOME",
    "ROUTING_DECISION",
    "STATIC_CLAIM_BUNDLE",
}

EXPECTED_ACTION_IDS = {
    "SPLIT-COM-E01",
    "SPLIT-FLT-E06",
    "SPLIT-MNT-E02",
    "SPLIT-RM-E01",
    "SPLIT-TEAM-E01",
    "SPLIT-TEAM-E03",
    "SPLIT-TEAM-T01",
    "EXTEND-ACC-E01",
    "EXTEND-HDL-E01",
    "EXTEND-MNT-E01",
    "REPAIR-HOV-C01",
    "REPAIR-NET-E03",
    "REPAIR-PAY-E02",
    "REPAIR-PAY-T01",
    "REPAIR-PRICE-E01",
    "REPAIR-SHW-C01",
    "REPAIR-ST-T01",
    "REPAIR-STR-C02",
}

EXPECTED_SPLIT_ACTIONS = {
    "SPLIT-COM-E01",
    "SPLIT-FLT-E06",
    "SPLIT-MNT-E02",
    "SPLIT-RM-E01",
    "SPLIT-TEAM-E01",
    "SPLIT-TEAM-E03",
    "SPLIT-TEAM-T01",
}
EXPECTED_EXTENSION_ACTIONS = {
    "EXTEND-ACC-E01",
    "EXTEND-HDL-E01",
    "EXTEND-MNT-E01",
}
EXPECTED_REPAIR_ACTIONS = EXPECTED_ACTION_IDS - EXPECTED_SPLIT_ACTIONS - EXPECTED_EXTENSION_ACTIONS

MIXED_ACCESS_BRANCHES = {
    ("DIA-E03", "DIA-E03-B02"),
    ("ERR-T02", "ERR-T02-B03"),
    ("ERR-T03", "ERR-T03-B01"),
    ("ERR-T03", "ERR-T03-B03"),
    ("ERR-T03", "ERR-T03-B04"),
    ("ERR-T05", "ERR-T05-B01"),
    ("ERR-T05", "ERR-T05-B02"),
    ("ERR-T06", "ERR-T06-B03"),
    ("HDL-E01", "HDL-E01-B-nvml-failure"),
    ("TEAM-E03", "TEAM-E03-B01"),
}

NET_LIVE_BRANCHES = {
    "NET-E03-B-tcp-unix",
    "NET-E03-B-tcp-windows",
    "NET-E03-B-udp-unix",
    "NET-E03-B-udp-windows",
}

# Exact carrier-level dispositions from the pinned independent reconciliation.
# These are intentionally narrower than every carrier under the surrounding MDX
# section: the other Host-team rows retain different reviewed treatments.
STATIC_TEAM_CATALOG_REASSIGN_CLAIMS = {
    "CLM-38257bb7c2529187",  # show api-keys
    "CLM-923d7604e486acd4",  # create api-key
    "CLM-fa287335656da956",  # delete api-key
    "CLM-4f08d5cc9817690b",  # show earnings
    "CLM-6a6993c68a1f04e4",  # metrics gpu
    "CLM-961b4271992ad45f",  # metrics gpu-locations
    "CLM-965828ea630d32ff",  # metrics gpu-trends
    "CLM-d3c031bf60590c17",  # metrics gpu pricing/demand row
    "CLM-da373c4653a28e82",  # destroy team
    "CLM-f09070a0effa9647",  # delete-team command-catalog row
}

TOP_LEVEL_EXTENSION_FIELDS = {
    "topology_candidate",
    "cross_page_handoffs",
    "branch_outcomes",
}


class CandidateError(RuntimeError):
    """Raised for pinned-input or topology-integrity failures."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise CandidateError(f"{path.name} must contain one JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_assembler() -> Any:
    spec = importlib.util.spec_from_file_location("host_docs_p1_assembler", ASSEMBLER_PATH)
    if spec is None or spec.loader is None:
        raise CandidateError("cannot load canonical assembler module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_pinned_inputs() -> dict[str, str]:
    paths = {
        "canonical_baseline_sha256": CANONICAL_PATH,
        "governing_goal_sha256": GOAL_PATH,
        "vv_evidence_skill_sha256": SKILL_PATH,
        "canonical_assembler_sha256": ASSEMBLER_PATH,
        "independent_topology_review_sha256": REVIEW_PATH,
        "rejected_manifest_sha256": REJECTED_MANIFEST_PATH,
        "full_reconcile_sha256": FULL_RECONCILE_PATH,
    }
    observed: dict[str, str] = {}
    for label, path in paths.items():
        if not path.is_file():
            raise CandidateError(f"required pinned input is missing: {path.name}")
        observed[label] = sha256_path(path)
        if observed[label] != EXPECTED_HASHES[label]:
            raise CandidateError(
                f"pinned input changed for {label}: expected {EXPECTED_HASHES[label]}, "
                f"observed {observed[label]}"
            )
    return observed


def procedure_index(candidate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["id"]): item for item in candidate["procedures"]}


def get_procedure(candidate: dict[str, Any], procedure_id: str) -> dict[str, Any]:
    try:
        return procedure_index(candidate)[procedure_id]
    except KeyError as error:
        raise CandidateError(f"missing procedure {procedure_id}") from error


def get_branch(procedure: dict[str, Any], branch_id: str) -> dict[str, Any]:
    for branch in procedure["branches"]:
        if branch["id"] == branch_id:
            return branch
    raise CandidateError(f"missing branch {branch_id} in {procedure['id']}")


def get_step(branch: dict[str, Any], step_id: str) -> dict[str, Any]:
    for step in branch["steps"]:
        if step["id"] == step_id:
            return step
    raise CandidateError(f"missing step {step_id} in {branch['id']}")


def dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def blank_gate(access: list[str], safety: list[str]) -> dict[str, Any]:
    return {
        "access_requirements": copy.deepcopy(access),
        "safety_requirements": copy.deepcopy(safety),
        "unmet_gate_behavior": (
            "Create a NOT_EXECUTED attempt and mark only the affected branch/claims "
            "BLOCKED; continue independent safe work."
        ),
        "gate_evaluation": {
            "status": "UNVALIDATED",
            "blocker_class": None,
            "reason": None,
            "claim_impact": [],
            "attempt_id": None,
        },
    }


def configure_procedure(
    procedure: dict[str, Any],
    *,
    procedure_id: str,
    title: str,
    goal: str,
    access: list[str],
    prerequisites: list[str],
    safety: list[str],
    expected: list[str],
    failure: list[str],
    limitations: list[str],
    cleanup: list[str],
) -> None:
    procedure["id"] = procedure_id
    procedure["title"] = title
    procedure["goal"] = goal
    procedure["access_classes"] = copy.deepcopy(access)
    procedure["prerequisites"] = copy.deepcopy(prerequisites)
    procedure["safety_constraints"] = copy.deepcopy(safety)
    procedure["expected_final_observables"] = copy.deepcopy(expected)
    procedure["failure_behavior"] = copy.deepcopy(failure)
    procedure["limitations"] = copy.deepcopy(limitations)
    procedure["cleanup"] = copy.deepcopy(cleanup)
    procedure["test_basis"] = {
        "goal": goal,
        "vv_kind": procedure["vv_kind"],
        "claim_boundary": copy.deepcopy(limitations),
    }
    access_text = " ".join(access).lower()
    procedure["authorized_environment"] = {
        "access_classes": copy.deepcopy(access),
        "approval_state": "NOT_AUTHORIZED_FOR_LIVE_EXECUTION",
        "target_alias": (
            "HOST_VV_TARGET"
            if any(
                token in access_text
                for token in (
                    "host",
                    "wan",
                    "credential",
                    "account",
                    "mutat",
                    "destruct",
                    "paid",
                    "financial",
                )
            )
            else None
        ),
    }
    procedure["evidence_sensitivity"] = (
        "restricted-or-sanitized"
        if any(
            token in access_text
            for token in ("credential", "account", "financial", "paid", "private", "log")
        )
        else "public-sanitized"
    )
    procedure["status"] = "UNVALIDATED"
    procedure["attempt_ids"] = []
    procedure["correction_ids"] = []
    procedure["retest_ids"] = []
    for branch in procedure["branches"]:
        branch["status"] = "UNVALIDATED"
        branch["execution_gate"] = blank_gate(access, safety)
        for step in branch["steps"]:
            step["status"] = "UNVALIDATED"


def configure_linear_model(procedure: dict[str, Any]) -> None:
    branch_ids = [branch["id"] for branch in procedure["branches"]]
    if len(branch_ids) != 1:
        raise CandidateError(f"{procedure['id']} is not a single-branch procedure")
    procedure["branch_execution_model"] = {
        "state": "LINEAR_SINGLE_BRANCH",
        "source_order": branch_ids,
        "ordered_edges": [],
        "alternative_groups": [],
        "pass_rule": (
            "All required steps and checkpoints in the single applicable branch, its "
            "final observable, and required cleanup must have current claim-suitable evidence."
        ),
        "reconciler": None,
    }


def configure_model(
    procedure: dict[str, Any],
    *,
    state: str,
    edges: list[dict[str, str]],
    groups: list[dict[str, Any]],
    pass_rule: str,
) -> None:
    procedure["branch_execution_model"] = {
        "state": state,
        "source_order": [branch["id"] for branch in procedure["branches"]],
        "ordered_edges": copy.deepcopy(edges),
        "alternative_groups": copy.deepcopy(groups),
        "pass_rule": pass_rule,
        "reconciler": None,
    }


def rename_branch_and_steps(
    branch: dict[str, Any],
    new_branch_id: str,
    branch_remap: dict[str, list[str]],
    step_remap: dict[str, list[str]],
) -> None:
    old_branch_id = str(branch["id"])
    old_step_ids = [str(step["id"]) for step in branch["steps"]]
    step_map = {
        old_id: f"{new_branch_id}-S{index:02d}"
        for index, old_id in enumerate(old_step_ids, start=1)
    }
    branch["id"] = new_branch_id
    branch_remap[old_branch_id] = [new_branch_id]
    for step in branch["steps"]:
        old_step_id = str(step["id"])
        step["id"] = step_map[old_step_id]
        step["dependencies"] = [step_map.get(dep, dep) for dep in step["dependencies"]]
        step_remap[old_step_id] = [str(step["id"])]


def clone_step(
    source: dict[str, Any],
    *,
    step_id: str,
    role: str,
    instruction: str,
    dependencies: list[str],
    expected: list[str],
    failure: list[str],
    required: bool = True,
    cleanup_required: bool = False,
) -> dict[str, Any]:
    step = copy.deepcopy(source)
    step["id"] = step_id
    step["role"] = role
    step["instruction_summary"] = instruction
    step["dependencies"] = copy.deepcopy(dependencies)
    step["expected_observables"] = copy.deepcopy(expected)
    step["failure_behavior"] = copy.deepcopy(failure)
    step["required"] = required
    step["cleanup_required"] = cleanup_required
    step["claim_ids"] = []
    step["source_carriers"] = []
    step["executable_template"] = None
    step["parameters"] = []
    step["execution_form_state"] = "NOT_APPLICABLE_NON_COMMAND_STEP"
    step["status"] = "UNVALIDATED"
    return step


def recompute_source_context(procedure: dict[str, Any]) -> None:
    spans: list[tuple[int, int]] = []
    headings: list[str] = []
    for branch in procedure["branches"]:
        for step in branch["steps"]:
            for span in step["source_lines"]:
                spans.append((int(span["start"]), int(span["end"])))
            headings.extend(str(value) for value in step["source_sections"])
    if spans:
        procedure["source_context"]["line_start"] = min(start for start, _ in spans)
        procedure["source_context"]["line_end"] = max(end for _, end in spans)
    procedure["source_context"]["headings"] = dedupe(headings)
    procedure["source_context"]["rendered_status"] = "UNVALIDATED"


def replace_procedure(
    candidate: dict[str, Any], old_id: str, replacements: list[dict[str, Any]]
) -> None:
    procedures = candidate["procedures"]
    index = next((i for i, item in enumerate(procedures) if item["id"] == old_id), None)
    if index is None:
        raise CandidateError(f"cannot replace absent procedure {old_id}")
    procedures[index : index + 1] = replacements


def action_record(
    action_id: str,
    action_type: str,
    source_procedure_id: str,
    result_procedure_ids: list[str],
    rationale: str,
) -> dict[str, Any]:
    return {
        "id": action_id,
        "action_type": action_type,
        "source_procedure_id": source_procedure_id,
        "result_procedure_ids": result_procedure_ids,
        "rationale": rationale,
        "implementation_state": "IMPLEMENTED_IN_ISOLATED_CANDIDATE",
        "independent_reconciliation_state": "PENDING",
        "vv_status": "UNVALIDATED",
    }


def retain_step_claims(step: dict[str, Any], claim_ids: set[str]) -> None:
    step["claim_ids"] = [value for value in step["claim_ids"] if value in claim_ids]
    step["source_carriers"] = [
        carrier
        for carrier in step["source_carriers"]
        if carrier["claim_id"] in claim_ids
    ]


def append_remap(
    mapping: dict[str, list[str]], old_id: str, new_ids: list[str]
) -> None:
    mapping[old_id] = dedupe(list(mapping.get(old_id, [])) + list(new_ids))


def consolidate_team_catalog_ownership(
    candidate: dict[str, Any],
    procedure_remap: dict[str, list[str]],
    branch_remap: dict[str, list[str]],
    step_remap: dict[str, list[str]],
) -> int:
    """Move the exact reviewed Host-team CLI carriers to the static catalog owner.

    The independently reviewed alignment records classify the table as static reference
    support.  Leaving any of its commands on live machine, finance, or owner-action
    steps would make a catalog row look like an executable workflow obligation.
    """

    catalog = get_procedure(candidate, "TEAM-C01")
    catalog_branch = get_branch(catalog, "TEAM-C01-B01")
    catalog_step = get_step(catalog_branch, "TEAM-C01-B01-S01")
    claim_by_id = {claim["id"]: claim for claim in candidate["claims"]}
    expected_ids = set(STATIC_TEAM_CATALOG_REASSIGN_CLAIMS)
    available_ids = {
        carrier["claim_id"]
        for procedure in candidate["procedures"]
        for branch in procedure["branches"]
        for step in branch["steps"]
        for carrier in step["source_carriers"]
    }
    if not expected_ids.issubset(available_ids):
        raise CandidateError("reviewed Host-team static-catalog carrier set drifted")

    for procedure in candidate["procedures"]:
        if procedure["id"] == "TEAM-C01":
            continue
        for branch in procedure["branches"]:
            for step in branch["steps"]:
                moved = [
                    carrier
                    for carrier in step["source_carriers"]
                    if carrier["claim_id"] in expected_ids
                ]
                if not moved:
                    continue
                moved_ids = {carrier["claim_id"] for carrier in moved}
                step["claim_ids"] = [
                    claim_id for claim_id in step["claim_ids"] if claim_id not in moved_ids
                ]
                step["source_carriers"] = [
                    carrier
                    for carrier in step["source_carriers"]
                    if carrier["claim_id"] not in moved_ids
                ]
                if step["id"] == "TEAM-E04-B01-S01" and not any(
                    carrier["kind"] == "command" for carrier in step["source_carriers"]
                ):
                    step["execution_form_state"] = "NOT_APPLICABLE_NON_COMMAND_STEP"
                catalog_step["claim_ids"].extend(sorted(moved_ids))
                catalog_step["source_carriers"].extend(copy.deepcopy(moved))
                for claim_id in moved_ids:
                    old_claim = claim_by_id[claim_id]
                    old_procedure = str(old_claim["procedure_id"])
                    old_branch = str(old_claim["branch_id"])
                    old_step = str(old_claim["step_id"])
                    append_remap(
                        procedure_remap,
                        old_procedure,
                        [str(procedure["id"]), "TEAM-C01"],
                    )
                    append_remap(
                        branch_remap,
                        old_branch,
                        [str(branch["id"]), "TEAM-C01-B01"],
                    )
                    append_remap(
                        step_remap,
                        old_step,
                        [str(step["id"]), "TEAM-C01-B01-S01"],
                    )

    catalog_step["claim_ids"] = sorted(set(catalog_step["claim_ids"]))
    catalog_step["source_carriers"] = sorted(
        catalog_step["source_carriers"], key=lambda item: item["claim_id"]
    )
    catalog_step["instruction_summary"] = (
        "Verify every Host-team CLI catalog link/signature and permission claim as "
        "static reference support; do not execute the catalog as a workflow."
    )
    catalog_step["execution_form_state"] = "NOT_APPLICABLE_NON_COMMAND_STEP"
    catalog["goal"] = (
        "Inspect the complete Host-team CLI command catalog without treating any row "
        "as a live mutation workflow."
    )
    catalog["safety_constraints"] = [
        "No command from the static Host-team CLI catalog is executed by this procedure."
    ]
    catalog_branch["execution_gate"]["safety_requirements"] = copy.deepcopy(
        catalog["safety_constraints"]
    )
    observed_reassign_ids = {
        carrier["claim_id"]
        for carrier in catalog_step["source_carriers"]
        if carrier["claim_id"] in expected_ids
    }
    if observed_reassign_ids != expected_ids or not expected_ids.issubset(
        set(catalog_step["claim_ids"])
    ):
        raise CandidateError("Host-team CLI catalog ownership is incomplete")
    return len(expected_ids)


def apply_genuine_splits(
    candidate: dict[str, Any],
    procedure_remap: dict[str, list[str]],
    branch_remap: dict[str, list[str]],
    step_remap: dict[str, list[str]],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    # 1. COM-E01: three independently meaningful external outcomes.
    original = copy.deepcopy(get_procedure(candidate, "COM-E01"))
    join = copy.deepcopy(original)
    join["branches"] = [copy.deepcopy(get_branch(original, "COM-E01-join"))]
    configure_procedure(
        join,
        procedure_id="COM-E01",
        title="Join the Host community channels",
        goal="Complete the documented community join flow and observe whether Host channels are available.",
        access=["external-service-interaction", "source/static-inspection"],
        prerequisites=["Intended Host account context", "Approved external-service interaction"],
        safety=["Never publish keys, tokens, install commands, renter data, or unsafe logs."],
        expected=["The intended Host community channels are visible or the exact join blocker is retained."],
        failure=["Invite, identity, or account-link drift remains UNVALIDATED or BLOCKED; it is not bypassed."],
        limitations=["Joining a community does not validate support response or product behavior."],
        cleanup=["Close the disposable browser/session and retain only sanitized observations."],
    )
    configure_linear_model(join)
    recompute_source_context(join)

    request = copy.deepcopy(original)
    request["branches"] = [copy.deepcopy(get_branch(original, "COM-E01-request"))]
    rename_branch_and_steps(request["branches"][0], "COM-E02-B01", branch_remap, step_remap)
    configure_procedure(
        request,
        procedure_id="COM-E02",
        title="Prepare a safe Host help request",
        goal="Prepare a useful, redacted help request without exposing secrets or renter data.",
        access=["local-safe", "source/static-inspection", "conditional-external-post"],
        prerequisites=["Exact symptom", "Reviewed diagnostic excerpts or bundle"],
        safety=["Do not post until secrets, setup commands, identifiers, and renter data are removed."],
        expected=["A bounded help request contains useful context and no prohibited content."],
        failure=["Any unresolved sensitive content blocks posting while unrelated source review continues."],
        limitations=["Draft quality does not prove that community or support will resolve the issue."],
        cleanup=["Remove temporary unredacted drafts and retain only an approved sanitized copy."],
    )
    configure_linear_model(request)
    recompute_source_context(request)

    route = copy.deepcopy(original)
    route["branches"] = [copy.deepcopy(get_branch(original, "COM-E01-expectations"))]
    rename_branch_and_steps(route["branches"][0], "COM-E03-B01", branch_remap, step_remap)
    configure_procedure(
        route,
        procedure_id="COM-E03",
        title="Choose community or support ownership",
        goal="Route a Host question to peer help or accountable support based on the issue boundary.",
        access=["source/static-inspection", "support-routing"],
        prerequisites=["Exact issue class and affected ownership boundary"],
        safety=["Do not place account, payout, backend, or private-data issues into a public channel."],
        expected=["The selected route matches the documented community/support ownership boundary."],
        failure=["Unclear ownership remains an explicit source-owner question."],
        limitations=["A correct route is not evidence that the underlying issue is fixed."],
        cleanup=["Retain only the sanitized routing rationale and approved evidence references."],
    )
    configure_linear_model(route)
    recompute_source_context(route)
    replace_procedure(candidate, "COM-E01", [join, request, route])
    procedure_remap["COM-E01"] = ["COM-E01", "COM-E02", "COM-E03"]
    actions.append(
        action_record(
            "SPLIT-COM-E01",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "COM-E01",
            procedure_remap["COM-E01"],
            "Community join, safe-request preparation, and ownership routing have independent outcomes and external effects.",
        )
    )

    # 2. FLT-E06: cleanup remains fleet-owned; decommission becomes a typed delegation.
    original = copy.deepcopy(get_procedure(candidate, "FLT-E06"))
    cleanup_proc = copy.deepcopy(original)
    cleanup_proc["branches"] = [copy.deepcopy(get_branch(original, "FLT-E06-B01"))]
    configure_procedure(
        cleanup_proc,
        procedure_id="FLT-E06",
        title="Fleet stale-storage cleanup",
        goal="Clean eligible stale storage for one explicit fleet machine and confirm protected data is unchanged.",
        access=["credentialed-cli", "host-mutating"],
        prerequisites=["Explicit selected machine", "Read-only contract/storage eligibility check", "Operation-specific cleanup authorization"],
        safety=["Never use a broad fleet selector; never clean protected or active-rental data."],
        expected=["Only eligible stale storage is released for the explicit machine."],
        failure=["Ambiguous ownership, active obligations, or uncertain data scope blocks cleanup."],
        limitations=["Cleanup does not prove that a machine is safely decommissioned."],
        cleanup=["Confirm protected storage and active obligations are unchanged after the bounded cleanup."],
    )
    configure_linear_model(cleanup_proc)
    recompute_source_context(cleanup_proc)

    delegate = copy.deepcopy(original)
    delegate["branches"] = [copy.deepcopy(get_branch(original, "FLT-E06-B02"))]
    rename_branch_and_steps(delegate["branches"][0], "FLT-E07-B01", branch_remap, step_remap)
    delegate["branches"][0]["steps"][0]["instruction_summary"] = (
        "Confirm the exact target is already unlisted, honor every end date, and obtain destructive authorization."
    )
    delegate["branches"][0]["steps"][1]["instruction_summary"] = (
        "Hand the exact approved target and preflight record to RM-E02; do not execute delete/decommission in the fleet procedure."
    )
    delegate["branches"][0]["steps"][1]["expected_observables"] = [
        "RM-E02 owns the destructive action, outcome, cleanup, and evidence."
    ]
    delegate["branches"][0]["steps"][2]["instruction_summary"] = (
        "Confirm the handoff record names RM-E02 and that no fleet-side destructive action was executed."
    )
    delegate["branches"][0]["steps"][2]["expected_observables"] = [
        "The exact target, readiness evidence, destructive owner, and no-duplicate-execution boundary are recorded."
    ]
    delegate["branches"][0]["steps"][2]["failure_behavior"] = [
        "Missing ownership or any fleet-side destructive action invalidates the handoff."
    ]
    configure_procedure(
        delegate,
        procedure_id="FLT-E07",
        title="Select and delegate a fleet decommission target",
        goal="Preflight one explicit fleet target and delegate decommission to its destructive owner without duplicate execution.",
        access=["credentialed-read-only", "composite-delegated-only"],
        prerequisites=["Explicit target", "Contract and storage inventory", "Named destructive owner"],
        safety=["No delete, uninstall, or decommission action is executed in this procedure."],
        expected=["The selected target and readiness evidence are handed to RM-E02."],
        failure=["Any unresolved contract, storage, target, or authorization question blocks the handoff."],
        limitations=["The handoff cannot inherit RM-E02 status or evidence."],
        cleanup=["Destructive cleanup is owned and confirmed only by RM-E02."],
    )
    configure_linear_model(delegate)
    recompute_source_context(delegate)
    replace_procedure(candidate, "FLT-E06", [cleanup_proc, delegate])
    procedure_remap["FLT-E06"] = ["FLT-E06", "FLT-E07"]
    actions.append(
        action_record(
            "SPLIT-FLT-E06",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "FLT-E06",
            procedure_remap["FLT-E06"],
            "Stale-storage cleanup and decommission have different outcomes and destructive gates.",
        )
    )

    # 3. MNT-E02: mutable schedule lifecycle vs read-only inspection.
    original = copy.deepcopy(get_procedure(candidate, "MNT-E02"))
    lifecycle = copy.deepcopy(original)
    lifecycle["branches"] = [copy.deepcopy(get_branch(original, "MNT-E02-B01"))]
    configure_procedure(
        lifecycle,
        procedure_id="MNT-E02",
        title="Schedule, verify, and conditionally cancel a maintenance window",
        goal="Create one bounded future maintenance record, verify it, and cancel only a test or erroneous record.",
        access=["credentialed-cli", "account-mutating"],
        prerequisites=["Explicit machine", "Future UTC epoch", "Duration", "Allowed category", "Operation-specific approval"],
        safety=["The fixed numeric example is never executed; cancellation is conditional on test or error intent."],
        expected=["The exact future maintenance record is shown and any authorized cancellation is confirmed."],
        failure=["Past time, wrong target, invalid category, or missing mutation approval blocks creation."],
        limitations=["A maintenance record does not authorize the underlying Host work."],
        cleanup=["Cancel only a test/erroneous record and confirm its intended final state."],
    )
    configure_linear_model(lifecycle)
    recompute_source_context(lifecycle)

    inspect = copy.deepcopy(original)
    inspect["branches"] = [copy.deepcopy(get_branch(original, "MNT-E02-B02"))]
    rename_branch_and_steps(inspect["branches"][0], "MNT-E03-B01", branch_remap, step_remap)
    configure_procedure(
        inspect,
        procedure_id="MNT-E03",
        title="Inspect maintenance windows for selected machines",
        goal="Read scheduled maintenance for an explicit bounded machine set without mutation.",
        access=["credentialed-read-only"],
        prerequisites=["Explicit comma-separated machine selection", "Read-only account context"],
        safety=["No create, cancel, or Host mutation is allowed in this inspection procedure."],
        expected=["Every selected machine's visible maintenance records are attributed to the intended context."],
        failure=["Wrong context, inaccessible target, or incomplete selection is retained as a blocker."],
        limitations=["Read-only visibility does not prove notification delivery or maintenance completion."],
        cleanup=["Clear temporary sensitive output and leave maintenance state unchanged."],
    )
    configure_linear_model(inspect)
    recompute_source_context(inspect)
    replace_procedure(candidate, "MNT-E02", [lifecycle, inspect])
    procedure_remap["MNT-E02"] = ["MNT-E02", "MNT-E03"]
    actions.append(
        action_record(
            "SPLIT-MNT-E02",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "MNT-E02",
            procedure_remap["MNT-E02"],
            "Schedule/show/cancel mutation and multi-machine read-only inspection require separate owners and gates.",
        )
    )

    # 4. RM-E01: separate cleanup, deletion, recreation, hardware, and uninstall outcomes.
    original = copy.deepcopy(get_procedure(candidate, "RM-E01"))
    old_main = copy.deepcopy(get_branch(original, "RM-E01-B01"))
    old_hardware = copy.deepcopy(get_branch(original, "RM-E01-B02"))
    old_uninstall = copy.deepcopy(get_branch(original, "RM-E01-B03"))

    cleanup_proc = copy.deepcopy(original)
    cleanup_branch = copy.deepcopy(old_main)
    cleanup_branch["steps"] = copy.deepcopy(old_main["steps"][:3])
    cleanup_branch["condition"] = "Normal unlist and bounded cleanup are separately authorized"
    cleanup_branch["steps"][2]["instruction_summary"] = (
        "Run only the separately authorized normal cleanup action for the intended target."
    )
    cleanup_proc["branches"] = [cleanup_branch]
    configure_procedure(
        cleanup_proc,
        procedure_id="RM-E01",
        title="Unlist and safely clean a Host machine",
        goal="Honor obligations, unlist the intended machine, and perform only bounded normal cleanup.",
        access=["credentialed-cli", "host-mutating"],
        prerequisites=["Exact machine", "Active-contract and stored-workload inventory", "Cleanup authorization"],
        safety=["Cleanup never implies deletion, recreation, hardware change, or uninstall."],
        expected=["The target is unlisted and only authorized stale state is cleaned."],
        failure=["Active commitments, protected data, or uncertain ownership blocks cleanup."],
        limitations=["This procedure does not decommission or recreate the machine."],
        cleanup=["Confirm no active obligation or protected data was changed."],
    )
    configure_linear_model(cleanup_proc)
    recompute_source_context(cleanup_proc)

    delete_proc = copy.deepcopy(original)
    delete_source = old_main["steps"][2]
    delete_branch = {
        "id": "RM-E02-B01",
        "condition": "Machine deletion or decommission is separately authorized after cleanup readiness",
        "status": "UNVALIDATED",
        "steps": [
            clone_step(
                old_main["steps"][0],
                step_id="RM-E02-B01-S01",
                role="setup",
                instruction="Consume the exact RM-E01 cleanup/readiness evidence and reconfirm destructive authorization.",
                dependencies=[],
                expected=["Target, obligations, stored data, recovery, and approval are exact."],
                failure=["Any unresolved identity, obligation, or recovery condition blocks deletion."],
            ),
            clone_step(
                delete_source,
                step_id="RM-E02-B01-S02",
                role="action",
                instruction="Run only the exact separately authorized supported delete/decommission action.",
                dependencies=["RM-E02-B01-S01"],
                expected=["The exact intended platform record is removed or decommissioned."],
                failure=["Unexpected state stops further action and triggers support escalation."],
            ),
            clone_step(
                old_main["steps"][4],
                step_id="RM-E02-B01-S03",
                role="checkpoint",
                instruction="Confirm the intended record/offer terminal state and absence of unintended residue.",
                dependencies=["RM-E02-B01-S02"],
                expected=["No unintended offer, record, contract, or residue remains."],
                failure=["Uncertain cleanup prevents any readiness or recreation claim."],
            ),
        ],
        "access_override": None,
        "execution_gate": blank_gate(["credentialed-cli", "host-destructive"], ["Default BLOCKED without exact destructive authorization, recovery, and idle-state proof."]),
    }
    delete_proc["branches"] = [delete_branch]
    configure_procedure(
        delete_proc,
        procedure_id="RM-E02",
        title="Delete or decommission a Host machine",
        goal="Perform one exact authorized deletion/decommission and prove its terminal state.",
        access=["credentialed-cli", "host-destructive", "support-coordinated"],
        prerequisites=["RM-E01 readiness evidence", "Exact target", "Named destructive approval", "Recovery plan"],
        safety=["Default BLOCKED; no broad selector, active contract/workload, or inferred target."],
        expected=["The intended machine record/offer reaches the approved terminal state."],
        failure=["Any uncertain result stops action and requires accountable support/recovery."],
        limitations=["Deletion does not itself validate a later recreation."],
        cleanup=["Prove intended terminal state and absence of unintended loss or residue."],
    )
    configure_linear_model(delete_proc)
    recompute_source_context(delete_proc)

    recreate_proc = copy.deepcopy(original)
    recreate_branch = copy.deepcopy(old_main)
    recreate_branch["steps"] = copy.deepcopy(old_main["steps"][3:5])
    rename_branch_and_steps(recreate_branch, "RM-E03-B01", branch_remap, step_remap)
    recreate_branch["condition"] = "A deleted/stale machine is approved for supported fresh recreation"
    recreate_branch["steps"][0]["dependencies"] = []
    recreate_proc["branches"] = [recreate_branch]
    configure_procedure(
        recreate_proc,
        procedure_id="RM-E03",
        title="Recreate a Host machine through the supported install path",
        goal="Register/install a fresh machine in the correct account and validate its new state.",
        access=["credentialed-install", "host-mutating", "paid-downstream"],
        prerequisites=["Approved recreation intent", "Correct Host account", "Fresh supported install source", "Prior record state understood"],
        safety=["Do not use undocumented reset/recovery flags or reuse credentials from chat."],
        expected=["The new machine, offer, storage, self-test, and verification-impact state are explicit."],
        failure=["Wrong context, stale source, or ambiguous prior record blocks recreation."],
        limitations=["A fresh record does not inherit evidence or verification from its predecessor."],
        cleanup=["Clear install secrets and complete any separately authorized downstream resource cleanup."],
    )
    configure_linear_model(recreate_proc)
    recompute_source_context(recreate_proc)

    hardware_proc = copy.deepcopy(original)
    hardware_proc["branches"] = [old_hardware]
    rename_branch_and_steps(hardware_proc["branches"][0], "RM-E04-B01", branch_remap, step_remap)
    configure_procedure(
        hardware_proc,
        procedure_id="RM-E04",
        title="Replace Host hardware and requalify the listing",
        goal="Perform an approved hardware change and observe the resulting spec, listing, self-test, and verification state.",
        access=["host-destructive", "maintenance-window-only", "paid-downstream"],
        prerequisites=["Ended/isolated workloads", "Recorded advertised capacity", "Hardware compatibility", "Recovery plan", "Exact maintenance approval"],
        safety=["No hardware change under an active rental or without recovery and requalification plans."],
        expected=["Hardware inventory and marketplace/verification effects match the actual supported change."],
        failure=["Unexpected device, spec, or verification state blocks relisting."],
        limitations=["A local hardware check cannot self-authorize product verification behavior."],
        cleanup=["Confirm Host health and complete separately gated self-test/offer restoration before accepting rentals."],
    )
    configure_linear_model(hardware_proc)
    recompute_source_context(hardware_proc)

    uninstall_proc = copy.deepcopy(original)
    uninstall_proc["branches"] = [old_uninstall]
    rename_branch_and_steps(uninstall_proc["branches"][0], "RM-E05-B01", branch_remap, step_remap)
    configure_procedure(
        uninstall_proc,
        procedure_id="RM-E05",
        title="Uninstall Vast Host software",
        goal="Use the current canonical uninstall source after obligations end and prove the approved software/platform state.",
        access=["host-destructive", "network-download", "support-coordinated"],
        prerequisites=["All contracts ended", "Machine unlisted", "Pinned current uninstall source", "Uninstall authorization"],
        safety=["No uninstall under an active rental or from an unverified mutable source."],
        expected=["Host service/software and platform record state match the approved decommission plan."],
        failure=["Source drift or uncertain service/platform residue triggers support escalation."],
        limitations=["Uninstall does not automatically delete backend records or stored obligations."],
        cleanup=["Confirm intended services/processes are absent and platform state is explicitly resolved."],
    )
    configure_linear_model(uninstall_proc)
    recompute_source_context(uninstall_proc)

    replace_procedure(
        candidate,
        "RM-E01",
        [cleanup_proc, delete_proc, recreate_proc, hardware_proc, uninstall_proc],
    )
    procedure_remap["RM-E01"] = ["RM-E01", "RM-E02", "RM-E03", "RM-E04", "RM-E05"]
    actions.append(
        action_record(
            "SPLIT-RM-E01",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "RM-E01",
            procedure_remap["RM-E01"],
            "Cleanup, deletion, recreation, hardware replacement, and uninstall require distinct destructive outcomes and final states.",
        )
    )

    # 5. TEAM-E01: live console flow vs static CLI catalog.
    original = copy.deepcopy(get_procedure(candidate, "TEAM-E01"))
    live = copy.deepcopy(original)
    live["branches"] = [copy.deepcopy(get_branch(original, "TEAM-E01-B01"))]
    configure_procedure(
        live,
        procedure_id="TEAM-E01",
        title="Create a Host team, least-privilege role, and operator invite",
        goal="Complete the authorized console team/role/invite flow and verify the operator's effective access.",
        access=["credentialed-web-console", "team/account-mutating"],
        prerequisites=["Intended team owner", "Reviewed least-privilege role", "Invitee consent", "Cleanup intent"],
        safety=["Do not use shared personal credentials; protect member identities and team data."],
        expected=["Membership, role, machine visibility, and denied out-of-scope access match intent."],
        failure=["Wrong context, missing 2FA, or excessive permissions blocks the invite/role result."],
        limitations=["Console success does not validate every CLI catalog command."],
        cleanup=["Remove test-only member/role and confirm revocation when not establishing a real team."],
    )
    configure_linear_model(live)
    recompute_source_context(live)

    catalog = copy.deepcopy(original)
    catalog["branches"] = [copy.deepcopy(get_branch(original, "TEAM-E01-B02"))]
    rename_branch_and_steps(catalog["branches"][0], "TEAM-C01-B01", branch_remap, step_remap)
    catalog["unit_type"] = "C"
    catalog["vv_kind"] = "verification"
    configure_procedure(
        catalog,
        procedure_id="TEAM-C01",
        title="Host team CLI command support catalog",
        goal="Inspect team/member/role command links and signatures without treating the catalog as a live mutation workflow.",
        access=["source/static-inspection", "generated-reference-inspection"],
        prerequisites=["Pinned CLI/API source and generated wrapper contracts"],
        safety=["No team, member, role, or key mutation is executed from this catalog procedure."],
        expected=["Every catalog link/signature is reconciled to its canonical source and permission claim."],
        failure=["Missing, stale, or contradictory command support remains a documentation/source defect."],
        limitations=["Static conformance cannot prove runtime authorization or mutation behavior."],
        cleanup=["Remove only temporary local inspection/render artifacts."],
    )
    configure_linear_model(catalog)
    recompute_source_context(catalog)
    replace_procedure(candidate, "TEAM-E01", [live, catalog])
    procedure_remap["TEAM-E01"] = ["TEAM-E01", "TEAM-C01"]
    actions.append(
        action_record(
            "SPLIT-TEAM-E01",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "TEAM-E01",
            procedure_remap["TEAM-E01"],
            "Live team creation/invite and static CLI support have different methods and side effects.",
        )
    )

    # 6. TEAM-E03: scoped key/machine work, finance records, and escalation ownership.
    original = copy.deepcopy(get_procedure(candidate, "TEAM-E03"))
    machine = copy.deepcopy(original)
    machine["branches"] = [copy.deepcopy(get_branch(original, "TEAM-E03-B01"))]
    configure_procedure(
        machine,
        procedure_id="TEAM-E03",
        title="Use a scoped team key for one bounded Host operation",
        goal="Create/select a least-scope team key, run one separately gated Host operation, and revoke temporary secret state.",
        access=["credentialed-cli/api", "team/account-read-only", "conditional-host-mutating"],
        prerequisites=["Secure non-chat key injection", "Exact team context", "One bounded operation", "Operation-specific authority"],
        safety=["Do not execute the mixed command catalog as one workflow; mutation and denied-scope probes need separate gates."],
        expected=["The selected operation is attributed to the intended team and temporary key state is removed."],
        failure=["Wrong owner, excessive scope, or mixed access remains a structural blocker."],
        limitations=["One operation does not validate every command in the catalog."],
        cleanup=["Revoke/rotate the temporary key, clear secret state, and reverse only the authorized test mutation."],
    )
    configure_linear_model(machine)
    recompute_source_context(machine)

    old_finance = copy.deepcopy(get_branch(original, "TEAM-E03-B02"))
    finance = copy.deepcopy(original)
    finance_branch = copy.deepcopy(old_finance)
    finance_branch["steps"] = [copy.deepcopy(old_finance["steps"][0])]
    rename_branch_and_steps(finance_branch, "TEAM-E04-B01", branch_remap, step_remap)
    finance_branch["condition"] = (
        "Earnings, payout, invoice, or market context is inspected read-only in the intended team"
    )
    invoice_branch = copy.deepcopy(old_finance)
    invoice_branch["steps"] = [copy.deepcopy(old_finance["steps"][1])]
    rename_branch_and_steps(invoice_branch, "TEAM-E04-B02", branch_remap, step_remap)
    invoice_branch["condition"] = (
        "Invoice information must be updated under separate billing-write authorization"
    )
    invoice_branch["steps"][0]["dependencies"] = []
    invoice_branch["steps"][0]["instruction_summary"] = (
        "Update only the approved invoice fields in the intended team context."
    )
    invoice_branch["execution_gate"] = blank_gate(
        ["credentialed-finance-context", "billing-write", "account-mutating"],
        [
            "Do not change payout, credit, tax, or unrelated account state; retain a private before/after record."
        ],
    )
    invoice_branch["access_override"] = [
        "credentialed-finance-context",
        "billing-write",
        "account-mutating",
    ]
    finance["branches"] = [finance_branch, invoice_branch]
    configure_procedure(
        finance,
        procedure_id="TEAM-E04",
        title="Review team finance context and conditionally update invoice information",
        goal="Inspect financial context read-only and update invoice information only through a separately gated billing-write branch.",
        access=["credentialed-finance-context", "financial-read-only", "conditional-billing-write"],
        prerequisites=["Intended team context", "Billing-read authority", "Private retention boundary"],
        safety=["Do not expose or mutate private financial data by inference."],
        expected=["Finance observations and any separately authorized invoice-only update are attributed to the intended team and role."],
        failure=["Wrong context, missing exact read/write scope, or unclear finance authority blocks the affected branch."],
        limitations=["Read-only visibility does not establish payout policy authority; invoice write authority does not authorize payout or credit changes."],
        cleanup=["Remove temporary financial downloads/output and confirm only approved invoice fields changed."],
    )
    finance_branch["execution_gate"] = blank_gate(
        ["credentialed-finance-context", "financial-read-only"],
        ["Do not mutate payout, invoice, tax, credit, or account state during read-only inspection."],
    )
    invoice_branch["execution_gate"] = blank_gate(
        ["credentialed-finance-context", "billing-write", "account-mutating"],
        [
            "Do not change payout, credit, tax, or unrelated account state; retain a private before/after record."
        ],
    )
    invoice_branch["access_override"] = [
        "credentialed-finance-context",
        "billing-write",
        "account-mutating",
    ]
    configure_model(
        finance,
        state="MIXED_TYPED_GRAPH",
        edges=[edge("TEAM-E04-B01", "TEAM-E04-B02")],
        groups=[group("GRP-TEAM-E04-INVOICE-WRITE", "CONDITIONAL", ["TEAM-E04-B02"])],
        pass_rule=(
            "Read-only finance context is required; invoice editing is conditional and must retain its independent billing-write gate and before/after evidence."
        ),
    )
    recompute_source_context(finance)

    escalation = copy.deepcopy(original)
    escalation_branch = copy.deepcopy(old_finance)
    escalation_branch["steps"] = [copy.deepcopy(old_finance["steps"][2])]
    rename_branch_and_steps(escalation_branch, "TEAM-E05-B01", branch_remap, step_remap)
    escalation_branch["condition"] = (
        "The monitored escalation contact is reviewed for the intended team/on-call owner"
    )
    escalation_branch["steps"][0]["dependencies"] = []
    escalation["branches"] = [escalation_branch]
    configure_procedure(
        escalation,
        procedure_id="TEAM-E05",
        title="Confirm Host team escalation-contact ownership",
        goal="Confirm the monitored escalation contact belongs to the intended team/on-call owner.",
        access=["team/account-read-only", "source-owner-validation"],
        prerequisites=["Intended team", "Named on-call owner", "Approved contact-data boundary"],
        safety=["Do not expose personal contact data in public evidence."],
        expected=["The accountable monitored contact is explicit for the intended team."],
        failure=["Missing or stale ownership remains an authority blocker."],
        limitations=["Contact ownership does not validate alert delivery."],
        cleanup=["Retain only the approved ownership decision/reference."],
    )
    configure_linear_model(escalation)
    recompute_source_context(escalation)
    replace_procedure(candidate, "TEAM-E03", [machine, finance, escalation])
    procedure_remap["TEAM-E03"] = ["TEAM-E03", "TEAM-E04", "TEAM-E05"]
    branch_remap["TEAM-E03-B02"] = [
        "TEAM-E04-B01",
        "TEAM-E04-B02",
        "TEAM-E05-B01",
    ]
    actions.append(
        action_record(
            "SPLIT-TEAM-E03",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "TEAM-E03",
            procedure_remap["TEAM-E03"],
            "Machine/key operations, finance records, and escalation contacts have distinct roles, permissions, and evidence owners.",
        )
    )

    # 7. TEAM-T01: diagnosis, migration, and three owner-only outcomes.
    original = copy.deepcopy(get_procedure(candidate, "TEAM-T01"))
    diagnose = copy.deepcopy(original)
    diagnose["branches"] = [copy.deepcopy(get_branch(original, "TEAM-T01-B01"))]
    configure_procedure(
        diagnose,
        procedure_id="TEAM-T01",
        title="Diagnose wrong Host team/account context",
        goal="Classify wrong-context, wrong-key, ownership, or permission symptoms and verify a safe context correction.",
        access=["team/account-read-only", "credentialed-conditional"],
        prerequisites=["Exact symptom", "Intended team/account", "Safe read-only ownership inventory"],
        safety=["Do not treat deletion, reinstall, payout change, or migration as a context fix."],
        expected=["The intended context and required machine permission are explicit."],
        failure=["Persistent mismatch is handed to support without destructive improvisation."],
        limitations=["Context correction does not migrate existing machines, earnings, or payout history."],
        cleanup=["Revoke wrong-context temporary keys/commands and clear secret state."],
    )
    configure_linear_model(diagnose)
    recompute_source_context(diagnose)

    migrate = copy.deepcopy(original)
    migrate["branches"] = [copy.deepcopy(get_branch(original, "TEAM-T01-B02"))]
    rename_branch_and_steps(migrate["branches"][0], "TEAM-T02-B01", branch_remap, step_remap)
    configure_procedure(
        migrate,
        procedure_id="TEAM-T02",
        title="Plan a support-coordinated Host account/team migration",
        goal="Inventory existing Host ownership and obtain the supported migration path before changing resources.",
        access=["team/account-read-only", "support-coordinated"],
        prerequisites=["Existing machine/earnings/payout/key inventory", "Approved support recipient"],
        safety=["No delete, reinstall, setup-key change, or payout change is attempted as migration."],
        expected=["Support owns an explicit migration path for the exact operation scope."],
        failure=["Missing visibility or accountable support ownership blocks migration."],
        limitations=["A support request does not prove backend migration completion."],
        cleanup=["Retain only the approved support packet and evidence references."],
    )
    configure_linear_model(migrate)
    recompute_source_context(migrate)

    old_owner = copy.deepcopy(get_branch(original, "TEAM-T01-B03"))
    old_setup = copy.deepcopy(old_owner["steps"][0])
    rename_claim = {"CLM-3dcc55f512950eb3"}
    transfer_claim = {"CLM-8b9f39822c566395"}
    delete_claims = {
        "CLM-88a586390c3e3125",
        "CLM-cb07a0823ae27d58",
        "CLM-f09070a0effa9647",
    }

    def owner_action_proc(
        procedure_id: str,
        branch_id: str,
        title: str,
        goal: str,
        selected_claims: set[str],
        action_instruction: str,
        access: list[str],
        safety: list[str],
        is_delete: bool,
    ) -> dict[str, Any]:
        proc = copy.deepcopy(original)
        proc["unit_type"] = "E"
        setup = copy.deepcopy(old_setup)
        retain_step_claims(setup, selected_claims)
        setup["id"] = f"{branch_id}-S01"
        setup["dependencies"] = []
        setup["instruction_summary"] = f"Inventory the exact records and owner preconditions for {title.lower()}."
        if is_delete:
            action = copy.deepcopy(old_owner["steps"][1])
            action["id"] = f"{branch_id}-S02"
            action["dependencies"] = [setup["id"]]
            action["instruction_summary"] = action_instruction
            action["required"] = True
            checkpoint = copy.deepcopy(old_owner["steps"][2])
            checkpoint["id"] = f"{branch_id}-S03"
            checkpoint["dependencies"] = [action["id"]]
        else:
            action = clone_step(
                old_owner["steps"][1],
                step_id=f"{branch_id}-S02",
                role="action",
                instruction=action_instruction,
                dependencies=[setup["id"]],
                expected=["The exact authorized owner action produces only its declared effect."],
                failure=["Unexpected ownership or record state stops the action and triggers support escalation."],
            )
            checkpoint = clone_step(
                old_owner["steps"][2],
                step_id=f"{branch_id}-S03",
                role="checkpoint",
                instruction=f"Confirm the final state after {title.lower()} matches the approved outcome.",
                dependencies=[action["id"]],
                expected=["Owner, team, resources, and records match the authorized outcome."],
                failure=["Any unintended change prevents completion and requires accountable recovery."],
            )
        branch = {
            "id": branch_id,
            "condition": f"{title} is separately authorized by the accountable team owner",
            "status": "UNVALIDATED",
            "steps": [setup, action, checkpoint],
            "access_override": None,
            "execution_gate": blank_gate(access, safety),
        }
        proc["branches"] = [branch]
        configure_procedure(
            proc,
            procedure_id=procedure_id,
            title=title,
            goal=goal,
            access=access,
            prerequisites=["Exact intended team", "Named accountable owner", "Read-only preflight", "Operation-specific authorization"],
            safety=safety,
            expected=["The exact owner action reaches only its approved final state."],
            failure=["Uncertain identity, records, authority, or irreversibility blocks the action."],
            limitations=["One owner action does not migrate unrelated machines, keys, earnings, or payout history."],
            cleanup=["Confirm final owner/team/resource state and escalate any uncertain recovery."],
        )
        configure_linear_model(proc)
        recompute_source_context(proc)
        return proc

    rename_proc = owner_action_proc(
        "TEAM-E06",
        "TEAM-E06-B01",
        "Rename a Host team",
        "Rename the intended Host team without implying resource or ownership migration.",
        rename_claim,
        "Perform only the separately authorized team display-name change.",
        ["credentialed-team-owner", "account-mutating"],
        ["A rename must not be presented as moving machines, keys, earnings, or payout setup."],
        False,
    )
    transfer_proc = owner_action_proc(
        "TEAM-E07",
        "TEAM-E07-B01",
        "Transfer Host team ownership",
        "Transfer ownership to the exact existing member after reviewing irreversible and billing consequences.",
        transfer_claim,
        "Perform only the separately authorized ownership transfer to the exact existing member.",
        ["credentialed-team-owner", "owner-only-destructive"],
        ["Default BLOCKED without recipient, billing, reversibility, and recovery review."],
        False,
    )
    delete_proc = owner_action_proc(
        "TEAM-E08",
        "TEAM-E08-B01",
        "Delete a Host team",
        "Delete the exact Host team only after machines, rentals, credits, earnings, payout/billing records, and support obligations are resolved.",
        delete_claims,
        "Perform only the separately authorized team deletion.",
        ["credentialed-team-owner", "owner-only-destructive", "support-coordinated"],
        ["Default BLOCKED while any active Host machine, rental, payout/billing record, or preservation need remains."],
        True,
    )
    # The original compound setup step is intentionally decomposed across three claim owners.
    step_remap["TEAM-T01-B03-S01"] = [
        "TEAM-E06-B01-S01",
        "TEAM-E07-B01-S01",
        "TEAM-E08-B01-S01",
    ]
    step_remap["TEAM-T01-B03-S02"] = ["TEAM-E08-B01-S02"]
    step_remap["TEAM-T01-B03-S03"] = ["TEAM-E08-B01-S03"]
    branch_remap["TEAM-T01-B03"] = [
        "TEAM-E06-B01",
        "TEAM-E07-B01",
        "TEAM-E08-B01",
    ]
    replace_procedure(
        candidate,
        "TEAM-T01",
        [diagnose, migrate, rename_proc, transfer_proc, delete_proc],
    )
    procedure_remap["TEAM-T01"] = [
        "TEAM-T01",
        "TEAM-T02",
        "TEAM-E06",
        "TEAM-E07",
        "TEAM-E08",
    ]
    actions.append(
        action_record(
            "SPLIT-TEAM-T01",
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT",
            "TEAM-T01",
            procedure_remap["TEAM-T01"],
            "Wrong-context diagnosis, support migration, rename, transfer, and deletion are distinct outcomes with separate owners.",
        )
    )

    branch_remap["RM-E01-B01"] = ["RM-E01-B01", "RM-E02-B01", "RM-E03-B01"]
    step_remap["RM-E01-B01-S03"] = ["RM-E01-B01-S03", "RM-E02-B01-S02"]
    branch_remap["TEAM-E03-B02"] = [
        "TEAM-E04-B01",
        "TEAM-E04-B02",
        "TEAM-E05-B01",
    ]

    return actions


def edge(source: str, target: str, relation: str = "BEFORE") -> dict[str, str]:
    return {"from_branch": source, "to_branch": target, "relation": relation}


def group(
    group_id: str,
    group_type: str,
    branch_ids: list[str],
    *,
    label: str | None = None,
    parent_branch: str | None = None,
    fallback_branch: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": group_id,
        "type": group_type,
        "branch_ids": branch_ids,
    }
    if label is not None:
        result["label"] = label
    if parent_branch is not None:
        result["parent_branch"] = parent_branch
    if fallback_branch is not None:
        result["fallback_branch"] = fallback_branch
    return result


def group_of_groups(
    group_id: str,
    group_type: str,
    group_ids: list[str],
    *,
    label: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": group_id,
        "type": group_type,
        "group_ids": group_ids,
    }
    if label is not None:
        result["label"] = label
    return result


def apply_structural_extensions(
    candidate: dict[str, Any],
    branch_remap: dict[str, list[str]],
    step_remap: dict[str, list[str]],
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    # ACC-E01: the account/team selector precedes one real common agreement tail.
    procedure = get_procedure(candidate, "ACC-E01")
    personal = get_branch(procedure, "ACC-E01-B-personal")
    team = get_branch(procedure, "ACC-E01-B-team")
    old_personal_steps = copy.deepcopy(personal["steps"])
    personal["steps"] = [old_personal_steps[0]]
    common_steps = copy.deepcopy(old_personal_steps[1:])
    common_branch = {
        "id": "ACC-E01-B-common",
        "condition": "The selected dedicated Host account or team context is ready for agreement acceptance",
        "status": "UNVALIDATED",
        "steps": common_steps,
        "access_override": None,
        "execution_gate": copy.deepcopy(personal["execution_gate"]),
    }
    old_to_new = {
        str(common_steps[0]["id"]): "ACC-E01-B-common-S01",
        str(common_steps[1]["id"]): "ACC-E01-B-common-S02",
    }
    for step in common_steps:
        old_id = str(step["id"])
        step["id"] = old_to_new[old_id]
        step["dependencies"] = [old_to_new.get(dep, dep) for dep in step["dependencies"]]
        step_remap[old_id] = [step["id"]]
    common_steps[0]["dependencies"] = []
    procedure["branches"] = [personal, team, common_branch]
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[
            edge("ACC-E01-B-personal", "ACC-E01-B-common"),
            edge("ACC-E01-B-team", "ACC-E01-B-common"),
        ],
        groups=[
            group(
                "GRP-ACC-E01-CONTEXT",
                "ONE_OF",
                ["ACC-E01-B-personal", "ACC-E01-B-team"],
                label="dedicated Host ownership context",
            )
        ],
        pass_rule=(
            "Exactly one dedicated personal/team context must be applicable, then the common "
            "agreement and Host-navigation tail must be dispositioned; no branch result is inherited."
        ),
    )
    branch_remap["ACC-E01-B-personal"] = ["ACC-E01-B-personal", "ACC-E01-B-common"]
    recompute_source_context(procedure)
    actions.append(
        action_record(
            "EXTEND-ACC-E01",
            "STRUCTURAL_PATH_EXTENSION",
            "ACC-E01",
            ["ACC-E01"],
            "ONE_OF(personal, team) now hands to a real common agreement/navigation branch instead of a synthetic reference.",
        )
    )

    # HDL-E01: add the two missing real paths and connect the stateful journey.
    procedure = get_procedure(candidate, "HDL-E01")
    storage_source = get_step(
        get_branch(procedure, "HDL-E01-B-storage-disposable"), "HDL-E01-S15"
    )
    raw_source = get_step(
        get_branch(procedure, "HDL-E01-B-install-raw"), "HDL-E01-S24"
    )
    existing_storage = {
        "id": "HDL-E01-B-storage-existing",
        "condition": "Existing prepared storage is retained instead of wiping a disposable device",
        "status": "UNVALIDATED",
        "steps": [
            clone_step(
                storage_source,
                step_id="HDL-E01-B-storage-existing-S01",
                role="checkpoint",
                instruction="Delegate existing XFS/project-quota validation to STO-E02 and consume its exact outcome/evidence.",
                dependencies=[],
                expected=["An exact existing-storage owner proves source, XFS, quota, capacity, and end state."],
                failure=["Missing or unsuitable existing-storage evidence blocks the install journey without wiping a device."],
            )
        ],
        "access_override": ["composite-delegated-only", "host-read-only"],
        "execution_gate": blank_gate(
            ["composite-delegated-only", "host-read-only"],
            ["No format, partition, mount mutation, or duplicated child execution is allowed in this branch."],
        ),
    }
    raw_download = {
        "id": "HDL-E01-B-install-raw-download",
        "condition": "The raw fallback is selected and a current installer artifact must be obtained",
        "status": "UNVALIDATED",
        "steps": [
            clone_step(
                raw_source,
                step_id="HDL-E01-B-install-raw-download-S01",
                role="setup",
                instruction="Obtain the exact current raw-installer artifact through the canonical setup/install owner before using the raw fallback.",
                dependencies=[],
                expected=["The raw installer source identity and approved download path are explicit before secret use."],
                failure=["The Host page omits an exact raw-installer download path; the raw branch remains structurally blocked until corrected."],
            )
        ],
        "access_override": ["source/static-inspection", "network-download", "composite-delegated-only"],
        "execution_gate": blank_gate(
            ["source/static-inspection", "network-download", "composite-delegated-only"],
            ["Do not invent or reuse a mutable installer URL; no download is authorized by this planning candidate."],
        ),
    }
    # Keep source order and place the new alternatives alongside their owning phases.
    branches: list[dict[str, Any]] = []
    for branch in procedure["branches"]:
        if branch["id"] == "HDL-E01-B-storage-disposable":
            branches.append(existing_storage)
        if branch["id"] == "HDL-E01-B-install-raw":
            branches.append(raw_download)
        branches.append(branch)
    procedure["branches"] = branches
    hdl_edges = [
        edge("HDL-E01-B-ssh-trust", "HDL-E01-B-system-update"),
        edge("HDL-E01-B-system-update", "HDL-E01-B-hwe"),
        edge("HDL-E01-B-system-update", "HDL-E01-B-nvidia"),
        edge("HDL-E01-B-hwe", "HDL-E01-B-nvidia"),
        edge("HDL-E01-B-nvidia", "HDL-E01-B-automatic-updates"),
        edge("HDL-E01-B-automatic-updates", "HDL-E01-B-ubuntu-server-x"),
        edge("HDL-E01-B-automatic-updates", "HDL-E01-B-desktop-origin"),
        edge("HDL-E01-B-ubuntu-server-x", "HDL-E01-B-storage-existing"),
        edge("HDL-E01-B-ubuntu-server-x", "HDL-E01-B-storage-disposable"),
        edge("HDL-E01-B-desktop-origin", "HDL-E01-B-storage-existing"),
        edge("HDL-E01-B-desktop-origin", "HDL-E01-B-storage-disposable"),
        edge("HDL-E01-B-storage-existing", "HDL-E01-B-persistence"),
        edge("HDL-E01-B-storage-disposable", "HDL-E01-B-persistence"),
        edge("HDL-E01-B-persistence", "HDL-E01-B-install-tui"),
        edge("HDL-E01-B-persistence", "HDL-E01-B-install-raw-download"),
        edge("HDL-E01-B-install-raw-download", "HDL-E01-B-install-raw"),
        edge("HDL-E01-B-install-tui", "HDL-E01-B-vm-grub-amd"),
        edge("HDL-E01-B-install-tui", "HDL-E01-B-vm-grub-intel"),
        edge("HDL-E01-B-install-tui", "HDL-E01-B-network"),
        edge("HDL-E01-B-install-raw", "HDL-E01-B-vm-grub-amd"),
        edge("HDL-E01-B-install-raw", "HDL-E01-B-vm-grub-intel"),
        edge("HDL-E01-B-install-raw", "HDL-E01-B-network"),
        edge("HDL-E01-B-vm-grub-amd", "HDL-E01-B-network"),
        edge("HDL-E01-B-vm-grub-intel", "HDL-E01-B-network"),
        edge("HDL-E01-B-network", "HDL-E01-B-final-verify"),
        edge("HDL-E01-B-final-verify", "HDL-E01-B-operate"),
        edge("HDL-E01-B-nvml-failure", "HDL-E01-B-nvidia", "ON_FAILURE_RETRY"),
    ]
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=hdl_edges,
        groups=[
            group("GRP-HDL-SSH", "CONDITIONAL", ["HDL-E01-B-ssh-trust"]),
            group("GRP-HDL-HWE", "CONDITIONAL", ["HDL-E01-B-hwe"]),
            group(
                "GRP-HDL-X-ORIGIN",
                "ONE_OF",
                ["HDL-E01-B-ubuntu-server-x", "HDL-E01-B-desktop-origin"],
            ),
            group(
                "GRP-HDL-STORAGE",
                "ONE_OF",
                ["HDL-E01-B-storage-existing", "HDL-E01-B-storage-disposable"],
            ),
            group(
                "GRP-HDL-INSTALL",
                "ONE_OF",
                ["HDL-E01-B-install-tui", "HDL-E01-B-install-raw"],
            ),
            group(
                "GRP-HDL-RAW-DOWNLOAD",
                "CONDITIONAL",
                ["HDL-E01-B-install-raw-download"],
                parent_branch="HDL-E01-B-install-raw",
            ),
            group(
                "GRP-HDL-VM",
                "OPTIONAL_ONE_OF",
                ["HDL-E01-B-vm-grub-amd", "HDL-E01-B-vm-grub-intel"],
            ),
            group("GRP-HDL-NVML", "FAILURE_ONLY", ["HDL-E01-B-nvml-failure"]),
        ],
        pass_rule=(
            "All required common phases and every applicable conditional phase must be dispositioned; "
            "exactly one X-origin, storage, and install path applies; raw install additionally requires "
            "the raw-download branch; optional VM and failure-only NVML results remain independently scoped."
        ),
    )
    recompute_source_context(procedure)
    actions.append(
        action_record(
            "EXTEND-HDL-E01",
            "STRUCTURAL_PATH_EXTENSION",
            "HDL-E01",
            ["HDL-E01"],
            "The stateful journey now has real existing-storage and raw-download branches plus canonical acyclic edges/groups.",
        )
    )

    # MNT-E01: one scale selector feeds a common maintenance and return-to-service tail.
    procedure = get_procedure(candidate, "MNT-E01")
    single = get_branch(procedure, "MNT-E01-B01")
    fleet = get_branch(procedure, "MNT-E01-B02")
    moved = copy.deepcopy(single["steps"][2:])
    single["steps"] = single["steps"][:2]
    moved_map = {
        moved[0]["id"]: "MNT-E01-B-common-S01",
        moved[1]["id"]: "MNT-E01-B-common-S02",
        moved[2]["id"]: "MNT-E01-B-common-S04",
    }
    for step in moved:
        old_id = str(step["id"])
        step["id"] = moved_map[old_id]
        step_remap[old_id] = [step["id"]]
    moved[0]["dependencies"] = []
    moved[1]["dependencies"] = [moved[0]["id"]]
    moved[2]["dependencies"] = ["MNT-E01-B-common-S03"]
    action_step = clone_step(
        moved[2],
        step_id="MNT-E01-B-common-S03",
        role="action",
        instruction="Hand off the exact authorized maintenance action to its accountable owner and consume its end-state evidence.",
        dependencies=[moved[1]["id"]],
        expected=["The selected maintenance owner records the action, abort conditions, rollback, and resulting Host state."],
        failure=["No generic maintenance mutation is executed while the exact child owner or authorization is unresolved."],
    )
    relist_step = clone_step(
        moved[2],
        step_id="MNT-E01-B-common-S05",
        role="action",
        instruction="Restore the reviewed listing/offer only after health and downstream checks satisfy the planned end state.",
        dependencies=[moved[2]["id"]],
        expected=["The intended future offer/listing state is restored without changing accepted contracts."],
        failure=["Failed health or unresolved verification effect blocks relisting."],
    )
    final_step = clone_step(
        moved[2],
        step_id="MNT-E01-B-common-S06",
        role="checkpoint",
        instruction="Confirm the selected machines are healthy and intentionally able to accept new rentals.",
        dependencies=[relist_step["id"]],
        expected=["Health, offer restoration, and accept-new-rentals state match the maintenance plan."],
        failure=["Any residual issue keeps the affected machine unlisted and non-ready."],
    )
    common = {
        "id": "MNT-E01-B-common",
        "condition": "The selected single machine or bounded fleet has an approved maintenance boundary",
        "status": "UNVALIDATED",
        "steps": [moved[0], moved[1], action_step, moved[2], relist_step, final_step],
        "access_override": None,
        "execution_gate": copy.deepcopy(single["execution_gate"]),
    }
    procedure["branches"] = [single, fleet, common]
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[
            edge("MNT-E01-B01", "MNT-E01-B-common", "HANDOFF"),
            edge("MNT-E01-B02", "MNT-E01-B-common", "HANDOFF"),
        ],
        groups=[group("GRP-MNT-E01-SCALE", "ONE_OF", ["MNT-E01-B01", "MNT-E01-B02"])],
        pass_rule=(
            "Exactly one scale-selection branch must be dispositioned, followed by the common "
            "wait, unlist, owned-maintenance handoff, health, offer-restoration, and accept-new-rentals tail."
        ),
    )
    branch_remap["MNT-E01-B01"] = ["MNT-E01-B01", "MNT-E01-B-common"]
    recompute_source_context(procedure)
    actions.append(
        action_record(
            "EXTEND-MNT-E01",
            "STRUCTURAL_PATH_EXTENSION",
            "MNT-E01",
            ["MNT-E01"],
            "ONE_OF(single, fleet) now feeds a real common maintenance/return-to-service tail with no duplicated mutation.",
        )
    )

    return actions


def apply_existing_id_repairs(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []

    procedure = get_procedure(candidate, "HOV-C01")
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[
            edge("HOV-C01-B-offer-contract", "HOV-C01-B-volume"),
            edge("HOV-C01-B-offer-contract", "HOV-C01-B-maintenance"),
        ],
        groups=[
            group("GRP-HOV-VOLUME", "CONDITIONAL", ["HOV-C01-B-volume"]),
            group("GRP-HOV-MAINTENANCE", "CONDITIONAL", ["HOV-C01-B-maintenance"]),
        ],
        pass_rule=(
            "The offer/contract branch is required; volume and maintenance claim bundles are "
            "independently conditional, and agreement/policy authority remains owned by exact handoffs."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-HOV-C01",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "HOV-C01",
            ["HOV-C01"],
            "Existing offer, volume, and maintenance IDs now form one required core plus independent conditional bundles.",
        )
    )

    procedure = get_procedure(candidate, "NET-E03")
    for branch in procedure["branches"]:
        if branch["id"] in NET_LIVE_BRANCHES:
            branch["execution_gate"]["access_requirements"] = [
                "HOST_VV_TARGET",
                "TEMPORARY_LISTENER_CAPTURE",
                "WAN_EXTERNAL_PROBE",
            ]
            branch["execution_gate"]["safety_requirements"] = [
                "Use one confirmed-unused approved port and exact protocol/endpoint/window.",
                "Use separate Host and external-client sessions with an overall timeout.",
                "Capture exact listener/capture PID ownership; do not capture renter traffic.",
                "Stop exact client/listener/capture processes and prove port/process absence.",
                "Do not expose restricted WAN or target coordinates in public evidence.",
            ]
        elif branch["id"] == "NET-E03-B-failure":
            branch["execution_gate"]["access_requirements"] = [
                "STATIC_SOURCE_INSPECTION",
                "COMPOSITE_DELEGATED_ONLY",
            ]
            branch["execution_gate"]["safety_requirements"] = [
                "No live error induction or inherited child result is allowed in the failure-only route."
            ]
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[],
        groups=[
            group(
                "GRP-NET-E03-TCP",
                "ONE_OF",
                ["NET-E03-B-tcp-unix", "NET-E03-B-tcp-windows"],
                label="external-client operating system for TCP",
            ),
            group(
                "GRP-NET-E03-UDP",
                "ONE_OF",
                ["NET-E03-B-udp-unix", "NET-E03-B-udp-windows"],
                label="external-client operating system for UDP",
            ),
            group_of_groups(
                "GRP-NET-E03-PROTOCOLS",
                "ALL_OF",
                ["GRP-NET-E03-TCP", "GRP-NET-E03-UDP"],
                label="both protocol obligations",
            ),
            group("GRP-NET-E03-FAILURE", "FAILURE_ONLY", ["NET-E03-B-failure"]),
        ],
        pass_rule=(
            "Both protocol obligations are required: exactly one TCP client-OS branch and exactly "
            "one UDP client-OS branch must have their own Host/client/cleanup evidence; the failure branch is diagnostic only."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-NET-E03",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "NET-E03",
            ["NET-E03"],
            "Two required ONE_OF groups express TCP and UDP without synthetic nodes; every live OS path retains Host-listener and WAN gates.",
        )
    )

    procedure = get_procedure(candidate, "PAY-E02")
    configure_model(
        procedure,
        state="ONE_OF",
        edges=[],
        groups=[group("GRP-PAY-E02-RECORD", "ONE_OF", ["PAY-E02-B01", "PAY-E02-B02"])],
        pass_rule=(
            "Exactly one requested record type applies per attempt; its access, private retention, "
            "output scope, and cleanup remain independently dispositioned."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-PAY-E02",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "PAY-E02",
            ["PAY-E02"],
            "The existing payout/earnings and billing-history branches are selected ONE_OF by requested record type.",
        )
    )

    procedure = get_procedure(candidate, "PAY-T01")
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[
            edge("PAY-T01-B03", "PAY-T01-B01"),
            edge("PAY-T01-B03", "PAY-T01-B02"),
        ],
        groups=[group("GRP-PAY-T01-SYMPTOM", "ONE_OF", ["PAY-T01-B01", "PAY-T01-B02"])],
        pass_rule=(
            "The source-basis branch is always required before exactly one observed symptom branch; "
            "UI state alone cannot establish current payout policy authority."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-PAY-T01",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "PAY-T01",
            ["PAY-T01"],
            "The existing source-basis branch now precedes a canonical ONE_OF symptom group.",
        )
    )

    procedure = get_procedure(candidate, "PRICE-E01")
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[edge("PRICE-E01-change", "PRICE-E01-adjust")],
        groups=[group("GRP-PRICE-E01-ADJUST", "CONDITIONAL", ["PRICE-E01-adjust"])],
        pass_rule=(
            "PRICE-C01's exact handoff must establish terms before the required change branch; "
            "a later adjustment is conditional on observed post-change signal and never rewrites accepted contracts."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-PRICE-E01",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "PRICE-E01",
            ["PRICE-E01"],
            "The existing change branch precedes an explicitly conditional adjustment; PRICE-C01 remains an external handoff owner.",
        )
    )

    procedure = get_procedure(candidate, "SHW-C01")
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[],
        groups=[
            group(
                "GRP-SHW-C01-VENDOR",
                "ONE_OF",
                ["SHW-C01-B-nvidia", "SHW-C01-B-amd"],
                label="candidate GPU vendor",
            ),
            group(
                "GRP-SHW-C01-FIT",
                "OUTCOME",
                ["SHW-C01-B-unsupported"],
                label="negative fit outcome when supported/conditional criteria are not met",
            ),
        ],
        pass_rule=(
            "Exactly one vendor path is evaluated; unsupported is a negative fit outcome, not a peer vendor "
            "and never satisfies a purchase/readiness success claim."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-SHW-C01",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "SHW-C01",
            ["SHW-C01"],
            "Existing NVIDIA/AMD IDs select vendor while unsupported is typed separately as a negative fit outcome.",
        )
    )

    procedure = get_procedure(candidate, "ST-T01")
    # Make each path's gate reflect its actual method instead of a copied aggregate.
    get_branch(procedure, "ST-T01-not-rentable")["execution_gate"]["access_requirements"] = [
        "credentialed-read-only",
        "host-read-only",
        "source/static-inspection",
    ]
    get_branch(procedure, "ST-T01-fresh-install")["execution_gate"]["access_requirements"] = [
        "HOST_VV_TARGET",
        "host-privileged-read-only",
        "bounded-log-follower",
    ]
    get_branch(procedure, "ST-T01-ignore-requirements")["execution_gate"]["access_requirements"] = [
        "source/static-inspection",
        "COMPOSITE_DELEGATED_ONLY",
        "paid-child-ST-E01",
    ]
    configure_model(
        procedure,
        state="CONDITIONAL",
        edges=[],
        groups=[
            group(
                "GRP-ST-T01-APPLICABLE",
                "CONDITIONAL_ONE_OR_MORE",
                ["ST-T01-not-rentable", "ST-T01-fresh-install", "ST-T01-ignore-requirements"],
            )
        ],
        pass_rule=(
            "Every applicable symptom/mode branch has its own gate and diagnostic outcome; not-rentable, "
            "fresh-install log watching, or ignore mode cannot imply qualification or inherit ST-E01 PASS."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-ST-T01",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "ST-T01",
            ["ST-T01"],
            "Existing symptom and mode paths are applicability-selected with distinct access, cleanup, and diagnostic limits.",
        )
    )

    procedure = get_procedure(candidate, "STR-C02")
    static_branches = [
        "STR-C02-results",
        "STR-C02-preflight",
        "STR-C02-images",
        "STR-C02-runtime",
        "STR-C02-offer",
        "STR-C02-ports",
        "STR-C02-runtime-errors",
    ]
    configure_model(
        procedure,
        state="MIXED_TYPED_GRAPH",
        edges=[],
        groups=[
            group("GRP-STR-C02-STATIC", "ALL_OF", static_branches),
            group("GRP-STR-C02-NCCL", "FAILURE_ONLY", ["STR-C02-nccl"]),
            group("GRP-STR-C02-BUNDLES", "FAILURE_ONLY", ["STR-C02-bundles"]),
        ],
        pass_rule=(
            "All seven static generated-contract bundles require source/generator evidence; NCCL and bundle "
            "branches are failure-only delegated paths and cannot inherit or confer runtime PASS in STR-C02."
        ),
    )
    actions.append(
        action_record(
            "REPAIR-STR-C02",
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR",
            "STR-C02",
            ["STR-C02"],
            "Existing static bundles remain one ALL_OF contract group; NCCL and bundle actions delegate to exact runtime owners.",
        )
    )

    return actions


def apply_mixed_access_blockers(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for procedure_id, branch_id in sorted(MIXED_ACCESS_BRANCHES):
        procedure = get_procedure(candidate, procedure_id)
        branch = get_branch(procedure, branch_id)
        gate = branch["execution_gate"]
        gate["access_requirements"] = dedupe(
            list(gate["access_requirements"]) + ["MIXED_ACCESS_SPLIT_REQUIRED"]
        )
        gate["safety_requirements"] = dedupe(
            list(gate["safety_requirements"])
            + [
                "Do not execute this mixed observation/mutation/load/retest branch as one unit; separately gated owners are required."
            ]
        )
        blockers.append(
            {
                "id": f"BLOCKER-MIXED-{branch_id}",
                "blocker_class": "MIXED_ACCESS_SPLIT_REQUIRED",
                "procedure_id": procedure_id,
                "branch_id": branch_id,
                "required_resolution": (
                    "Split observation, mutation/destructive/financial/load action, and retest into "
                    "separately gated owned paths before P1 freeze or execution."
                ),
                "freeze_blocking": True,
                "vv_status": "UNVALIDATED",
            }
        )
    return blockers


def build_model_coverage(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for procedure in sorted(candidate["procedures"], key=lambda item: item["id"]):
        branch_ids = [branch["id"] for branch in procedure["branches"]]
        model = procedure["branch_execution_model"]
        if model["state"] == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED":
            records.append(
                {
                    "procedure_id": procedure["id"],
                    "model_state": model["state"],
                    "required_branch_ids": [],
                    "grouped_branch_ids": [],
                    "unresolved_branch_ids": branch_ids,
                    "coverage_state": "UNRESOLVED_FREEZE_BLOCKING",
                    "vv_status": "UNVALIDATED",
                }
            )
            continue
        grouped: list[str] = []
        for typed_group in model["alternative_groups"]:
            grouped.extend(typed_group.get("branch_ids", []))
        required = [branch_id for branch_id in branch_ids if branch_id not in set(grouped)]
        records.append(
            {
                "procedure_id": procedure["id"],
                "model_state": model["state"],
                "required_branch_ids": required,
                "grouped_branch_ids": grouped,
                "unresolved_branch_ids": [],
                "coverage_state": "EXHAUSTIVE_DRAFT_MODEL",
                "vv_status": "UNVALIDATED",
            }
        )
    return records


def build_branch_outcomes(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    outcome_overrides: dict[tuple[str, str], tuple[str, bool, str]] = {
        ("COM-E03", "COM-E03-B01"): (
            "ROUTING_DECISION",
            False,
            "Routing correctness cannot inherit the downstream support/community result.",
        ),
        ("FLT-E07", "FLT-E07-B01"): (
            "DELEGATED_PATH",
            False,
            "The fleet owner supplies a bounded handoff; RM-E02 owns destructive outcome/evidence.",
        ),
        ("HDL-E01", "HDL-E01-B-storage-existing"): (
            "DELEGATED_PATH",
            False,
            "STO-E02 owns existing-storage runtime evidence and cleanup.",
        ),
        ("HDL-E01", "HDL-E01-B-install-raw-download"): (
            "DELEGATED_PATH",
            False,
            "The canonical installer owner must supply an exact source/download result.",
        ),
        ("HDL-E01", "HDL-E01-B-nvml-failure"): (
            "FAILURE_ONLY_DIAGNOSTIC",
            False,
            "Failure-only driver/NVML diagnosis cannot satisfy the normal install path.",
        ),
        ("NET-E03", "NET-E03-B-failure"): (
            "FAILURE_ONLY_DIAGNOSTIC",
            False,
            "A timeout/networking-error diagnosis cannot satisfy TCP or UDP reachability.",
        ),
        ("SHW-C01", "SHW-C01-B-unsupported"): (
            "NEGATIVE_FIT_OUTCOME",
            False,
            "Unsupported fit is a valid decision outcome but not a readiness success.",
        ),
        ("ST-T01", "ST-T01-not-rentable"): (
            "DIAGNOSTIC_ONLY",
            False,
            "Not-rentable diagnosis cannot establish qualification.",
        ),
        ("ST-T01", "ST-T01-fresh-install"): (
            "DIAGNOSTIC_ONLY",
            False,
            "Log watching observes an installer-started child attempt but cannot inherit its result.",
        ),
        ("ST-T01", "ST-T01-ignore-requirements"): (
            "DIAGNOSTIC_ONLY",
            False,
            "Ignore-requirements mode is diagnostic only and remains delegated to ST-E01.",
        ),
        ("STR-C02", "STR-C02-nccl"): (
            "DELEGATED_PATH",
            False,
            "ERR-T04 owns applicable Host NCCL/Fabric diagnosis and evidence.",
        ),
        ("STR-C02", "STR-C02-bundles"): (
            "DELEGATED_PATH",
            False,
            "DIA-E01 owns bundle creation, secret review, retention, and cleanup evidence.",
        ),
    }
    static_str = {
        "STR-C02-results",
        "STR-C02-preflight",
        "STR-C02-images",
        "STR-C02-runtime",
        "STR-C02-offer",
        "STR-C02-ports",
        "STR-C02-runtime-errors",
    }
    records: list[dict[str, Any]] = []
    for procedure in sorted(candidate["procedures"], key=lambda item: item["id"]):
        conditional_branches = {
            branch_id
            for typed_group in procedure["branch_execution_model"]["alternative_groups"]
            if typed_group["type"]
            in {
                "CONDITIONAL",
                "CONDITIONAL_ALL_APPLICABLE",
                "CONDITIONAL_ONE_OR_MORE",
                "OPTIONAL_ONE_OF",
            }
            for branch_id in typed_group.get("branch_ids", [])
        }
        failure_branches = {
            branch_id
            for typed_group in procedure["branch_execution_model"]["alternative_groups"]
            if typed_group["type"] == "FAILURE_ONLY"
            for branch_id in typed_group.get("branch_ids", [])
        }
        for branch in procedure["branches"]:
            key = (procedure["id"], branch["id"])
            if key in outcome_overrides:
                outcome_class, contributes, boundary = outcome_overrides[key]
            elif procedure["id"] == "STR-C02" and branch["id"] in static_str:
                outcome_class, contributes, boundary = (
                    "STATIC_CLAIM_BUNDLE",
                    True,
                    "Static source/generator conformance is bounded to the reference claim and is not runtime validation.",
                )
            elif branch["id"] in failure_branches:
                outcome_class, contributes, boundary = (
                    "FAILURE_ONLY_DIAGNOSTIC",
                    False,
                    "Failure-only evidence is scoped to diagnosis/remediation and cannot satisfy the normal path.",
                )
            elif branch["id"] in conditional_branches:
                outcome_class, contributes, boundary = (
                    "CONDITIONAL_SUCCESS_PATH",
                    True,
                    "This branch contributes only when its recorded applicability predicate is true.",
                )
            else:
                outcome_class, contributes, boundary = (
                    "APPLICABLE_SUCCESS_PATH",
                    True,
                    "This branch contributes only within the procedure's pass rule and never by alias or inference.",
                )
            records.append(
                {
                    "procedure_id": procedure["id"],
                    "branch_id": branch["id"],
                    "outcome_class": outcome_class,
                    "contributes_to_parent_pass_when_applicable": contributes,
                    "claim_boundary": boundary,
                    "vv_status": "UNVALIDATED",
                }
            )
    return records


def owner_requirement(owner_type: str, owner_id: str) -> dict[str, str]:
    collection = "procedures" if owner_type == "PROCEDURE" else "support_contracts"
    return {
        "owner_type": owner_type,
        "owner_id": owner_id,
        "required_outcome_ref": f"{collection}/{owner_id}/expected_final_observables"
        if owner_type == "PROCEDURE"
        else f"{collection}/{owner_id}/expected_observables",
        "required_evidence_ref": f"{collection}/{owner_id}/evidence_plan/evidence_refs"
        if owner_type == "PROCEDURE"
        else f"{collection}/{owner_id}/evidence_refs",
    }


def handoff_binding(
    binding_id: str,
    source_procedure_id: str,
    source_branch_id: str | None,
    targets: list[tuple[str, str]],
    trigger: str,
    applicability: str,
    required_order: str,
) -> dict[str, Any]:
    return {
        "id": binding_id,
        "source_procedure_id": source_procedure_id,
        "source_branch_id": source_branch_id,
        "target_requirements": [owner_requirement(kind, owner_id) for kind, owner_id in targets],
        "trigger_predicate": trigger,
        "applicability_predicate": applicability,
        "required_order": required_order,
        "access_inheritance_rule": "Each target keeps its own access/safety gate; source authorization never broadens it.",
        "cleanup_inheritance_rule": "Each executed target owns and proves its cleanup/end state; the source does not duplicate it.",
        "parent_rollup_rule": "NO_PARENT_PASS_BY_ALIAS_OR_HANDOFF",
        "vv_status": "UNVALIDATED",
    }


def build_cross_page_handoffs(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    families: dict[str, list[dict[str, Any]]] = {key: [] for key in (
        "HANDOFF-SETUP-001",
        "HANDOFF-HOV-001",
        "HANDOFF-QST-001",
        "HANDOFF-HDL-001",
        "HANDOFF-FLT-RM-001",
        "HANDOFF-ERROR-OWNERS-001",
        "HANDOFF-STR-001",
        "HANDOFF-API-001",
    )}

    setup_sources = ["FIT-C01", "SHW-C01", "SHW-C02"]
    setup_targets = [
        "ACC-E01", "SEC-E01", "SEC-E02", "HWP-E01", "HWP-C01", "STO-E01",
        "STO-E02", "STO-E03", "NET-E01", "NET-E02", "INS-E01", "INS-E02",
        "HDL-E01", "PRICE-C01", "PRICE-E01", "ST-E01", "STR-C01", "STR-C02",
        "VER-C01", "VST-C01", "VST-C02", "DAY1-E01", "DAY1-E02",
    ]
    for source in setup_sources:
        families["HANDOFF-SETUP-001"].append(
            handoff_binding(
                f"BIND-SETUP-{source}",
                source,
                None,
                [("PROCEDURE", target) for target in setup_targets],
                "The fit/hardware decision selects a documented Host setup journey.",
                "Only stages applicable to the selected persona, hardware, storage, install, and validation path apply.",
                "FIT/SHW -> ACC/SEC -> HWP/STO/NET -> ONE_OF(INS, HDL) -> PRICE -> ST/STR -> VER/VST -> DAY1",
            )
        )
    families["HANDOFF-SETUP-001"].append(
        handoff_binding(
            "BIND-SETUP-PRICE-C01-PRICE-E01",
            "PRICE-C01",
            "PRICE-C01-main",
            [("PROCEDURE", "PRICE-E01")],
            "Derived listing terms are ready for an authorized future-offer mutation.",
            "Only when PRICE-C01 authority and terms are current for the intended Host.",
            "PRICE-C01 -> PRICE-E01-change -> observation -> conditional PRICE-E01-adjust",
        )
    )

    hov_targets = [
        "FIT-C01", "ACC-E01", "SEC-E01", "HWP-C01", "STO-E02", "NET-E01",
        "INS-E01", "HDL-E01", "PRICE-E01", "ST-E01", "VER-C01", "DAY1-E01",
    ]
    families["HANDOFF-HOV-001"].append(
        handoff_binding(
            "BIND-HOV-ROUTE",
            "HOV-P01",
            "HOV-P01-B-main",
            [("PROCEDURE", target) for target in hov_targets],
            "The first-host orientation routes to a concrete child stage.",
            "Only child stages selected by the Host's current journey state apply.",
            "Orientation -> exact applicable child procedure; no duplicated child execution",
        )
    )
    families["HANDOFF-HOV-001"].append(
        handoff_binding(
            "BIND-HOV-CONTRACT-AUTHORITY",
            "HOV-C01",
            "HOV-C01-B-offer-contract",
            [("PROCEDURE", "AGR-C01"), ("PROCEDURE", "POL-C01")],
            "Offer/contract or availability/workload prose requires agreement or policy authority.",
            "When the claim crosses product contract, availability, or workload-policy boundaries.",
            "HOV-C01 claim inspection -> exact AGR-C01/POL-C01 authority outcome",
        )
    )

    qst_targets = [
        "FIT-C01", "SHW-C01", "ACC-E01", "SEC-E01", "HWP-C01", "STO-E02",
        "NET-E01", "INS-E01", "HDL-E01", "PRICE-C01", "PRICE-E01", "ST-E01",
        "VER-C01", "DAY1-E01", "EARN-C01", "PAY-E01",
    ]
    families["HANDOFF-QST-001"].append(
        handoff_binding(
            "BIND-QST-STAGES",
            "QST-P01",
            "QST-P01-B-main",
            [("PROCEDURE", target) for target in qst_targets],
            "The quickstart reaches the matching documented stage.",
            "Every applicable QST stage retains the exact child disposition; skipped stages need rationale.",
            "QST-S01 through QST-S08 -> exact child outcome/evidence references",
        )
    )

    hdl_targets = ["STO-E02", "STO-E03", "INS-E01", "INS-E02", "VM-E02", "NET-E03", "PRICE-E01", "ST-E01", "DAY1-E01"]
    families["HANDOFF-HDL-001"].append(
        handoff_binding(
            "BIND-HDL-CHILDREN",
            "HDL-E01",
            None,
            [("PROCEDURE", target) for target in hdl_targets],
            "A storage, install, VM, WAN, listing, paid-test, or first-day child owner is reached.",
            "Only the exact branch selected by current storage/install/hardware/journey state applies.",
            "Storage/install owner -> networking/final checks -> listing -> paid self-test -> DAY1 after cleanup",
        )
    )

    families["HANDOFF-FLT-RM-001"].append(
        handoff_binding(
            "BIND-FLT-DECOMMISSION-RM",
            "FLT-E07",
            "FLT-E07-B01",
            [("PROCEDURE", "RM-E02")],
            "One explicit fleet target passes read-only decommission preflight.",
            "Only with exact target, ended obligations, recovery plan, and destructive owner authorization.",
            "FLT-E07 preflight -> RM-E02 destructive action/outcome/cleanup",
        )
    )
    families["HANDOFF-FLT-RM-001"].append(
        handoff_binding(
            "BIND-MNT-HARDWARE-RM",
            "MNT-E01",
            "MNT-E01-B-common",
            [("PROCEDURE", "RM-E04")],
            "The selected maintenance action is a hardware replacement.",
            "Only the hardware-replacement maintenance subtype; other maintenance requires its exact accountable owner.",
            "MNT scale/preflight -> RM-E04 hardware action/qualification -> MNT health/relist tail",
        )
    )

    error_sources = ["DIA-E03", "ERR-T01", "ERR-T02", "ERR-T03", "ERR-T04", "ERR-T05", "ERR-T06"]
    error_targets = ["NET-E03", "STO-E02", "STO-E03", "VM-E02", "ST-E01", "DIA-E01"]
    for source in error_sources:
        families["HANDOFF-ERROR-OWNERS-001"].append(
            handoff_binding(
                f"BIND-ERROR-{source}",
                source,
                None,
                [("PROCEDURE", target) for target in error_targets],
                "Read-only diagnosis identifies an exact correction or evidence owner.",
                "Only the target matching the observed symptom and required access applies.",
                "Exact symptom -> read-only diagnosis -> authorized owner procedure -> linked retest",
            )
        )

    for binding_id, branch_id, target in (
        ("BIND-STR-RESULTS-ST", "STR-C02-results", "ST-E01"),
        ("BIND-STR-NCCL-ERR", "STR-C02-nccl", "ERR-T04"),
        ("BIND-STR-BUNDLE-DIA", "STR-C02-bundles", "DIA-E01"),
        ("BIND-STR-PORTS-NET", "STR-C02-ports", "NET-E03"),
    ):
        families["HANDOFF-STR-001"].append(
            handoff_binding(
                binding_id,
                "STR-C02",
                branch_id,
                [("PROCEDURE", target)],
                "The static reference occurrence requires separately gated runtime or diagnostic evidence.",
                f"Only when {branch_id} is applicable to the observed result/failure.",
                f"STR-C02 static claim -> {target} owned result/evidence/cleanup",
            )
        )

    command_owner_map = {
        "cancel-maint": ["FLT-E03", "MNT-E02", "TEAM-E03"],
        "cleanup-machine": ["FLT-E06", "RM-E01", "TEAM-E03"],
        "defrag-machines": ["FLT-E05", "TEAM-E03"],
        "delete-machine": ["RM-E02"],
        "list-machine": ["MNT-E01", "PRICE-E01"],
        "list-machines": ["FLT-E02", "MNT-E01", "TEAM-E03"],
        "metrics-gpu": ["MET-E02", "TEAM-E04"],
        "metrics-gpu-locations": ["MET-E02", "TEAM-E04"],
        "metrics-gpu-trends": ["MET-E02", "TEAM-E04"],
        "remove-defjob": ["FLT-E04", "TEAM-E03"],
        "schedule-maint": ["FLT-E03", "MNT-E02", "TEAM-E03"],
        "self-test-machine": ["DIA-E01", "ST-E01", "STR-C02", "TEAM-E03"],
        "set-defjob": ["FLT-E04", "TEAM-E03"],
        "set-min-bid": ["PRICE-E01", "TEAM-E03"],
        "show-machine": ["FLT-E01", "MNT-E01", "TEAM-E03"],
        "show-machines": ["FLT-E01", "FLT-E05", "MNT-E01", "TEAM-E03"],
        "show-maints": ["FLT-E03", "MNT-E02", "MNT-E03"],
        "unlist-machine": ["MNT-E01", "RM-E01", "TEAM-E03"],
    }
    wrapper_contracts = [
        contract
        for contract in candidate["support_contracts"]
        if contract["kind"] == "wrapper-import-render-contract"
    ]
    for contract in sorted(wrapper_contracts, key=lambda item: item["id"]):
        match = re.match(r"SUPPORT-CONTRACT-host-(?:cli|sdk)-(.+)$", contract["id"])
        if match is None or match.group(1) not in command_owner_map:
            raise CandidateError(f"API handoff lacks owner mapping for {contract['id']}")
        slug = match.group(1)
        targets = [("SUPPORT_CONTRACT", contract["id"])] + [
            ("PROCEDURE", owner_id) for owner_id in command_owner_map[slug]
        ]
        families["HANDOFF-API-001"].append(
            handoff_binding(
                f"BIND-API-{contract['id'].removeprefix('SUPPORT-CONTRACT-host-')}",
                "API-P01",
                "API-P01-workflows",
                targets,
                f"The selected Host workflow uses the {slug} CLI/SDK contract.",
                "Exactly one interface/reference is selected and every mutating child retains its own authority gate.",
                "Authenticate -> exact wrapper/source contract -> exact owning Host procedure",
            )
        )

    records: list[dict[str, Any]] = []
    for family_id in sorted(families):
        records.append(
            {
                "id": family_id,
                "relation": "HANDOFF",
                "bindings": sorted(families[family_id], key=lambda item: item["id"]),
                "family_rollup_rule": "No source procedure inherits a target status, attempt, evidence, authority, or cleanup result.",
                "vv_status": "UNVALIDATED",
            }
        )
    return records


def sync_claim_and_reverse_indexes(candidate: dict[str, Any]) -> None:
    assembler = load_assembler()
    claim_owner: dict[str, tuple[str, str, str]] = {}
    step_by_id: dict[str, dict[str, Any]] = {}
    for procedure in candidate["procedures"]:
        for branch in procedure["branches"]:
            for step in branch["steps"]:
                step_by_id[step["id"]] = step
                for claim_id in step["claim_ids"]:
                    if claim_id in claim_owner:
                        raise CandidateError(f"claim {claim_id} is owned by more than one step")
                    claim_owner[claim_id] = (procedure["id"], branch["id"], step["id"])

    claim_by_id = {claim["id"]: claim for claim in candidate["claims"]}
    for claim in candidate["claims"]:
        if claim["step_id"] is None:
            continue
        if claim["id"] not in claim_owner:
            raise CandidateError(f"step-bound claim {claim['id']} has no candidate step owner")
        procedure_id, branch_id, step_id = claim_owner[claim["id"]]
        claim["procedure_id"] = procedure_id
        claim["branch_id"] = branch_id
        claim["step_id"] = step_id
        claim["source_alignment"] = assembler.computed_source_alignment(
            claim["source"], step_by_id[step_id]
        )

    for row in candidate["legacy_crosswalk"]:
        claim = claim_by_id[row["claim_id"]]
        for field in (
            "page_id",
            "procedure_id",
            "branch_id",
            "step_id",
            "supporting_route_id",
            "fragment_id",
        ):
            row[field] = claim[field]
        row["source_alignment"] = claim["source_alignment"]

    by_procedure: dict[str, list[str]] = defaultdict(list)
    by_page_claim: dict[str, list[str]] = defaultdict(list)
    for claim in candidate["claims"]:
        if claim["procedure_id"] is not None:
            by_procedure[claim["procedure_id"]].append(claim["id"])
        by_page_claim[claim["page_id"]].append(claim["id"])
    for procedure in candidate["procedures"]:
        procedure["claim_ids"] = sorted(by_procedure[procedure["id"]])

    candidate["procedures"] = sorted(candidate["procedures"], key=lambda item: item["id"])
    by_page_proc: dict[str, list[str]] = defaultdict(list)
    for procedure in candidate["procedures"]:
        by_page_proc[procedure["page_id"]].append(procedure["id"])
    for page in candidate["pages"]:
        page["procedure_ids"] = sorted(by_page_proc[page["id"]])
        page["claim_ids"] = sorted(by_page_claim[page["id"]])


def carrier_fingerprint(baseline: dict[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    for procedure in baseline["procedures"]:
        for branch in procedure["branches"]:
            for step in branch["steps"]:
                for carrier in step["source_carriers"]:
                    result[sha256_json(carrier)] += 1
    return result


def immutable_claim_fingerprint(baseline: dict[str, Any]) -> dict[str, str]:
    mutable_owner_fields = {
        "procedure_id",
        "branch_id",
        "step_id",
        "source_alignment",
    }
    return {
        claim["id"]: sha256_json(
            {key: value for key, value in claim.items() if key not in mutable_owner_fields}
        )
        for claim in baseline["claims"]
    }


def update_reconciliation_counts(candidate: dict[str, Any]) -> None:
    candidate["reconciliation"]["pages"] = len(candidate["pages"])
    candidate["reconciliation"]["procedures"] = len(candidate["procedures"])
    candidate["reconciliation"]["branches"] = sum(
        len(procedure["branches"]) for procedure in candidate["procedures"]
    )
    candidate["reconciliation"]["steps"] = sum(
        len(branch["steps"])
        for procedure in candidate["procedures"]
        for branch in procedure["branches"]
    )
    candidate["reconciliation"]["claims"] = len(candidate["claims"])
    candidate["reconciliation"]["legacy_crosswalk_rows"] = len(
        candidate["legacy_crosswalk"]
    )
    candidate["reconciliation"]["source_alignment_counts"] = dict(
        sorted(
            Counter(
                str(row["source_alignment"])
                for row in candidate["legacy_crosswalk"]
            ).items()
        )
    )
    candidate["reconciliation"]["independent_second_pass"] = "PENDING"
    candidate["reconciliation"]["same_agent_limit"] = (
        "This derivative topology candidate was produced after an independent design review, "
        "but its applied graph still requires a new independent full-baseline reconciliation."
    )


def candidate_content_hash(candidate: dict[str, Any]) -> str:
    projection = copy.deepcopy(candidate)
    projection.get("topology_candidate", {}).pop("content_sha256_excluding_self", None)
    return sha256_json(projection)


def build_candidate() -> tuple[dict[str, Any], dict[str, Any]]:
    observed_hashes = assert_pinned_inputs()
    canonical = load_json(CANONICAL_PATH)
    review = load_json(REVIEW_PATH)
    rejected_manifest = load_json(REJECTED_MANIFEST_PATH)
    full_reconcile = load_json(FULL_RECONCILE_PATH)
    if review.get("verdict", {}).get("decision") != "REJECT_NOT_INTEGRATION_READY":
        raise CandidateError("independent review verdict changed unexpectedly")
    if rejected_manifest.get("manifest_state") != "PROPOSED_CORRECTIONS_NOT_APPLIED_NOT_FROZEN":
        raise CandidateError("rejected manifest state changed unexpectedly")
    if (
        review.get("authority_and_provenance", {})
        .get("artifacts", {})
        .get("full_reconcile_report_sha256")
        != observed_hashes["full_reconcile_sha256"]
    ):
        raise CandidateError("independent review/full-reconcile provenance link changed")
    carrier_claim_by_source_hash = {
        carrier["source"]["text_sha256"]: carrier["claim_id"]
        for procedure in canonical["procedures"]
        for branch in procedure["branches"]
        for step in branch["steps"]
        for carrier in step["source_carriers"]
    }
    reviewed_static_team_claims = {
        carrier_claim_by_source_hash[record["source"]["text_sha256"]]
        for record in full_reconcile.get("source_alignment_review", {}).get("records", [])
        if record.get("disposition") == "REASSIGN_TO_STATIC_TEAM_COMMAND_CATALOG"
    }
    if reviewed_static_team_claims != STATIC_TEAM_CATALOG_REASSIGN_CLAIMS:
        raise CandidateError("reviewed static-team carrier disposition set changed")

    candidate = copy.deepcopy(canonical)
    candidate["schema_version"] = "1.1-topology-candidate"
    candidate["state"] = "DRAFT_NOT_FROZEN"
    candidate["freeze"]["state"] = "NOT_FROZEN"
    candidate["freeze"]["frozen_at"] = None
    candidate["freeze"]["reconciler"] = None
    candidate["freeze"]["blocking_checks"] = dedupe(
        list(candidate["freeze"]["blocking_checks"])
        + [
            "Applied topology candidate requires a new independent full-baseline reconciliation.",
            "Mixed-access branch blockers, safe command forms, raw/rendered coverage, and source defects remain unresolved.",
        ]
    )
    candidate["freeze"]["change_record"].append(
        {
            "event": "BUILD_ISOLATED_TOPOLOGY_CANDIDATE",
            "predecessor": canonical["baseline_id"],
            "disposition": "DRAFT_NOT_FROZEN_AWAITING_INDEPENDENT_RECONCILIATION",
            "history_preserved": True,
        }
    )
    candidate["execution_readiness"]["new_live_execution_allowed"] = False
    candidate["completion_and_acceptance"]["evidence_package_complete"] = False
    candidate["completion_and_acceptance"]["target_acceptance_candidate"] = False

    procedure_remap: dict[str, list[str]] = {}
    branch_remap: dict[str, list[str]] = {}
    step_remap: dict[str, list[str]] = {}
    actions = apply_genuine_splits(
        candidate, procedure_remap, branch_remap, step_remap
    )
    team_catalog_reassignments = consolidate_team_catalog_ownership(
        candidate, procedure_remap, branch_remap, step_remap
    )
    actions.extend(apply_structural_extensions(candidate, branch_remap, step_remap))
    actions.extend(apply_existing_id_repairs(candidate))
    if {record["id"] for record in actions} != EXPECTED_ACTION_IDS:
        raise CandidateError("normalized action implementation is not the exact reviewed 7/3/8 set")

    mixed_blockers = apply_mixed_access_blockers(candidate)
    sync_claim_and_reverse_indexes(candidate)
    update_reconciliation_counts(candidate)
    candidate["cross_page_handoffs"] = build_cross_page_handoffs(candidate)
    candidate["branch_outcomes"] = build_branch_outcomes(candidate)
    model_coverage = build_model_coverage(candidate)

    unresolved_model_ids = [
        record["procedure_id"]
        for record in model_coverage
        if record["coverage_state"] == "UNRESOLVED_FREEZE_BLOCKING"
    ]
    unresolved_blockers = [
        {
            "id": "BLOCKER-HDL-RAW-INSTALLER-SOURCE",
            "blocker_class": "DOCUMENTATION_SOURCE_DEFECT",
            "procedure_id": "HDL-E01",
            "branch_id": "HDL-E01-B-install-raw-download",
            "reason": "The Host page selects raw fallback but does not state an exact current raw-installer download path/source identity.",
            "required_resolution": "Correct the docs/source owner contract, retain the failure, and independently review the exact safe source form.",
            "freeze_blocking": True,
            "vv_status": "UNVALIDATED",
        },
        {
            "id": "BLOCKER-MNT-ACTION-OWNER",
            "blocker_class": "OWNER_SELECTION_REQUIRED",
            "procedure_id": "MNT-E01",
            "branch_id": "MNT-E01-B-common",
            "reason": "Hardware replacement has an exact RM-E04 binding; other maintenance action subtypes still require an exact accountable child owner at plan instantiation.",
            "required_resolution": "Bind the selected maintenance action to an exact owned procedure, gate, rollback, and outcome before execution.",
            "freeze_blocking": True,
            "vv_status": "UNVALIDATED",
        },
        {
            "id": "BLOCKER-INDEPENDENT-CANDIDATE-RECONCILIATION",
            "blocker_class": "INDEPENDENT_REVIEW_PENDING",
            "procedure_id": None,
            "branch_id": None,
            "reason": "The applied candidate has not received an independent full reconciliation against its current content hash.",
            "required_resolution": "Run a new independent current-candidate reconciliation and retain reviewer provenance before any promotion/freeze.",
            "freeze_blocking": True,
            "vv_status": "UNVALIDATED",
        },
        {
            "id": "BLOCKER-CANONICAL-INTEGRATION-PROVENANCE",
            "blocker_class": "SCHEMA_INTEGRATION_REQUIRED",
            "procedure_id": None,
            "branch_id": None,
            "reason": "The canonical assembler does not yet own the topology extension fields, and the original 82-procedure partition provenance must not be rewritten to imply it produced this 97-procedure derivative.",
            "required_resolution": "Extend and independently validate the canonical assembler/provenance contract or translate the reviewed topology losslessly before promotion.",
            "freeze_blocking": True,
            "vv_status": "UNVALIDATED",
        },
    ]
    unresolved_blockers.extend(mixed_blockers)
    unresolved_blockers.extend(
        {
            "id": f"BLOCKER-MODEL-{procedure_id}",
            "blocker_class": "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED",
            "procedure_id": procedure_id,
            "branch_id": None,
            "reason": "This non-target procedure retains its canonical unresolved multi-branch state.",
            "required_resolution": "Independently type and reconcile every real branch before P1 freeze.",
            "freeze_blocking": True,
            "vv_status": "UNVALIDATED",
        }
        for procedure_id in unresolved_model_ids
    )
    unresolved_safe_form_steps = [
        step
        for procedure in candidate["procedures"]
        for branch in procedure["branches"]
        for step in branch["steps"]
        if step["execution_form_state"]
        == "UNVALIDATED_SAFE_PARAMETERIZATION_REQUIRED"
    ]
    unresolved_safe_form_command_carriers = sum(
        carrier["kind"] == "command"
        for step in unresolved_safe_form_steps
        for carrier in step["source_carriers"]
    )
    static_non_executable_command_carriers = sum(
        carrier["kind"] == "command"
        for procedure in candidate["procedures"]
        for branch in procedure["branches"]
        for step in branch["steps"]
        if step["execution_form_state"] == "NOT_APPLICABLE_NON_COMMAND_STEP"
        for carrier in step["source_carriers"]
    )

    candidate["topology_candidate"] = {
        "record_type": "HOST_DOCS_P1_ISOLATED_TOPOLOGY_CANDIDATE",
        "candidate_state": "DRAFT_NOT_FROZEN_NOT_EXECUTION_AUTHORITY",
        "operating_mode": "PLAN_AND_EXECUTE_PLANNING_PHASE_ONLY_NO_LIVE_EXECUTION",
        "input_artifacts": {
            "canonical_baseline": {
                "artifact_ref": "verification/procedure-baseline-p1.json",
                "sha256": observed_hashes["canonical_baseline_sha256"],
            },
            "governing_goal": {
                "artifact_ref": "HOST-DOCS-PROCEDURE-VV-GOAL.md",
                "sha256": observed_hashes["governing_goal_sha256"],
            },
            "vv_evidence_skill": {
                "artifact_ref": "vv-evidence/SKILL.md",
                "sha256": observed_hashes["vv_evidence_skill_sha256"],
            },
            "canonical_assembler": {
                "artifact_ref": "scripts/assemble_procedure_baseline.py",
                "sha256": observed_hashes["canonical_assembler_sha256"],
            },
            "independent_topology_review": {
                "artifact_ref": "host-docs-p1-topology-review.json",
                "sha256": observed_hashes["independent_topology_review_sha256"],
            },
            "rejected_manifest": {
                "artifact_ref": "host-docs-p1-topology-corrections.json",
                "sha256": observed_hashes["rejected_manifest_sha256"],
            },
            "full_reconcile": {
                "artifact_ref": "host-docs-p1-full-reconcile.json",
                "sha256": observed_hashes["full_reconcile_sha256"],
            },
        },
        "claim_boundary": [
            "This is an isolated planning candidate, not canonical integration, P1 freeze, execution authority, PASS, acceptance, or approval.",
            "No Host, WAN, documented, credentialed, mutating, destructive, or paid command was executed by this builder.",
            "Legacy carriers and claims are preserved; claim-bundle and semantic-schema integration is intentionally excluded.",
        ],
        "normalized_actions": sorted(actions, key=lambda item: item["id"]),
        "id_remap": {
            "procedures": [
                {"old_id": old_id, "new_ids": new_ids}
                for old_id, new_ids in sorted(procedure_remap.items())
            ],
            "branches": [
                {"old_id": old_id, "new_ids": new_ids}
                for old_id, new_ids in sorted(branch_remap.items())
            ],
            "steps": [
                {"old_id": old_id, "new_ids": new_ids}
                for old_id, new_ids in sorted(step_remap.items())
            ],
        },
        "procedure_model_coverage": model_coverage,
        "unresolved_blockers": sorted(unresolved_blockers, key=lambda item: item["id"]),
        "blocker_register_scope": {
            "scope": "TOPOLOGY_DERIVATIVE_ONLY_NOT_COMPLETE_P1_FREEZE_REGISTER",
            "complete_p1_freeze_register": False,
            "topology_blocker_record_count": len(unresolved_blockers),
            "known_unenumerated_freeze_conditions": [
                "Safe executable parameterization remains unresolved for applicable command-bearing steps.",
                "Rendered-context coverage and generator/source-contract currentness remain inherited freeze checks.",
                "Canonical topology/schema composition and an independent current-composition reconciliation remain required.",
            ],
        },
        "freeze_gate": {
            "freeze_allowed": False,
            "live_execution_allowed": False,
            "blocking_record_ids": sorted(record["id"] for record in unresolved_blockers),
            "independent_reconciliation_complete": False,
            "human_acceptance": "NOT_DECIDED",
        },
        "counts": {},
        "content_sha256_excluding_self": None,
    }

    counts = {
        "split_action_domains": len(EXPECTED_SPLIT_ACTIONS),
        "structural_extension_domains": len(EXPECTED_EXTENSION_ACTIONS),
        "existing_id_repair_domains": len(EXPECTED_REPAIR_ACTIONS),
        "pages": len(candidate["pages"]),
        "procedures": len(candidate["procedures"]),
        "branches": sum(len(proc["branches"]) for proc in candidate["procedures"]),
        "steps": sum(
            len(branch["steps"])
            for proc in candidate["procedures"]
            for branch in proc["branches"]
        ),
        "claims": len(candidate["claims"]),
        "legacy_crosswalk_rows": len(candidate["legacy_crosswalk"]),
        "step_source_carriers": sum(
            len(step["source_carriers"])
            for proc in candidate["procedures"]
            for branch in proc["branches"]
            for step in branch["steps"]
        ),
        "cross_page_handoff_families": len(candidate["cross_page_handoffs"]),
        "cross_page_handoff_bindings": sum(
            len(record["bindings"]) for record in candidate["cross_page_handoffs"]
        ),
        "mixed_access_freeze_blockers": len(mixed_blockers),
        "unresolved_branch_models": len(unresolved_model_ids),
        "canonical_integration_schema_blockers": 1,
        "reviewed_static_team_catalog_reassignments": team_catalog_reassignments,
        "unresolved_safe_parameterization_steps": len(unresolved_safe_form_steps),
        "unresolved_safe_parameterization_command_carriers": unresolved_safe_form_command_carriers,
        "static_non_executable_command_carriers": static_non_executable_command_carriers,
    }
    candidate["topology_candidate"]["counts"] = counts

    assembler = load_assembler()
    identity_payload = assembler.plan_identity_payload(candidate)
    candidate["plan_baseline_sha256"] = sha256_json(identity_payload)
    target_revision = str(candidate["source_identity"]["docs_target_revision"])
    candidate["baseline_id"] = (
        f"P1-DRAFT-{target_revision[:12]}-{candidate['plan_baseline_sha256'][:12]}"
    )
    candidate["topology_candidate"]["content_sha256_excluding_self"] = candidate_content_hash(candidate)

    metadata = {
        "canonical": canonical,
        "review": review,
        "rejected_manifest": rejected_manifest,
        "full_reconcile": full_reconcile,
    }
    return candidate, metadata


def find_cycle(nodes: set[str], arcs: list[tuple[str, str]]) -> list[str] | None:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in arcs:
        adjacency[source].append(target)
    state: dict[str, int] = {node: 0 for node in nodes}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for target in adjacency.get(node, []):
            if state.get(target, 0) == 0:
                found = visit(target)
                if found is not None:
                    return found
            elif state.get(target) == 1:
                start = stack.index(target)
                return stack[start:] + [target]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(nodes):
        if state[node] == 0:
            found = visit(node)
            if found is not None:
                return found
    return None


def extension_sensitive_paths(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}"
            if str(key).lower() in {
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
            } and item not in (None, "", False, [], {}):
                findings.append(path)
            findings.extend(extension_sensitive_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(extension_sensitive_paths(item, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        if re.search(r"(?:/Users/|/private/tmp/|\\Users\\|file://)", value):
            findings.append(prefix)
        if re.search(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b", value):
            findings.append(prefix)
    return sorted(set(findings))


def validate_candidate(
    candidate: dict[str, Any], canonical: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    assembler = load_assembler()

    allowed_top = set(assembler.BASELINE_TOP_LEVEL_FIELDS) | TOP_LEVEL_EXTENSION_FIELDS
    unknown_top = sorted(set(candidate) - allowed_top)
    missing_extension = sorted(TOP_LEVEL_EXTENSION_FIELDS - set(candidate))
    if unknown_top:
        errors.append(f"unknown candidate top-level fields: {unknown_top}")
    if missing_extension:
        errors.append(f"missing topology extension fields: {missing_extension}")

    # Reuse the canonical shape/source validator on a projection.  The expected
    # errors are intentional and machine-pinned: original human-review partition
    # counts remain truthful, while NET-E03's reviewed ALL_OF(group references)
    # requires the versioned canonical schema extension that is still freeze-blocking.
    projection = copy.deepcopy(candidate)
    for field in TOP_LEVEL_EXTENSION_FIELDS:
        projection.pop(field, None)
    projection["schema_version"] = canonical["schema_version"]
    projection["plan_baseline_sha256"] = sha256_json(
        assembler.plan_identity_payload(projection)
    )
    projection["baseline_id"] = (
        f"P1-DRAFT-{projection['source_identity']['docs_target_revision'][:12]}-"
        f"{projection['plan_baseline_sha256'][:12]}"
    )
    projection_errors = assembler.validate(projection, REPO)
    expected_projection_errors = {
        "partition provenance procedure totals do not match baseline",
        "procedure NET-E03 branch group missing required fields: ['branch_ids']",
        "procedure NET-E03 branch group has unknown fields: ['group_ids']",
        "procedure NET-E03 has invalid branch group",
    }
    unexpected_projection_errors = sorted(
        set(projection_errors) - expected_projection_errors
    )
    if unexpected_projection_errors:
        errors.extend(
            f"canonical projection: {error}" for error in unexpected_projection_errors
        )
    missing_projection_errors = sorted(
        expected_projection_errors - set(projection_errors)
    )
    if missing_projection_errors:
        errors.append(
            "candidate projection no longer exposes its pinned schema/provenance blockers: "
            f"{missing_projection_errors}"
        )

    topology = candidate.get("topology_candidate", {})
    actions = topology.get("normalized_actions", [])
    action_ids = {record.get("id") for record in actions}
    if action_ids != EXPECTED_ACTION_IDS or len(actions) != len(EXPECTED_ACTION_IDS):
        errors.append("candidate does not implement the exact reviewed 18 action domains")
    action_types = Counter(record.get("action_type") for record in actions)
    if action_types != Counter(
        {
            "GENUINE_PROCEDURE_OR_OWNER_SPLIT": 7,
            "STRUCTURAL_PATH_EXTENSION": 3,
            "EXISTING_ID_TYPED_OR_HANDOFF_REPAIR": 8,
        }
    ):
        errors.append("candidate action classes do not reconcile to exact 7/3/8")
    for record in actions:
        if record.get("implementation_state") != "IMPLEMENTED_IN_ISOLATED_CANDIDATE":
            errors.append(f"action {record.get('id')} is not applied in candidate")
        if record.get("vv_status") != "UNVALIDATED":
            errors.append(f"action {record.get('id')} has invalid planning V&V status")

    procedures = candidate.get("procedures", [])
    proc_by_id = {str(proc.get("id")): proc for proc in procedures}
    if len(proc_by_id) != len(procedures):
        errors.append("duplicate procedure ID")
    page_ids = {page.get("id") for page in candidate.get("pages", [])}
    branch_owner: dict[str, str] = {}
    step_owner: dict[str, tuple[str, str]] = {}
    for proc in procedures:
        type_match = re.fullmatch(r"[A-Z0-9]+-([A-Z])\d+", str(proc.get("id")))
        if type_match is not None and proc.get("unit_type") != type_match.group(1):
            errors.append(
                f"procedure {proc.get('id')} unit type does not match its stable ID"
            )
        if proc.get("page_id") not in page_ids:
            errors.append(f"procedure {proc.get('id')} has unknown page")
        model = proc.get("branch_execution_model", {})
        branch_ids = [str(branch.get("id")) for branch in proc.get("branches", [])]
        branch_set = set(branch_ids)
        if model.get("state") not in ALLOWED_MODEL_STATES:
            errors.append(f"procedure {proc.get('id')} has invalid model state")
        if model.get("source_order") != branch_ids:
            errors.append(f"procedure {proc.get('id')} model source order is stale")
        grouped: list[str] = []
        typed_groups = model.get("alternative_groups", [])
        all_group_ids = {str(group.get("id")) for group in typed_groups}
        if len(all_group_ids) != len(typed_groups):
            errors.append(f"procedure {proc.get('id')} has duplicate group ID")
        group_arcs: list[tuple[str, str]] = []
        for typed_group in typed_groups:
            allowed_keys = {
                "id", "type", "branch_ids", "group_ids", "label", "parent_branch", "fallback_branch"
            }
            branch_members = typed_group.get("branch_ids")
            group_members = typed_group.get("group_ids")
            if (
                set(typed_group) - allowed_keys
                or not {"id", "type"}.issubset(typed_group)
                or (branch_members is None) == (group_members is None)
            ):
                errors.append(f"procedure {proc.get('id')} has noncanonical group shape")
            if typed_group.get("type") not in ALLOWED_GROUP_TYPES:
                errors.append(f"procedure {proc.get('id')} has unsupported group type")
            if branch_members is not None:
                if not branch_members or not set(branch_members).issubset(branch_set):
                    errors.append(f"procedure {proc.get('id')} has invalid group members")
                grouped.extend(branch_members)
            if group_members is not None:
                if (
                    not group_members
                    or not set(group_members).issubset(all_group_ids)
                    or typed_group.get("id") in group_members
                ):
                    errors.append(f"procedure {proc.get('id')} has invalid nested group members")
                group_arcs.extend(
                    (str(typed_group.get("id")), str(member))
                    for member in group_members
                    if member in all_group_ids
                )
            for key in ("parent_branch", "fallback_branch"):
                if typed_group.get(key) is not None and typed_group.get(key) not in branch_set:
                    errors.append(f"procedure {proc.get('id')} group has invalid {key}")
        if len(grouped) != len(set(grouped)):
            errors.append(f"procedure {proc.get('id')} assigns one branch to multiple typed groups")
        group_cycle = find_cycle(all_group_ids, group_arcs)
        if group_cycle is not None:
            errors.append(
                f"procedure {proc.get('id')} nested group graph is cyclic: {' -> '.join(group_cycle)}"
            )
        arcs: list[tuple[str, str]] = []
        for branch_edge in model.get("ordered_edges", []):
            if set(branch_edge) != {"from_branch", "to_branch", "relation"}:
                errors.append(f"procedure {proc.get('id')} has noncanonical edge shape")
                continue
            source = branch_edge.get("from_branch")
            target = branch_edge.get("to_branch")
            if (
                source not in branch_set
                or target not in branch_set
                or source == target
                or branch_edge.get("relation") not in ALLOWED_EDGE_RELATIONS
            ):
                errors.append(f"procedure {proc.get('id')} has invalid branch edge")
            else:
                arcs.append((str(source), str(target)))
        cycle = find_cycle(branch_set, arcs)
        if cycle is not None:
            errors.append(f"procedure {proc.get('id')} branch graph is cyclic: {' -> '.join(cycle)}")
        if model.get("state") == "LINEAR_SINGLE_BRANCH" and len(branch_ids) != 1:
            errors.append(f"procedure {proc.get('id')} falsely claims linear single branch")
        if model.get("state") == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED" and len(branch_ids) <= 1:
            errors.append(f"procedure {proc.get('id')} falsely claims unresolved multi-branch")
        for branch in proc.get("branches", []):
            branch_id = str(branch.get("id"))
            if branch_id in branch_owner:
                errors.append(f"duplicate branch ID {branch_id}")
            branch_owner[branch_id] = str(proc.get("id"))
            for step in branch.get("steps", []):
                step_id = str(step.get("id"))
                if step_id in step_owner:
                    errors.append(f"duplicate step ID {step_id}")
                step_owner[step_id] = (str(proc.get("id")), branch_id)
                unknown_dependencies = set(step.get("dependencies", [])) - {
                    str(local_step.get("id"))
                    for local_branch in proc.get("branches", [])
                    for local_step in local_branch.get("steps", [])
                }
                if unknown_dependencies:
                    errors.append(f"step {step_id} has cross-owner/unknown dependencies")

    catalog_locations: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for proc in procedures:
        for branch in proc.get("branches", []):
            for step in branch.get("steps", []):
                for carrier in step.get("source_carriers", []):
                    if carrier.get("claim_id") in STATIC_TEAM_CATALOG_REASSIGN_CLAIMS:
                        catalog_locations[str(carrier["claim_id"])].append(
                            (str(proc["id"]), str(branch["id"]), str(step["id"]))
                        )
    expected_catalog_location = ("TEAM-C01", "TEAM-C01-B01", "TEAM-C01-B01-S01")
    for claim_id in sorted(STATIC_TEAM_CATALOG_REASSIGN_CLAIMS):
        if catalog_locations.get(claim_id) != [expected_catalog_location]:
            errors.append(
                f"reviewed static-team carrier {claim_id} has incorrect executable owner"
            )
    try:
        catalog_proc = proc_by_id["TEAM-C01"]
        catalog_step = get_step(
            get_branch(catalog_proc, "TEAM-C01-B01"), "TEAM-C01-B01-S01"
        )
        if catalog_proc.get("unit_type") != "C":
            errors.append("TEAM-C01 is not typed as a conformance/static procedure")
        if catalog_step.get("execution_form_state") != "NOT_APPLICABLE_NON_COMMAND_STEP":
            errors.append("TEAM-C01 static catalog is incorrectly executable")
    except (KeyError, CandidateError):
        errors.append("TEAM-C01 static catalog owner is incomplete")

    try:
        fleet_delegate = proc_by_id["FLT-E07"]
        fleet_branch = get_branch(fleet_delegate, "FLT-E07-B01")
        fleet_steps = fleet_branch["steps"]
        if set(fleet_delegate.get("access_classes", [])) != {
            "credentialed-read-only",
            "composite-delegated-only",
        }:
            errors.append("FLT-E07 access is not read-only delegated preflight")
        expected_fleet_instructions = [
            "Confirm the exact target is already unlisted, honor every end date, and obtain destructive authorization.",
            "Hand the exact approved target and preflight record to RM-E02; do not execute delete/decommission in the fleet procedure.",
            "Confirm the handoff record names RM-E02 and that no fleet-side destructive action was executed.",
        ]
        if [step.get("instruction_summary") for step in fleet_steps] != expected_fleet_instructions:
            errors.append("FLT-E07 leaks destructive execution or child outcome into its wrapper")
    except (KeyError, CandidateError):
        errors.append("FLT-E07 delegated preflight owner is incomplete")

    try:
        rm_cleanup = get_branch(proc_by_id["RM-E01"], "RM-E01-B01")
        if re.search(r"\b(?:delete|recreate|decommission|uninstall)\b", rm_cleanup.get("condition", ""), re.I):
            errors.append("RM-E01 cleanup condition leaks a split destructive outcome")
    except (KeyError, CandidateError):
        errors.append("RM-E01 cleanup owner is incomplete")

    try:
        finance_proc = proc_by_id["TEAM-E04"]
        finance_model = finance_proc["branch_execution_model"]
        finance_read = get_branch(finance_proc, "TEAM-E04-B01")
        invoice_write = get_branch(finance_proc, "TEAM-E04-B02")
        expected_finance_edges = [{
            "from_branch": "TEAM-E04-B01",
            "to_branch": "TEAM-E04-B02",
            "relation": "BEFORE",
        }]
        expected_invoice_groups = [{
            "id": "GRP-TEAM-E04-INVOICE-WRITE",
            "type": "CONDITIONAL",
            "branch_ids": ["TEAM-E04-B02"],
        }]
        if [branch["id"] for branch in finance_proc["branches"]] != [
            "TEAM-E04-B01",
            "TEAM-E04-B02",
        ]:
            errors.append("TEAM-E04 read and invoice-write paths are not independently owned")
        if finance_model.get("ordered_edges") != expected_finance_edges or finance_model.get("alternative_groups") != expected_invoice_groups:
            errors.append("TEAM-E04 invoice-write conditional topology is incomplete")
        read_access = set(finance_read["execution_gate"]["access_requirements"])
        write_access = set(invoice_write["execution_gate"]["access_requirements"])
        if "financial-read-only" not in read_access or {
            "billing-write",
            "account-mutating",
        } & read_access:
            errors.append("TEAM-E04 finance-read gate is not read-only")
        if not {"billing-write", "account-mutating"}.issubset(write_access):
            errors.append("TEAM-E04 invoice-write gate is not monotonic over mutation")
        read_text = " ".join(
            step.get("instruction_summary", "") for step in finance_read["steps"]
        )
        write_text = " ".join(
            step.get("instruction_summary", "") for step in invoice_write["steps"]
        )
        if re.search(r"\b(?:edit|update|change)\b", read_text, re.I):
            errors.append("TEAM-E04 read-only branch contains a write instruction")
        if "Update only the approved invoice fields" not in write_text:
            errors.append("TEAM-E04 invoice-write branch lacks bounded write ownership")
        if any("escalat" in branch.get("condition", "").lower() for branch in finance_proc["branches"]):
            errors.append("TEAM-E04 retains the split escalation-contact outcome")
    except (KeyError, CandidateError):
        errors.append("TEAM-E04 finance owner is incomplete")

    try:
        delete_action = get_step(
            get_branch(proc_by_id["TEAM-E08"], "TEAM-E08-B01"),
            "TEAM-E08-B01-S02",
        )
        if delete_action.get("instruction_summary") != (
            "Perform only the separately authorized team deletion."
        ) or delete_action.get("required") is not True:
            errors.append("TEAM-E08 deletion action is optional or retains compound owner actions")
        if delete_action.get("execution_form_state") != "UNVALIDATED_SAFE_PARAMETERIZATION_REQUIRED":
            errors.append("TEAM-E08 deletion action hides its unresolved safe executable form")
    except (KeyError, CandidateError):
        errors.append("TEAM-E08 deletion owner is incomplete")

    changed_sources = {
        record["source_procedure_id"]
        for record in actions
    }
    for procedure_id in changed_sources:
        if procedure_id not in proc_by_id:
            errors.append(f"normalized action source owner {procedure_id} disappeared")
        elif proc_by_id[procedure_id]["branch_execution_model"]["state"] == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED":
            errors.append(f"normalized target {procedure_id} retains unresolved topology")

    coverage = topology.get("procedure_model_coverage", [])
    coverage_by_proc = {record.get("procedure_id"): record for record in coverage}
    if set(coverage_by_proc) != set(proc_by_id) or len(coverage_by_proc) != len(coverage):
        errors.append("procedure model coverage is not one-to-one with candidate procedures")
    for proc_id, proc in proc_by_id.items():
        record = coverage_by_proc.get(proc_id, {})
        all_ids = {branch["id"] for branch in proc["branches"]}
        partitions = [
            set(record.get("required_branch_ids", [])),
            set(record.get("grouped_branch_ids", [])),
            set(record.get("unresolved_branch_ids", [])),
        ]
        if set.union(*partitions) != all_ids or sum(map(len, partitions)) != len(all_ids):
            errors.append(f"procedure {proc_id} model coverage is not exact/exclusive")

    # Planning result status remains separate from shape-validation PASS labels.
    status_records: list[tuple[str, Any]] = []
    status_records.extend((f"page {item['id']}", item.get("status")) for item in candidate["pages"])
    status_records.extend((f"procedure {item['id']}", item.get("status")) for item in procedures)
    for proc in procedures:
        for branch in proc["branches"]:
            status_records.append((f"branch {branch['id']}", branch.get("status")))
            status_records.append((f"gate {branch['id']}", branch["execution_gate"]["gate_evaluation"].get("status")))
            status_records.extend((f"step {step['id']}", step.get("status")) for step in branch["steps"])
    status_records.extend((f"claim {item['id']}", item.get("status")) for item in candidate["claims"])
    status_records.extend((f"crosswalk {item['occurrence_id']}", item.get("status")) for item in candidate["legacy_crosswalk"])
    status_records.extend((f"outcome {item['branch_id']}", item.get("vv_status")) for item in candidate["branch_outcomes"])
    status_records.extend((f"handoff {item['id']}", item.get("vv_status")) for item in candidate["cross_page_handoffs"])
    status_records.extend((f"blocker {item['id']}", item.get("vv_status")) for item in topology.get("unresolved_blockers", []))
    for label, status in status_records:
        if status not in ALLOWED_STATUSES:
            errors.append(f"{label} has invalid V&V status")
        if status == "PASS":
            errors.append(f"{label} improperly claims PASS in planning candidate")

    claim_by_id = {claim["id"]: claim for claim in candidate["claims"]}
    if len(claim_by_id) != len(candidate["claims"]):
        errors.append("duplicate claim ID")
    crosswalk_by_claim = {row["claim_id"]: row for row in candidate["legacy_crosswalk"]}
    if len(crosswalk_by_claim) != len(candidate["legacy_crosswalk"]):
        errors.append("legacy crosswalk is not one-to-one with claims")
    for claim_id, claim in claim_by_id.items():
        row = crosswalk_by_claim.get(claim_id)
        if row is None:
            errors.append(f"claim {claim_id} lacks legacy crosswalk")
            continue
        for field in ("page_id", "procedure_id", "branch_id", "step_id", "supporting_route_id", "fragment_id"):
            if row.get(field) != claim.get(field):
                errors.append(f"claim/crosswalk target mismatch for {claim_id} field {field}")
        if claim.get("procedure_id") is not None:
            if claim.get("procedure_id") not in proc_by_id:
                errors.append(f"claim {claim_id} has unknown procedure owner")
            if claim.get("step_id") is not None:
                if claim.get("branch_id") not in branch_owner:
                    errors.append(f"claim {claim_id} has unknown branch owner")
                if claim.get("step_id") not in step_owner:
                    errors.append(f"claim {claim_id} has unknown step owner")
                elif step_owner[claim["step_id"]] != (claim["procedure_id"], claim["branch_id"]):
                    errors.append(f"claim {claim_id} step/procedure ownership is inconsistent")

    if set(claim_by_id) != {claim["id"] for claim in canonical["claims"]}:
        errors.append("legacy claim population changed")
    if immutable_claim_fingerprint(candidate) != immutable_claim_fingerprint(canonical):
        errors.append("legacy claim content changed beyond deterministic owner references")
    if carrier_fingerprint(candidate) != carrier_fingerprint(canonical):
        errors.append("legacy step source-carrier multiset changed")
    if len(candidate["legacy_crosswalk"]) != len(canonical["legacy_crosswalk"]):
        errors.append("legacy crosswalk population changed")
    canonical_crosswalk = {
        row["claim_id"]: {
            key: value
            for key, value in row.items()
            if key
            not in {"procedure_id", "branch_id", "step_id", "source_alignment"}
        }
        for row in canonical["legacy_crosswalk"]
    }
    candidate_crosswalk = {
        row["claim_id"]: {
            key: value
            for key, value in row.items()
            if key
            not in {"procedure_id", "branch_id", "step_id", "source_alignment"}
        }
        for row in candidate["legacy_crosswalk"]
    }
    if candidate_crosswalk != canonical_crosswalk:
        errors.append("legacy crosswalk changed outside deterministic topology targets")

    expected_proc_claims: dict[str, set[str]] = defaultdict(set)
    expected_page_procs: dict[str, set[str]] = defaultdict(set)
    expected_page_claims: dict[str, set[str]] = defaultdict(set)
    for claim in candidate["claims"]:
        if claim["procedure_id"] is not None:
            expected_proc_claims[claim["procedure_id"]].add(claim["id"])
        expected_page_claims[claim["page_id"]].add(claim["id"])
    for proc in procedures:
        expected_page_procs[proc["page_id"]].add(proc["id"])
        if set(proc["claim_ids"]) != expected_proc_claims[proc["id"]]:
            errors.append(f"procedure {proc['id']} claim reverse index is stale")
    for page in candidate["pages"]:
        if set(page["procedure_ids"]) != expected_page_procs[page["id"]]:
            errors.append(f"page {page['id']} procedure reverse index is stale")
        if set(page["claim_ids"]) != expected_page_claims[page["id"]]:
            errors.append(f"page {page['id']} claim reverse index is stale")

    # Every changed legacy owner must land in the declared one-to-many remap.
    remap = topology.get("id_remap", {})
    remap_maps = {
        kind: {record["old_id"]: set(record["new_ids"]) for record in remap.get(kind, [])}
        for kind in ("procedures", "branches", "steps")
    }
    old_sets = {
        "procedures": {proc["id"] for proc in canonical["procedures"]},
        "branches": {branch["id"] for proc in canonical["procedures"] for branch in proc["branches"]},
        "steps": {step["id"] for proc in canonical["procedures"] for branch in proc["branches"] for step in branch["steps"]},
    }
    new_sets = {
        "procedures": set(proc_by_id),
        "branches": set(branch_owner),
        "steps": set(step_owner),
    }
    for kind, records in remap_maps.items():
        for old_id, new_ids in records.items():
            if old_id not in old_sets[kind] or not new_ids or not new_ids.issubset(new_sets[kind]):
                errors.append(f"invalid {kind} ID remap for {old_id}")
        for old_id in old_sets[kind] - new_sets[kind]:
            if old_id not in records:
                errors.append(f"missing deterministic remap for removed {kind} ID {old_id}")
    canonical_claims = {claim["id"]: claim for claim in canonical["claims"]}
    fields_to_kind = (("procedure_id", "procedures"), ("branch_id", "branches"), ("step_id", "steps"))
    for claim_id, old_claim in canonical_claims.items():
        new_claim = claim_by_id[claim_id]
        for field, kind in fields_to_kind:
            old_id = old_claim.get(field)
            new_id = new_claim.get(field)
            if old_id == new_id or old_id is None:
                continue
            if new_id not in remap_maps[kind].get(old_id, set()):
                errors.append(f"claim {claim_id} changed {field} without declared deterministic remap")

    outcomes = candidate.get("branch_outcomes", [])
    outcome_keys = {(record.get("procedure_id"), record.get("branch_id")) for record in outcomes}
    expected_outcome_keys = {(owner, branch_id) for branch_id, owner in branch_owner.items()}
    if outcome_keys != expected_outcome_keys or len(outcomes) != len(expected_outcome_keys):
        errors.append("branch outcomes are not one-to-one with candidate branches")
    for record in outcomes:
        if record.get("outcome_class") not in ALLOWED_OUTCOME_CLASSES:
            errors.append(f"branch outcome {record.get('branch_id')} has invalid class")
        if record.get("outcome_class") in {
            "DELEGATED_PATH", "DIAGNOSTIC_ONLY", "FAILURE_ONLY_DIAGNOSTIC", "NEGATIVE_FIT_OUTCOME", "ROUTING_DECISION"
        } and record.get("contributes_to_parent_pass_when_applicable"):
            errors.append(f"branch outcome {record.get('branch_id')} improperly contributes to parent PASS")

    blockers = topology.get("unresolved_blockers", [])
    blocker_ids = {record.get("id") for record in blockers}
    expected_model_blocker_ids = {
        f"BLOCKER-MODEL-{record['procedure_id']}"
        for record in coverage
        if record.get("coverage_state") == "UNRESOLVED_FREEZE_BLOCKING"
    }
    expected_mixed_blocker_ids = {
        f"BLOCKER-MIXED-{branch_id}"
        for _procedure_id, branch_id in MIXED_ACCESS_BRANCHES
    }
    expected_singleton_blocker_ids = {
        "BLOCKER-HDL-RAW-INSTALLER-SOURCE",
        "BLOCKER-MNT-ACTION-OWNER",
        "BLOCKER-INDEPENDENT-CANDIDATE-RECONCILIATION",
        "BLOCKER-CANONICAL-INTEGRATION-PROVENANCE",
    }
    expected_topology_blocker_ids = (
        expected_model_blocker_ids
        | expected_mixed_blocker_ids
        | expected_singleton_blocker_ids
    )
    if blocker_ids != expected_topology_blocker_ids or len(blockers) != len(blocker_ids):
        errors.append("topology blocker register is not the exact derived structural subset")
    if len(blockers) != 47:
        errors.append("topology blocker register no longer reconciles to 47 records")
    blocker_scope = topology.get("blocker_register_scope", {})
    if (
        blocker_scope.get("scope")
        != "TOPOLOGY_DERIVATIVE_ONLY_NOT_COMPLETE_P1_FREEZE_REGISTER"
        or blocker_scope.get("complete_p1_freeze_register") is not False
        or blocker_scope.get("topology_blocker_record_count") != len(blockers)
        or not blocker_scope.get("known_unenumerated_freeze_conditions")
    ):
        errors.append("topology blocker subset is mislabeled as a complete P1 freeze register")
    for procedure_id, branch_id in MIXED_ACCESS_BRANCHES:
        blocker_id = f"BLOCKER-MIXED-{branch_id}"
        try:
            branch = get_branch(proc_by_id[procedure_id], branch_id)
        except (KeyError, CandidateError):
            errors.append(f"mixed-access branch {branch_id} is missing from its owner")
            continue
        if blocker_id not in blocker_ids:
            errors.append(f"mixed-access branch {branch_id} lacks machine freeze blocker")
        if "MIXED_ACCESS_SPLIT_REQUIRED" not in branch["execution_gate"]["access_requirements"]:
            errors.append(f"mixed-access branch {branch_id} gate did not propagate")
    if "BLOCKER-HDL-RAW-INSTALLER-SOURCE" not in blocker_ids:
        errors.append("HDL raw-download source defect is not freeze-blocking")
    if "BLOCKER-CANONICAL-INTEGRATION-PROVENANCE" not in blocker_ids:
        errors.append("canonical assembler/provenance integration gap is not freeze-blocking")
    freeze_gate = topology.get("freeze_gate", {})
    if (
        freeze_gate.get("freeze_allowed") is not False
        or freeze_gate.get("live_execution_allowed") is not False
        or set(freeze_gate.get("blocking_record_ids", [])) != blocker_ids
    ):
        errors.append("topology freeze gate does not fail closed over every blocker")

    for branch_id in NET_LIVE_BRANCHES:
        try:
            gate = get_branch(proc_by_id["NET-E03"], branch_id)["execution_gate"]
        except (KeyError, CandidateError):
            errors.append(f"NET-E03 branch {branch_id} is missing")
            continue
        required = {"HOST_VV_TARGET", "TEMPORARY_LISTENER_CAPTURE", "WAN_EXTERNAL_PROBE"}
        if not required.issubset(gate.get("access_requirements", [])):
            errors.append(f"NET-E03 branch {branch_id} lacks monotonic Host/WAN gate")
        safety_text = " ".join(gate.get("safety_requirements", [])).lower()
        for token in ("timeout", "pid", "port/process absence"):
            if token not in safety_text:
                errors.append(f"NET-E03 branch {branch_id} lacks {token} safety/cleanup condition")
    try:
        net_groups = {
            typed_group["id"]: typed_group
            for typed_group in proc_by_id["NET-E03"]["branch_execution_model"][
                "alternative_groups"
            ]
        }
        if net_groups.get("GRP-NET-E03-PROTOCOLS") != {
            "id": "GRP-NET-E03-PROTOCOLS",
            "type": "ALL_OF",
            "group_ids": ["GRP-NET-E03-TCP", "GRP-NET-E03-UDP"],
            "label": "both protocol obligations",
        }:
            errors.append("NET-E03 lacks typed ALL_OF composition over TCP and UDP groups")
    except KeyError:
        errors.append("NET-E03 lacks typed ALL_OF composition over TCP and UDP groups")

    handoffs = candidate.get("cross_page_handoffs", [])
    expected_handoff_ids = {
        "HANDOFF-SETUP-001", "HANDOFF-HOV-001", "HANDOFF-QST-001", "HANDOFF-HDL-001",
        "HANDOFF-FLT-RM-001", "HANDOFF-ERROR-OWNERS-001", "HANDOFF-STR-001", "HANDOFF-API-001",
    }
    if {record.get("id") for record in handoffs} != expected_handoff_ids or len(handoffs) != 8:
        errors.append("cross-page handoff families do not reconcile to reviewed set of eight")
    support_ids = {contract["id"] for contract in candidate["support_contracts"]}
    wrapper_ids = {
        contract["id"]
        for contract in candidate["support_contracts"]
        if contract["kind"] == "wrapper-import-render-contract"
    }
    api_targets: set[str] = set()
    handoff_arcs: list[tuple[str, str]] = []
    binding_ids: set[str] = set()
    for family in handoffs:
        if family.get("relation") != "HANDOFF" or family.get("family_rollup_rule") == "":
            errors.append(f"handoff family {family.get('id')} has invalid relation/rollup")
        for binding in family.get("bindings", []):
            if binding.get("id") in binding_ids:
                errors.append(f"duplicate handoff binding ID {binding.get('id')}")
            binding_ids.add(str(binding.get("id")))
            source_proc = binding.get("source_procedure_id")
            source_branch = binding.get("source_branch_id")
            if source_proc not in proc_by_id:
                errors.append(f"handoff binding {binding.get('id')} has unknown source owner")
            elif source_branch is not None and branch_owner.get(source_branch) != source_proc:
                errors.append(f"handoff binding {binding.get('id')} has invalid source branch")
            if not binding.get("trigger_predicate") or not binding.get("applicability_predicate"):
                errors.append(f"handoff binding {binding.get('id')} lacks trigger/applicability")
            if binding.get("parent_rollup_rule") != "NO_PARENT_PASS_BY_ALIAS_OR_HANDOFF":
                errors.append(f"handoff binding {binding.get('id')} has unsafe rollup")
            for target in binding.get("target_requirements", []):
                kind = target.get("owner_type")
                owner_id = target.get("owner_id")
                if kind == "PROCEDURE":
                    if owner_id not in proc_by_id:
                        errors.append(f"handoff binding {binding.get('id')} has unknown procedure target")
                    else:
                        handoff_arcs.append((str(source_proc), str(owner_id)))
                elif kind == "SUPPORT_CONTRACT":
                    if owner_id not in support_ids:
                        errors.append(f"handoff binding {binding.get('id')} has unknown support target")
                    if family.get("id") == "HANDOFF-API-001":
                        api_targets.add(str(owner_id))
                else:
                    errors.append(f"handoff binding {binding.get('id')} has invalid target owner type")
                if not target.get("required_outcome_ref") or not target.get("required_evidence_ref"):
                    errors.append(f"handoff binding {binding.get('id')} lacks outcome/evidence owner refs")
    if api_targets != wrapper_ids:
        errors.append("API handoff does not enumerate all and only 33 wrapper support contracts")
    handoff_cycle = find_cycle(set(proc_by_id), handoff_arcs)
    if handoff_cycle is not None:
        errors.append(f"cross-page procedure handoff graph is cyclic: {' -> '.join(handoff_cycle)}")

    sensitive = extension_sensitive_paths(
        {field: candidate.get(field) for field in TOP_LEVEL_EXTENSION_FIELDS}
    )
    if sensitive:
        errors.append(f"topology extension contains restricted/absolute metadata: {sensitive[:5]}")

    reconciliation = candidate.get("reconciliation", {})
    actual_counts = {
        "pages": len(candidate["pages"]),
        "procedures": len(procedures),
        "branches": len(branch_owner),
        "steps": len(step_owner),
        "claims": len(candidate["claims"]),
        "legacy_crosswalk_rows": len(candidate["legacy_crosswalk"]),
    }
    for field, count in actual_counts.items():
        if reconciliation.get(field) != count:
            errors.append(f"reconciliation count mismatch for {field}")
    declared_counts = topology.get("counts", {})
    for field, count in actual_counts.items():
        if declared_counts.get(field) != count:
            errors.append(f"topology count mismatch for {field}")
    if declared_counts.get("split_action_domains") != 7 or declared_counts.get("structural_extension_domains") != 3 or declared_counts.get("existing_id_repair_domains") != 8:
        errors.append("topology declared action denominators are not 7/3/8")
    unresolved_safe_steps = [
        step
        for proc in procedures
        for branch in proc["branches"]
        for step in branch["steps"]
        if step.get("execution_form_state")
        == "UNVALIDATED_SAFE_PARAMETERIZATION_REQUIRED"
    ]
    unresolved_safe_commands = sum(
        carrier.get("kind") == "command"
        for step in unresolved_safe_steps
        for carrier in step.get("source_carriers", [])
    )
    static_non_executable_commands = sum(
        carrier.get("kind") == "command"
        for proc in procedures
        for branch in proc["branches"]
        for step in branch["steps"]
        if step.get("execution_form_state") == "NOT_APPLICABLE_NON_COMMAND_STEP"
        for carrier in step.get("source_carriers", [])
    )
    if declared_counts.get("reviewed_static_team_catalog_reassignments") != len(
        STATIC_TEAM_CATALOG_REASSIGN_CLAIMS
    ):
        errors.append("reviewed static-team catalog reassignment count is stale")
    if declared_counts.get("unresolved_safe_parameterization_steps") != len(
        unresolved_safe_steps
    ) or declared_counts.get(
        "unresolved_safe_parameterization_command_carriers"
    ) != unresolved_safe_commands:
        errors.append("unresolved safe-parameterization counts are stale")
    if declared_counts.get("static_non_executable_command_carriers") != static_non_executable_commands:
        errors.append("static non-executable command-carrier count is stale")

    computed_plan_digest = sha256_json(assembler.plan_identity_payload(candidate))
    expected_id = (
        f"P1-DRAFT-{candidate['source_identity']['docs_target_revision'][:12]}-"
        f"{computed_plan_digest[:12]}"
    )
    if candidate.get("plan_baseline_sha256") != computed_plan_digest:
        errors.append("candidate plan baseline digest mismatch")
    if candidate.get("baseline_id") != expected_id:
        errors.append("candidate baseline ID mismatch")
    if topology.get("content_sha256_excluding_self") != candidate_content_hash(candidate):
        errors.append("candidate content hash mismatch")

    input_records = topology.get("input_artifacts", {})
    for label, expected_hash in EXPECTED_HASHES.items():
        short_label = {
            "canonical_baseline_sha256": "canonical_baseline",
            "governing_goal_sha256": "governing_goal",
            "vv_evidence_skill_sha256": "vv_evidence_skill",
            "canonical_assembler_sha256": "canonical_assembler",
            "independent_topology_review_sha256": "independent_topology_review",
            "rejected_manifest_sha256": "rejected_manifest",
            "full_reconcile_sha256": "full_reconcile",
        }[label]
        if input_records.get(short_label, {}).get("sha256") != expected_hash:
            errors.append(f"candidate input pin mismatch for {short_label}")

    if candidate.get("state") != "DRAFT_NOT_FROZEN" or candidate.get("freeze", {}).get("state") != "NOT_FROZEN":
        errors.append("candidate lifecycle does not remain draft/not-frozen")
    if candidate.get("execution_readiness", {}).get("new_live_execution_allowed") is not False:
        errors.append("candidate improperly authorizes live execution")
    if candidate.get("completion_and_acceptance", {}).get("evidence_package_complete") is not False or candidate.get("completion_and_acceptance", {}).get("target_acceptance_candidate") is not False:
        errors.append("candidate improperly claims completion or acceptance readiness")

    return sorted(set(errors))


def run_self_test(candidate: dict[str, Any], canonical: dict[str, Any]) -> int:
    tests = 0
    failures: list[str] = []

    valid_errors = validate_candidate(candidate, canonical)
    tests += 1
    if valid_errors:
        failures.append("valid candidate rejected: " + "; ".join(valid_errors[:3]))

    def expect_failure(
        name: str,
        mutator: Callable[[dict[str, Any]], None],
        expected_substring: str,
    ) -> None:
        nonlocal tests
        tests += 1
        mutated = copy.deepcopy(candidate)
        mutator(mutated)
        observed = validate_candidate(mutated, canonical)
        if not any(expected_substring in error for error in observed):
            failures.append(
                f"{name}: expected {expected_substring!r}; observed {observed[:4]}"
            )

    expect_failure(
        "missing-action",
        lambda value: value["topology_candidate"]["normalized_actions"].pop(),
        "exact reviewed 18 action domains",
    )
    expect_failure(
        "wrong-action-class",
        lambda value: next(
            item
            for item in value["topology_candidate"]["normalized_actions"]
            if item["id"] == "SPLIT-COM-E01"
        ).update({"action_type": "STRUCTURAL_PATH_EXTENSION"}),
        "exact 7/3/8",
    )
    expect_failure(
        "target-unresolved",
        lambda value: get_procedure(value, "HOV-C01")["branch_execution_model"].update(
            {"state": "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED"}
        ),
        "normalized target HOV-C01 retains unresolved topology",
    )
    expect_failure(
        "noncanonical-relation",
        lambda value: get_procedure(value, "PRICE-E01")["branch_execution_model"]["ordered_edges"][0].update(
            {"relation": "PRECEDES"}
        ),
        "invalid branch edge",
    )
    expect_failure(
        "branch-cycle",
        lambda value: get_procedure(value, "PRICE-E01")["branch_execution_model"]["ordered_edges"].append(
            edge("PRICE-E01-adjust", "PRICE-E01-change")
        ),
        "branch graph is cyclic",
    )
    expect_failure(
        "unknown-edge-target",
        lambda value: get_procedure(value, "PRICE-E01")["branch_execution_model"]["ordered_edges"][0].update(
            {"to_branch": "SYNTHETIC-NODE"}
        ),
        "invalid branch edge",
    )
    expect_failure(
        "unsupported-group",
        lambda value: get_procedure(value, "NET-E03")["branch_execution_model"]["alternative_groups"][0].update(
            {"type": "ALL_OF_GROUPS"}
        ),
        "unsupported group type",
    )
    expect_failure(
        "duplicate-group-membership",
        lambda value: get_procedure(value, "NET-E03")["branch_execution_model"]["alternative_groups"][1]["branch_ids"].append(
            "NET-E03-B-tcp-unix"
        ),
        "multiple typed groups",
    )
    expect_failure(
        "missing-model-coverage",
        lambda value: value["topology_candidate"]["procedure_model_coverage"].pop(),
        "model coverage is not one-to-one",
    )

    def corrupt_claim_owner(value: dict[str, Any]) -> None:
        claim = next(item for item in value["claims"] if item["id"] == "CLM-43d6fe7ed37501fd")
        claim["procedure_id"] = "COM-E01"

    expect_failure(
        "stale-claim-owner",
        corrupt_claim_owner,
        "claim/crosswalk target mismatch",
    )

    def corrupt_crosswalk(value: dict[str, Any]) -> None:
        row = next(item for item in value["legacy_crosswalk"] if item["claim_id"] == "CLM-43d6fe7ed37501fd")
        row["step_id"] = "STALE-STEP"

    expect_failure(
        "stale-crosswalk-owner",
        corrupt_crosswalk,
        "claim/crosswalk target mismatch",
    )

    def remove_carrier(value: dict[str, Any]) -> None:
        for proc in value["procedures"]:
            for branch in proc["branches"]:
                for step in branch["steps"]:
                    if step["source_carriers"]:
                        step["source_carriers"].pop()
                        return

    expect_failure(
        "carrier-loss",
        remove_carrier,
        "source-carrier multiset changed",
    )
    expect_failure(
        "claim-content-change",
        lambda value: value["claims"][0].update({"text": "changed"}),
        "legacy claim content changed",
    )

    def duplicate_branch(value: dict[str, Any]) -> None:
        proc = get_procedure(value, "NET-E03")
        proc["branches"][1]["id"] = proc["branches"][0]["id"]

    expect_failure("duplicate-branch", duplicate_branch, "duplicate branch ID")

    def duplicate_step(value: dict[str, Any]) -> None:
        proc = get_procedure(value, "MNT-E01")
        proc["branches"][1]["steps"][0]["id"] = proc["branches"][0]["steps"][0]["id"]

    expect_failure("duplicate-step", duplicate_step, "duplicate step ID")
    expect_failure(
        "planning-pass",
        lambda value: get_procedure(value, "COM-E01").update({"status": "PASS"}),
        "improperly claims PASS",
    )
    expect_failure(
        "stable-id-unit-type",
        lambda value: get_procedure(value, "TEAM-E06").update({"unit_type": "T"}),
        "unit type does not match its stable ID",
    )

    def dislodge_static_team_carrier(value: dict[str, Any]) -> None:
        catalog_step = get_step(
            get_branch(get_procedure(value, "TEAM-C01"), "TEAM-C01-B01"),
            "TEAM-C01-B01-S01",
        )
        index = next(
            index
            for index, carrier in enumerate(catalog_step["source_carriers"])
            if carrier["claim_id"] in STATIC_TEAM_CATALOG_REASSIGN_CLAIMS
        )
        carrier = catalog_step["source_carriers"].pop(index)
        get_step(
            get_branch(get_procedure(value, "TEAM-E03"), "TEAM-E03-B01"),
            "TEAM-E03-B01-S01",
        )["source_carriers"].append(carrier)

    expect_failure(
        "static-team-owner",
        dislodge_static_team_carrier,
        "incorrect executable owner",
    )
    expect_failure(
        "fleet-wrapper-destructive-leak",
        lambda value: get_step(
            get_branch(get_procedure(value, "FLT-E07"), "FLT-E07-B01"),
            "FLT-E07-B01-S01",
        ).update({"instruction_summary": "Unlist the target before delegation."}),
        "leaks destructive execution or child outcome",
    )
    expect_failure(
        "rm-cleanup-owner-leak",
        lambda value: get_branch(
            get_procedure(value, "RM-E01"), "RM-E01-B01"
        ).update({"condition": "Cleanup or recreate is authorized"}),
        "cleanup condition leaks a split destructive outcome",
    )
    expect_failure(
        "finance-write-gate-reduction",
        lambda value: get_branch(
            get_procedure(value, "TEAM-E04"), "TEAM-E04-B02"
        )["execution_gate"]["access_requirements"].remove("billing-write"),
        "invoice-write gate is not monotonic",
    )
    expect_failure(
        "optional-team-delete",
        lambda value: get_step(
            get_branch(get_procedure(value, "TEAM-E08"), "TEAM-E08-B01"),
            "TEAM-E08-B01-S02",
        ).update({"required": False}),
        "deletion action is optional",
    )
    expect_failure(
        "complete-blocker-register-claim",
        lambda value: value["topology_candidate"]["blocker_register_scope"].update(
            {"complete_p1_freeze_register": True}
        ),
        "mislabeled as a complete P1 freeze register",
    )

    def remove_mixed_blocker(value: dict[str, Any]) -> None:
        blockers = value["topology_candidate"]["unresolved_blockers"]
        blockers[:] = [
            item
            for item in blockers
            if item["id"] != "BLOCKER-MIXED-DIA-E03-B02"
        ]

    expect_failure(
        "missing-mixed-blocker",
        remove_mixed_blocker,
        "lacks machine freeze blocker",
    )
    expect_failure(
        "missing-mixed-gate",
        lambda value: get_branch(get_procedure(value, "DIA-E03"), "DIA-E03-B02")["execution_gate"]["access_requirements"].remove(
            "MIXED_ACCESS_SPLIT_REQUIRED"
        ),
        "gate did not propagate",
    )
    expect_failure(
        "missing-net-host-profile",
        lambda value: get_branch(get_procedure(value, "NET-E03"), "NET-E03-B-tcp-windows")["execution_gate"]["access_requirements"].remove(
            "TEMPORARY_LISTENER_CAPTURE"
        ),
        "lacks monotonic Host/WAN gate",
    )
    expect_failure(
        "missing-net-nested-all-of",
        lambda value: get_procedure(value, "NET-E03")["branch_execution_model"][
            "alternative_groups"
        ].pop(2),
        "lacks typed ALL_OF composition",
    )

    def remove_raw_blocker(value: dict[str, Any]) -> None:
        blockers = value["topology_candidate"]["unresolved_blockers"]
        blockers[:] = [
            item
            for item in blockers
            if item["id"] != "BLOCKER-HDL-RAW-INSTALLER-SOURCE"
        ]

    expect_failure(
        "missing-raw-source-blocker",
        remove_raw_blocker,
        "raw-download source defect is not freeze-blocking",
    )
    expect_failure(
        "unsafe-freeze-gate",
        lambda value: value["topology_candidate"]["freeze_gate"].update({"freeze_allowed": True}),
        "freeze gate does not fail closed",
    )
    expect_failure(
        "missing-handoff-family",
        lambda value: value["cross_page_handoffs"].pop(),
        "handoff families do not reconcile",
    )

    def remove_api_binding(value: dict[str, Any]) -> None:
        family = next(item for item in value["cross_page_handoffs"] if item["id"] == "HANDOFF-API-001")
        family["bindings"].pop()

    expect_failure(
        "missing-api-contract",
        remove_api_binding,
        "API handoff does not enumerate",
    )

    def unknown_handoff_target(value: dict[str, Any]) -> None:
        family = value["cross_page_handoffs"][0]
        family["bindings"][0]["target_requirements"][0]["owner_id"] = "UNKNOWN-PROCEDURE"

    expect_failure(
        "unknown-handoff-target",
        unknown_handoff_target,
        "unknown support target",
    )

    def cyclic_handoff(value: dict[str, Any]) -> None:
        family = next(item for item in value["cross_page_handoffs"] if item["id"] == "HANDOFF-FLT-RM-001")
        family["bindings"].append(
            handoff_binding(
                "BIND-SELFTEST-CYCLE",
                "RM-E04",
                "RM-E04-B01",
                [("PROCEDURE", "MNT-E01")],
                "mutation",
                "mutation",
                "mutation",
            )
        )

    expect_failure(
        "handoff-cycle",
        cyclic_handoff,
        "handoff graph is cyclic",
    )
    expect_failure(
        "absolute-metadata",
        lambda value: value["topology_candidate"].update({"debug_path": "/private/tmp/private.json"}),
        "restricted/absolute metadata",
    )
    expect_failure(
        "restricted-key-field",
        lambda value: value["topology_candidate"].update({"raw_target": "restricted-coordinate"}),
        "restricted/absolute metadata",
    )
    expect_failure(
        "reconciliation-count",
        lambda value: value["reconciliation"].update({"procedures": 1}),
        "reconciliation count mismatch",
    )
    expect_failure(
        "declared-count",
        lambda value: value["topology_candidate"]["counts"].update({"branches": 1}),
        "topology count mismatch",
    )
    expect_failure(
        "plan-digest",
        lambda value: value.update({"plan_baseline_sha256": "0" * 64}),
        "plan baseline digest mismatch",
    )
    expect_failure(
        "content-hash",
        lambda value: value["topology_candidate"].update({"content_sha256_excluding_self": "0" * 64}),
        "content hash mismatch",
    )
    expect_failure(
        "frozen-state",
        lambda value: value["freeze"].update({"state": "FROZEN"}),
        "lifecycle does not remain draft",
    )
    expect_failure(
        "live-authority",
        lambda value: value["execution_readiness"].update({"new_live_execution_allowed": True}),
        "improperly authorizes live execution",
    )
    expect_failure(
        "missing-outcome",
        lambda value: value["branch_outcomes"].pop(),
        "branch outcomes are not one-to-one",
    )

    def unsafe_negative_outcome(value: dict[str, Any]) -> None:
        record = next(item for item in value["branch_outcomes"] if item["branch_id"] == "SHW-C01-B-unsupported")
        record["contributes_to_parent_pass_when_applicable"] = True

    expect_failure(
        "negative-outcome-pass",
        unsafe_negative_outcome,
        "improperly contributes to parent PASS",
    )

    def remove_step_remap(value: dict[str, Any]) -> None:
        rows = value["topology_candidate"]["id_remap"]["steps"]
        rows[:] = [row for row in rows if row["old_id"] != "COM-E01-request-s01"]

    expect_failure(
        "undeclared-id-remap",
        remove_step_remap,
        "missing deterministic remap for removed steps ID",
    )
    expect_failure(
        "input-pin",
        lambda value: value["topology_candidate"]["input_artifacts"]["canonical_baseline"].update({"sha256": "0" * 64}),
        "input pin mismatch",
    )
    expect_failure(
        "unknown-top-level",
        lambda value: value.update({"parallel_ledger": {}}),
        "unknown candidate top-level fields",
    )
    expect_failure(
        "unknown-procedure-field",
        lambda value: value["procedures"][0].update({"unvalidated_extra": True}),
        "canonical projection",
    )

    tests += 1
    replay, _ = build_candidate()
    if json.dumps(replay, sort_keys=True, ensure_ascii=False) != json.dumps(
        candidate, sort_keys=True, ensure_ascii=False
    ):
        failures.append("deterministic replay changed candidate content")

    if failures:
        raise CandidateError(
            f"self-test failed ({len(failures)}/{tests}): " + " | ".join(failures)
        )
    return tests


def canonical_serialized_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Temporary output path; the canonical baseline is never a permitted target.",
    )
    parser.add_argument(
        "--check",
        type=Path,
        help="Validate and replay-compare an existing candidate instead of writing.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run focused fail-closed mutation and deterministic-replay tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate, metadata = build_candidate()
    errors = validate_candidate(candidate, metadata["canonical"])
    if errors:
        raise CandidateError("candidate validation failed: " + " | ".join(errors))

    self_test_count = 0
    if args.self_test:
        self_test_count = run_self_test(candidate, metadata["canonical"])

    if args.check is not None:
        if not args.check.is_file():
            raise CandidateError(f"check target is missing: {args.check.name}")
        checked = load_json(args.check)
        checked_errors = validate_candidate(checked, metadata["canonical"])
        if checked_errors:
            raise CandidateError("checked candidate failed: " + " | ".join(checked_errors))
        if checked != candidate:
            raise CandidateError("checked candidate does not match deterministic replay")
        if args.check.read_bytes() != canonical_serialized_bytes(candidate):
            raise CandidateError("checked candidate bytes are not canonical deterministic serialization")
        mode = "check"
        output = args.check
    else:
        output = args.output.resolve()
        if output == CANONICAL_PATH.resolve():
            raise CandidateError("refusing to overwrite canonical procedure baseline")
        if output.parent != Path("/private/tmp"):
            raise CandidateError("isolated topology candidate output must be directly under /private/tmp")
        write_json(output, candidate)
        mode = "build"

    print(
        json.dumps(
            {
                "validation_result": "CONFORMANT",
                "mode": mode,
                "candidate": output.name,
                "baseline_id": candidate["baseline_id"],
                "content_sha256_excluding_self": candidate["topology_candidate"]["content_sha256_excluding_self"],
                "counts": candidate["topology_candidate"]["counts"],
                "self_tests": self_test_count,
                "freeze_allowed": False,
                "live_execution_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CandidateError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
