#!/usr/bin/env python3
"""Fail-closed projection for the four bounded Payout Account corrections.

The retained user-supplied UI transcription is evidence for the displayed
provider choices only.  It is not payment, account-state, fee, eligibility, or
bank-route evidence.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

REGISTRY = "verification/current-host-payout-provider-correction.json"
REGISTRY_SHA256 = "a93f8976805b1cd773d1216780419fcb3e361d496142abe61484719f9bbe27be"
ATTEMPT = "verification/evidence/2026-09-14-payout-provider-correction-attempt-01"
BASELINE = ATTEMPT + "/pre-correction-model.json"
BASELINE_SHA256 = "1b22bc97a8dc73fa34c047331a8a6a76e3a7564d8579cee5414139c269cf2857"
BEFORE_SOURCE = ATTEMPT + "/pre-correction-payment.mdx"
BEFORE_SOURCE_SHA256 = "02022ade67dcc35c44c660a5d3cdac7547c889c3a30e239eff56b57b22525992"
SOURCE = "host/payment.mdx"
OBSERVATION = "verification/evidence/2026-09-14-payout-ui-intake-attempt-01/observation.json"
OBSERVATION_SHA256 = "2ea94e5628c754d6d67ce4fb3b0f7fdcaf3bdb1a30ae28e50e483e83de19a9ef"
STATIC_CHECK = ATTEMPT + "/source-link-check.json"
STATIC_CHECK_SHA256 = "004aa077b2b1f1c15f3213d705235ee91bd128718352b8bda9c3cb09026fc970"
MARKER = "HOST-PAYOUT-PROVIDER-CORRECTION-01"
DECISION = "CURRENT_HOST_PAYOUT_PROVIDER_UI_CORRECTION"
IDS = {
    "MCL-77f72f0e0ac77e54": ("PayPal", "PAYOUT-UI-PAYPAL-01"),
    "MCL-a04f3ef2f5a7d5fd": ("Stripe", "PAYOUT-UI-STRIPE-01"),
    "MCL-cc62439b0f816902": ("Wise", "PAYOUT-UI-WISE-01"),
    "MCL-9826b26393329d27": (None, "PAYOUT-UI-DIRECT-01"),
}
CHANGED_LINES = {31, 98, 99, 101}
LANES = ["REPOSITORY_STATIC_CHECK", "RUNTIME_OR_UI_OBSERVATION"]


def fail(message: str) -> None:
    raise ValueError("payout provider correction: " + message)


def require(value: Any, message: str) -> None:
    if not value:
        fail(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def objhash(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    result = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(result)
    return result


def safe(root: Path, ref: str) -> Path:
    require(isinstance(ref, str) and ref and not ref.startswith("/") and "\\" not in ref and
            all(part not in {"", ".", ".."} for part in ref.split("/")), "unsafe path")
    path = root.resolve()
    for part in ref.split("/"):
        path /= part
        require(not path.is_symlink(), "unsafe symlink")
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()), "missing path " + ref)
    return path


def pinned(root: Path, ref: str, wanted: str) -> bytes:
    value = safe(root, ref).read_bytes()
    require(digest(value) == wanted, "digest drift " + ref)
    return value


def keys(value: Any, expected: set[str], label: str) -> None:
    require(isinstance(value, dict) and set(value) == expected, "invalid " + label + " keys")


def span(source: str, start: int, end: int, lines: list[str]) -> dict[str, Any]:
    text = "\n".join(lines[start - 1:end])
    return {"source_file": source, "start": start, "end": end, "text_sha256": digest(text.encode())}


def predecessor(root: Path, baseline: dict[str, Any], before_source: bytes) -> None:
    """Run every sealed predecessor gate against its exact old payment bytes."""
    cleanup = module("current_host_review_cleanup")

    def validate_cleanup_prior(repo: Path, model: dict[str, Any]) -> None:
        jurisdiction = module("current_host_jurisdiction")
        original = jurisdiction.predecessor

        def validate_jurisdiction_prior(inner_root: Path, inner_model: dict[str, Any], old: dict[str, bytes]) -> None:
            original(inner_root, inner_model, {**old, SOURCE: before_source})

        jurisdiction.predecessor = validate_jurisdiction_prior
        jurisdiction.validate_model(model, repo)

    cleanup.predecessor = validate_cleanup_prior
    cleanup.validate_model(baseline, root)


def correction(after_source_sha256: str) -> dict[str, str]:
    return {
        "id": MARKER,
        "scope": "Four exact Host Payouts provider-list/setup occurrences",
        "history": "The sealed cleanup predecessor and the pre-correction Host Payouts source are hash-pinned. Each predecessor FAIL literal remains in its claim history.",
        "current": "Three bounded provider-list occurrences and one provider-setup instruction are tied to the user-supplied Payout Account UI transcription and user-attributed Earnings URL; Host Payouts source " + BEFORE_SOURCE_SHA256 + " → " + after_source_sha256 + ".",
        "reason": "The UI crop supports displayed Stripe, PayPal and Wise choices only. It does not establish an active account, a completed payment, fees, eligibility, provider-mediated bank routes, or a universal ACH/wire/SWIFT exclusion.",
    }


def project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    registry = json.loads(pinned(root, REGISTRY, REGISTRY_SHA256))
    keys(registry, {"schema_version", "record_type", "generated_at", "baseline", "source", "static_check", "observation", "transitions"}, "registry")
    require(registry["schema_version"] == "1.0" and registry["record_type"] == "HOST_PAYOUT_PROVIDER_UI_CORRECTION", "wrong registry type")
    require(registry["baseline"] == {"path": BASELINE, "sha256": BASELINE_SHA256}, "baseline substitution")
    keys(registry["source"], {"path", "before_artifact", "before_sha256", "after_sha256", "changed_lines"}, "source")
    require(registry["source"] == {"path": SOURCE, "before_artifact": {"path": BEFORE_SOURCE, "sha256": BEFORE_SOURCE_SHA256},
                                   "before_sha256": BEFORE_SOURCE_SHA256, "after_sha256": registry["source"]["after_sha256"],
                                   "changed_lines": sorted(CHANGED_LINES)}, "source scope drift")
    keys(registry["observation"], {"path", "sha256"}, "observation")
    require(registry["observation"] == {"path": OBSERVATION, "sha256": OBSERVATION_SHA256}, "observation substitution")
    keys(registry["static_check"], {"path", "sha256"}, "static check")
    require(registry["static_check"] == {"path": STATIC_CHECK, "sha256": STATIC_CHECK_SHA256}, "static check substitution")
    before_source = pinned(root, BEFORE_SOURCE, BEFORE_SOURCE_SHA256)
    after_source = pinned(root, SOURCE, registry["source"]["after_sha256"])
    before_lines, after_lines = before_source.decode().splitlines(), after_source.decode().splitlines()
    require(len(before_lines) == len(after_lines), "line-stable source correction required")
    require({index + 1 for index, pair in enumerate(zip(before_lines, after_lines)) if pair[0] != pair[1]} == CHANGED_LINES, "source edits exceed exact approved lines")
    require(after_lines[30] == "The payout providers shown under [Earnings > Payout Account](https://cloud.vast.ai/earnings/) are:", "provider wording drift")
    require(after_lines[97] == '<span id="direct-bank-transfer" aria-hidden="true" /><span id="can-vast-send-direct-bank-transfers" aria-hidden="true" />', "legacy aliases missing")
    require(after_lines[98] == "### How do I set up payouts?" and after_lines[100] == "Set up payouts through Stripe, PayPal or Wise under [Earnings > Payout Account](https://cloud.vast.ai/earnings/).", "setup wording drift")
    require(not any(token in after_lines[100].casefold() for token in ("ach", "wire", "swift", "not available", "direct bank")), "unsupported global bank prohibition remains")
    static_check = json.loads(pinned(root, STATIC_CHECK, STATIC_CHECK_SHA256))
    require(static_check.get("record_type") == "PAYOUT_PROVIDER_SOURCE_LINK_CHECK" and static_check.get("source") == {"path": SOURCE, "sha256": digest(after_source)}, "static link source drift")
    expected_static = {cid: 31 if provider else 101 for cid, (provider, _obs) in IDS.items()}
    require({item.get("claim_id"): item.get("line") for item in static_check.get("checks", [])} == expected_static and all(item.get("href") == "https://cloud.vast.ai/earnings/" and item.get("result") == "PASS" for item in static_check["checks"]), "static link check drift")
    observation = json.loads(pinned(root, OBSERVATION, OBSERVATION_SHA256))
    require(observation.get("record_type") == "USER_SUPPLIED_PAYOUT_UI_EVIDENCE_INTAKE" and observation.get("source", {}).get("attributed_url") == "https://cloud.vast.ai/earnings/", "invalid UI observation")
    observed = {item.get("id"): item for item in observation.get("observations", [])}
    require(set(observed) == set(value[1] for value in IDS.values()), "UI observations differ from four bounded findings")
    require("Does not establish" in observed["PAYOUT-UI-DIRECT-01"].get("supports", ""), "bank-transfer limitation missing")
    baseline = json.loads(pinned(root, BASELINE, BASELINE_SHA256))
    predecessor(root, baseline, before_source)
    before = {claim["id"]: claim for page in baseline["pages"] for claim in page["claims"]}
    require(len(before) == 2013 and set(IDS) <= set(before), "baseline claim inventory drift")
    keys_by_id = {}
    for entry in registry["transitions"]:
        keys(entry, {"claim_id", "before_sha256", "observation_ids"}, "transition")
        cid = entry["claim_id"]
        expected_ids = [IDS[cid][1]] if IDS[cid][0] else ["PAYOUT-UI-PAYPAL-01", "PAYOUT-UI-STRIPE-01", "PAYOUT-UI-WISE-01"]
        require(cid in IDS and cid not in keys_by_id and entry["before_sha256"] == objhash(before[cid]) and entry["observation_ids"] == expected_ids, "transition predecessor or observation drift")
        keys_by_id[cid] = entry
    require(set(keys_by_id) == set(IDS), "four exact transitions required")
    result = copy.deepcopy(baseline)
    after = {claim["id"]: claim for page in result["pages"] for claim in page["claims"]}
    def evidence_ref(observation_id: str) -> dict[str, str]:
        return {"id": "EV-" + observation_id, "role": "USER_SUPPLIED_UI_OBSERVATION", "limit": "User-supplied cropped Payout Account view, URL user-attributed and capture time unknown; no transaction, active-account, fee, eligibility, or bank-route proof.", "artifact_ref": OBSERVATION}
    static_evidence = {"id": "EV-PAYOUT-PROVIDER-SOURCE-LINK-01", "role": "CURRENT_REPOSITORY_STATIC_CHECK", "limit": static_check["limit"], "artifact_ref": STATIC_CHECK}
    common_source = {"repository": "Vast AI product UI", "revision": "user-supplied-screenshot-sha256:a8531ae800b796ce185dc468a2e817d958d5362bf37c31284a09214a7dd48819", "path": "https://cloud.vast.ai/earnings/", "locator": "Payout Account", "source_kind": "USER_ATTRIBUTED_PRODUCT_UI"}
    for cid, (provider, observation_id) in IDS.items():
        prior, claim = before[cid], after[cid]
        if provider:
            spans = [span(SOURCE, 31, 31, after_lines), span(SOURCE, {"Wise": 33, "PayPal": 34, "Stripe": 35}[provider], {"Wise": 33, "PayPal": 34, "Stripe": 35}[provider], after_lines)]
            text = "\n".join("\n".join(after_lines[item["start"] - 1:item["end"]]) for item in spans)
            headings = ["Payout Methods"]
        else:
            spans, text, headings = [span(SOURCE, 101, 101, after_lines)], after_lines[100], ["How do I set up payouts?"]
        claim_evidence = [static_evidence, *[evidence_ref(item) for item in keys_by_id[cid]["observation_ids"]]]
        claim.update({"text": text, "headings": headings, "spans": spans, "status": "PASS", "classification": "REVIEWED_UI_PROVIDER_OPTION", "required_evidence_types": LANES,
                      "owner_role": "Documentation reviewer", "rationale": "The bounded user-supplied Earnings > Payout Account UI observation shows the named provider choice, and the current source link was checked for the same scope.",
                      "next_action": "Recheck this exact Payout Account view and wording if the provider cards or Earnings route changes.", "evidence_refs": claim_evidence, "source_refs": [], "coverage_state": "CHANGED",
                      "history": {**prior["history"], "carry_decision": DECISION, "reason": prior["history"].get("reason", "") + " Exact provider UI correction; no payout transaction or universal bank-transfer conclusion is inferred.",
                                  "predecessor": {"claim_id": cid, "status": prior["status"], "text": prior["text"], "text_sha256": digest(prior["text"].encode())}}})
        require(claim["text"] == "\n".join("\n".join(after_lines[s["start"] - 1:s["end"]]) for s in claim["spans"]), "claim literal/span drift " + cid)
        if provider:
            require(observed[observation_id]["claim_id"] == cid, "observation claim binding drift")
        else:
            require(all(observed[item]["claim_id"] in IDS for item in keys_by_id[cid]["observation_ids"]) and "PAYOUT-UI-DIRECT-01" not in keys_by_id[cid]["observation_ids"], "FAQ uses unsupported absence observation")
    page = next(page for page in result["pages"] if page["source_file"] == SOURCE)
    page["source_sha256"] = digest(after_source)
    page["coverage_state"] = "CHANGED"
    for claim in page["claims"]:
        if claim["id"] not in IDS:
            require(not any(set(range(item["start"], item["end"] + 1)) & CHANGED_LINES for item in claim["spans"]), "unrelated changed claim " + claim["id"])
    for procedure in page["procedures"]:
        for node in [procedure, *procedure["nodes"]]:
            if any(set(range(item["start"], item["end"] + 1)) & CHANGED_LINES for item in node.get("spans", [])):
                node["spans"] = []
                node["status"] = "STALE"
                node["coverage_state"] = "CHANGED"
                node["limits"] = [*node.get("limits", []), "Payout-provider source span changed; no procedure evidence transfers."]
                node["history"] = {**node.get("history", {}), "carry_decision": DECISION + "_SOURCE_CHANGED"}
    for item in result["source"]["source_manifest"]:
        if item["path"] == SOURCE:
            item["sha256"] = digest(after_source)
    require(sum(before[cid] == after[cid] for cid in before) == 2009, "unrelated claim drift")
    result["counts"]["claim_statuses"] = dict(sorted(Counter(claim["status"] for claim in after.values()).items()))
    result["generated_at"] = registry["generated_at"]
    result["corrections"].append(correction(digest(after_source)))
    return result


def validate_model(model: dict[str, Any], root: Path) -> None:
    require(model == project(root), "whole model differs from payout-provider projection")


def load_payout_provider_correction(root: Path, model: dict[str, Any]) -> dict[str, Any] | None:
    present = (root / REGISTRY).is_file()
    marked = any(item.get("id") == MARKER for item in model.get("corrections", []))
    if not present:
        require(not marked, "payout-marked model has no registry")
        return None
    validate_model(model, root)
    return {"registry": json.loads(pinned(root, REGISTRY, REGISTRY_SHA256)), "registry_sha256": REGISTRY_SHA256,
            "baseline": BASELINE, "baseline_sha256": BASELINE_SHA256, "observation": OBSERVATION, "observation_sha256": OBSERVATION_SHA256, "static_check": STATIC_CHECK, "static_check_sha256": STATIC_CHECK_SHA256}
