#!/usr/bin/env python3
"""Build an isolated deterministic P1 context/governance candidate.

This builder is intentionally orthogonal to the topology and raw-claim candidates.  It
adds page personas and source/rendered section occurrences, typed procedure validation
contexts, branch cleanup/end-state contracts, evidence-governance policies, accountable
roles, append-only change provenance, and procedure authority questions.  It does not
change procedure/branch/step IDs or dependency topology, does not execute documented
instructions, and never assigns PASS.

The canonical baseline is never overwritten.  The default output is a temporary
candidate suitable for independent review and later deterministic composition.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
CANONICAL_PATH = REPO / "verification/procedure-baseline-p1.json"
AUDIT_PATH = Path("/private/tmp/host-docs-p1-goal-schema-audit.json")
DEFAULT_OUTPUT = Path("/private/tmp/procedure-baseline-p1-context-candidate.json")

EXPECTED_CANONICAL_SHA256 = "2aaffc06411c85ecdfee51c60432a7b3e9dfb970cafbb71f56ff243f21fcc912"
EXPECTED_AUDIT_SHA256 = "4aa7984dd7bac5abaa396ec9bdf14f90929fafcbe5015dca6788734387f1b090"
EXPECTED_COUNTS = {"pages": 39, "sections": 254, "procedures": 82, "branches": 193, "steps": 454}
ALLOWED_VV_STATUSES = {"UNVALIDATED", "PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE", "STALE"}
ADDED_RESULT_STATUSES = {"UNVALIDATED", "BLOCKED"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMPORT_RE = re.compile(r"^import\s+([A-Za-z_$][\w$]*)\s+from\s+['\"]([^'\"]+)['\"];?\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\((/host/[^)\s]+)\)")
PRIVATE_PATH_RE = re.compile(r"(?:/Users/|/private/tmp/|file://)")

PERSONA_CATALOG = {
    "pro-operator": "Professional Host operator",
    "headless-operator": "Headless or datacenter Host operator",
    "business-owner": "Host business owner",
    "hobbyist": "Hobbyist or first-time Host",
}

DISPOSITION_RATIONALES = {
    "procedure-bearing": (
        "The page contains one or more complete, diagnostic, or operational Host procedures "
        "whose ordered outcomes require procedure-level V&V."
    ),
    "conceptual/policy": (
        "The page primarily supports Host decisions, concepts, policy, or source-owner claims; "
        "it is not converted into a synthetic command test."
    ),
    "navigation/cross-page journey": (
        "The page routes the Host through ordered child pages or canonical references; child "
        "procedures retain their own execution and cleanup obligations."
    ),
    "generated-reference": (
        "The page is a generated reference whose source/generator contract and rendered use "
        "must be checked separately from runtime procedures."
    ),
    "reference-only": "The page is a reference surface and does not itself define an end-to-end workflow.",
    "no-actionable-instruction": "No actionable Host instruction was identified at this pinned source revision.",
}

SOURCE_OWNER_ROLES = {
    "legal": "ROLE-SOURCE-OWNER-LEGAL-POLICY",
    "finance": "ROLE-SOURCE-OWNER-FINANCE-MARKET",
    "security": "ROLE-SOURCE-OWNER-IDENTITY-SECURITY",
    "engineering": "ROLE-SOURCE-OWNER-HOST-ENGINEERING",
    "product": "ROLE-SOURCE-OWNER-HOST-PRODUCT",
    "documentation": "ROLE-SOURCE-OWNER-DOCUMENTATION",
}

HIGH_RISK_TERMS = {
    "destructive", "mutating", "mutation", "paid", "listener", "packet-capture",
    "service-restart", "service-impacting", "reboot", "storage", "firewall", "router",
    "financial/contract effect", "financial/account mutating", "account-mutating", "account mutating", "team/account mutating",
    "host-root", "credentialed-install", "secret-bearing install flow", "potentially destructive",
}
SENSITIVE_TERMS = {
    "credential", "secret", "api", "account", "team", "payment", "financial", "billing",
    "machine", "offer", "instance", "network", "wan", "ssh", "log", "diagnostic",
    "packet-capture", "private-business-data", "privacy-sensitive", "security-sensitive",
}


class CandidateError(RuntimeError):
    """The candidate cannot be safely or deterministically built."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def canonical_json(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_id(prefix: str, namespace: str, *parts: Any) -> str:
    payload = namespace + "\0" + "\0".join(str(part) for part in parts)
    return prefix + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def repo_file(raw: str) -> Path:
    path = Path(raw)
    require(not path.is_absolute() and ".." not in path.parts, f"repository path escapes root: {raw!r}")
    resolved = (REPO / path).resolve()
    require(REPO.resolve() in resolved.parents and resolved.is_file(), f"missing repository file: {raw!r}")
    return resolved


def load_json_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateError(f"{path}: invalid UTF-8 JSON: {exc}") from exc
    require(isinstance(value, dict), f"{path}: top level must be an object")
    return value, raw


def topology_signature(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_ids": [page["id"] for page in record.get("pages", [])],
        "procedure_ids": [proc["id"] for proc in record.get("procedures", [])],
        "procedure_pages": [(proc["id"], proc["page_id"]) for proc in record.get("procedures", [])],
        "branch_models": [
            (proc["id"], copy.deepcopy(proc["branch_execution_model"]))
            for proc in record.get("procedures", [])
        ],
        "branches": [
            (proc["id"], copy.deepcopy(branch))
            for proc in record.get("procedures", [])
            for branch in proc.get("branches", [])
        ],
    }


def inventory_counts(record: dict[str, Any]) -> dict[str, int]:
    return {
        "pages": len(record.get("pages", [])),
        "procedures": len(record.get("procedures", [])),
        "branches": sum(len(proc.get("branches", [])) for proc in record.get("procedures", [])),
        "steps": sum(
            len(branch.get("steps", []))
            for proc in record.get("procedures", [])
            for branch in proc.get("branches", [])
        ),
    }


def preflight(baseline: dict[str, Any], baseline_raw: bytes, audit: dict[str, Any], audit_raw: bytes) -> None:
    require(sha256_bytes(baseline_raw) == EXPECTED_CANONICAL_SHA256,
            "canonical P1 baseline changed; explicitly rebaseline before rebuilding this candidate")
    require(sha256_bytes(audit_raw) == EXPECTED_AUDIT_SHA256,
            "goal-schema audit changed; explicitly review and repin before rebuilding this candidate")
    require(inventory_counts(baseline) == {key: EXPECTED_COUNTS[key] for key in ("pages", "procedures", "branches", "steps")},
            f"unexpected canonical topology: {inventory_counts(baseline)}")
    require(baseline.get("state") == "DRAFT_NOT_FROZEN", "canonical baseline is not a draft")
    require(baseline.get("freeze", {}).get("state") == "NOT_FROZEN", "canonical baseline freeze state changed")
    require(baseline.get("execution_readiness", {}).get("new_live_execution_allowed") is False,
            "canonical baseline unexpectedly permits live execution")
    verdict = audit.get("verdict", {})
    require(isinstance(verdict, dict) and verdict.get("p1_freeze") == "NO_GO"
            and verdict.get("candidate_integration") == "NO_GO",
            "audit no longer records P1/candidate integration as NO_GO")
    finding_ids = {finding.get("id") for finding in audit.get("findings", [])}
    require({f"P1-SCHEMA-{number:03d}" for number in range(4, 10)} <= finding_ids,
            "audit is missing a required context/governance finding")
    require(all(page.get("status") == "UNVALIDATED" for page in baseline["pages"]),
            "canonical page result changed")
    require(all(proc.get("status") == "UNVALIDATED" for proc in baseline["procedures"]),
            "canonical procedure result changed")


