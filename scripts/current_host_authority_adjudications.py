"""Fail-closed, source-scoped Host authority transition.

This adapter is deliberately limited to four reviewed documentation pages.  It
rebinds unchanged literals from a frozen current model after the citation-only
source edits, then applies the four listing-control proofs and exact agreement
atoms.  It is not a generic changed-page carry-forward mechanism.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
REGISTRY = "verification/current-host-authority-adjudications.json"
DECISION = "CURRENT_HOST_AUTHORITY_SOURCE_TRANSITION"
BASELINE = "verification/evidence/2026-09-09-host-authority-correction-attempt-01/pre-authority-current-host-docs-review.json"
BASELINE_SHA256 = "8b24aad067b2d98d41cd1824a31a831fa88f9a9cfaa8cb39379c6c37839bdaf9"
REGISTRY_SHA256 = "6f500300b5953823ce34fd456773c924bd5bed4adcdd4077d57a5ecfed9fa66d"
PAGES = {
    "/host/hosting-overview": ("host/hosting-overview.mdx", "3d64b0bcfba203133725d654d1bb4c462b7ab8cfb577e94fcba3c37ffcf80ec3"),
    "/host/workload-policy": ("host/workload-policy.mdx", "9fa484d51b1988d68ce1618767d15a3d9d5d7123c98d1a4baf8cd7e27d0b661d"),
    "/host/hosting-agreement": ("host/hosting-agreement.mdx", "f7742a02b08626e474464d85a850903d436c1c3e1db18fb19764471ba5123c1b"),
    "/host/community": ("host/community.mdx", "6c0132ee35c6ad5d9324b3eaf6d1def8862db27752acd8a884903caaf7e58022"),
}
TECHNICAL = {
    "MCL-508003945b6ef934": "- Minimum GPU count (`min_chunk`).",
    "MCL-c85a4e96752730ab": "- Interruptible minimum bid.",
    "MCL-437e58c77dcafecc": "- Maximum prepaid discount (`discount_rate`).",
    "MCL-943ba22ec56a356a": "- Offer end date.",
}
AGREEMENT_PASS = {
    "MCL-805ef8a72833f2b8": "- Troubleshooting local hardware problems. [Hosting Agreement — Performance of Services](https://cloud.vast.ai/host/agreement) assigns the provider responsibility for running, troubleshooting, and maintaining the hardware.",
    "MCL-3cfe1a3c265f0223": "Vast bears no responsibility for technical assistance for the hardware or software required to get the hardware to function properly. See [Hosting Agreement — Performance of Services](https://cloud.vast.ai/host/agreement).",
    "MCL-1a4146b033bd9b88": "Do not read renter files while investigating a report. See [Hosting Agreement — Operation and Maintenance](https://cloud.vast.ai/host/agreement).",
    "MCL-f855ff5e92cfbec1": "Do not read, download, store, review, print, or save renter data. See [Hosting Agreement — Operation and Maintenance](https://cloud.vast.ai/host/agreement).",
    "MCL-181b0127498ba639": "Vast bears no responsibility for technical assistance for the hardware or software required to get the hardware to function properly. See [Hosting Agreement — Performance of Services](https://cloud.vast.ai/host/agreement).",
}
AGREEMENT_PARTIAL = {
    "MCL-ed68c47bda19e986": "Plan maintenance when the machine has no running instances or after active rental contracts end. [Hosting Agreement — Operation and Maintenance](https://cloud.vast.ai/host/agreement) requires preventative and remedial maintenance when an Authorized User is not actively using the hardware. For planned downtime, use [Maintenance Windows](/host/maintenance-windows). For unlisting, deleting, recreating, or uninstalling, see [Remove or Recreate](/host/removing-recreating-machines).",
    "MCL-8fe2020c0e7efe26": "When a report appears, treat it as a machine-health or contract-quality signal, not permission to inspect renter data. See [Hosting Agreement — Operation and Maintenance](https://cloud.vast.ai/host/agreement). Start with host-side evidence:",
    "MCL-399798a3c4946b5f": "| Intellectual-property concerns | Escalate credible concerns; do not inspect private renter data. See [Hosting Agreement — Operation and Maintenance](https://cloud.vast.ai/host/agreement). |",
}
NEW_AGREEMENT = "- Use reasonable safeguards and physical security around the hardware to protect Vast.ai Content. See [Hosting Agreement — Intellectual Property and Data Security](https://cloud.vast.ai/host/agreement)."
PRESENTATION_MARKUP = '<div className="persona-chips"><span className="persona-chip">All host personas</span></div>'
RESIDUAL_PREDECESSOR = {
    "- Troubleshooting local driver, storage, and network problems.": "MCL-805ef8a72833f2b8",
    "Do not review private workload output while investigating a report.": "MCL-1a4146b033bd9b88",
    "Do not copy or share renter files or private workload output while investigating a report.": "MCL-1a4146b033bd9b88",
    "If the issue points to platform state, policy, abuse, account state, or a backend machine-record mismatch, collect timestamps, screenshots, report details, and host-side logs, then escalate to Vast support. For log commands and diagnostic collection, see [Host Diagnostics](/host/common-errors-diagnostics#logs).": "MCL-1a4146b033bd9b88",
    "Do not stop, inspect, modify, or interfere with renter containers. The operational rules are summarized in [Workload Policy](/host/workload-policy).": "MCL-f855ff5e92cfbec1",
    "Your OS, drivers, BIOS, storage, power, thermals, and router remain host-operated concerns. See [Is Vast for Me?](/host/persona-decision-guide).": "MCL-181b0127498ba639",
}
ARTIFACT_SHA256 = {
    "agreement": "7e400189f805d177d0770dfecff5e123b4016fc62c8bd46e2ec127918d5ed8ca",
    "cli": "f1e8d8f4deb28da8d09d5686c2b70d2b7b13dd68e1046c4ce95438a9ab739d87",
    "request": "d04afab6cff838e948d1e730d5dd4525320bf096616a2dfc8a987b5fb6b92efa",
    "response": "c0dfb89456e9207c86157f66e226c05e62a328fc9fd4aa9d891bb27a827ae86d",
    "readback": "0691db52a0d697b8f6e1c9b85dc8af91abc2223c240eefb5a212e257d7092072",
    "verification": "00ea44fc85b0aad6de0d403f8f97d678c2948ee614c9524a0b42e5e273181e3f",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canon(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(f"authority adjudication: {message}")


def _read(repo: Path, relative: str) -> bytes:
    root, requested = repo.resolve(strict=True), Path(relative)
    _require(not requested.is_absolute() and ".." not in requested.parts, "unsafe path")
    path = root
    for part in requested.parts:
        path /= part
        _require(not path.is_symlink(), "symlink path")
    path = path.resolve(strict=True)
    _require(path.is_relative_to(root) and path.is_file(), "missing artifact")
    return path.read_bytes()


def _json(data: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            _require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(data, object_pairs_hook=unique)
    _require(isinstance(value, dict), "expected JSON object")
    return value


def _source_ref(heading: str) -> dict[str, str]:
    return {"repository": "vast-ai/hosting-agreement", "revision": "sha256:1b04ae5bb85fdbdb687cf8fb331e2d7b56f061ffb0a6edf05751a79e4aff689c", "path": "https://cloud.vast.ai/host/agreement", "locator": heading, "source_kind": "AUTHORITATIVE_DOCUMENTATION_CITATION"}


def _current_span(source_file: str, lines: list[str], literal: str) -> dict[str, Any]:
    wanted = literal.splitlines()
    hits = [index for index in range(len(lines) - len(wanted) + 1) if lines[index:index + len(wanted)] == wanted]
    _require(len(hits) == 1, f"current literal drift: {literal[:40]}")
    start = hits[0] + 1
    return {"source_file": source_file, "start": start, "end": start + len(wanted) - 1, "text_sha256": _sha(literal.encode())}


def validate(repo: Path = REPO) -> tuple[dict[str, Any], dict[str, Any]]:
    registry_bytes = _read(repo, REGISTRY)
    _require(_sha(registry_bytes) == REGISTRY_SHA256, "registry digest drift")
    registry = _json(registry_bytes)
    _require(set(registry) == {"schema_version", "artifact_type", "purpose", "baseline", "artifacts"}, "registry keys")
    _require(registry["schema_version"] == 1 and registry["artifact_type"] == "CURRENT_HOST_AUTHORITY_ADJUDICATION_INPUT", "registry identity")
    _require(registry["baseline"] == {"path": BASELINE, "sha256": BASELINE_SHA256}, "baseline pin")
    _require(_sha(_read(repo, BASELINE)) == BASELINE_SHA256, "baseline digest drift")
    expected_artifacts = {
        "agreement": "verification/evidence/2026-09-09-host-authority-correction-attempt-01/agreement-source-01.json",
        "cli": "verification/evidence/2026-09-09-host-authority-correction-attempt-01/cli-listing-source-01.json",
        "request": "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-request-01.json",
        "response": "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-response-01.json",
        "readback": "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/host-read-after-01.json",
        "verification": "verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/listing-readback-verification-01.json",
    }
    _require([(item.get("id"), item.get("path")) for item in registry["artifacts"]] == list(expected_artifacts.items()), "artifact allowlist")
    data: dict[str, dict[str, Any]] = {}
    for item in registry["artifacts"]:
        _require(set(item) == {"id", "path", "sha256"} and item["sha256"] == ARTIFACT_SHA256[item["id"]] and _sha(_read(repo, item["path"])) == ARTIFACT_SHA256[item["id"]], "artifact digest drift")
        data[item["id"]] = _json(_read(repo, item["path"]))
    agreement = data["agreement"]
    _require(agreement["url"] == "https://cloud.vast.ai/host/agreement" and agreement["body_text_sha256"] == "1b04ae5bb85fdbdb687cf8fb331e2d7b56f061ffb0a6edf05751a79e4aff689c" and
             [(item["heading"], item["heading_id"], item["text_sha256"]) for item in agreement["sections"]] == [
                 ("PERFORMANCE OF SERVICES", "", "7295e122dc2c222ed3017940a70fade0c863091ab77e131681c80f965c0ae711"),
                 ("OPERATION AND MAINTENANCE", "", "755d42b65def84a36a89e2dd50a515edcc722a2b6ccc72dfda466bc12efe14f7"),
                 ("INTELLECTUAL PROPERTY AND DATA SECURITY", "", "fef83109ea3b422d9edc33a15813c72d5e09c7204bab7d796d32a6af4399bb85"),
             ], "agreement capture drift")
    cli = data["cli"]
    _require(cli["revision"] == "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd" and cli["path"] == "vastai/cli/commands/machines.py" and cli["source_sha256"] == "1c58876ada8c3912550396a6b2862e5de565c68b53c84554eb368e2140dc66d3" and cli["local_bytes_match"] is True and "min_chunk" in cli["excerpts"][0]["text"] and "price_min_bid" in cli["excerpts"][0]["text"] and "credit_discount_max" in cli["excerpts"][0]["text"] and "end_date" in cli["excerpts"][0]["text"], "CLI proof drift")
    request, response, readback, verification = (data[key] for key in ("request", "response", "readback", "verification"))
    _require(request["body"]["min_chunk"] == 1 and request["body"]["price_min_bid"] == 0.3 and request["body"]["credit_discount_max"] == 0.0 and request["body"]["end_date"] == 1789423200 and response["status"] == "PASS" and response["http_status"] == 200, "listing request/result drift")
    selected, observed = readback["selected_fields"], verification["observed"]
    _require(selected["listed_min_gpu_count"] == 1 and selected["min_bid_price"] == 0.3 and selected["credit_discount_max"] == 0.0 and selected["end_date"] == 1789423200.0 and verification["status"] == "PASS" and all(verification["matches"].values()) and observed["listed_min_gpu_count"] == 1, "listing readback drift")
    return registry, _json(_read(repo, BASELINE))


def _rebound(old: dict[str, Any], source_file: str, lines: list[str]) -> dict[str, Any] | None:
    # The product-publication gate already owns this exact post-publication
    # record.  Verify its literal still exists, but retain every byte of the
    # claim so that gate can verify its dedicated post-publication hash.
    if old["id"] == "MCL-e12ac9f6be2ce502":
        _current_span(source_file, lines, old["text"])
        updated = copy.deepcopy(old)
        updated["coverage_state"] = "CHANGED"
        return updated
    spans, fragments, offset = [], old["text"].splitlines(), 0
    for span in old["spans"]:
        count = span["end"] - span["start"] + 1
        fragment = "\n".join(fragments[offset:offset + count])
        offset += count
        # The frozen claim joins its source spans without an extra separator;
        # every span must therefore recover exactly once at the new source.
        _require(fragment and _sha(fragment.encode()) == span["text_sha256"], f"frozen span reconstruction drift: {old['id']}")
        spans.append(_current_span(source_file, lines, fragment))
    _require(offset == len(fragments), f"frozen span partition drift: {old['id']}")
    updated = copy.deepcopy(old)
    updated.update({"spans": spans, "coverage_state": "CHANGED", "history": {**old["history"], "carry_decision": DECISION, "reason": old["history"]["reason"] + " Exact unchanged literal was rebound through the authority transition; no whole-page PASS transfer occurred."}})
    return updated


def _authority_update(old: dict[str, Any], source_file: str, lines: list[str], literal: str, status: str, classification: str, lanes: list[str], rationale: str, refs: list[dict[str, str]], limit: str) -> dict[str, Any]:
    updated = copy.deepcopy(old)
    partial = status == "FAIL"
    next_action = ("Retain the cited clause as partial evidence, then obtain an accountable owner source for the remaining report/escalation, contract-timing, maintenance-window, or intellectual-property procedure wording and the required approved runtime observation where applicable; do not promote this mixed occurrence." if partial else "Re-run this exact source binding if the documented occurrence, captured agreement section, pinned CLI revision, or retained listing readback changes; do not transfer this result to broader behavior.")
    evidence = [{"id": f"AUTHORITY-{old['id']}-01", "role": DECISION, "limit": limit, "artifact_ref": REGISTRY}]
    if classification == "IMPLEMENTATION_OR_CONCEPT":
        evidence.extend([{"id": "AUTHORITY-CLI-SOURCE-01", "role": "CANONICAL_IMPLEMENTATION_SOURCE", "limit": limit, "artifact_ref": "verification/evidence/2026-09-09-host-authority-correction-attempt-01/cli-listing-source-01.json"}, *[{"id": f"AUTHORITY-{key.upper()}-01", "role": "RETAINED_LISTING_READBACK", "limit": limit, "artifact_ref": f"verification/evidence/2026-09-09-h100x4-listing-rental-attempt-02/rate-001/{name}"} for key, name in (("request", "listing-request-01.json"), ("response", "listing-response-01.json"), ("readback", "host-read-after-01.json"), ("verification", "listing-readback-verification-01.json"))]])
    elif refs and refs[0]["repository"] == "vast-ai/hosting-agreement":
        evidence.append({"id": "AUTHORITY-AGREEMENT-SOURCE-01", "role": "AUTHORITATIVE_DOCUMENTATION_CITATION", "limit": limit, "artifact_ref": "verification/evidence/2026-09-09-host-authority-correction-attempt-01/agreement-source-01.json"})
    updated.update({"text": literal, "spans": [_current_span(source_file, lines, literal)], "status": status, "classification": classification, "required_evidence_types": old["required_evidence_types"] if partial else lanes, "owner_role": old["owner_role"] if partial else "Authorized documentation and source-evidence reviewer", "rationale": rationale, "next_action": next_action, "source_refs": refs, "evidence_refs": evidence, "coverage_state": "CHANGED", "history": {**old["history"], "carry_decision": DECISION, "reason": old["history"]["reason"] + " The full prior claim is retained in the frozen pre-authority model; this exact source transition is bounded by the authority registry."}})
    return updated


def apply_current_host_authority_adjudications(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    registry, baseline = validate(repo)
    baseline_pages = {page["route"]: page for page in baseline["pages"]}
    current = {page["route"]: page for page in pages if page["route"] in PAGES}
    _require(set(current) == set(PAGES), "target page set")
    summaries: list[dict[str, str]] = []
    for route, page in current.items():
        source_file, expected_sha = PAGES[route]
        source = _read(repo, source_file)
        _require(page["source_file"] == source_file and page["source_sha256"] == expected_sha == _sha(source) and page["coverage_state"] == "CHANGED", "current page drift")
        lines = source.decode().splitlines()
        # Presentation-only MDX is not a client documentation claim and must
        # not inflate the reviewed current-claim inventory.
        raw = [claim for claim in page["claims"] if claim["text"] != PRESENTATION_MARKUP]
        replacements: dict[str, dict[str, Any]] = {}
        for old in baseline_pages[route]["claims"]:
            if old["id"] in TECHNICAL:
                literal = TECHNICAL[old["id"]]
                refs = [{"repository": "vast-ai/vast-cli", "revision": "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd", "path": "vastai/cli/commands/machines.py", "locator": "list_machine_impl request mapping and list machine options", "source_kind": "CANONICAL_IMPLEMENTATION_SOURCE"}]
                replacements[old["id"]] = _authority_update(old, source_file, lines, literal, "PASS", "IMPLEMENTATION_OR_CONCEPT", ["CANONICAL_IMPLEMENTATION_SOURCE"], "Pinned CLI source exposes this exact listing setting and maps it into the request; retained Host request/readback corroborate one accepted stored value only.", refs, "Exact setting exposure and one accepted/stored value only; not server-side enforcement, a nonzero discount calculation, expiry execution, or existing-contract behavior.")
            elif old["id"] in AGREEMENT_PASS:
                literal = AGREEMENT_PASS[old["id"]]
                heading = "PERFORMANCE OF SERVICES" if old["id"] in {"MCL-805ef8a72833f2b8", "MCL-3cfe1a3c265f0223", "MCL-181b0127498ba639"} else "OPERATION AND MAINTENANCE"
                replacements[old["id"]] = _authority_update(old, source_file, lines, literal, "PASS", "POLICY_OR_COMMERCIAL", ["AUTHORITATIVE_DOCUMENTATION_CITATION"], "The named captured agreement section directly supports this narrowed obligation only.", [_source_ref(heading)], "Exact clause-to-occurrence binding only; no Discord, setup procedure, container, escalation, or runtime result is implied.")
            elif old["id"] in AGREEMENT_PARTIAL:
                literal = AGREEMENT_PARTIAL[old["id"]]
                replacements[old["id"]] = _authority_update(old, source_file, lines, literal, "FAIL", "POLICY_OR_COMMERCIAL", ["AUTHORITATIVE_DOCUMENTATION_CITATION"], "CONFIRMED_CITATION_DEFECT: Citation covers only a clause-level subset of this mixed occurrence; the required owner source for the remaining procedure and any required runtime observation are still missing.", [_source_ref("OPERATION AND MAINTENANCE")], "Partial clause coverage only; the original required lanes and owner remain. Not a maintenance-window workflow, report procedure, IP-escalation rule, contract guarantee, or runtime result.")
            else:
                rebound = _rebound(old, source_file, lines)
                if rebound is not None:
                    replacements[old["id"]] = rebound
        rebuilt = list(replacements.values())
        def span_key(claim: dict[str, Any]) -> tuple[tuple[str, int, int, str], ...]:
            return tuple((span["source_file"], span["start"], span["end"], span["text_sha256"]) for span in claim["spans"])
        raw_keys = [span_key(claim) for claim in raw]
        _require(len(raw_keys) == len(set(raw_keys)), f"ambiguous raw claim identity: {route}")
        covered_spans = {item for claim in rebuilt for item in span_key(claim)}
        # A changed page can contain the same literal under different headings;
        # retain every raw occurrence not already represented by the exact span.
        rebuilt.extend(claim for claim in raw if not all(item in covered_spans for item in span_key(claim)))
        rebuilt_keys = [span_key(claim) for claim in rebuilt]
        _require(len(rebuilt_keys) == len(set(rebuilt_keys)), f"duplicate rebuilt claim identity: {route}")
        baseline_by_id = {claim["id"]: claim for claim in baseline_pages[route]["claims"]}
        for claim in rebuilt:
            predecessor_id = RESIDUAL_PREDECESSOR.get(claim["text"])
            if predecessor_id is None:
                continue
            predecessor = next((item for page_claims in baseline_pages.values() for item in page_claims["claims"] if item["id"] == predecessor_id), None)
            _require(predecessor is not None, f"residual predecessor missing: {predecessor_id}")
            claim.update({
                "status": "FAIL", "classification": predecessor["classification"],
                "required_evidence_types": predecessor["required_evidence_types"], "owner_role": predecessor["owner_role"],
                "rationale": "CONFIRMED_CITATION_DEFECT: This split residual retains the predecessor's required citation, owner, and evidence lanes; no authoritative source covers its remaining obligation or permission wording.",
                "next_action": "Obtain an accountable owner source for this exact residual wording and, where required, an approved representative runtime observation; retain both against this occurrence without broadening the cited agreement clause.",
                "history": {**claim["history"], "baseline_claim_id": predecessor_id,
                            "baseline_source_text_sha256": predecessor["history"]["baseline_source_text_sha256"],
                            "reason": "Split residual from frozen " + predecessor_id + "; it remains a citation/authority finding and receives no historical PASS transfer."},
            })
        if route == "/host/hosting-agreement":
            match = [claim for claim in rebuilt if claim["text"] == NEW_AGREEMENT]
            _require(len(match) == 1, "data-security atom missing")
            atom = match[0]
            atom.update({"id": "AUTH-DATA-SECURITY-01", "status": "PASS", "classification": "POLICY_OR_COMMERCIAL", "required_evidence_types": ["AUTHORITATIVE_DOCUMENTATION_CITATION"], "owner_role": "Authorized documentation and source-evidence reviewer", "rationale": "The captured Intellectual Property and Data Security section directly supports reasonable safeguards and physical security only.", "next_action": "Re-review this exact clause binding if the source or occurrence changes; technical security effectiveness remains outside this result.", "source_refs": [_source_ref("INTELLECTUAL PROPERTY AND DATA SECURITY")], "evidence_refs": [{"id": "AUTHORITY-DATA-SECURITY-01", "role": DECISION, "limit": "Clause wording only; not proof that a specific host is secure or technically isolated.", "artifact_ref": REGISTRY}, {"id": "AUTHORITY-AGREEMENT-SOURCE-01", "role": "AUTHORITATIVE_DOCUMENTATION_CITATION", "limit": "Clause wording only; not proof that a specific host is secure or technically isolated.", "artifact_ref": "verification/evidence/2026-09-09-host-authority-correction-attempt-01/agreement-source-01.json"}], "history": {"baseline_claim_id": None, "baseline_source_text_sha256": None, "carry_decision": DECISION, "reason": "New exact agreement-cited atom; broader prior data-isolation wording remains separately retained."}, "coverage_state": "CHANGED"})
        page["claims"] = rebuilt
    for claim_id in [*TECHNICAL, *AGREEMENT_PASS, *AGREEMENT_PARTIAL, "AUTH-DATA-SECURITY-01"]:
        summaries.append({"id": f"AUTHORITY-{claim_id}-01", "scope": claim_id, "history": "Full predecessor is retained in the frozen pre-authority model." if claim_id.startswith("MCL-") else "New bounded cited atom.", "current": "PASS" if claim_id in TECHNICAL or claim_id in AGREEMENT_PASS or claim_id == "AUTH-DATA-SECURITY-01" else "FAIL (partial clause; original lanes remain required)", "reason": registry["purpose"]})
    return summaries
