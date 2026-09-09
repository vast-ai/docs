"""Fail-closed adjudication for four retained H100x4 listing/rental observations.

This is intentionally a tiny allowlisted importer, not a general live-evidence
loader.  It binds three atomic first-24-hours claims to a successful listing,
a fresh client offer, and one created client contract/independent client read.
It retains cleanup for a fourth, compound occurrence without promoting it.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY = "verification/current-h100x4-rental-adjudications.json"
TRANSITION_BASELINE_SOURCE = ("verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/"
                              "transition-baseline/host/first-24-hours.pre-two-defects.mdx")
DECISION = "CURRENT_H100X4_LISTING_RENTAL_RUNTIME_ADJUDICATION"
EVIDENCE_ROOT = "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02"
MACHINE = 150296
OFFER = 50363390
INSTANCE = 50364501
LABEL = "host-docs-vv-150296-20260909-attempt02-run03"
TARGETS = {
    "MCL-fabfbad844e625b4": ("Monitor", 44, 44),
    "MCL-7d10fc61bf9a884b": ("Test Like A Client", 63, 63),
    "MCL-92edb99129fc96c9": ("Test Like A Client", 71, 71),
    "MCL-da591d84b7d08317": ("Test Like A Client", 76, 76),
}
OUTCOMES = {
    "MCL-fabfbad844e625b4": "PASS",
    "MCL-7d10fc61bf9a884b": "PASS",
    "MCL-92edb99129fc96c9": "PASS",
    # Line 76 also contains conditional SSH/Jupyter troubleshooting.  Cleanup
    # proves the destruction clause but cannot prove the full occurrence.
    "MCL-da591d84b7d08317": "UNVALIDATED",
}
CLAIM_ARTIFACTS = {
    "MCL-fabfbad844e625b4": ["LISTING_REQUEST", "LISTING_RESPONSE", "LISTING_READBACK", "LISTING_VERIFICATION", "OFFER_SEARCH_REQUEST", "OFFER_SEARCH_RESPONSE"],
    "MCL-7d10fc61bf9a884b": ["FRESH_OFFER", "CREATE_REQUEST", "CREATE_RESPONSE", "INSTANCE_READ"],
    "MCL-92edb99129fc96c9": ["CREATE_RESPONSE", "INSTANCE_READ"],
    "MCL-da591d84b7d08317": ["CREATE_RESPONSE", "INSTANCE_READ", "CLEANUP"],
}
ARTIFACTS = {
    "LISTING_REQUEST": f"{EVIDENCE_ROOT}/rate-001/listing-request-01.json",
    "LISTING_RESPONSE": f"{EVIDENCE_ROOT}/rate-001/listing-response-01.json",
    "LISTING_READBACK": f"{EVIDENCE_ROOT}/rate-001/host-read-after-01.json",
    "LISTING_VERIFICATION": f"{EVIDENCE_ROOT}/rate-001/listing-readback-verification-01.json",
    "OFFER_SEARCH_REQUEST": f"{EVIDENCE_ROOT}/offer-search-request-01.json",
    "OFFER_SEARCH_RESPONSE": f"{EVIDENCE_ROOT}/offer-search-response-01.json",
    "FRESH_OFFER": f"{EVIDENCE_ROOT}/rental-run-03/rental-fresh-offer-01.json",
    "CREATE_REQUEST": f"{EVIDENCE_ROOT}/rental-run-03/rental-create-request-01.json",
    "CREATE_RESPONSE": f"{EVIDENCE_ROOT}/rental-run-03/rental-create-response-01.json",
    "INSTANCE_READ": f"{EVIDENCE_ROOT}/rental-run-03/instance-read-03.json",
    "CLEANUP": f"{EVIDENCE_ROOT}/rental-run-03/cleanup-main.json",
}
LIMIT = ("Exact 2026-09-09 listing-and-client-rental observation only: one-GPU contract 50364501 on machine 150296, "
         "created from offer 50363390 and then destroyed. It does not establish the stock/TUI install flow, SSH or Jupyter, "
         "broad search/ranking, host stability, full self-test, general workload readiness, other accounts or rentals, or future availability.")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"h100x4 rental adjudication: {message}")


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


def _time(value: str) -> datetime:
    _require(isinstance(value, str), "missing timestamp")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("h100x4 rental adjudication: invalid timestamp") from error


def _query(value: Any) -> bool:
    return value == {"machine_id": {"eq": MACHINE}, "num_gpus": {"eq": 1}, "rentable": {"eq": True},
                     "rented": {"eq": False}, "type": "on-demand", "limit": 10, "allocated_storage": 10,
                     "order": [["dph_total", "asc"]]}


def _validate_observations(items: dict[str, dict[str, Any]]) -> None:
    request, response = items["LISTING_REQUEST"], items["LISTING_RESPONSE"]
    readback, verified = items["LISTING_READBACK"], items["LISTING_VERIFICATION"]
    _keys(request, {"basis", "body", "collector_sha256", "credential_role", "endpoint", "guards", "method", "recorded_at", "source_sha256"}, "listing request")
    _require(request["method"] == "PUT" and request["endpoint"] == "/machines/create_asks/" and request["credential_role"] == "HOST" and
             request["body"] == {"machine": MACHINE, "price_gpu": 3.0, "price_disk": 0.5, "price_inetu": 0.01, "price_inetd": 0.01,
                                 "price_min_bid": 0.3, "min_chunk": 1, "end_date": 1789423200, "credit_discount_max": 0.0,
                                 "duration": None, "vol_size": 0, "vol_price": None}, "listing request mismatch")
    _keys(response, {"body", "endpoint", "finished", "http_status", "limitation", "method", "response_sha256", "started", "status"}, "listing response")
    _require(response["method"] == "PUT" and response["endpoint"] == "/machines/create_asks/" and response["http_status"] == 200 and
             response["status"] == "PASS" and response["body"] == {"success": True}, "listing response mismatch")
    _keys(readback, {"credential_role", "endpoint", "finished", "http_status", "limitation", "method", "response_sha256", "selected_fields", "started"}, "listing readback")
    expected_listing = {"id": MACHINE, "machine_id": MACHINE, "num_gpus": 4, "gpu_name": "H100 PCIE", "listed": True,
                        "listed_gpu_cost": 3.0, "listed_storage_cost": 0.5, "listed_inet_up_cost": 0.01, "listed_inet_down_cost": 0.01,
                        "min_bid_price": 0.3, "credit_discount_max": 0.0, "listed_min_gpu_count": 1, "end_date": 1789423200.0,
                        "duration": None, "volume_total_size": 0.0, "volume_rented_size": 0.0, "listed_volume_cost": None,
                        "current_rentals_running": 0, "current_rentals_resident": 0, "gpu_occupancy": "x x x x ",
                        "error_description": None, "verification": "unverified", "driver_version": "595.71.05"}
    _require(readback["method"] == "GET" and readback["endpoint"] == f"/machines/{MACHINE}?owner=me" and readback["credential_role"] == "HOST" and
             readback["http_status"] == 200 and readback["selected_fields"] == expected_listing, "listing readback mismatch")
    _keys(verified, {"expected", "limitation", "matches", "observed", "recorded_at", "status"}, "listing verification")
    _require(verified["status"] == "PASS" and all(verified["matches"].values()) and verified["expected"] == verified["observed"] and
             verified["observed"] == {key: expected_listing[key] for key in verified["observed"]}, "listing verification mismatch")

    search_request, search_response, fresh = items["OFFER_SEARCH_REQUEST"], items["OFFER_SEARCH_RESPONSE"], items["FRESH_OFFER"]
    _keys(search_request, {"basis", "body", "credential_role", "endpoint", "method", "recorded_at"}, "offer search request")
    _require(search_request["method"] == "POST" and search_request["endpoint"] == "/bundles/" and search_request["credential_role"] == "CLIENT" and _query(search_request["body"]), "offer search request mismatch")
    _keys(search_response, {"endpoint", "finished", "http_status", "limitation", "method", "offer_count", "offers", "response_sha256", "started", "status"}, "offer search response")
    _require(search_response["method"] == "POST" and search_response["endpoint"] == "/bundles/" and search_response["http_status"] == 200 and search_response["status"] == "PASS" and search_response["offer_count"] == 1 and isinstance(search_response["offers"], list) and len(search_response["offers"]) == 1, "offer search response mismatch")
    offer = search_response["offers"][0]
    _require(offer["id"] == OFFER and offer["machine_id"] == MACHINE and offer["num_gpus"] == 1 and offer["rentable"] is True and offer["rented"] is False, "offer search correlation mismatch")
    _keys(fresh, {"metadata", "offer", "query", "status"}, "fresh offer")
    _keys(fresh["metadata"], {"started", "finished", "method", "endpoint", "http_status", "response_sha256"}, "fresh offer metadata")
    _require(fresh["status"] == "PASS" and fresh["metadata"]["method"] == "POST" and fresh["metadata"]["endpoint"] == "/bundles/" and fresh["metadata"]["http_status"] == 200 and _query(fresh["query"]) and
             fresh["offer"]["id"] == OFFER and fresh["offer"]["machine_id"] == MACHINE and fresh["offer"]["num_gpus"] == 1 and fresh["offer"]["rentable"] is True and fresh["offer"]["rented"] is False, "fresh offer mismatch")

    create_request, create_response, instance = items["CREATE_REQUEST"], items["CREATE_RESPONSE"], items["INSTANCE_READ"]
    _keys(create_request, {"body", "collector_sha256", "credential_role", "endpoint", "machine_id", "method", "recorded_at", "source_revision", "source_sha256"}, "create request")
    _require(create_request["method"] == "PUT" and create_request["endpoint"] == f"/asks/{OFFER}/" and create_request["credential_role"] == "CLIENT" and create_request["machine_id"] == MACHINE and create_request["body"].get("label") == LABEL and create_request["body"].get("cancel_unavail") is True, "create request mismatch")
    _keys(create_response, {"body", "metadata"}, "create response")
    _keys(create_response["metadata"], {"started", "finished", "method", "endpoint", "http_status", "response_sha256"}, "create response metadata")
    _require(create_response["metadata"]["method"] == "PUT" and create_response["metadata"]["endpoint"] == f"/asks/{OFFER}/" and create_response["metadata"]["http_status"] == 200 and create_response["body"] == {"success": True, "new_contract": INSTANCE}, "create response mismatch")
    _keys(instance, {"instance", "metadata"}, "instance read")
    _keys(instance["metadata"], {"started", "finished", "method", "endpoint", "http_status", "response_sha256"}, "instance read metadata")
    observed = instance["instance"]
    _require(instance["metadata"]["method"] == "GET" and instance["metadata"]["endpoint"] == f"/instances/{INSTANCE}/?owner=me" and instance["metadata"]["http_status"] == 200 and
             observed["id"] == INSTANCE and observed["machine_id"] == MACHINE and observed["num_gpus"] == 1 and observed["label"] == LABEL, "client instance read mismatch")

    cleanup = items["CLEANUP"]
    _keys(cleanup, {"actor", "attempts", "instance_id", "limitations", "machine_id", "matching_rows", "owned_list_readback", "recorded_at", "status"}, "cleanup")
    _require(cleanup["actor"] == "main" and cleanup["status"] == "PASS" and cleanup["instance_id"] == INSTANCE and cleanup["machine_id"] == MACHINE and cleanup["matching_rows"] == [] and isinstance(cleanup["attempts"], list) and len(cleanup["attempts"]) == 2, "cleanup identity mismatch")
    before, after = cleanup["attempts"]
    _require(before["instance"]["id"] == INSTANCE and before["instance"]["machine_id"] == MACHINE and before["instance"]["num_gpus"] == 1 and before["instance"]["label"] == LABEL and
             before["delete"]["method"] == "DELETE" and before["delete"]["endpoint"] == f"/instances/{INSTANCE}/" and before["delete"]["http_status"] == 200 and before["acknowledgement"] == {"success": True} and
             after["read"]["method"] == "GET" and after["read"]["endpoint"] == f"/instances/{INSTANCE}/?owner=me" and after["read"]["http_status"] == 200 and after.get("absent") is True and
             cleanup["owned_list_readback"]["method"] == "GET" and cleanup["owned_list_readback"]["endpoint"] == "/instances?owner=me" and cleanup["owned_list_readback"]["http_status"] == 200, "cleanup predicate mismatch")

    sequence = [request["recorded_at"], response["started"], response["finished"], readback["started"], readback["finished"], verified["recorded_at"], search_request["recorded_at"], search_response["started"], search_response["finished"], fresh["metadata"]["started"], fresh["metadata"]["finished"], create_request["recorded_at"], create_response["metadata"]["started"], create_response["metadata"]["finished"], instance["metadata"]["started"], instance["metadata"]["finished"], before["read"]["started"], before["read"]["finished"], before["delete"]["started"], before["delete"]["finished"], after["read"]["started"], after["read"]["finished"], cleanup["owned_list_readback"]["started"], cleanup["owned_list_readback"]["finished"], cleanup["recorded_at"]]
    parsed = [_time(value) for value in sequence]
    _require(parsed == sorted(parsed), "observation timestamps are not chronological")


def _validate(repo: Path, source_path: str) -> dict[str, Any]:
    registry = _json(_read(repo, REGISTRY))
    _keys(registry, {"schema_version", "artifact_type", "purpose", "artifacts", "adjudications"}, "registry")
    _require(registry["schema_version"] == 1 and registry["artifact_type"] == "H100X4_LISTING_RENTAL_RUNTIME_ADJUDICATION_INPUT" and registry["purpose"] == "THREE_PASS_ONE_PARTIAL_FIRST_24_HOURS_RUNTIME_CLAIMS", "registry identity drift")
    _require(isinstance(registry["artifacts"], list) and [item.get("id") for item in registry["artifacts"] if isinstance(item, dict)] == list(ARTIFACTS), "artifact allowlist drift")
    items: dict[str, dict[str, Any]] = {}
    for artifact in registry["artifacts"]:
        _keys(artifact, {"id", "path", "sha256"}, "artifact")
        _require(artifact["path"] == ARTIFACTS[artifact["id"]] and isinstance(artifact["sha256"], str) and len(artifact["sha256"]) == 64, "artifact identity drift")
        payload = _read(repo, artifact["path"])
        _require(_sha(payload) == artifact["sha256"], "artifact digest drift")
        items[artifact["id"]] = _json(payload)
    _validate_observations(items)
    entries = registry["adjudications"]
    _require(isinstance(entries, list) and [item.get("claim_id") for item in entries if isinstance(item, dict)] == list(TARGETS), "target allowlist drift")
    for entry in entries:
        _keys(entry, {"id", "claim_id", "route", "source_file", "source_sha256", "headings", "span", "literal", "literal_sha256", "prior_status", "required_evidence_types", "outcome_status", "previous_claim", "previous_claim_sha256", "artifact_ids", "limits"}, "adjudication")
        heading, start, end = TARGETS[entry["claim_id"]]
        _keys(entry["span"], {"start", "end", "text_sha256"}, "span")
        _require(entry["id"] == f"H100X4-RENTAL-{entry['claim_id']}-01" and entry["route"] == "/host/first-24-hours" and entry["source_file"] == "host/first-24-hours.mdx" and entry["headings"] == [heading] and
                 (entry["span"]["start"], entry["span"]["end"]) == (start, end) and entry["prior_status"] == "UNVALIDATED" and entry["required_evidence_types"] == ["RUNTIME_OR_UI_OBSERVATION"] and entry["outcome_status"] == OUTCOMES[entry["claim_id"]] and entry["limits"] == LIMIT and
                 isinstance(entry["previous_claim"], dict) and entry["previous_claim"].get("id") == entry["claim_id"] and entry["previous_claim"].get("status") == "UNVALIDATED" and _canonical(entry["previous_claim"]) == entry["previous_claim_sha256"] and
                 entry["artifact_ids"] == CLAIM_ARTIFACTS[entry["claim_id"]], "claim binding drift")
        source = _read(repo, source_path)
        _require(_sha(source) == entry["source_sha256"], "source digest drift")
        literal = "\n".join(source.decode().splitlines()[start - 1:end])
        _require(literal == entry["literal"] and _sha(literal.encode()) == entry["literal_sha256"] == entry["span"]["text_sha256"], "source occurrence drift")
    return registry


def validate(repo: Path = REPO) -> dict[str, Any]:
    """Validate the original registry against the live, pre-transition source.

    This public path deliberately remains the historical strict gate: it does
    not accept a caller-selected source and therefore cannot bless an edited
    first-24-hours page.
    """
    return _validate(repo, "host/first-24-hours.mdx")


def validate_transition_baseline(repo: Path = REPO) -> dict[str, Any]:
    """Validate only the immutable pre-two-defects page used by the adapter."""
    return _validate(repo, TRANSITION_BASELINE_SOURCE)


def _apply(registry: dict[str, Any], pages: list[dict[str, Any]]) -> list[dict[str, str]]:
    claims: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for page in pages:
        for claim in page["claims"]:
            if claim.get("id") in TARGETS:
                _require(claim["id"] not in claims, "duplicate target claim id")
                claims[claim["id"]] = (page, claim)
    _require(set(claims) == set(TARGETS), "missing target claim id")
    matches: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for entry in registry["adjudications"]:
        page, claim = claims.get(entry["claim_id"], (None, None))
        _require(page is not None and claim is not None and page["route"] == entry["route"] and page["source_file"] == entry["source_file"] and page["source_sha256"] == entry["source_sha256"] and claim == entry["previous_claim"] and _canonical(claim) == entry["previous_claim_sha256"], "current claim drift or reapplication")
        matches.append((entry, claim))
    summaries: list[dict[str, str]] = []
    for entry, claim in matches:
        updated = copy.deepcopy(claim)
        evidence_refs = [{"id": entry["id"], "role": DECISION, "limit": LIMIT, "artifact_ref": REGISTRY}, *[{"id": artifact_id, "role": "RETAINED_H100X4_LISTING_RENTAL_OBSERVATION", "limit": LIMIT, "artifact_ref": ARTIFACTS[artifact_id]} for artifact_id in entry["artifact_ids"]]]
        if entry["outcome_status"] == "PASS":
            updated.update({"status": "PASS", "rationale": "The exact retained listing, fresh client offer, one-GPU client contract, independent client read, and cleanup observation satisfy this atomic runtime-only claim.",
                            "next_action": "Retest this exact bounded chain after any source, listing, offer, machine, contract, label, response, timestamp, cleanup, or evidence change. Keep stock-flow, SSH/Jupyter, stability, self-test, and broader marketplace claims separately reviewed.",
                            "evidence_refs": evidence_refs, "source_refs": [], "history": {**claim["history"], "carry_decision": DECISION, "reason": claim["history"]["reason"] + " Exact H100x4 listing-and-client-rental runtime observation is separately bound; original UNVALIDATED claim is hash-pinned and no broader PASS transfers."}})
        else:
            updated.update({"rationale": "Retained cleanup proves only that the exact task-created contract was deleted and absent afterwards. This same source occurrence also contains conditional SSH/Jupyter troubleshooting, which this evidence did not exercise or establish.",
                            "next_action": "An authorized source/owner check must bind the line-76 SSH/Jupyter conditional and its Network & Ports troubleshooting to a suitable source or representative authorized observation; do not promote this full compound occurrence from cleanup alone.",
                            "evidence_refs": evidence_refs, "history": {**claim["history"], "carry_decision": f"{DECISION}_PARTIAL", "reason": claim["history"]["reason"] + " Exact cleanup is retained as partial evidence only; the full compound source occurrence remains UNVALIDATED."}})
        claim.clear(); claim.update(updated)
        current = "PASS / exact H100x4 listing-and-client-rental observation only." if entry["outcome_status"] == "PASS" else "UNVALIDATED / exact cleanup retained as partial evidence; SSH/Jupyter conditional is not established."
        summaries.append({"id": entry["id"], "scope": entry["claim_id"], "history": "Original UNVALIDATED claim is hash-pinned in the rental adjudication registry.", "current": current, "reason": LIMIT})
    return summaries


def apply_current_h100x4_rental_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    return _apply(validate(repo), pages)


def apply_transition_baseline_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    """Materialize the old-page result for an exact transition comparison.

    It is intentionally separate from the current-page importer so the old
    whole-page digest remains mandatory and the current page receives no
    automatic PASS transfer.
    """
    return _apply(validate_transition_baseline(repo), pages)