def normalize_heading(value: str) -> str:
    value = value.replace("`", "").replace("&amp;", "and")
    value = re.sub(r"\{#[^}]+\}\s*$", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(value.split())


def anchor_for(value: str) -> str:
    value = value.replace("`", "").lower()
    value = re.sub(r"[^a-z0-9 _-]+", "", value)
    return re.sub(r"[-\s_]+", "-", value).strip("-") or "introduction"


def parse_frontmatter_personas(lines: list[str], file: str) -> list[str]:
    require(lines and lines[0].strip() == "---", f"{file}: expected MDX frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise CandidateError(f"{file}: unterminated MDX frontmatter") from exc
    personas: list[str] = []
    active = False
    for line in lines[1:end]:
        if line.strip() == "personas:":
            active = True
            continue
        if active:
            match = re.match(r"^\s+-\s+([^#]+?)\s*$", line)
            if match:
                personas.append(match.group(1).strip(" \"'"))
                continue
            if line and not line[0].isspace():
                active = False
    require(personas, f"{file}: no frontmatter personas")
    require(all(persona in PERSONA_CATALOG for persona in personas),
            f"{file}: unknown persona in {personas}")
    return personas


def heading_records(lines: list[str], file: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    for index, line in enumerate(lines, 1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        level = len(match.group(1))
        title = re.sub(r"\s+\{#[^}]+\}\s*$", "", match.group(2)).strip()
        while stack and int(stack[-1]["level"]) >= level:
            stack.pop()
        path = [str(item["title"]) for item in stack] + [title]
        record = {"title": title, "normalized": normalize_heading(title), "level": level,
                  "line_start": index, "heading_path": path}
        headings.append(record)
        stack.append(record)
    for position, heading in enumerate(headings):
        end = len(lines)
        for later in headings[position + 1:]:
            if int(later["level"]) <= int(heading["level"]):
                end = int(later["line_start"]) - 1
                break
        heading["line_end"] = end
    require(headings, f"{file}: no headings available for actionable-section binding")
    return headings


def introduction_record(lines: list[str], headings: list[dict[str, Any]], file: str) -> dict[str, Any]:
    try:
        frontmatter_end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---") + 1
    except StopIteration as exc:
        raise CandidateError(f"{file}: unterminated frontmatter") from exc
    start = frontmatter_end + 1
    while start <= len(lines) and not lines[start - 1].strip():
        start += 1
    end = int(headings[0]["line_start"]) - 1
    require(start <= end, f"{file}: declared Introduction has no source body")
    return {"title": "Introduction", "normalized": "introduction", "level": 1,
            "line_start": start, "line_end": end, "heading_path": ["Introduction"]}


def source_imports(lines: list[str]) -> dict[str, str]:
    imports: dict[str, str] = {}
    for line in lines:
        match = IMPORT_RE.match(line.strip())
        if match:
            imports[match.group(1)] = match.group(2).lstrip("/")
    return imports


def section_records(page: dict[str, Any], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    file = str(page["source_file"])
    path = repo_file(file)
    raw = path.read_bytes()
    require(sha256_bytes(raw) == page["source_sha256"], f"{file}: page source hash changed")
    lines = raw.decode("utf-8").splitlines()
    headings = heading_records(lines, file)
    by_normalized: dict[str, list[dict[str, Any]]] = {}
    for heading in headings:
        by_normalized.setdefault(str(heading["normalized"]), []).append(heading)
    imports = source_imports(lines)
    fragment_by_file = {fragment["source_file"]: fragment for fragment in baseline.get("fragments", [])}
    contract_by_import = {
        str(contract["import_path"]).lstrip("/"): contract
        for contract in baseline.get("support_contracts", [])
    }
    page_by_route = {item["route"]: item for item in baseline["pages"]}
    procedures = [proc for proc in baseline["procedures"] if proc["page_id"] == page["id"]]
    output: list[dict[str, Any]] = []
    for ordinal, label in enumerate(page["actionable_sections"], 1):
        normalized = normalize_heading(str(label))
        if normalized == "introduction":
            heading = introduction_record(lines, headings, file)
        else:
            matches = by_normalized.get(normalized, [])
            require(len(matches) == 1, f"{file}: actionable section {label!r} maps to {len(matches)} headings")
            heading = matches[0]
        start, end = int(heading["line_start"]), int(heading["line_end"])
        span_text = "\n".join(lines[start - 1:end])
        span_hash = sha256_bytes(span_text.encode("utf-8"))
        heading_path = list(heading["heading_path"])
        section_id = stable_id("SECTION-", "host-docs-p1-actionable-section-v1", page["id"], *heading_path)
        raw_id = stable_id("RAWOCC-", "host-docs-p1-raw-section-occurrence-v1", file, *heading_path, span_hash, ordinal)
        anchor = anchor_for(str(heading["title"]))
        rendered_id = stable_id("RENDOCC-", "host-docs-p1-rendered-section-occurrence-v1",
                                page["route"], anchor, section_id)
        procedure_refs = sorted({
            proc["id"]
            for proc in procedures
            if not (int(proc["source_context"]["line_end"]) < start
                    or int(proc["source_context"]["line_start"]) > end)
        })
        links = sorted(set(LINK_RE.findall(span_text)))
        handoff_routes = sorted({link.split("#", 1)[0].split("?", 1)[0] for link in links})
        handoff_page_ids = sorted({page_by_route[route]["id"] for route in handoff_routes if route in page_by_route})
        import_occurrences: list[dict[str, Any]] = []
        for component, import_file in sorted(imports.items()):
            if not re.search(rf"<{re.escape(component)}(?:\s|/|>)", span_text):
                continue
            fragment = fragment_by_file.get(import_file)
            contract = contract_by_import.get(import_file)
            require(fragment is not None and contract is not None,
                    f"{file}: imported component {component} lacks fragment/support contract")
            import_occurrences.append({
                "id": stable_id("IMPOCC-", "host-docs-p1-import-occurrence-v1", section_id, component, import_file),
                "component": component,
                "source_file": import_file,
                "fragment_id": fragment["id"],
                "support_contract_id": contract["id"],
                "status": "UNVALIDATED",
            })
        output.append({
            "id": section_id,
            "legacy_label": label,
            "heading_path": heading_path,
            "source_span": {"file": file, "line_start": start, "line_end": end,
                            "source_file_sha256": page["source_sha256"], "source_span_sha256": span_hash},
            "raw_occurrence": {"id": raw_id, "inspection_state": "DISCOVERED_PENDING_INDEPENDENT_REVIEW",
                               "status": "UNVALIDATED"},
            "rendered_occurrence": {
                "id": rendered_id,
                "route": page["route"],
                "anchor": anchor,
                "anchor_basis": "DERIVED_EXPECTATION_PENDING_RENDERED_REVIEW",
                "evidence_refs": [],
                "status": "UNVALIDATED",
            },
            "procedure_refs": procedure_refs,
            "handoff_routes": handoff_routes,
            "handoff_page_ids": handoff_page_ids,
            "import_occurrences": import_occurrences,
            "status": "UNVALIDATED",
        })
    require(len(output) == len(page["actionable_sections"]), f"{page['id']}: section count changed")
    return output


def owner_role_for(proc: dict[str, Any], page: dict[str, Any]) -> str:
    haystack = " ".join([
        proc["id"], proc.get("title", ""), proc.get("goal", ""), page.get("navigation_group", ""),
        page.get("title", ""), " ".join(proc.get("access_classes", [])),
    ]).lower()
    if any(word in haystack for word in ("agreement", "legal", "tax", "policy")):
        return SOURCE_OWNER_ROLES["legal"]
    if any(word in haystack for word in ("payment", "payout", "billing", "earning", "price", "market", "finance")):
        return SOURCE_OWNER_ROLES["finance"]
    if any(word in haystack for word in ("security", "credential", "api key", "2fa", "account", "team")):
        return SOURCE_OWNER_ROLES["security"]
    if any(word in haystack for word in ("install", "storage", "network", "port", "hardware", "vm", "driver", "diagnostic")):
        return SOURCE_OWNER_ROLES["engineering"]
    if any(word in haystack for word in ("generated", "glossary", "reference")):
        return SOURCE_OWNER_ROLES["documentation"]
    return SOURCE_OWNER_ROLES["product"]


def typed_representative_context(proc: dict[str, Any], page: dict[str, Any]) -> dict[str, Any]:
    previous = proc["representative_context"]
    if isinstance(previous, dict):
        environment = str(previous.get("environment", "")).strip()
        intended_user = str(previous.get("intended_user", "")).strip()
        limit = str(previous.get("representativeness_limit", "")).strip()
    else:
        environment = str(previous).strip()
        intended_user = ", ".join(PERSONA_CATALOG[persona] for persona in page["persona_ids"])
        limit = "The context description is provisional until a claim-suitable attempt demonstrates its exact applicability."
    require(environment and intended_user and limit, f"{proc['id']}: incomplete representative context source")
    start_predicates: list[dict[str, Any]] = []
    for ordinal, prerequisite in enumerate(proc["prerequisites"], 1):
        start_predicates.append({
            "id": f"{proc['id']}-START-{ordinal:02d}",
            "predicate_type": "DOCUMENTED_PREREQUISITE_REQUIRED_STATE",
            "description": prerequisite,
            "definition_basis": "CANONICAL_PREREQUISITE_REQUIRES_INDEPENDENT_START_STATE_REVIEW",
            "expected_value": True,
            "observed_value": None,
            "evidence_requirement": {"artifact_type": "START_STATE_OBSERVATION", "observation_ref": None},
            "status": "UNVALIDATED",
        })
    return {
        "schema_version": "host-docs-procedure-context/1.0",
        "persona_ids": list(page["persona_ids"]),
        "intended_user": intended_user,
        "validation_use_case": {
            "id": f"USECASE-{proc['id']}",
            "user_goal": proc["goal"],
            "intended_outcome": list(proc["expected_final_observables"]),
            "claim_boundary": list(proc["test_basis"]["claim_boundary"]),
            "applicable_branch_ids": [branch["id"] for branch in proc["branches"]],
            "status": "UNVALIDATED",
        },
        "environment": {
            "description": environment,
            "target_alias": proc["authorized_environment"].get("target_alias"),
            "declared_access_classes": list(proc["authorized_environment"].get("access_classes", [])),
            "authorization_state": proc["authorized_environment"].get("approval_state"),
            "status": "UNVALIDATED",
        },
        "start_state": {
            "predicates": start_predicates,
            "must_be_observed_before_execution": True,
            "observation_attempt_id": None,
            "status": "UNVALIDATED",
        },
        "representativeness_rationale": (
            f"This context is representative only if the recorded intended user uses {environment} "
            f"to pursue the bounded goal for {proc['id']}; no current attempt has demonstrated that match."
        ),
        "representativeness_limit": limit,
        "status": "UNVALIDATED",
    }


def branch_access_terms(branch: dict[str, Any]) -> list[str]:
    gate = branch.get("execution_gate", {})
    values = list(gate.get("access_requirements", []))
    override = branch.get("access_override")
    if isinstance(override, list):
        values.extend(str(item) for item in override)
    elif override:
        values.append(str(override))
    return sorted(set(values))


def has_terms(values: list[str], terms: set[str]) -> bool:
    text = " ".join(values).lower()
    return any(term in text for term in terms)


def is_no_cleanup_statement(value: str) -> bool:
    normalized = value.strip().lower().rstrip(".")
    return normalized in {
        "none", "no resources created", "no runtime cleanup", "no runtime cleanup; remove sensitive financial inputs from public artifacts",
        "no external cleanup; delete or restrict unsanitized financial working data", "no runtime cleanup; sanitize hardware identifiers",
        "no runtime cleanup", "no runtime cleanup; ensure no personal tax data is captured",
        "no runtime resources; remove only isolated generated scratch output", "no cleanup for source review; remove any sensitive hardware identifiers from retained evidence",
    } or normalized.startswith("no resources created")


def cleanup_contract(proc: dict[str, Any]) -> dict[str, Any]:
    branch_contracts: list[dict[str, Any]] = []
    is_parent = proc.get("unit_type") == "P"
    source_cleanup = [str(item) for item in proc.get("cleanup", [])]
    for branch in proc["branches"]:
        access = branch_access_terms(branch)
        cleanup_steps = [
            {"step_id": step["id"], "instruction": step["instruction_summary"], "source": "CANONICAL_BRANCH_STEP"}
            for step in branch["steps"]
            if step.get("role") == "cleanup" or step.get("cleanup_required") is True
        ]
        risk_bearing = has_terms(access, HIGH_RISK_TERMS)
        sensitive = has_terms(access, SENSITIVE_TERMS)
        prose_actions = [item for item in source_cleanup if not is_no_cleanup_statement(item)]
        if is_parent:
            required = False
            ownership = "DELEGATED_TO_APPLICABLE_CHILD_PROCEDURE"
            rationale = "This parent journey creates no independent runtime state; each selected child owns and confirms its cleanup."
            cleanup_steps = []
        else:
            required = bool(cleanup_steps or risk_bearing or (sensitive and prose_actions))
            ownership = "PROCEDURE_EXECUTOR" if required else "NO_RUNTIME_STATE_CREATED"
            rationale = None if required else (
                "The planned branch is read-only, conceptual, or source-inspection work and creates no runtime resource; "
                "evidence handling remains governed separately."
            )
            if required and not cleanup_steps:
                cleanup_steps = [
                    {"step_id": None, "instruction": item, "source": "CANONICAL_CLEANUP_PROSE_PENDING_STEP_RECONCILIATION"}
                    for item in prose_actions
                ]
        end_state: list[dict[str, Any]] = []
        if required:
            for ordinal, step in enumerate(cleanup_steps, 1):
                instruction = str(step["instruction"]).strip().rstrip(".")
                end_state.append({
                    "id": f"ENDSTATE-{branch['id']}-{ordinal:02d}",
                    "predicate": f"Cleanup action is complete and its intended end state is observed: {instruction}.",
                    "expected_value": True,
                    "observation_ref": None,
                    "status": "UNVALIDATED",
                })
            if not end_state:
                end_state.append({
                    "id": f"ENDSTATE-{branch['id']}-01",
                    "predicate": "No temporary resource, mutation, listener, process, spend, or secret introduced by the branch remains.",
                    "expected_value": True,
                    "observation_ref": None,
                    "status": "UNVALIDATED",
                })
        missing_structured_step = required and not any(item["source"] == "CANONICAL_BRANCH_STEP" for item in cleanup_steps)
        blocked = bool(required and (risk_bearing or missing_structured_step))
        branch_contracts.append({
            "branch_id": branch["id"],
            "cleanup_required": required,
            "ownership": ownership,
            "delegated_to": "APPLICABLE_CHILD_PROCEDURE_SELECTED_BY_BRANCH" if is_parent else None,
            "cleanup_steps": cleanup_steps,
            "rollback_or_fallback": list(source_cleanup) if required else [],
            "required_end_state": end_state,
            "confirmation_observable": [item["predicate"] for item in end_state],
            "not_required_rationale": rationale,
            "decision_review_state": "PENDING_INDEPENDENT_REVIEW",
            "owner_role_id": "ROLE-PROCEDURE-EXECUTOR" if required else (
                "ROLE-APPLICABLE-CHILD-PROCEDURE" if is_parent else "ROLE-P1-RECONCILER"
            ),
            "escalation": {
                "required_if_cleanup_uncertain": required,
                "owner_role_id": "ROLE-HUMAN-SAFETY-APPROVER" if required else None,
                "path": "STOP_FOLLOW_UP_EXCEPT_CLEANUP_AND_ESCALATE_TO_NAMED_APPROVER" if required else None,
            },
            "blocker": ({
                "class": "CLEANUP_PLAN_OR_AUTHORIZATION_UNRESOLVED",
                "reason": "Risk-bearing or prose-only cleanup requires exact step reconciliation and named approval before execution.",
                "claim_impact": [proc["id"], branch["id"]],
            } if blocked else None),
            "status": "BLOCKED" if blocked else "UNVALIDATED",
        })
    return {
        "schema_version": "host-docs-cleanup-contract/1.0",
        "source_cleanup_instructions": source_cleanup,
        "branch_contracts": branch_contracts,
        "rollup_rule": "Every applicable branch must satisfy its required end-state predicates or retain an explicit reviewed child/not-required decision.",
        "status": "BLOCKED" if any(item["status"] == "BLOCKED" for item in branch_contracts) else "UNVALIDATED",
    }


def evidence_governance(baseline: dict[str, Any]) -> dict[str, Any]:
    masking_functions = [
        {"id": "MASK-SECRET", "fields": ["api_key", "authorization", "cookie", "password", "private_key", "setup_key", "token"],
         "replacement": "[REDACTED_SECRET]", "deterministic_rule": "Replace the entire value; never retain a prefix or suffix."},
        {"id": "ALIAS-ACCOUNT", "fields": ["account_id", "account_email", "team_id"],
         "replacement": "ACCOUNT_ALIAS", "deterministic_rule": "Map each raw value to an attempt-scoped opaque alias outside Git."},
        {"id": "ALIAS-HOST-RESOURCE", "fields": ["machine_id", "offer_id", "instance_id", "contract_id"],
         "replacement": "RESOURCE_ALIAS", "deterministic_rule": "Map each raw value to an attempt-scoped typed opaque alias outside Git."},
        {"id": "ALIAS-NETWORK", "fields": ["ip_address", "hostname", "private_network", "port_mapping"],
         "replacement": "NETWORK_ALIAS", "deterministic_rule": "Replace exact endpoints and topology with the approved target/endpoint alias."},
        {"id": "SANITIZE-DIAGNOSTIC", "fields": ["command_output", "logs", "screenshots", "raw_api_response"],
         "replacement": "SANITIZED_EXCERPT", "deterministic_rule": "Apply all field masks first, retain only claim-relevant bounded output, then independently inspect."},
    ]
    forbidden = sorted({field for item in masking_functions for field in item["fields"]})
    artifact_policies = [
        {"id": "ARTIFACT-SOURCE-INSPECTION", "artifact_type": "SOURCE_INSPECTION", "raw_sensitivity": "PUBLIC_SOURCE",
         "storage": "REPOSITORY_VERIFICATION_PACKAGE", "retention": "GIT_HISTORY", "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
         "public_projection": "ALLOW_BOUNDED_SOURCE_FACTS", "masking_function_ids": [], "forbidden_public_fields": forbidden, "status": "UNVALIDATED"},
        {"id": "ARTIFACT-RAW-TRANSCRIPT", "artifact_type": "RAW_ATTEMPT_TRANSCRIPT", "raw_sensitivity": "RESTRICTED",
         "storage": "APPROVED_RESTRICTED_STORE_OUTSIDE_GIT", "retention": "PENDING_OWNER_POLICY", "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
         "public_projection": "DENY_RAW_ALLOW_SANITIZED_DERIVATIVE", "masking_function_ids": [item["id"] for item in masking_functions],
         "forbidden_public_fields": forbidden, "status": "UNVALIDATED"},
        {"id": "ARTIFACT-RAW-SCREENSHOT", "artifact_type": "RAW_SCREENSHOT_OR_VIDEO", "raw_sensitivity": "RESTRICTED",
         "storage": "APPROVED_RESTRICTED_STORE_OUTSIDE_GIT", "retention": "PENDING_OWNER_POLICY", "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
         "public_projection": "DENY_RAW_ALLOW_SANITIZED_DERIVATIVE", "masking_function_ids": [item["id"] for item in masking_functions],
         "forbidden_public_fields": forbidden, "status": "UNVALIDATED"},
        {"id": "ARTIFACT-SANITIZED-OBSERVATION", "artifact_type": "SANITIZED_OBSERVATION", "raw_sensitivity": "PUBLIC_SANITIZED",
         "storage": "REPOSITORY_VERIFICATION_PACKAGE", "retention": "GIT_HISTORY", "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
         "public_projection": "ALLOW_AFTER_INDEPENDENT_REDACTION_REVIEW", "masking_function_ids": [item["id"] for item in masking_functions],
         "forbidden_public_fields": forbidden, "status": "UNVALIDATED"},
        {"id": "ARTIFACT-PUBLIC-PROJECTION", "artifact_type": "PUBLIC_REVIEW_PROJECTION", "raw_sensitivity": "PUBLIC_SANITIZED",
         "storage": "REPOSITORY_GENERATED_REVIEW_ARTIFACT", "retention": "GIT_HISTORY", "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
         "public_projection": "ALLOWLIST_ONLY_FAIL_CLOSED", "masking_function_ids": [item["id"] for item in masking_functions],
         "forbidden_public_fields": forbidden, "status": "UNVALIDATED"},
    ]
    branch_policies: list[dict[str, Any]] = []
    for proc in baseline["procedures"]:
        for branch in proc["branches"]:
            access = branch_access_terms(branch)
            sensitive = has_terms(access, SENSITIVE_TERMS)
            risk = has_terms(access, HIGH_RISK_TERMS)
            refs = ["ARTIFACT-SANITIZED-OBSERVATION", "ARTIFACT-PUBLIC-PROJECTION"]
            if any(term in " ".join(access).lower() for term in ("browser", "web console", "account")):
                refs.append("ARTIFACT-RAW-SCREENSHOT")
            if sensitive or risk or any(step.get("execution_form_state") != "NOT_APPLICABLE_NON_COMMAND_STEP" for step in branch["steps"]):
                refs.append("ARTIFACT-RAW-TRANSCRIPT")
            else:
                refs.append("ARTIFACT-SOURCE-INSPECTION")
            branch_policies.append({
                "branch_id": branch["id"],
                "procedure_id": proc["id"],
                "declared_access_profile": access,
                "access_profile_basis": "CANONICAL_BRANCH_EXECUTION_GATE_UNCHANGED",
                "access_scope_review_state": (
                    "UNVALIDATED_PENDING_TOPOLOGY_RECONCILIATION"
                    if proc["branch_execution_model"].get("state") == "UNRESOLVED_MULTI_BRANCH_RECONCILIATION_REQUIRED"
                    else "UNVALIDATED"
                ),
                "raw_sensitivity": "RESTRICTED" if sensitive or risk else "PUBLIC_SOURCE_OR_SANITIZED",
                "artifact_policy_ids": sorted(set(refs)),
                "forbidden_public_fields": forbidden if sensitive or risk else [],
                "public_projection": "SANITIZED_ALLOWLIST_ONLY" if sensitive or risk else "BOUNDED_SOURCE_FACTS_ONLY",
                "reviewer_role_id": "ROLE-INDEPENDENT-REVIEWER",
                "status": "UNVALIDATED",
            })
    return {
        "schema_version": "host-docs-evidence-governance/1.0",
        "sensitivity_classes": ["PUBLIC_SOURCE", "PUBLIC_SANITIZED", "RESTRICTED", "SECRET_BEARING"],
        "masking_functions": masking_functions,
        "artifact_policies": artifact_policies,
        "branch_policies": branch_policies,
        "public_projection_default": "DENY_UNLESS_ALLOWLISTED_AND_INDEPENDENTLY_REVIEWED",
        "status": "UNVALIDATED",
    }


def governance_roles() -> list[dict[str, Any]]:
    roles = [
        ("ROLE-P1-AUTHOR", "P1 candidate author", "ACTOR-P1-CONTEXT-BUILDER", "ASSIGNED_AUTOMATION_ACTOR"),
        ("ROLE-P1-RECONCILER", "Second-pass inventory reconciler", None, "PENDING_ASSIGNMENT"),
        ("ROLE-INDEPENDENT-REVIEWER", "Independent evidence reviewer", None, "PENDING_ASSIGNMENT"),
        ("ROLE-HUMAN-SAFETY-APPROVER", "Named human live-operation safety approver", None, "PENDING_NAMED_HUMAN"),
        ("ROLE-HUMAN-ACCEPTANCE-OWNER", "Named human product/process acceptance owner", None, "PENDING_NAMED_HUMAN"),
        ("ROLE-PROCEDURE-EXECUTOR", "Authorized procedure executor", None, "PENDING_ASSIGNMENT"),
        ("ROLE-APPLICABLE-CHILD-PROCEDURE", "Applicable child-procedure owner", None, "PENDING_FROZEN_HANDOFF"),
    ]
    for role in SOURCE_OWNER_ROLES.values():
        roles.append((role, role.replace("ROLE-SOURCE-OWNER-", "").replace("-", " ").title() + " source owner", None,
                      "PENDING_NAMED_HUMAN_OR_TEAM"))
    return [
        {"id": role_id, "title": title, "actor_id": actor_id, "assignment_state": state,
         "identity_scope": "OPAQUE_NON_PERSONAL_IDENTIFIER" if actor_id else "NO_IDENTITY_ASSIGNED",
         "status": "UNVALIDATED"}
        for role_id, title, actor_id, state in roles
    ]


def authority_requirement(proc: dict[str, Any], page: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    owner_role = owner_role_for(proc, page)
    def applies(item: dict[str, Any]) -> bool:
        scope = item.get("scope")
        if isinstance(scope, list):
            return proc["id"] in scope
        if isinstance(scope, dict):
            return proc["id"] in scope.get("procedure_ids", [])
        if isinstance(scope, str):
            return proc["id"] in re.findall(r"[A-Z]+-[A-Z0-9]+", scope)
        return False

    applicable_uncertainties = [item for item in baseline.get("uncertainties", []) if applies(item)]
    if applicable_uncertainties:
        question = " ".join(str(item.get("question") or item.get("description")) for item in applicable_uncertainties)
        source_question_ids = [item["id"] for item in applicable_uncertainties]
    else:
        question = (
            f"Which named owner and exact versioned authoritative source support the bounded claim for {proc['id']}: "
            f"{proc['goal']}"
        )
        source_question_ids = []
    source_by_id = {item["id"]: item for item in baseline["authority_sources"]}
    source_identities = []
    for ref in proc["authority_refs"]:
        source = source_by_id[ref]
        source_identities.append({
            "authority_source_id": ref,
            "repository_relative_path": source["path"],
            "revision_or_digest": source["sha256"],
            "recorded_authority_state": source["authority_state"],
            "bounded_support": source["claim_limit"],
        })
    current_state = proc["authority_state"]
    return {
        "id": f"AUTHREQ-{proc['id']}",
        "question_id": f"AUTHQ-{proc['id']}",
        "source_question_ids": source_question_ids,
        "accountable_owner_role_id": owner_role,
        "question": question,
        "candidate_source_identities": source_identities,
        "required_authoritative_source": {
            "repository_relative_path": None,
            "revision_or_digest": None,
            "state": "PENDING_OWNER_EXACT_SOURCE_DECISION",
        },
        "bounded_claim_supported": {
            "goal": proc["goal"],
            "claim_boundary": list(proc["test_basis"]["claim_boundary"]),
            "procedure_id": proc["id"],
        },
        "current_authority_state": current_state,
        "decision_required": "Name the accountable owner and record the exact source identity/revision plus its bounded support or contradiction.",
        "decision_record_id": None,
        "status": "BLOCKED" if current_state == "NOT_IDENTIFIED" else "UNVALIDATED",
    }


def normalized_content_digest(candidate: dict[str, Any]) -> str:
    clone = copy.deepcopy(candidate)
    clone["candidate_metadata"]["normalized_content_sha256"] = None
    for event in clone["governance"]["change_records"]:
        if event["id"] == "CHANGE-P1-CONTEXT-CANDIDATE":
            event["output_artifact"]["sha256"] = None
    return sha256_bytes(canonical_json(clone))


def build_candidate(baseline: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(baseline)
    candidate["schema_version"] = "1.0-context-governance-candidate"
    candidate["record_type"] = "host-docs-procedure-baseline-context-governance-candidate"
    page_by_id: dict[str, dict[str, Any]] = {}
    for page in candidate["pages"]:
        lines = repo_file(page["source_file"]).read_text(encoding="utf-8").splitlines()
        page["persona_ids"] = parse_frontmatter_personas(lines, page["source_file"])
        page["disposition_rationale"] = DISPOSITION_RATIONALES[page["disposition"]]
        page["actionable_section_records"] = section_records(page, baseline)
        page_by_id[page["id"]] = page

    authority_questions: list[dict[str, Any]] = []
    for proc in candidate["procedures"]:
        page = page_by_id[proc["page_id"]]
        proc["representative_context_legacy"] = copy.deepcopy(proc["representative_context"])
        proc["representative_context"] = typed_representative_context(proc, page)
        proc["cleanup_contract"] = cleanup_contract(proc)
        proc["authority_requirement"] = authority_requirement(proc, page, baseline)
        authority_questions.append(copy.deepcopy(proc["authority_requirement"]))

    requirements_by_proc = {proc["id"]: proc["authority_requirement"]["id"] for proc in candidate["procedures"]}
    for page in candidate["pages"]:
        page["authority_requirement_ids"] = [requirements_by_proc[proc_id] for proc_id in page["procedure_ids"]]

    evidence = evidence_governance(baseline)
    candidate["evidence_governance"] = evidence
    roles = governance_roles()
    baseline_change = {
        "id": "CHANGE-P1-BASELINE-RECOVERY",
        "recorded_at": baseline["created_at"],
        "recorded_at_precision": "SECOND",
        "actor_role_id": "ROLE-P1-AUTHOR",
        "actor_id": "ACTOR-P1-PRIMARY-AUTOMATION",
        "event": "NORMALIZED_REFERENCE_TO_CANONICAL_RECOVERY_EVENT",
        "legacy_event": copy.deepcopy(baseline["freeze"]["change_record"][0]),
        "rationale": "Preserve the canonical supersession event while supplying complete append-only provenance metadata.",
        "affected_ids": {"baseline_id": baseline["baseline_id"]},
        "input_artifact": {"artifact_id": "BASELINE-B-RETAINED-HISTORY", "sha256": None,
                           "digest_state": "NOT_RECORDED_IN_CANONICAL_EVENT"},
        "output_artifact": {"artifact_id": baseline["baseline_id"], "sha256": EXPECTED_CANONICAL_SHA256,
                            "digest_state": "EXACT_FILE_SHA256"},
        "evidence_impact": "Historical command-occurrence evidence is retained but cannot imply procedure PASS.",
        "stale_result_impact": "No prior command-level result is promoted into the procedure candidate.",
        "status": "UNVALIDATED",
    }
    context_change = {
        "id": "CHANGE-P1-CONTEXT-CANDIDATE",
        "recorded_at": audit["created_at"],
        "recorded_at_precision": "DATE",
        "actor_role_id": "ROLE-P1-AUTHOR",
        "actor_id": "ACTOR-P1-CONTEXT-BUILDER",
        "event": "BUILD_ISOLATED_CONTEXT_GOVERNANCE_CANDIDATE",
        "rationale": "Address P1-SCHEMA-004 through P1-SCHEMA-009 without modifying topology or raw-claim bundles.",
        "affected_ids": {
            "page_ids": [page["id"] for page in candidate["pages"]],
            "procedure_ids": [proc["id"] for proc in candidate["procedures"]],
            "branch_ids": [branch["id"] for proc in candidate["procedures"] for branch in proc["branches"]],
        },
        "input_artifact": {"artifact_id": baseline["baseline_id"], "sha256": EXPECTED_CANONICAL_SHA256,
                           "audit_sha256": EXPECTED_AUDIT_SHA256, "digest_state": "EXACT_FILE_SHA256"},
        "output_artifact": {"artifact_id": "P1-CONTEXT-GOVERNANCE-CANDIDATE", "sha256": None,
                            "digest_state": "NORMALIZED_CONTENT_SHA256_EXCLUDING_THIS_FIELD"},
        "evidence_impact": "Adds planned context/governance contracts only; it supplies no runtime or rendered evidence.",
        "stale_result_impact": "No result is made current or stale; all added V&V result fields remain UNVALIDATED or BLOCKED.",
        "status": "UNVALIDATED",
    }
    candidate["governance"] = {
        "schema_version": "host-docs-governance/1.0",
        "roles": roles,
        "role_separation_constraints": [
            "The P1 author cannot independently approve the same candidate as reconciler or acceptance owner.",
            "The safety approver and acceptance owner must be named humans with their exact roles recorded.",
            "An inventory reconciler does not inherit safety-approval or acceptance authority.",
        ],
        "change_records": [baseline_change, context_change],
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
        "topology_effect": "NO_ID_BRANCH_STEP_OR_DEPENDENCY_CHANGE",
        "executable_unit_effect": "NO_NEW_EXECUTABLE_TEST_UNIT",
        "execution_performed": False,
        "pass_assigned": False,
    }
    candidate["candidate_metadata"] = {
        "candidate_id": "P1-CONTEXT-GOVERNANCE-CANDIDATE",
        "state": "DRAFT_NOT_FROZEN",
        "source_schema_version": baseline["schema_version"],
        "source_baseline_id": baseline["baseline_id"],
        "source_baseline_sha256": EXPECTED_CANONICAL_SHA256,
        "schema_audit_sha256": EXPECTED_AUDIT_SHA256,
        "builder": "scripts/build_procedure_context_candidate.py",
        "normalized_digest_profile": "SHA256_CANONICAL_JSON_EXCLUDING_NORMALIZED_DIGEST_AND_ITS_CHANGE_EVENT_OUTPUT_FIELD",
        "normalized_content_sha256": None,
        "scope_boundaries": [
            "Topology corrections and executable command forms are not integrated by this candidate.",
            "Raw material-claim bundles and atomic semantic occurrences are not changed by this candidate.",
            "No documented instruction, rendered-page workflow, Host/WAN/API/credentialed/paid action, or mutation was executed.",
        ],
        "composition_contract": {
            "page_join_key": "page.id",
            "page_fields": ["persona_ids", "disposition_rationale", "actionable_section_records", "authority_requirement_ids"],
            "procedure_join_key": "procedure.id",
            "procedure_fields": ["representative_context_legacy", "representative_context", "cleanup_contract", "authority_requirement"],
            "top_level_fields": ["evidence_governance", "governance", "context_governance_reconciliation", "candidate_metadata"],
            "claims_and_topology_policy": "REQUIRE_EXACT_SOURCE_BASELINE_OR_EXPLICIT_REBASE",
            "split_rebase_rule": "If a topology integration creates or replaces IDs, rebind contexts, cleanup, evidence policy, and authority ownership before composition; never copy a parent result to children.",
        },
        "unresolved_blockers": [
            f"All {section_total} rendered section occurrences require browser evidence and independent review.",
            "Every procedure start-state predicate remains unobserved and UNVALIDATED.",
            "Risk-bearing or prose-only cleanup contracts remain BLOCKED until exact steps and approval are reconciled.",
            "Branch access scope remains subject to the separate topology reconciliation.",
            f"Named governance assignments remain pending for {len(pending_roles)} roles.",
            "Every procedure authority requirement still needs an exact owner decision and authoritative source boundary.",
            "Material-claim authority questions and atomic semantic occurrence design remain in the separate claim workstream.",
        ],
        "status": "UNVALIDATED",
    }
    digest = normalized_content_digest(candidate)
    candidate["candidate_metadata"]["normalized_content_sha256"] = digest
    candidate["governance"]["change_records"][-1]["output_artifact"]["sha256"] = digest
    return candidate


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")
    else:
        yield path, value


def validate_candidate(candidate: dict[str, Any], baseline: dict[str, Any]) -> None:
    require(candidate.get("schema_version") == "1.0-context-governance-candidate", "candidate schema differs")
    require(candidate.get("record_type") == "host-docs-procedure-baseline-context-governance-candidate",
            "candidate record type differs")
    require(topology_signature(candidate) == topology_signature(baseline), "candidate changed canonical topology")
    require(inventory_counts(candidate) == inventory_counts(baseline), "candidate changed topology counts")
    unchanged_top_level = {
        "authority_sources", "authority_state_vocabulary", "baseline_id", "claims",
        "completion_and_acceptance", "created_at", "execution_readiness", "fragments", "freeze",
        "legacy_crosswalk", "operating_mode", "plan_baseline_sha256", "reconciliation", "scope",
        "source_identity", "state", "status_vocabulary", "support_contracts", "supporting_routes",
        "uncertainties",
    }
    for key in unchanged_top_level:
        require(candidate.get(key) == baseline.get(key), f"candidate changed orthogonal canonical domain: {key}")
    added_page_fields = {"persona_ids", "disposition_rationale", "actionable_section_records", "authority_requirement_ids"}
    for source_page, candidate_page in zip(baseline["pages"], candidate["pages"], strict=True):
        projection = {key: value for key, value in candidate_page.items() if key not in added_page_fields}
        require(projection == source_page, f"{source_page['id']}: candidate changed an original page field")
    added_procedure_fields = {"representative_context_legacy", "cleanup_contract", "authority_requirement"}
    for source_proc, candidate_proc in zip(baseline["procedures"], candidate["procedures"], strict=True):
        projection = {key: copy.deepcopy(value) for key, value in candidate_proc.items() if key not in added_procedure_fields}
        projection["representative_context"] = copy.deepcopy(candidate_proc["representative_context_legacy"])
        require(projection == source_proc, f"{source_proc['id']}: candidate changed an original procedure field")
    metadata = candidate.get("candidate_metadata", {})
    require(metadata.get("source_baseline_sha256") == EXPECTED_CANONICAL_SHA256, "candidate baseline pin differs")
    require(metadata.get("schema_audit_sha256") == EXPECTED_AUDIT_SHA256, "candidate audit pin differs")
    require(metadata.get("state") == "DRAFT_NOT_FROZEN" and metadata.get("status") == "UNVALIDATED",
            "candidate overstates readiness")
    require(metadata.get("normalized_content_sha256") == normalized_content_digest(candidate),
            "candidate normalized content digest differs")

    page_ids = {page["id"] for page in candidate["pages"]}
    procedure_ids = {proc["id"] for proc in candidate["procedures"]}
    branch_ids = {branch["id"] for proc in candidate["procedures"] for branch in proc["branches"]}
    role_ids = {role["id"] for role in candidate["governance"]["roles"]}
    section_ids: set[str] = set()
    raw_ids: set[str] = set()
    rendered_ids: set[str] = set()
    section_total = 0
    for page in candidate["pages"]:
        require(page["persona_ids"] and all(item in PERSONA_CATALOG for item in page["persona_ids"]),
                f"{page['id']}: invalid persona IDs")
        require(isinstance(page.get("disposition_rationale"), str) and page["disposition_rationale"].strip(),
                f"{page['id']}: missing disposition rationale")
        records = page.get("actionable_section_records", [])
        require(len(records) == len(page["actionable_sections"]), f"{page['id']}: section records differ")
        source_lines = repo_file(page["source_file"]).read_text(encoding="utf-8").splitlines()
        for section in records:
            section_total += 1
            require(section["id"] not in section_ids, f"duplicate section ID {section['id']}")
            section_ids.add(section["id"])
            span = section["source_span"]
            require(span["file"] == page["source_file"] and span["source_file_sha256"] == page["source_sha256"],
                    f"{section['id']}: source identity differs")
            require(1 <= span["line_start"] <= span["line_end"] <= len(source_lines),
                    f"{section['id']}: invalid source span")
            text = "\n".join(source_lines[span["line_start"] - 1:span["line_end"]])
            require(span["source_span_sha256"] == sha256_bytes(text.encode("utf-8")),
                    f"{section['id']}: stale source span")
            raw = section["raw_occurrence"]
            rendered = section["rendered_occurrence"]
            require(raw["id"] not in raw_ids and raw["status"] == "UNVALIDATED",
                    f"{section['id']}: invalid raw occurrence")
            raw_ids.add(raw["id"])
            require(rendered["id"] not in rendered_ids and rendered["status"] == "UNVALIDATED"
                    and rendered["route"] == page["route"] and not rendered["evidence_refs"],
                    f"{section['id']}: rendered occurrence does not fail closed")
            rendered_ids.add(rendered["id"])
            require(set(section["procedure_refs"]) <= procedure_ids, f"{section['id']}: invalid procedure ref")
            require(set(section["handoff_page_ids"]) <= page_ids, f"{section['id']}: invalid handoff page")
            for occurrence in section["import_occurrences"]:
                require(occurrence["status"] == "UNVALIDATED" and occurrence["fragment_id"]
                        and occurrence["support_contract_id"], f"{occurrence['id']}: invalid import occurrence")
        require(page["authority_requirement_ids"], f"{page['id']}: no authority requirement")

    require(section_total == EXPECTED_COUNTS["sections"], f"section count is {section_total}, not 254")
    cleanup_branch_ids: set[str] = set()
    authority_ids: set[str] = set()
    authority_question_ids: set[str] = set()
    for proc in candidate["procedures"]:
        context = proc.get("representative_context")
        require(isinstance(context, dict) and context.get("schema_version") == "host-docs-procedure-context/1.0",
                f"{proc['id']}: context schema differs")
        require(context["persona_ids"] and context["intended_user"] and context["validation_use_case"]["id"],
                f"{proc['id']}: incomplete intended-use context")
        require(context["status"] == "UNVALIDATED" and context["environment"]["status"] == "UNVALIDATED"
                and context["validation_use_case"]["status"] == "UNVALIDATED",
                f"{proc['id']}: context overstates evidence")
        start = context["start_state"]
        require(start["status"] == "UNVALIDATED" and start["observation_attempt_id"] is None
                and len(start["predicates"]) == len(proc["prerequisites"]),
                f"{proc['id']}: start state is not explicit/unobserved")
        for predicate in start["predicates"]:
            require(predicate["status"] == "UNVALIDATED" and predicate["observed_value"] is None
                    and predicate["evidence_requirement"]["observation_ref"] is None,
                    f"{predicate['id']}: start state invents an observation")
        cleanup = proc.get("cleanup_contract")
        require(cleanup and len(cleanup["branch_contracts"]) == len(proc["branches"]),
                f"{proc['id']}: cleanup branch coverage differs")
        for item in cleanup["branch_contracts"]:
            require(item["branch_id"] in branch_ids and item["branch_id"] not in cleanup_branch_ids,
                    f"{proc['id']}: invalid/duplicate cleanup branch {item['branch_id']}")
            cleanup_branch_ids.add(item["branch_id"])
            require(item["status"] in ADDED_RESULT_STATUSES, f"{item['branch_id']}: invalid cleanup status")
            if item["cleanup_required"]:
                require(item["required_end_state"] and item["confirmation_observable"]
                        and item["owner_role_id"] and item["escalation"]["required_if_cleanup_uncertain"]
                        and (item["cleanup_steps"] or (item["status"] == "BLOCKED" and item["blocker"])),
                        f"{item['branch_id']}: incomplete required cleanup")
            else:
                require(item["not_required_rationale"] and item["owner_role_id"],
                        f"{item['branch_id']}: cleanup exclusion lacks ownership/rationale")
        authority = proc.get("authority_requirement")
        require(authority and authority["id"] not in authority_ids and authority["question_id"] not in authority_question_ids,
                f"{proc['id']}: duplicate/missing authority requirement")
        authority_ids.add(authority["id"])
        authority_question_ids.add(authority["question_id"])
        require(authority["accountable_owner_role_id"] in role_ids and authority["question"].strip()
                and authority["decision_required"].strip(), f"{proc['id']}: authority question lacks ownership/action")
        require(authority["required_authoritative_source"]["state"] == "PENDING_OWNER_EXACT_SOURCE_DECISION"
                and authority["decision_record_id"] is None and authority["status"] in ADDED_RESULT_STATUSES,
                f"{proc['id']}: authority is incorrectly resolved")
        for source in authority["candidate_source_identities"]:
            require(not Path(source["repository_relative_path"]).is_absolute() and source["revision_or_digest"],
                    f"{proc['id']}: authority source identity is not repo-relative/digested")

    require(cleanup_branch_ids == branch_ids, "cleanup contracts do not cover every branch exactly once")
    evidence = candidate.get("evidence_governance", {})
    branch_policies = evidence.get("branch_policies", [])
    require(len(branch_policies) == EXPECTED_COUNTS["branches"], "branch evidence-policy count differs")
    require({item["branch_id"] for item in branch_policies} == branch_ids,
            "branch evidence policies do not cover exact topology")
    artifact_ids = {item["id"] for item in evidence["artifact_policies"]}
    mask_ids = {item["id"] for item in evidence["masking_functions"]}
    for item in evidence["artifact_policies"]:
        require(item["status"] == "UNVALIDATED" and set(item["masking_function_ids"]) <= mask_ids,
                f"{item['id']}: invalid artifact policy")
        require(not item["public_projection"].startswith("ALLOW_RAW"), f"{item['id']}: raw public projection allowed")
    for item in branch_policies:
        require(item["status"] == "UNVALIDATED" and set(item["artifact_policy_ids"]) <= artifact_ids,
                f"{item['branch_id']}: invalid evidence policy refs/status")
        require(item["reviewer_role_id"] in role_ids, f"{item['branch_id']}: reviewer role unresolved")

    required_roles = {
        "ROLE-P1-AUTHOR", "ROLE-P1-RECONCILER", "ROLE-INDEPENDENT-REVIEWER",
        "ROLE-HUMAN-SAFETY-APPROVER", "ROLE-HUMAN-ACCEPTANCE-OWNER",
    }
    require(required_roles <= role_ids and len(role_ids) == len(candidate["governance"]["roles"]),
            "governance roles are missing or duplicated")
    assigned = [role for role in candidate["governance"]["roles"] if role["actor_id"]]
    incompatible = {"ROLE-P1-RECONCILER", "ROLE-INDEPENDENT-REVIEWER", "ROLE-HUMAN-SAFETY-APPROVER",
                    "ROLE-HUMAN-ACCEPTANCE-OWNER"}
    author_actors = {role["actor_id"] for role in assigned if role["id"] == "ROLE-P1-AUTHOR"}
    require(not any(role["id"] in incompatible and role["actor_id"] in author_actors for role in assigned),
            "author occupies an incompatible review/approval role")
    changes = candidate["governance"]["change_records"]
    require([item["id"] for item in changes] == ["CHANGE-P1-BASELINE-RECOVERY", "CHANGE-P1-CONTEXT-CANDIDATE"],
            "append-only change sequence differs")
    for item in changes:
        require(item["recorded_at"] and item["actor_role_id"] in role_ids and item["rationale"]
                and item["affected_ids"] and item["input_artifact"] and item["output_artifact"]
                and item["evidence_impact"] and item["stale_result_impact"] and item["status"] == "UNVALIDATED",
                f"{item['id']}: incomplete change provenance")
    require(candidate["governance"]["human_acceptance"] == "NOT_DECIDED", "candidate claims human acceptance")

    for path, value in walk(candidate):
        if isinstance(value, str):
            require(not PRIVATE_PATH_RE.search(value), f"private/machine-local path at {path}")
        if path.endswith(".status") and isinstance(value, str) and (
                path.startswith("$.candidate_metadata") or path.startswith("$.governance")
                or ".actionable_section_records" in path or ".cleanup_contract" in path
                or ".authority_requirement" in path or ".representative_context" in path
                or path.startswith("$.evidence_governance")):
            require(value in ADDED_RESULT_STATUSES, f"new result status is not fail-closed at {path}: {value}")
        if path.endswith((".status", ".vv_status")) and isinstance(value, str):
            require(value in ALLOWED_VV_STATUSES, f"invalid V&V status at {path}: {value}")


def self_test(candidate: dict[str, Any], baseline: dict[str, Any]) -> int:
    tests: list[tuple[str, Any]] = []

    def mutation(name: str, mutate) -> None:
        value = copy.deepcopy(candidate)
        mutate(value)
        try:
            validate_candidate(value, baseline)
        except CandidateError:
            tests.append((name, True))
        else:
            tests.append((name, False))

    mutation("missing page persona fails closed", lambda d: d["pages"][0].update(persona_ids=[]))
    mutation("forged section source hash fails closed",
             lambda d: d["pages"][0]["actionable_section_records"][0]["source_span"].update(source_span_sha256="0" * 64))
    mutation("rendered PASS fails closed",
             lambda d: d["pages"][0]["actionable_section_records"][0]["rendered_occurrence"].update(status="PASS"))
    mutation("string procedure context fails closed", lambda d: d["procedures"][0].update(representative_context="legacy"))
    mutation("invented start-state observation fails closed",
             lambda d: d["procedures"][0]["representative_context"]["start_state"]["predicates"][0].update(observed_value=True))
    mutation("required cleanup without end state fails closed",
             lambda d: next(item for p in d["procedures"] for item in p["cleanup_contract"]["branch_contracts"]
                            if item["cleanup_required"]).update(required_end_state=[]))
    mutation("cleanup exclusion without rationale fails closed",
             lambda d: next(item for p in d["procedures"] for item in p["cleanup_contract"]["branch_contracts"]
                            if not item["cleanup_required"]).update(not_required_rationale=None))
    mutation("missing branch evidence policy fails closed", lambda d: d["evidence_governance"]["branch_policies"].pop())
    mutation("raw public projection fails closed",
             lambda d: d["evidence_governance"]["artifact_policies"][0].update(public_projection="ALLOW_RAW"))
    mutation("author/reviewer identity collision fails closed", lambda d: d["governance"]["roles"][2].update(
        actor_id="ACTOR-P1-CONTEXT-BUILDER", assignment_state="ASSIGNED_AUTOMATION_ACTOR"))
    mutation("change removal fails closed", lambda d: d["governance"]["change_records"].pop(0))
    mutation("authority owner removal fails closed",
             lambda d: d["procedures"][0]["authority_requirement"].update(accountable_owner_role_id=None))
    mutation("claim bundle mutation fails closed", lambda d: d["claims"][0].update(status="BLOCKED"))
    mutation("topology mutation fails closed", lambda d: d["procedures"][0]["branches"].pop())
    mutation("private path injection fails closed", lambda d: d["candidate_metadata"].update(builder="/private/tmp/builder.py"))
    mutation("candidate digest mutation fails closed", lambda d: d["candidate_metadata"].update(normalized_content_sha256="f" * 64))

    failed = [name for name, passed in tests if not passed]
    if failed:
        raise CandidateError("self-tests failed: " + "; ".join(failed))
    print(f"SELF-TEST PASS: {len(tests)}/{len(tests)} fail-closed mutations rejected")
    return len(tests)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="isolated candidate output")
    parser.add_argument("--check", nargs="?", const=str(DEFAULT_OUTPUT), help="validate and reproduce an existing candidate")
    parser.add_argument("--self-test", action="store_true", help="run focused fail-closed mutation tests")
    args = parser.parse_args()
    baseline, baseline_raw = load_json_object(CANONICAL_PATH)
    audit, audit_raw = load_json_object(AUDIT_PATH)
    preflight(baseline, baseline_raw, audit, audit_raw)
    expected = build_candidate(baseline, audit)
    validate_candidate(expected, baseline)
    if args.self_test:
        self_test(expected, baseline)
    if args.check is not None:
        path = Path(args.check)
        actual, actual_raw = load_json_object(path)
        validate_candidate(actual, baseline)
        require(actual == expected, f"{path}: content differs from deterministic rebuild")
        require(actual_raw == canonical_json(expected, pretty=True), f"{path}: serialization is not canonical")
        print(f"CHECK PASS: {path}")
    else:
        require(args.output.resolve() != CANONICAL_PATH.resolve(), "refusing to overwrite canonical P1 baseline")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical_json(expected, pretty=True))
        print(f"WROTE: {args.output}")
    counts = expected["context_governance_reconciliation"]
    print("COUNTS: " + json.dumps(counts, sort_keys=True))
    print(f"NORMALIZED_CONTENT_SHA256: {expected['candidate_metadata']['normalized_content_sha256']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CandidateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
