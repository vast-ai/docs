"""Fail-closed binding for the bounded client-connection attempt.

This importer is deliberately small and allowlisted.  It preserves the exact
pre-binding claims in a hash-pinned registry, corrects only the three explicit
connection-outcome taxonomies, and never turns an incomplete browser or
self-test attempt into a product failure or a broad workflow PASS.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY = "verification/current-host-connection-adjudications.json"
EVIDENCE_ROOT = "verification/evidence/2026-09-09-host-ssh-jupyter-selftest-attempt-01"
MACHINE, INSTANCE = 150296, 50386523
DECISION = "CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION"
TARGETS = (
    "COR-01-MCL-323c8fb8180f5f62-REPLACEMENT", "MCL-4c49eaf437cfa29e",
    "MCL-1ebb3e6e2b370757", "MCL-3fb43d8a410371df", "MCL-da591d84b7d08317",
    "MCL-eeaf6da83da9eca7",
)
OUTCOMES = {
    "COR-01-MCL-323c8fb8180f5f62-REPLACEMENT": "PASS", "MCL-4c49eaf437cfa29e": "PASS",
    "MCL-1ebb3e6e2b370757": "BLOCKED", "MCL-3fb43d8a410371df": "UNVALIDATED",
    "MCL-da591d84b7d08317": "UNVALIDATED", "MCL-eeaf6da83da9eca7": "BLOCKED",
}
TAXONOMY_OUTCOMES = {
    "MCL-4c49eaf437cfa29e": ("RUNTIME_BEHAVIOR", ["RUNTIME_OR_UI_OBSERVATION"]),
    "MCL-1ebb3e6e2b370757": ("RUNTIME_BEHAVIOR", ["RUNTIME_OR_UI_OBSERVATION"]),
    "MCL-3fb43d8a410371df": ("RUNTIME_BEHAVIOR", ["RUNTIME_OR_UI_OBSERVATION"]),
}
ARTIFACTS = {
    "CLIENT_SEARCH": "documented-client-02.json", "SSH": "direct-ssh-01.json",
    "JUPYTER_HTTP": "jupyter-browser-open-01.json", "JUPYTER_HTTPS": "jupyter-browser-open-02.json",
    "JUPYTER_CERTIFICATE": "jupyter-certificate-snapshot-01.json", "JUPYTER_SCOPED_TLS": "jupyter-scoped-tls-01.json",
    "CLEANUP": "cleanup-main-01.json", "HOST_IDLE": "host-idle-04.json", "SSH_IDLE": "ssh-idle-04.json",
    "SELFTEST_PREFLIGHT": "selftest-normal-preflight-01.json", "CANONICAL_CLI": "canonical-cli-source-01.json",
}


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(f"connection adjudication: {message}")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _json(data: bytes) -> dict[str, Any]:
    value = json.loads(data, object_pairs_hook=_unique)
    _require(isinstance(value, dict), "expected JSON object")
    return value


def _read(repo: Path, relative: str) -> bytes:
    root, requested = repo.resolve(strict=True), Path(relative)
    _require(not requested.is_absolute() and ".." not in requested.parts, "unsafe path")
    lexical = root
    for part in requested.parts:
        lexical /= part
        _require(not lexical.is_symlink(), "symlink path")
    path = lexical.resolve(strict=True)
    _require(path.is_relative_to(root) and path.is_file(), "missing or escaped artifact")
    return path.read_bytes()


def _keys(value: Any, expected: set[str], label: str) -> None:
    _require(isinstance(value, dict) and set(value) == expected, f"invalid {label}")


def _validate_observations(items: dict[str, dict[str, Any]]) -> None:
    canonical = items["CANONICAL_CLI"]
    _require(canonical["source_revision"] == "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd" and canonical["source_worktree_clean"] is True, "canonical source identity drift")
    expected_sources = {
        "vastai/cli/commands/offers.py": "73b9b6dfc2d7f0d678caa1d21ea20e63ad8d22339cca4d31c9c6241b90801c48",
        "vastai/cli/commands/machines.py": "1c58876ada8c3912550396a6b2862e5de565c68b53c84554eb368e2140dc66d3",
        "vastai/cli/self_test/machine_diagnostics.py": "9cd1ddbdffbc97d86e0ecf00b3e166bcbffc8d0f5d9daf97cc561eda61e72152",
        "vastai/cli/util.py": "6b1601e89249accd1552d420135e2ada28c4dba30dce066f0e144053d0d109ea",
    }
    _require({item["path"]: item["source_sha256"] for item in canonical["sources"] if item["path"] in expected_sources} == expected_sources, "canonical source set drift")
    search = items["CLIENT_SEARCH"]
    _require(search["status"] == "PASS" and search["exit_code"] == 0 and search["source_revision"] == "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd" and search["credential_role"] == "CLIENT" and search["command"] == ["vastai", "--retry", "1", "--raw", "search", "offers", "machine_id=150296 verified=any", "--limit", "200"], "client search drift")
    _require(any(row.get("machine_id") == MACHINE and row.get("id") == 50363390 and row.get("rentable") is True and row.get("rented") is False for row in search["rows"]), "client search correlation")
    ssh = items["SSH"]
    _require(ssh["status"] == "PASS" and ssh["exit_code"] == 0 and ssh["machine_id"] == MACHINE and ssh["instance_id"] == INSTANCE and ssh["stdout"] == "HOST_DOCS_VV_50386523_SSH_OK\n", "SSH observation drift")
    http, https, certificate, scoped = (items[key] for key in ("JUPYTER_HTTP", "JUPYTER_HTTPS", "JUPYTER_CERTIFICATE", "JUPYTER_SCOPED_TLS"))
    _require(http["exit_code"] == 1 and "ERR_CONNECTION_RESET" in http["stderr"] and https["exit_code"] == 1 and "ERR_CERT_AUTHORITY_INVALID" in https["stderr"] and "Your connection is not private" in certificate["stdout"], "Jupyter browser blocker drift")
    _require(scoped["machine_id"] == MACHINE and scoped["instance_id"] == INSTANCE and "not macOS/browser trust" in scoped["tls_verification"] and [item["path"] for item in scoped["observations"]] == ["/api/status", "/tree"] and all(item["status"] == "PASS" and item["http_status"] == 200 for item in scoped["observations"]), "Jupyter scoped TLS drift")
    cleanup, host_idle, ssh_idle = (items[key] for key in ("CLEANUP", "HOST_IDLE", "SSH_IDLE"))
    _require(cleanup["status"] == "PASS" and cleanup["machine_id"] == MACHINE and cleanup["instance_id"] == INSTANCE and cleanup["events"][-1].get("absent") is True and cleanup["remaining_matches"] == [], "cleanup drift")
    _require(host_idle["status"] == "PASS" and host_idle["machine_id"] == MACHINE and host_idle["guards"]["zero_running"] and host_idle["guards"]["zero_resident"], "host idle drift")
    _require(ssh_idle["status"] == "PASS" and ssh_idle["machine_id"] == MACHINE and ssh_idle["guards"]["zero_compute_processes"] and ssh_idle["guards"]["zero_containers"], "SSH idle drift")
    preflight = items["SELFTEST_PREFLIGHT"]
    result = preflight["structured_result"]
    checks = {item["id"]: item for item in result["checks"]}
    _require(preflight["status"] == "BLOCKED" and preflight["exit_code"] == 0 and preflight["source_revision"] == "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd" and result["success"] is False and result["stage"] == "preflight_requirements" and result["failure_code"] == "preflight_requirements_failed", "preflight result drift")
    _require(result["failure"]["failed_check_ids"] == ["reliability", "network.upload"] and checks["reliability"]["actual"] == 0.8506588 and checks["reliability"]["required"] == 0.9 and checks["network.upload"]["actual"] == 221.1 and checks["network.upload"]["required"] == 500.0, "preflight thresholds drift")
    _require(preflight["transport_events"] == [{"method": "POST", "path": "/api/v0/bundles/", "allowed": True, "at": preflight["transport_events"][0]["at"], "http_status": 200}] and len(preflight["bundle_inventory"]) == 1 and preflight["bundle_inventory"][0]["mode"] == "0o600" and len(preflight["bundle_inventory"][0]["members"]) == 4, "preflight no-rental/bundle drift")


def validate(repo: Path = REPO) -> dict[str, Any]:
    registry = _json(_read(repo, REGISTRY))
    _keys(registry, {"schema_version", "artifact_type", "purpose", "attempt", "artifacts", "adjudications"}, "registry")
    _require(registry["schema_version"] == 1 and registry["artifact_type"] == "CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION_INPUT" and registry["attempt"] == EVIDENCE_ROOT, "registry identity drift")
    _require([item.get("id") for item in registry["artifacts"]] == list(ARTIFACTS), "artifact allowlist drift")
    items: dict[str, dict[str, Any]] = {}
    for item in registry["artifacts"]:
        _keys(item, {"id", "path", "sha256"}, "artifact")
        _require(item["path"] == f"{EVIDENCE_ROOT}/{ARTIFACTS[item['id']]}" and isinstance(item["sha256"], str) and len(item["sha256"]) == 64, "artifact identity drift")
        payload = _read(repo, item["path"])
        _require(_sha(payload) == item["sha256"], "artifact digest drift")
        items[item["id"]] = _json(payload)
    _validate_observations(items)
    entries = registry["adjudications"]
    _require([entry.get("claim_id") for entry in entries] == list(TARGETS), "target allowlist drift")
    for entry in entries:
        _keys(entry, {"id", "claim_id", "route", "source_file", "source_sha256", "headings", "span", "literal", "literal_sha256", "previous_claim", "previous_claim_sha256", "outcome_status", "taxonomy", "artifact_ids", "limits", "rationale", "next_action", "source_refs"}, "adjudication")
        claim = entry["previous_claim"]
        _require(entry["id"] == f"CONNECTION-{entry['claim_id']}-01" and entry["claim_id"] in TARGETS and entry["route"] in {"/host/first-24-hours", "/host/how-to-self-test"} and _canonical(claim) == entry["previous_claim_sha256"] and claim["id"] == entry["claim_id"], "previous claim drift")
        _require(entry["taxonomy"]["prior_classification"] == claim["classification"] and entry["taxonomy"]["prior_required_evidence_types"] == claim["required_evidence_types"], "taxonomy prior drift")
        expected_taxonomy = TAXONOMY_OUTCOMES.get(entry["claim_id"], (claim["classification"], claim["required_evidence_types"]))
        _require((entry["taxonomy"]["outcome_classification"], entry["taxonomy"]["outcome_required_evidence_types"]) == expected_taxonomy and entry["taxonomy"]["correction"] is (entry["claim_id"] in TAXONOMY_OUTCOMES), "taxonomy outcome drift")
        if entry["claim_id"] in TAXONOMY_OUTCOMES:
            _require(entry["taxonomy"].get("outcome_owner_role") == "Authorized client/browser/network operator", "taxonomy ownership drift")
        source = _read(repo, entry["source_file"])
        _require(_sha(source) == entry["source_sha256"], "source digest drift")
        start, end = entry["span"]["start"], entry["span"]["end"]
        literal = "\n".join(source.decode().splitlines()[start - 1:end])
        _require(entry["span"] == claim["spans"][0] and literal == entry["literal"] and _sha(literal.encode()) == entry["literal_sha256"] == entry["span"]["text_sha256"], "source occurrence drift")
        _require(entry["outcome_status"] == OUTCOMES[entry["claim_id"]] and all(item in ARTIFACTS for item in entry["artifact_ids"]) and isinstance(entry["source_refs"], list), "outcome drift")
    return registry


def apply_current_host_connection_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    registry = validate(repo)
    claims: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for page in pages:
        for claim in page["claims"]:
            if claim.get("id") in TARGETS:
                _require(claim["id"] not in claims, "duplicate target claim")
                claims[claim["id"]] = (page, claim)
    _require(set(claims) == set(TARGETS), "missing target claim")
    summaries: list[dict[str, str]] = []
    for entry in registry["adjudications"]:
        page, claim = claims[entry["claim_id"]]
        _require(page["route"] == entry["route"] and page["source_file"] == entry["source_file"] and page["source_sha256"] == entry["source_sha256"] and claim == entry["previous_claim"] and _canonical(claim) == entry["previous_claim_sha256"], "current claim drift or reapplication")
        updated = copy.deepcopy(claim)
        taxonomy = entry["taxonomy"]
        new_refs = [{"id": entry["id"], "role": DECISION, "limit": entry["limits"], "artifact_ref": REGISTRY}, *[{"id": artifact_id, "role": "RETAINED_CONNECTION_ATTEMPT_OBSERVATION", "limit": entry["limits"], "artifact_ref": f"{EVIDENCE_ROOT}/{ARTIFACTS[artifact_id]}"} for artifact_id in entry["artifact_ids"]]]
        # The corrected search was previously a retained historical FAIL.
        # Keep those exact links visible as history, but never use them to
        # establish the new bounded runtime PASS.
        evidence_refs = [*claim["evidence_refs"], *new_refs] if entry["claim_id"] == "COR-01-MCL-323c8fb8180f5f62-REPLACEMENT" else new_refs
        updated.update({"status": entry["outcome_status"], "classification": taxonomy["outcome_classification"], "required_evidence_types": taxonomy["outcome_required_evidence_types"], "owner_role": taxonomy.get("outcome_owner_role", claim["owner_role"]), "rationale": entry["rationale"], "next_action": entry["next_action"], "evidence_refs": evidence_refs, "source_refs": entry["source_refs"], "history": {**claim["history"], "carry_decision": DECISION, "reason": claim["history"]["reason"] + " Exact prior claim is hash-pinned in the connection adjudication registry; this bounded observation does not transfer a broader workflow result."}})
        claim.clear(); claim.update(updated)
        summaries.append({"id": entry["id"], "scope": entry["claim_id"], "history": "Full prior claim is hash-pinned in the connection adjudication registry.", "current": f"{entry['outcome_status']} / {entry['rationale']}", "reason": entry["limits"]})
    return summaries
