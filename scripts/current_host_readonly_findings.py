"""Validate and apply exactly two current read-only FAIL findings.

This module is intentionally not a general adjudicator. It never performs I/O
other than bounded local reads, never promotes a claim, and rejects reapplication.
The builder owner may call ``apply_current_readonly_findings`` after the other
current adjudications and before counts are calculated.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


REGISTRY_PATH = "verification/current-host-readonly-findings.json"
ATTEMPT = "verification/evidence/2026-09-08-host-client-unblocking-attempt-01"
VM_SOURCE = f"{ATTEMPT}/vm-helper-source-retest-02.json"
VM_STATUS = f"{ATTEMPT}/vm-status-01.json"
CLI_CAPTURE = f"{ATTEMPT}/client-discovery-cli-source-01.json"
CLI_REVISION = "18c4f2ccd6da587d5352f8741c71805a9a18e1ae"
CLI_PATH = "vastai/cli/commands/machines.py"
CLI_SOURCE_SHA256 = "64aef749a44e1c66742ba7796c6bcec9053ee87ae882bab783393bcbb2e29bbe"
CLI_EXCERPT_SHA256 = "b6564ec1f61f5cf757c4852b271cf656caf147cd3f94316436f3577139490724"
DECISION = "CURRENT_HOST_READONLY_FAIL_ADJUDICATION"

TARGETS = {
    "MCL-dfebca7edafe9c59": {
        "route": "/host/vms", "source_file": "host/vms.mdx",
        "source_sha256": "3f9cab3e239c3e048af39506adb8d6e83d0c497e82c34d11fad171a85cde822e",
        "start": 48, "end": 48,
        "text": "| `off` | VM support is disabled or a previous test failed. |",
        "text_sha256": "85b6c26e7391c0b82ea0198764f1a73c92c9c3375667dead904db55481bee253",
        "headings": ["Check VM Status"],
    },
    "MCL-323c8fb8180f5f62": {
        "route": "/host/first-24-hours", "source_file": "host/first-24-hours.mdx",
        "source_sha256": "3ab83e7558387edc07416aa84c4cf8e5721f1312a4c94f3841c1af4ecd8cf970",
        "start": 59, "end": 61, "text": "```text\nvastai show machines\n```",
        "text_sha256": "1934a5794a3df886da32b090bd84490c98c65dae0a7faeb746ca9312600ce2b6",
        "headings": ["Test Like A Client"],
    },
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"current read-only findings: {message}")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json(data: bytes) -> dict[str, Any]:
    value = json.loads(data, object_pairs_hook=_unique_object)
    _require(isinstance(value, dict), "expected object")
    return value


def _read(repo: Path, relative: str) -> bytes:
    root = repo.resolve(strict=True)
    file = (root / relative).resolve(strict=True)
    _require(file.is_relative_to(root) and file.is_file(), "artifact escaped repository")
    return file.read_bytes()


def _validate_vm_evidence(repo: Path, finding: dict[str, Any]) -> None:
    expected = [(VM_SOURCE, "bdf9fa2e438dee4913f11f4e7c8d5abe64f98bab1fd29df6df1b6b6eaab21455"),
                (VM_STATUS, "135f486a53342f25708db0b041ae08f8ff449866ff6083ddbf8b0e7caf6a2860")]
    _require([(row.get("artifact_ref"), row.get("sha256")) for row in finding["evidence"]] == expected,
             "VM evidence allowlist changed")
    helper = _read(repo, VM_SOURCE)
    status = _read(repo, VM_STATUS)
    _require(_sha(helper) == expected[0][1] and _sha(status) == expected[1][1], "VM evidence digest drift")
    source = _json(helper)
    _require(source.get("source_sha256") == "bb7c5922931aacbdff85528fcfb52733639db00361ae00b232f3cbfad0d251de", "VM helper identity drift")
    excerpt = next((row.get("text") for row in source.get("excerpts", []) if row.get("start") == 298 and row.get("end") == 317), None)
    _require(isinstance(excerpt, str) and 'open("/var/lib/vastai_kaalia/kaalia.cfg", "r")' in excerpt and "except:\n        pass\n    print(\"off\")" in excerpt,
             "VM helper does not establish config-read fallback")
    observed = _json(status).get("observed")
    _require(isinstance(observed, dict) and observed.get("source_sha256") == source["source_sha256"] and
             observed.get("state_file_readability") == {".tried_vm_on": True, "kaalia.cfg": False} and observed.get("status_token") == "off",
             "VM status does not establish the bounded counterexample")


def _validate_cli_evidence(repo: Path, finding: dict[str, Any]) -> None:
    expected = [(CLI_CAPTURE, "b68f35f899c5ef68bbfd9bb6515fd0025f66467ec381b7a297ed0286532a27d6")]
    _require([(row.get("artifact_ref"), row.get("sha256")) for row in finding["evidence"]] == expected,
             "CLI evidence allowlist changed")
    capture_bytes = _read(repo, CLI_CAPTURE)
    _require(_sha(capture_bytes) == expected[0][1], "CLI capture digest drift")
    capture = _json(capture_bytes)
    _require(set(capture) == {"schema_version", "capture_id", "source_repository", "source_revision", "source_path", "source_sha256", "locator", "excerpt", "excerpt_sha256", "finding", "limit"}, "CLI capture fields changed")
    _require(capture["source_repository"] == "vast-ai/vast-cli" and capture["source_revision"] == CLI_REVISION and
             capture["source_path"] == CLI_PATH and capture["source_sha256"] == CLI_SOURCE_SHA256 and
             capture["locator"] == "show__machines, lines 62-78" and capture["excerpt_sha256"] == CLI_EXCERPT_SHA256 and
             _sha(capture["excerpt"].encode()) == CLI_EXCERPT_SHA256, "CLI capture identity drift")
    _require("help=\"[Host] Show hosted machines\"" in capture["excerpt"] and
             "Show the machines user is offering for rent." in capture["excerpt"], "pinned Host-inventory excerpt drift")


def validate_current_readonly_findings(repo: Path) -> dict[str, Any]:
    """Return the exactly two retained FAIL findings or raise on any drift."""
    registry = _json(_read(repo, REGISTRY_PATH))
    _require(set(registry) == {"schema_version", "artifact_type", "adjudication_id", "limits", "findings"}, "registry fields changed")
    _require(registry["schema_version"] == 1 and registry["artifact_type"] == "EXACT_FAIL_ONLY_CURRENT_HOST_READONLY_FINDINGS" and
             registry["adjudication_id"] == "CURRENT-HOST-READONLY-FAIL-FINDINGS-01", "registry identity changed")
    _require(isinstance(registry["limits"], str) and "Neither finding proves" in registry["limits"], "limits changed")
    findings = registry["findings"]
    _require(isinstance(findings, list) and len(findings) == 2, "exactly two findings required")
    _require([row.get("claim_id") for row in findings] == list(TARGETS), "target allowlist changed")
    for finding in findings:
        _require(set(finding) == {"claim_id", "occurrence", "previous_claim_sha256", "previous_claim", "status", "classification", "required_evidence_types", "reason", "next_action", "evidence"}, "finding fields changed")
        target = TARGETS[finding["claim_id"]]
        _require(finding["occurrence"] == target, "exact occurrence changed")
        _require(_canonical_sha(finding["previous_claim"]) == finding["previous_claim_sha256"], "previous claim digest drift")
        _require(finding["previous_claim"]["id"] == finding["claim_id"] and finding["previous_claim"]["status"] == "UNVALIDATED", "previous claim is not the original")
        _require(finding["status"] == "FAIL" and finding["classification"] == "CONFIRMED_DOCUMENTATION_DEFECT" and
                 finding["required_evidence_types"] == ["CANONICAL_IMPLEMENTATION_SOURCE"], "only exact FAIL classification allowed")
        _require(isinstance(finding["reason"], str) and isinstance(finding["next_action"], str) and finding["reason"] and finding["next_action"], "finding meaning missing")
        _require(isinstance(finding["evidence"], list) and finding["evidence"], "finding evidence missing")
        if finding["claim_id"] == "MCL-dfebca7edafe9c59":
            _validate_vm_evidence(repo, finding)
        else:
            _validate_cli_evidence(repo, finding)
        source = _read(repo, target["source_file"])
        _require(_sha(source) == target["source_sha256"], "current page hash drift")
        lines = source.decode("utf-8").splitlines()
        _require("\n".join(lines[target["start"] - 1:target["end"]]) == target["text"] and
                 _sha(target["text"].encode()) == target["text_sha256"], "current page occurrence drift")
    return registry


def apply_current_readonly_findings(pages: list[dict[str, Any]], repo: Path) -> list[dict[str, str]]:
    """Mutate precisely two original claims to FAIL after complete validation."""
    registry = validate_current_readonly_findings(repo)
    matches = {claim["id"]: (page, claim) for page in pages for claim in page["claims"] if claim.get("id") in TARGETS}
    _require(set(matches) == set(TARGETS) and sum(1 for page in pages for claim in page["claims"] if claim.get("id") in TARGETS) == 2,
             "exact current target set required")
    for finding in registry["findings"]:
        page, claim = matches[finding["claim_id"]]
        target = TARGETS[finding["claim_id"]]
        _require(page.get("route") == target["route"] and page.get("source_file") == target["source_file"] and page.get("source_sha256") == target["source_sha256"], "target page identity changed")
        _require(claim == finding["previous_claim"], "current claim differs from preserved original")
    summaries = []
    for finding in registry["findings"]:
        _, claim = matches[finding["claim_id"]]
        updated = copy.deepcopy(claim)
        updated.update({"status": "FAIL", "classification": finding["classification"],
                        "required_evidence_types": finding["required_evidence_types"], "rationale": finding["reason"],
                        "next_action": finding["next_action"],
                        "evidence_refs": [{"id": registry["adjudication_id"], "role": DECISION, "limit": registry["limits"], "artifact_ref": REGISTRY_PATH}] +
                        [{"id": Path(row["artifact_ref"]).stem, "role": "RETAINED_READONLY_FINDING_EVIDENCE", "limit": registry["limits"], "artifact_ref": row["artifact_ref"]} for row in finding["evidence"]]})
        if finding["claim_id"] == "MCL-323c8fb8180f5f62":
            updated["source_refs"] = [{"repository": "vast-ai/vast-cli", "revision": CLI_REVISION, "path": CLI_PATH,
                                       "locator": "show__machines, lines 62-78", "source_kind": "CANONICAL_IMPLEMENTATION_SOURCE"}]
        updated["history"].update({"carry_decision": DECISION,
                                   "reason": f"Confirmed bounded documentation defect; full original claim retained in {REGISTRY_PATH}."})
        claim.clear()
        claim.update(updated)
        summaries.append({"id": registry["adjudication_id"], "scope": finding["claim_id"],
                          "history": "Original UNVALIDATED claim retained in registry.",
                          "current": "FAIL / CONFIRMED_DOCUMENTATION_DEFECT; bounded correction required.",
                          "reason": finding["reason"]})
    return summaries
