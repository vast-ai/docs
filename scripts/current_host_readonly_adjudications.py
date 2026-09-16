"""Fail-closed importer for ten retained Host CLI command occurrences.

This is deliberately not a generic evidence importer.  Its allowlist is the
ten complete documentation command occurrences named in the review plan; the
registry pins their source occurrence, every argv, the retained captures and
the clean canonical CLI provenance.  Two self-test rows are refreshed as
BLOCKED prerequisites only.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY = "verification/current-host-readonly-adjudications.json"
REGISTRY_SHA256 = "06c00cb9482d3911df398c2b39841f52e998d304054f0016fc27c779763d5073"
CANONICAL_CLI = "18c4f2ccd6da587d5352f8741c71805a9a18e1ae"
BLOCKER_RATIONALE = ("CURRENT PREREQUISITE: The present Host-owner key can read the Ada candidate, "
                     "but explicit self-test workload authorization, create permission, controlled "
                     "spend/window/runtime bounds, and cleanup authority limited to task-created "
                     "resources are not recorded.")
TARGETS = {
    "CUR-142629d88fb18726": ("/host/market-metrics", "host/market-metrics.mdx", "7df0a055897a5f5a0629127c5ccb36a46e563ddee2c263dee9146e925d5f7d7d", ["CLI"], 77, 81),
    "CUR-705da5057d7f3360": ("/host/market-metrics", "host/market-metrics.mdx", "7df0a055897a5f5a0629127c5ccb36a46e563ddee2c263dee9146e925d5f7d7d", ["CLI"], 85, 93),
    "CUR-2c04f5e4d6ef0b20": ("/host/market-metrics", "host/market-metrics.mdx", "7df0a055897a5f5a0629127c5ccb36a46e563ddee2c263dee9146e925d5f7d7d", ["CLI"], 97, 103),
    "MCL-f0b9b724554ce68a": ("/host/fleet-operations", "host/fleet-operations.mdx", "33412e18772fdf9e2999e71c930f4897cb45083c06784f7aece8a22e8932c6a1", ["Fleet State"], 21, 23),
    "MCL-aa735864a1cb734d": ("/host/fleet-operations", "host/fleet-operations.mdx", "33412e18772fdf9e2999e71c930f4897cb45083c06784f7aece8a22e8932c6a1", ["Monitor"], 76, 76),
    "MCL-96ee15f730e698d8": ("/host/not-in-search", "host/not-in-search.mdx", "bef28db52291a1cd4e4af75389da836f9125a6619bdf9663e83c8ce25a592570", ["Check the machine directly"], 28, 30),
    "MCL-728ef13be833d21e": ("/host/not-in-search", "host/not-in-search.mdx", "bef28db52291a1cd4e4af75389da836f9125a6619bdf9663e83c8ce25a592570", ["Check the machine directly"], 34, 36),
    "MCL-a54378e7f20b92e9": ("/host/not-in-search", "host/not-in-search.mdx", "bef28db52291a1cd4e4af75389da836f9125a6619bdf9663e83c8ce25a592570", ["Check the machine directly"], 40, 42),
    "MCL-e7db8b5148b63289": ("/host/not-in-search", "host/not-in-search.mdx", "bef28db52291a1cd4e4af75389da836f9125a6619bdf9663e83c8ce25a592570", ["Check the machine directly"], 46, 48),
    "MCL-50f964a1bb6a2e95": ("/host/maintenance-windows", "host/maintenance-windows.mdx", "832534186a6ad55837c3d81b06d486eccc923a5b5b8d36358ffe643b428f5d46", ["Before Maintenance"], 22, 25),
}
CHECKS = {
    "CUR-142629d88fb18726": [("D", "D06"), ("D", "D07"), ("D", "D08")],
    "CUR-705da5057d7f3360": [("E", "E01"), ("D", "D09"), ("E", "E02"), ("E", "E03"), ("E", "E04"), ("D", "D10"), ("E", "E05")],
    "CUR-2c04f5e4d6ef0b20": [("E", "E06"), ("E", "E07"), ("E", "E08"), ("E", "E09"), ("D", "D12")],
    "MCL-f0b9b724554ce68a": [("D", "D01")],
    "MCL-aa735864a1cb734d": [("D", "D01")],
    "MCL-96ee15f730e698d8": [("N", "HOST-02")], "MCL-728ef13be833d21e": [("S", "HOST-05")],
    "MCL-a54378e7f20b92e9": [("S", "HOST-06")], "MCL-e7db8b5148b63289": [("S", "HOST-07")],
    "MCL-50f964a1bb6a2e95": [("N", "HOST-03"), ("N", "HOST-01")],
}


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canon(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _read(relative: str) -> bytes:
    root = REPO.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
        raise ValueError("readonly adjudication: unsafe or missing artifact")
    return path.read_bytes()


def _object(data: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        answer: dict[str, Any] = {}
        for key, value in pairs:
            if key in answer:
                raise ValueError("readonly adjudication: duplicate JSON key")
            answer[key] = value
        return answer
    value = json.loads(data, object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError("readonly adjudication: expected object")
    return value


def _keys(value: Any, fields: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"readonly adjudication: invalid {label}")


def _source_refs(binding: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"repository": "vast-ai/vast-cli", "revision": CANONICAL_CLI, "path": row["path"],
             "locator": row["url"], "source_kind": "CANONICAL_CLI_SOURCE"} for row in binding]


def validate(repo: Path = REPO) -> dict[str, Any]:
    # repo is accepted for the focused unit tests; all reads remain bounded.
    global REPO
    old = REPO
    REPO = Path(repo).resolve()
    try:
        registry_bytes = _read(REGISTRY)
        if _sha(registry_bytes) != REGISTRY_SHA256:
            raise ValueError("readonly adjudication: unreviewed registry drift")
        registry = _object(registry_bytes)
        _keys(registry, {"schema_version", "artifact_type", "purpose", "canonical_cli_revision", "artifacts", "adjudications", "blocker_refreshes"}, "registry")
        if registry["schema_version"] != 1 or registry["artifact_type"] != "CURRENT_HOST_READONLY_COMMAND_ADJUDICATION_INPUT" or registry["canonical_cli_revision"] != CANONICAL_CLI:
            raise ValueError("readonly adjudication: unsupported registry")
        artifacts = registry["artifacts"]
        if not isinstance(artifacts, list) or len(artifacts) != 7:
            raise ValueError("readonly adjudication: exact artifacts required")
        artifact_data: dict[str, dict[str, Any]] = {}
        for item in artifacts:
            _keys(item, {"path", "sha256", "kind"}, "artifact pin")
            path = item["path"]
            if not isinstance(path, str) or not path.startswith("verification/evidence/2026-09-08-") or _sha(_read(path)) != item["sha256"]:
                raise ValueError("readonly adjudication: artifact digest mismatch")
            artifact_data[item["kind"]] = _object(_read(path))
        if set(artifact_data) != {"batch_d", "batch_e", "provenance", "ada_readiness", "new_cli", "new_search", "new_provenance"}:
            raise ValueError("readonly adjudication: artifact kind substitution")
        provenance = artifact_data["provenance"]
        if provenance.get("revision") != CANONICAL_CLI or provenance.get("per_path_git_status") != "clean for every listed file":
            raise ValueError("readonly adjudication: canonical CLI is not clean")
        new_provenance = artifact_data["new_provenance"]
        if new_provenance.get("revision") != CANONICAL_CLI or new_provenance.get("entry_point") != "vastai.cli.main:main":
            raise ValueError("readonly adjudication: new canonical CLI provenance drift")
        source_files = {row.get("path"): {key: row[key] for key in ("path", "sha256", "url")} for row in [*provenance.get("files", []), *new_provenance.get("files", [])] if isinstance(row, dict)}
        for path, row in source_files.items():
            url = f"https://github.com/vast-ai/vast-cli/blob/{CANONICAL_CLI}/{path}"
            if set(row) != {"path", "sha256", "url"} or row["url"] != url or not isinstance(row["sha256"], str) or len(row["sha256"]) != 64:
                raise ValueError("readonly adjudication: canonical source URL/hash drift")
        d_records = {row.get("check_id"): row for row in artifact_data["batch_d"].get("records", []) if isinstance(row, dict)}
        e_records = {row.get("check_id"): row for row in artifact_data["batch_e"].get("records", []) if isinstance(row, dict)}
        n_records = {row.get("check_id"): row for row in artifact_data["new_cli"].get("records", []) if isinstance(row, dict)}
        s_records = {row.get("check_id"): row for row in artifact_data["new_search"].get("records", []) if isinstance(row, dict)}
        if artifact_data["batch_d"].get("source_revision") != CANONICAL_CLI or artifact_data["batch_d"].get("runner_platform") != "macOS" or artifact_data["batch_e"].get("runner_platform") != "macOS" or artifact_data["batch_e"].get("source_provenance") != "batch-d-source-provenance.json" or artifact_data["new_cli"].get("source_revision") != CANONICAL_CLI or artifact_data["new_cli"].get("entry_point") != "vastai.cli.main:main via existing source checkout .venv/bin/python and PYTHONPATH" or artifact_data["new_search"].get("source_revision") != CANONICAL_CLI or artifact_data["new_search"].get("entry_point") != "vastai.cli.main:main" or artifact_data["new_search"].get("credential_role") != "host":
            raise ValueError("readonly adjudication: wrong execution environment")
        approved = set(TARGETS)
        entries = registry["adjudications"]
        if not isinstance(entries, list) or {row.get("claim_id") for row in entries if isinstance(row, dict)} != approved:
            raise ValueError("readonly adjudication: exact target set required")
        for row in entries:
            _keys(row, {"id", "claim_id", "route", "source_file", "source_sha256", "headings", "span", "literal", "literal_sha256", "previous_claim", "previous_claim_sha256", "prior_status", "required_evidence_types", "checks", "source_binding", "limits"}, "adjudication")
            _keys(row["span"], {"start", "end", "text_sha256"}, "span")
            expected_lanes = (["CANONICAL_IMPLEMENTATION_SOURCE"] if row["claim_id"] == "MCL-aa735864a1cb734d"
                              else ["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"])
            target = TARGETS[row["claim_id"]]
            if (row["route"], row["source_file"], row["source_sha256"], row["headings"], row["span"]["start"], row["span"]["end"]) != target:
                raise ValueError("readonly adjudication: target occurrence drift")
            if not isinstance(row["previous_claim"], dict) or _canon(row["previous_claim"]) != row["previous_claim_sha256"]:
                raise ValueError("readonly adjudication: original claim hash mismatch")
            if row["prior_status"] != "UNVALIDATED" or row["required_evidence_types"] != expected_lanes or _sha(row["literal"].encode()) != row["literal_sha256"]:
                raise ValueError("readonly adjudication: lane or literal drift")
            if not isinstance(row["checks"], list) or [(item.get("batch"), item.get("check_id")) for item in row["checks"] if isinstance(item, dict)] != CHECKS[row["claim_id"]]:
                raise ValueError("readonly adjudication: missing command proof")
            for check in row["checks"]:
                _keys(check, {"batch", "check_id", "argv", "required_output"}, "command check")
                if not isinstance(check["required_output"], dict) or not check["required_output"]:
                    raise ValueError("readonly adjudication: missing output predicate")
                record = ({"D": d_records, "E": e_records, "N": n_records, "S": s_records}.get(check["batch"], {})).get(check["check_id"])
                if not record or record.get("argv") != check["argv"] or record.get("exit_code") != 0 or record.get("observation_status") != "PASS" or record.get("execution_success", True) is not True:
                    raise ValueError("readonly adjudication: argv, exit, or observation mismatch")
                if check["batch"] == "N" and record.get("credential_role") != "host":
                    raise ValueError("readonly adjudication: Host role mismatch")
                for key, expected in check["required_output"].items():
                    actual = record.get(key)
                    if isinstance(expected, list):
                        if not isinstance(actual, list) or not set(expected).issubset(actual):
                            raise ValueError("readonly adjudication: output shape mismatch")
                    elif actual != expected:
                        raise ValueError("readonly adjudication: output shape mismatch")
            binding = row["source_binding"]
            if not isinstance(binding, list) or not binding:
                raise ValueError("readonly adjudication: missing canonical source binding")
            for source in binding:
                _keys(source, {"path", "sha256", "url"}, "source binding")
                if source_files.get(source["path"]) != source or source["url"] != f"https://github.com/vast-ai/vast-cli/blob/{CANONICAL_CLI}/{source['path']}":
                    raise ValueError("readonly adjudication: borrowed or stale source binding")
        blockers = registry["blocker_refreshes"]
        expected_blockers = {"MCL-eeaf6da83da9eca7", "MCL-3aca6b1f291d4d0c"}
        if not isinstance(blockers, list) or {row.get("claim_id") for row in blockers if isinstance(row, dict)} != expected_blockers:
            raise ValueError("readonly adjudication: exact blocker set required")
        ada = artifact_data["ada_readiness"]
        if ada.get("check_id") != "ADA-01" or ada.get("method") != "GET" or ada.get("http_status") != 200 or ada.get("status") != "PASS" or ada.get("read_only") is not True:
            raise ValueError("readonly adjudication: Ada readiness is not a bounded read-only observation")
        for row in blockers:
            _keys(row, {"claim_id", "previous_claim", "previous_claim_sha256", "prior_status", "evidence_ref", "rationale", "next_action"}, "blocker refresh")
            if not isinstance(row["previous_claim"], dict) or _canon(row["previous_claim"]) != row["previous_claim_sha256"] or row["prior_status"] != "BLOCKED" or row["evidence_ref"] != "verification/evidence/2026-09-08-host-ada-readiness-attempt-01/api-01.json" or row["rationale"] != BLOCKER_RATIONALE or "create permission" not in row["next_action"] or "cleanup" not in row["next_action"]:
                raise ValueError("readonly adjudication: stale blocker rationale")
        return registry
    finally:
        REPO = old


def apply_current_host_readonly_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    registry = validate(repo)
    claims = {claim["id"]: (page, claim) for page in pages for claim in page["claims"]}
    summaries: list[dict[str, str]] = []
    for entry in registry["adjudications"]:
        page, claim = claims.get(entry["claim_id"], (None, None))
        if page is None or claim is None or page["route"] != entry["route"] or page["source_file"] != entry["source_file"] or page["source_sha256"] != entry["source_sha256"] or claim["headings"] != entry["headings"] or claim["spans"] != [{"source_file": entry["source_file"], **entry["span"]}] or claim["text"] != entry["literal"] or claim != entry["previous_claim"] or _canon(claim) != entry["previous_claim_sha256"]:
            raise ValueError("readonly adjudication: target claim drift")
        updated = copy.deepcopy(claim)
        updated.update({"status": "PASS", "rationale": "Exact canonical CLI source bindings and every documented argv match retained macOS source-entry-point command observations.", "next_action": "Re-run this exact bounded command-proof adjudication if its source occurrence, canonical CLI revision, capture, argv, output shape, or source binding changes.", "evidence_refs": [{"id": entry["id"], "role": "CURRENT_HOST_READONLY_COMMAND_ADJUDICATION", "limit": entry["limits"], "artifact_ref": REGISTRY}], "source_refs": _source_refs(entry["source_binding"]), "history": {**claim["history"], "carry_decision": "CURRENT_HOST_READONLY_SOURCE_ADJUDICATION" if entry["claim_id"] == "MCL-aa735864a1cb734d" else "CURRENT_HOST_READONLY_COMMAND_ADJUDICATION", "reason": claim["history"]["reason"] + " Exact current command adjudication is separately bound; no workflow or historical PASS transfer is inferred."}})
        claim.clear(); claim.update(updated)
        summaries.append({"id": entry["id"], "scope": entry["claim_id"], "history": "Original full current claim is hash-pinned in this readonly adjudication registry.", "current": "PASS / exact command acceptance and output shape", "reason": entry["limits"]})
    for entry in registry["blocker_refreshes"]:
        page, claim = claims.get(entry["claim_id"], (None, None))
        if page is None or claim is None or claim != entry["previous_claim"] or claim["status"] != "BLOCKED" or _canon(claim) != entry["previous_claim_sha256"]:
            raise ValueError("readonly adjudication: blocker target drift")
        updated = copy.deepcopy(claim)
        updated.update({"rationale": entry["rationale"], "next_action": entry["next_action"], "evidence_refs": [*claim["evidence_refs"], {"id": "ADA-01", "role": "CURRENT_PREREQUISITE_REFRESH", "limit": "Read-only candidate access/metadata snapshot only; it is not authorization, reservation, workload execution, health, or cleanup proof.", "artifact_ref": entry["evidence_ref"]}]})
        claim.clear(); claim.update(updated)
        summaries.append({"id": f"CURRENT-SELFTEST-PREREQUISITE-REFRESH-{entry['claim_id']}", "scope": entry["claim_id"], "history": "Frozen legacy blocker triplet remains on the current claim; this is an additive readiness refresh.", "current": "BLOCKED / prerequisites refreshed", "reason": entry["next_action"]})
    return summaries
