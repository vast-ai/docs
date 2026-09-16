"""Fail-closed adjudication of four atomic post-install host observations.

This module deliberately validates only the retained H100x4 direct-route
snapshot.  It does not make the modified route evidence for the stock setup
flow, TUI, listing, self-test, rental, reboot, or general readiness.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any


REPO = Path(__file__).resolve().parents[1]
REGISTRY = "verification/current-h100x4-direct-postinstall-adjudications.json"
ATTEMPT = "verification/evidence/2026-09-09-h100x4-direct-install-attempt-02/postcheck-02.json"
ATTEMPT_SHA256 = "f30120d55712dbbd5b34af9a62d12690f9ffa1e84aee0f0e515fcce74c39e9c7"
DECISION = "CURRENT_H100X4_DIRECT_POSTINSTALL_RUNTIME_ADJUDICATION"
TARGETS = {
    "MCL-ead93c85c2ff4168": ("Headless Fallback", 65, 65, "POST-03", "GPU_INVENTORY_4_H100"),
    "MCL-82fa8860fe3ef124": ("After Install", 134, 134, "POST-01", "FOUR_SERVICES_ACTIVE"),
    "MCL-2f9f572d80e1e8f9": ("After Install", 135, 135, "POST-05", "DOCKER_XFS_PROJECT_QUOTA"),
    "MCL-aa383ba37f55f306": ("After Install", 136, 136, "POST-07", "PROJECT_QUOTA_ON"),
}
LIMIT = ("Observed only on the identified H100x4 host and timestamped snapshot after the approved modified direct route. "
         "It does not establish the stock setup-page download or command, TUI, driver or libvirt installation, Docker persistence or reboot, "
         "external network/NAT, account registration/listing, automatic self-test, workload result, rental readiness, or general host health. "
         "A transient bandwidth-test diagnostics container was still running at this snapshot.")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"h100x4 postinstall adjudication: {message}")


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
    root = repo.resolve(strict=True)
    requested = Path(relative)
    _require(not requested.is_absolute() and ".." not in requested.parts, "unsafe artifact path")
    lexical = root
    for part in requested.parts:
        lexical /= part
        _require(not lexical.is_symlink(), "artifact path contains symlink")
    path = lexical.resolve(strict=True)
    _require(path.is_relative_to(root) and path.is_file(), "unsafe or missing artifact")
    return path.read_bytes()


def _keys(value: Any, expected: set[str], label: str) -> None:
    _require(isinstance(value, dict) and set(value) == expected, f"invalid {label}")


def _observation_map(artifact: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _require(artifact.get("schema_version") == 1 and artifact.get("attempt_id") == "ATTEMPT-2026-09-09-H100X4-DIRECT-INSTALL-02" and
             artifact.get("target") == "NEW_H100X4_HOST" and isinstance(artifact.get("ssh_host_fingerprint"), str) and
             artifact.get("ssh_host_fingerprint").startswith("SHA256:") and artifact.get("exit_code") == 0 and
             isinstance(artifact.get("started"), str) and isinstance(artifact.get("finished"), str) and
             isinstance(artifact.get("boot_sha256"), str) and len(artifact["boot_sha256"]) == 64,
             "attempt identity or timing drift")
    observations = artifact.get("observations")
    _require(isinstance(observations, list), "missing observations")
    result: dict[str, dict[str, Any]] = {}
    for item in observations:
        _keys(item, {"id", "argv", "exit_code", "stdout", "stderr", "stdout_sha256"}, "observation")
        _require(isinstance(item["id"], str) and item["id"] not in result and isinstance(item["argv"], list) and
                 all(isinstance(part, str) for part in item["argv"]) and item["exit_code"] == 0 and
                 isinstance(item["stdout"], str) and isinstance(item["stderr"], str) and
                 item["stdout_sha256"] == _sha(item["stdout"].encode()), "observation identity or output drift")
        result[item["id"]] = item
    return result


def _predicate(kind: str, stdout: str) -> bool:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if kind == "GPU_INVENTORY_4_H100":
        return len(lines) == 4 and all(line.startswith("NVIDIA H100 PCIe,") and line.endswith("MiB") for line in lines)
    if kind == "FOUR_SERVICES_ACTIVE":
        return lines == ["active", "active", "active", "active"]
    if kind == "DOCKER_XFS_PROJECT_QUOTA":
        return len(lines) == 1 and " xfs " in f" {lines[0]} " and any(option in lines[0].split(",") for option in ("pquota", "prjquota"))
    if kind == "PROJECT_QUOTA_ON":
        match = re.search(r"(?ms)^Project quota state on /var/lib/docker \([^\n]+\)\n(?P<body>.*?)(?=^[A-Za-z]+ quota state on |\Z)", stdout)
        return bool(match and re.search(r"(?m)^  Accounting: ON\s*$", match["body"]) and
                    re.search(r"(?m)^  Enforcement: ON\s*$", match["body"]))
    return False


def validate(repo: Path = REPO) -> dict[str, Any]:
    registry = _json(_read(repo, REGISTRY))
    _keys(registry, {"schema_version", "artifact_type", "purpose", "artifact", "adjudications"}, "registry")
    _require(registry["schema_version"] == 1 and registry["artifact_type"] == "H100X4_DIRECT_POSTINSTALL_RUNTIME_ADJUDICATION_INPUT" and
             registry["purpose"] == "EXACT_FOUR_RUNTIME_ONLY_CLAIMS" and registry["artifact"] == {"path": ATTEMPT, "sha256": ATTEMPT_SHA256},
             "registry identity drift")
    artifact_bytes = _read(repo, ATTEMPT)
    _require(_sha(artifact_bytes) == ATTEMPT_SHA256, "postcheck artifact digest drift")
    observations = _observation_map(_json(artifact_bytes))
    entries = registry["adjudications"]
    _require(isinstance(entries, list) and [item.get("claim_id") for item in entries if isinstance(item, dict)] == list(TARGETS), "target allowlist drift")
    for item in entries:
        _keys(item, {"id", "claim_id", "route", "source_file", "source_sha256", "headings", "span", "literal", "literal_sha256", "prior_status", "required_evidence_types", "previous_claim", "previous_claim_sha256", "selector", "limits"}, "adjudication")
        claim_id = item["claim_id"]
        heading, start, end, observation_id, kind = TARGETS[claim_id]
        _keys(item["span"], {"start", "end", "text_sha256"}, "span")
        _keys(item["selector"], {"observation_id", "argv", "stdout_sha256", "predicate"}, "selector")
        _require(item["id"] == f"H100X4-POSTINSTALL-{claim_id}-01" and item["route"] == "/host/installing-host-software" and
                 item["source_file"] == "host/installing-host-software.mdx" and item["headings"] == [heading] and
                 (item["span"]["start"], item["span"]["end"]) == (start, end) and item["prior_status"] == "UNVALIDATED" and
                 item["required_evidence_types"] == ["RUNTIME_OR_UI_OBSERVATION"] and item["limits"] == LIMIT and
                 isinstance(item["previous_claim"], dict) and item["previous_claim"]["id"] == claim_id and
                 item["previous_claim"]["status"] == "UNVALIDATED" and _canonical(item["previous_claim"]) == item["previous_claim_sha256"],
                 "claim binding drift")
        source = _read(repo, item["source_file"])
        _require(_sha(source) == item["source_sha256"], "source page digest drift")
        literal = "\n".join(source.decode().splitlines()[start - 1:end])
        _require(literal == item["literal"] and _sha(literal.encode()) == item["literal_sha256"] == item["span"]["text_sha256"], "source occurrence drift")
        selector = item["selector"]
        observed = observations.get(observation_id)
        _require(selector["observation_id"] == observation_id and selector["predicate"] == kind and observed is not None and
                 selector["argv"] == observed["argv"] and selector["stdout_sha256"] == observed["stdout_sha256"] and
                 _predicate(kind, observed["stdout"]), "observation selector or predicate drift")
    return registry


def apply_current_h100x4_direct_postinstall_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    registry = validate(repo)
    claims: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for page in pages:
        for claim in page["claims"]:
            if claim.get("id") not in TARGETS:
                continue
            _require(claim["id"] not in claims, "duplicate target claim id")
            claims[claim["id"]] = (page, claim)
    _require(set(claims) == set(TARGETS), "missing target claim id")
    matches: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for entry in registry["adjudications"]:
        page, claim = claims.get(entry["claim_id"], (None, None))
        _require(page is not None and claim is not None and page["route"] == entry["route"] and page["source_file"] == entry["source_file"] and
                 page["source_sha256"] == entry["source_sha256"] and claim == entry["previous_claim"] and
                 _canonical(claim) == entry["previous_claim_sha256"], "current claim drift or reapplication")
        matches.append((entry, page, claim))
    summaries: list[dict[str, str]] = []
    for entry, _page, claim in matches:
        updated = copy.deepcopy(claim)
        updated.update({"status": "PASS",
                        "rationale": "The exact retained direct-route post-install observation satisfies this atomic runtime-only claim on the identified H100x4 snapshot.",
                        "next_action": "Retest this exact bounded runtime observation after any source, target, boot, command, output, or evidence change. Keep stock-flow, listing, self-test, rental, reboot, and broader-health claims separately reviewed.",
                        "evidence_refs": [
                            {"id": entry["id"], "role": DECISION, "limit": LIMIT, "artifact_ref": REGISTRY},
                            {"id": entry["selector"]["observation_id"], "role": "RETAINED_H100X4_POSTINSTALL_OBSERVATION",
                             "limit": LIMIT, "artifact_ref": registry["artifact"]["path"]},
                        ],
                        "source_refs": [],
                        "history": {**claim["history"], "carry_decision": DECISION,
                                    "reason": claim["history"]["reason"] + " Exact direct-postinstall runtime observation is separately bound; original UNVALIDATED claim is hash-pinned in the adjudication registry and no historical PASS transferred."}})
        claim.clear()
        claim.update(updated)
        summaries.append({"id": entry["id"], "scope": entry["claim_id"], "history": "Original UNVALIDATED claim is hash-pinned in the adjudication registry.",
                          "current": "PASS / exact H100x4 direct-postinstall runtime observation only.", "reason": LIMIT})
    return summaries
