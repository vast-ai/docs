#!/usr/bin/env python3
"""Recompute the reviewed P1 context/governance model on repaired topology.

This is an isolated composition input.  It binds exact reviewed topology and context
artifacts, then recomputes every ID-bound section, procedure context, cleanup contract,
authority requirement, and evidence policy from the repaired topology.  It never writes
the canonical baseline, executes a documented instruction, or assigns PASS.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from build_procedure_context_candidate import (
    CandidateError,
    ADDED_RESULT_STATUSES,
    PRIVATE_PATH_RE,
    authority_requirement,
    canonical_json,
    cleanup_contract,
    evidence_governance,
    inventory_counts,
    load_json_object,
    parse_frontmatter_personas,
    repo_file,
    section_records,
    sha256_bytes,
    sha256_path,
    typed_representative_context,
)


REPO = Path(__file__).resolve().parents[1]
TOPOLOGY_PATH = Path("/private/tmp/procedure-baseline-p1-topology-reviewer2-candidate.json")
TOPOLOGY_REVIEW_PATH = Path("/private/tmp/host-docs-p1-topology-reviewer2.json")
CONTEXT_PATH = Path("/private/tmp/procedure-baseline-p1-context-candidate.json")
CONTEXT_REVIEW_PATH = Path("/private/tmp/procedure-baseline-p1-context-review.json")
CONTEXT_BUILDER_PATH = REPO / "scripts/build_procedure_context_candidate.py"
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-context-topology-rebase-candidate.json")

EXPECTED = {
    "topology": "41f1c65bec8dd1e45d842884915bb117273c7ca018f41b3c3b6c3eb5fefa4599",
    "topology_review": "3075e4e86849d38f615155d69a64eac2482092030598ac41e520626f162c506b",
    "context": "24900d77adaa610c01a80b3937a5489fe9454d472b1e8c963e701e8b86f28e3d",
    "context_review": "9b6043de4a1061989e0b660c4c4b9e5e8443b83f072c7045bed236280c354d90",
    "context_builder": "90e1a97092ae659c93327ece79456875ef2abc17142a19d1b01ae43e02d51953",
}
EXPECTED_COUNTS = {"pages": 39, "procedures": 97, "branches": 203, "steps": 468}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")
    else:
        yield path, value


def source_projection(candidate: dict[str, Any]) -> dict[str, Any]:
    """Remove only fields introduced by this context/governance rebase."""
    value = copy.deepcopy(candidate)
    for key in (
        "context_topology_rebase_metadata",
        "context_governance_reconciliation",
        "evidence_governance",
        "governance",
    ):
        value.pop(key, None)
    value["schema_version"] = value.pop("source_schema_version")
    value["record_type"] = value.pop("source_record_type")
    for page in value["pages"]:
        for key in (
            "persona_ids",
            "disposition_rationale",
            "actionable_section_records",
            "authority_requirement_ids",
        ):
            page.pop(key, None)
    for proc in value["procedures"]:
        proc["representative_context"] = proc.pop("representative_context_legacy")
        for key in ("cleanup_contract", "authority_requirement"):
            proc.pop(key, None)
    return value


def normalized_digest(candidate: dict[str, Any]) -> str:
    value = copy.deepcopy(candidate)
    value["context_topology_rebase_metadata"]["normalized_content_sha256"] = None
    for event in value["governance"]["change_records"]:
        if event["id"] == "CHANGE-P1-CONTEXT-TOPOLOGY-REBASE":
            event["output_artifact"]["sha256"] = None
    return sha256_bytes(canonical_json(value))


def preflight(
    topology: dict[str, Any],
    topology_raw: bytes,
    topology_review: dict[str, Any],
    context: dict[str, Any],
    context_raw: bytes,
    context_review: dict[str, Any],
) -> None:
    require(sha256_bytes(topology_raw) == EXPECTED["topology"], "repaired topology bytes changed")
    require(sha256_path(TOPOLOGY_REVIEW_PATH) == EXPECTED["topology_review"], "topology review bytes changed")
    require(sha256_bytes(context_raw) == EXPECTED["context"], "reviewed context candidate bytes changed")
    require(sha256_path(CONTEXT_REVIEW_PATH) == EXPECTED["context_review"], "context review bytes changed")
    require(sha256_path(CONTEXT_BUILDER_PATH) == EXPECTED["context_builder"], "reviewed context builder bytes changed")
    require(inventory_counts(topology) == EXPECTED_COUNTS, f"unexpected repaired topology counts: {inventory_counts(topology)}")
    require(topology.get("state") == "DRAFT_NOT_FROZEN", "topology is not a draft")
    require(topology.get("freeze", {}).get("state") == "NOT_FROZEN", "topology is unexpectedly frozen")
    require(topology.get("execution_readiness", {}).get("new_live_execution_allowed") is False,
            "topology unexpectedly permits live execution")
    require(topology.get("topology_candidate", {}).get("freeze_gate", {}).get("freeze_allowed") is False,
            "topology candidate unexpectedly permits freeze")
    require(context.get("candidate_metadata", {}).get("source_baseline_sha256") ==
            "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912",
            "reviewed context source binding changed")
    require(context.get("candidate_metadata", {}).get("normalized_content_sha256") ==
            "1d6de38de49fc2141eea70d20fe3b3d7fba008e37d454298983f32b7b9842f8a",
            "reviewed context normalized digest changed")
    require(topology_review.get("verdict", {}).get("replacement_candidate_for_isolated_composition_input") == "GO",
            "topology review does not permit isolated composition")
    require(context_review.get("verdicts", {}).get("candidate_layer_integration", {}).get("decision") == "GO",
            "context review does not permit isolated composition")


def build_candidate(topology: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(topology)
    candidate["source_schema_version"] = candidate["schema_version"]
    candidate["source_record_type"] = candidate["record_type"]
    candidate["schema_version"] = "host-docs-p1-context-topology-rebase/1.0"
    candidate["record_type"] = "HOST_DOCS_P1_CONTEXT_TOPOLOGY_REBASE_CANDIDATE"

    reviewed_page_by_id = {page["id"]: page for page in context["pages"]}
    page_by_id: dict[str, dict[str, Any]] = {}
    for page in candidate["pages"]:
        reviewed = reviewed_page_by_id[page["id"]]
        lines = repo_file(page["source_file"]).read_text(encoding="utf-8").splitlines()
        personas = parse_frontmatter_personas(lines, page["source_file"])
        require(personas == reviewed["persona_ids"], f"{page['id']}: reviewed persona derivation changed")
        page["persona_ids"] = personas
        page["disposition_rationale"] = reviewed["disposition_rationale"]
        page["actionable_section_records"] = section_records(page, candidate)
        page_by_id[page["id"]] = page

    authority_questions: list[dict[str, Any]] = []
    for proc in candidate["procedures"]:
        page = page_by_id[proc["page_id"]]
        proc["representative_context_legacy"] = copy.deepcopy(proc["representative_context"])
        proc["representative_context"] = typed_representative_context(proc, page)
        proc["cleanup_contract"] = cleanup_contract(proc)
        proc["authority_requirement"] = authority_requirement(proc, page, candidate)
        authority_questions.append(copy.deepcopy(proc["authority_requirement"]))

    requirements_by_proc = {proc["id"]: proc["authority_requirement"]["id"] for proc in candidate["procedures"]}
    for page in candidate["pages"]:
        page["authority_requirement_ids"] = [requirements_by_proc[item] for item in page["procedure_ids"]]

    evidence = evidence_governance(candidate)
    candidate["evidence_governance"] = evidence
    roles = copy.deepcopy(context["governance"]["roles"])
    change = {
        "id": "CHANGE-P1-CONTEXT-TOPOLOGY-REBASE",
        "recorded_at": topology["created_at"],
        "recorded_at_precision": "SECOND",
        "timestamp_basis": "INHERITED_PINNED_SOURCE_TARGET_IDENTITY_NOT_EXECUTION_TIME",
        "actor_role_id": "ROLE-P1-AUTHOR",
        "actor_id": "ACTOR-P1-CONTEXT-BUILDER",
        "event": "RECOMPUTE_CONTEXT_GOVERNANCE_ON_REPAIRED_TOPOLOGY",
        "rationale": "Recompute every ID-bound reviewed context/governance contract after topology repair; copy no result from a parent to split children.",
        "affected_ids": {
            "page_ids": [page["id"] for page in candidate["pages"]],
            "procedure_ids": [proc["id"] for proc in candidate["procedures"]],
            "branch_ids": [branch["id"] for proc in candidate["procedures"] for branch in proc["branches"]],
        },
        "input_artifacts": [
            {"artifact_id": "P1-REPAIRED-TOPOLOGY-CANDIDATE", "sha256": EXPECTED["topology"]},
            {"artifact_id": "P1-TOPOLOGY-INDEPENDENT-REVIEW", "sha256": EXPECTED["topology_review"]},
            {"artifact_id": "P1-REVIEWED-CONTEXT-CANDIDATE", "sha256": EXPECTED["context"]},
            {"artifact_id": "P1-CONTEXT-INDEPENDENT-REVIEW", "sha256": EXPECTED["context_review"]},
            {"artifact_id": "P1-REVIEWED-CONTEXT-BUILDER", "sha256": EXPECTED["context_builder"]},
        ],
        "output_artifact": {
            "artifact_id": "P1-CONTEXT-TOPOLOGY-REBASE-CANDIDATE",
            "sha256": None,
            "digest_state": "NORMALIZED_CONTENT_SHA256_EXCLUDING_SELF_FIELDS",
        },
        "evidence_impact": "Adds planned context/governance contracts only; no runtime, rendered, or result evidence is added.",
        "stale_result_impact": "No result is copied or promoted; every recomputed record remains UNVALIDATED or BLOCKED.",
        "status": "UNVALIDATED",
    }
    candidate["governance"] = {
        "schema_version": "host-docs-governance/1.0",
        "roles": roles,
        "role_separation_constraints": copy.deepcopy(context["governance"]["role_separation_constraints"]),
        "change_records": copy.deepcopy(context["governance"]["change_records"]) + [change],
        "human_acceptance": "NOT_DECIDED",
        "status": "UNVALIDATED",
    }

    section_total = sum(len(page["actionable_section_records"]) for page in candidate["pages"])
    branch_contracts = [item for proc in candidate["procedures"] for item in proc["cleanup_contract"]["branch_contracts"]]
    authority_states = Counter(item["current_authority_state"] for item in authority_questions)
    pending_roles = [role["id"] for role in roles if role["assignment_state"].startswith("PENDING")]
    candidate["context_governance_reconciliation"] = {
        "pages": len(candidate["pages"]),
        "actionable_sections": section_total,
        "raw_section_occurrences": section_total,
        "rendered_section_occurrences": section_total,
        "procedures": len(candidate["procedures"]),
        "typed_procedure_contexts": len(candidate["procedures"]),
        "cleanup_branch_contracts": len(branch_contracts),
        "cleanup_required": sum(item["cleanup_required"] for item in branch_contracts),
        "cleanup_not_required_or_delegated": sum(not item["cleanup_required"] for item in branch_contracts),
        "cleanup_blocked": sum(item["status"] == "BLOCKED" for item in branch_contracts),
        "branch_evidence_policies": len(evidence["branch_policies"]),
        "artifact_policies": len(evidence["artifact_policies"]),
        "procedure_authority_requirements": len(authority_questions),
        "authority_state_counts": dict(sorted(authority_states.items())),
        "pending_role_ids": pending_roles,
        "topology_effect": "RECOMPUTED_ON_EXACT_REPAIRED_TOPOLOGY_WITHOUT_TOPOLOGY_MUTATION",
        "executable_unit_effect": "NO_NEW_EXECUTABLE_TEST_UNIT",
        "execution_performed": False,
        "pass_assigned": False,
    }
    candidate["context_topology_rebase_metadata"] = {
        "candidate_id": "P1-CONTEXT-TOPOLOGY-REBASE-CANDIDATE",
        "builder": "scripts/build_procedure_context_topology_rebase.py",
        "input_sha256": copy.deepcopy(EXPECTED),
        "normalized_content_sha256": None,
        "normalized_digest_profile": "SHA256_CANONICAL_JSON_EXCLUDING_SELF_DIGEST_AND_CHANGE_OUTPUT_DIGEST",
        "composition_policy": "ISOLATED_INPUT_REQUIRES_INDEPENDENT_REVIEW_AND_FINAL_COMPOSITION",
        "split_rebase_policy": "RECOMPUTED_FROM_CHILD_TOPOLOGY; NO PARENT RESULT OR OBSERVATION COPIED",
        "state": "DRAFT_NOT_FROZEN",
        "status": "UNVALIDATED",
    }
    digest = normalized_digest(candidate)
    candidate["context_topology_rebase_metadata"]["normalized_content_sha256"] = digest
    change["output_artifact"]["sha256"] = digest
    return candidate


def validate(candidate: dict[str, Any], topology: dict[str, Any]) -> None:
    require(candidate.get("schema_version") == "host-docs-p1-context-topology-rebase/1.0", "wrong schema")
    require(candidate.get("record_type") == "HOST_DOCS_P1_CONTEXT_TOPOLOGY_REBASE_CANDIDATE", "wrong record type")
    require(source_projection(candidate) == topology, "context rebase changed repaired topology or orthogonal data")
    require(inventory_counts(candidate) == EXPECTED_COUNTS, "candidate counts differ from repaired topology")
    require(candidate.get("state") == "DRAFT_NOT_FROZEN", "candidate is not a draft")
    require(candidate.get("freeze", {}).get("state") == "NOT_FROZEN", "candidate is unexpectedly frozen")
    require(candidate.get("execution_readiness", {}).get("new_live_execution_allowed") is False,
            "candidate unexpectedly permits live execution")
    require(candidate["context_governance_reconciliation"]["execution_performed"] is False,
            "candidate claims execution")
    require(candidate["context_governance_reconciliation"]["pass_assigned"] is False, "candidate claims PASS")
    require(candidate["context_governance_reconciliation"]["executable_unit_effect"] == "NO_NEW_EXECUTABLE_TEST_UNIT",
            "candidate creates an executable unit")

    page_ids = {page["id"] for page in candidate["pages"]}
    proc_ids = {proc["id"] for proc in candidate["procedures"]}
    branch_pairs = {(proc["id"], branch["id"]) for proc in candidate["procedures"] for branch in proc["branches"]}
    require(len(page_ids) == len(candidate["pages"]), "duplicate page ID")
    require(len(proc_ids) == len(candidate["procedures"]), "duplicate procedure ID")
    require(len(branch_pairs) == EXPECTED_COUNTS["branches"], "duplicate or missing branch identity")
    require({(item["procedure_id"], item["branch_id"]) for item in candidate["evidence_governance"]["branch_policies"]}
            == branch_pairs, "evidence policies do not exactly cover repaired branches")
    for page in candidate["pages"]:
        require(page["authority_requirement_ids"] == [f"AUTHREQ-{item}" for item in page["procedure_ids"]],
                f"{page['id']}: authority requirements do not follow repaired procedure IDs")
        require(len(page["actionable_section_records"]) == len(page["actionable_sections"]),
                f"{page['id']}: actionable section coverage changed")
    for proc in candidate["procedures"]:
        branch_ids = [branch["id"] for branch in proc["branches"]]
        representative_context = proc.get("representative_context")
        require(isinstance(representative_context, dict), f"{proc['id']}: missing typed representative context")
        validation_use_case = representative_context.get("validation_use_case")
        require(isinstance(validation_use_case, dict), f"{proc['id']}: missing validation use case")
        require(validation_use_case.get("applicable_branch_ids") == branch_ids,
                f"{proc['id']}: representative context is not rebound to repaired branches")
        cleanup = proc.get("cleanup_contract")
        require(isinstance(cleanup, dict) and isinstance(cleanup.get("branch_contracts"), list),
                f"{proc['id']}: missing cleanup contract")
        require([item["branch_id"] for item in cleanup["branch_contracts"]] == branch_ids,
                f"{proc['id']}: cleanup contracts are not rebound to repaired branches")
        authority = proc.get("authority_requirement")
        require(isinstance(authority, dict), f"{proc['id']}: missing authority requirement")
        require(authority.get("id") == f"AUTHREQ-{proc['id']}",
                f"{proc['id']}: authority requirement is not child-specific")
        bounded = authority.get("bounded_claim_supported")
        require(isinstance(bounded, dict) and bounded.get("procedure_id") == proc["id"],
                f"{proc['id']}: authority claim still references a parent")

    expected_digest = normalized_digest(candidate)
    require(candidate["context_topology_rebase_metadata"]["normalized_content_sha256"] == expected_digest,
            "normalized digest mismatch")
    require(candidate["governance"]["change_records"][-1]["output_artifact"]["sha256"] == expected_digest,
            "change output digest mismatch")
    for path, value in walk(candidate):
        if isinstance(value, str):
            if path.endswith(".status"):
                require(value in ADDED_RESULT_STATUSES or value in {
                    "DRAFT_NOT_FROZEN", "PENDING", "NOT_READY", "NOT_DECIDED",
                    "DISCOVERED_PENDING_INDEPENDENT_REVIEW", "PENDING_INDEPENDENT_REVIEW",
                    "PENDING_OWNER_EXACT_SOURCE_DECISION", "UNVALIDATED_PENDING_TOPOLOGY_RECONCILIATION",
                }, f"{path}: unexpected status-like value {value!r}")
            require(not PRIVATE_PATH_RE.search(value), f"{path}: private path leaked")


def self_test(candidate: dict[str, Any], topology: dict[str, Any]) -> int:
    tests: list[tuple[str, bool]] = []

    def mutation(name: str, mutate: Callable[[dict[str, Any]], None]) -> None:
        value = copy.deepcopy(candidate)
        mutate(value)
        if name != "digest forgery fails closed":
            digest = normalized_digest(value)
            value["context_topology_rebase_metadata"]["normalized_content_sha256"] = digest
            value["governance"]["change_records"][-1]["output_artifact"]["sha256"] = digest
        try:
            validate(value, topology)
        except CandidateError:
            tests.append((name, True))
        else:
            tests.append((name, False))

    mutation("topology mutation fails closed", lambda d: d["procedures"][0]["branches"].pop())
    mutation("split child context removal fails closed", lambda d: d["procedures"][-1].pop("representative_context"))
    mutation("branch policy removal fails closed", lambda d: d["evidence_governance"]["branch_policies"].pop())
    mutation("cleanup branch removal fails closed", lambda d: d["procedures"][0]["cleanup_contract"]["branch_contracts"].pop())
    mutation("parent authority reference fails closed", lambda d: d["procedures"][-1]["authority_requirement"]["bounded_claim_supported"].update(procedure_id="PARENT"))
    mutation("page authority removal fails closed", lambda d: d["pages"][0]["authority_requirement_ids"].pop())
    mutation("PASS fails closed", lambda d: d["procedures"][0]["cleanup_contract"].update(status="PASS"))
    mutation("live enable fails closed", lambda d: d["execution_readiness"].update(new_live_execution_allowed=True))
    mutation("freeze enable fails closed", lambda d: d["freeze"].update(state="FROZEN"))
    mutation("execution claim fails closed", lambda d: d["context_governance_reconciliation"].update(execution_performed=True))
    mutation("private path fails closed", lambda d: d["context_topology_rebase_metadata"].update(note="/private/tmp/raw"))
    mutation("digest forgery fails closed", lambda d: d["context_topology_rebase_metadata"].update(normalized_content_sha256="0" * 64))
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
    topology, topology_raw = load_json_object(TOPOLOGY_PATH)
    topology_review, _ = load_json_object(TOPOLOGY_REVIEW_PATH)
    context, context_raw = load_json_object(CONTEXT_PATH)
    context_review, _ = load_json_object(CONTEXT_REVIEW_PATH)
    preflight(topology, topology_raw, topology_review, context, context_raw, context_review)
    expected = build_candidate(topology, context)
    validate(expected, topology)
    tests = self_test(expected, topology) if args.self_test else 0
    if args.check is not None:
        actual, actual_raw = load_json_object(Path(args.check))
        validate(actual, topology)
        require(actual == expected, "candidate content differs from deterministic rebuild")
        require(actual_raw == canonical_json(expected, pretty=True), "candidate serialization is not canonical")
        mode = "check"
        output = Path(args.check)
    else:
        require(args.output.resolve() != (REPO / "verification/procedure-baseline-p1.json").resolve(),
                "refusing to overwrite canonical P1")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_json(expected, pretty=True))
        mode = "write"
        output = args.output
    print(json.dumps({
        "mode": mode,
        "path": str(output),
        "sha256": sha256_path(output),
        "normalized_content_sha256": expected["context_topology_rebase_metadata"]["normalized_content_sha256"],
        "counts": inventory_counts(expected),
        "self_tests": tests,
        "result": "PASS",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CandidateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
