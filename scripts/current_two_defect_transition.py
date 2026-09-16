"""Fail-closed, exact two-document transition for the September corrections.

This is a narrow adapter, not a generic carry-forward: it accepts precisely
two page edits, checks every other prior literal against current source, and
replays rental proof only against the immutable pre-edit page.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ATTEMPT = "verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01"
BASELINE = f"{ATTEMPT}/transition-baseline/current-host-docs-review.pre-two-defects.json"
BASELINE_SHA256 = "9714a8773317edb5a48ee2e7989f745efad2251b9d21b68308b48948c9789ccf"
CURRENT_PAGE_SHA256 = {"/host/first-24-hours": "d9cc6ad167e90ffb35e2af7f62882a6059bd05b14384a459a5bcb1cfc45f3502", "/host/vms": "e72464044e8404350d1860dc9a57bd12a0576fda0279a860948786b89bb9151a"}
REGISTRY = "verification/current-two-defect-transition.json"
FINDINGS = "verification/current-host-readonly-findings.json"
FINDINGS_SHA256 = "48134e3bb58ed35247547c0315089590b58edaac8d679c3ecfebe6af8240622b"
EXPECTED_ARTIFACT_HASHES = {
    f"{ATTEMPT}/transition-baseline/host/first-24-hours.pre-two-defects.mdx": "3ab83e7558387edc07416aa84c4cf8e5721f1312a4c94f3841c1af4ecd8cf970",
    f"{ATTEMPT}/transition-baseline/host/vms.pre-two-defects.mdx": "3f9cab3e239c3e048af39506adb8d6e83d0c497e82c34d11fad171a85cde822e",
    f"{ATTEMPT}/cli-query-source-inspection-01.json": "8d73fb0cb62c1656b4cb3e2732a5ed25f516585d2ea0cfefbf49245bc2fa7b88",
    f"{ATTEMPT}/cli-query-semantic-retest-01.json": "67b93037ca7db4c64ccedecc461e3a5ea8b7a86ada83e4db75e7af7d9f3e0abd",
    "verification/evidence/2026-09-08-host-client-unblocking-attempt-01/vm-helper-source-retest-02.json": "bdf9fa2e438dee4913f11f4e7c8d5abe64f98bab1fd29df6df1b6b6eaab21455",
    "verification/evidence/2026-09-08-host-client-unblocking-attempt-01/vm-status-01.json": "135f486a53342f25708db0b041ae08f8ff449866ff6083ddbf8b0e7caf6a2860",
    "verification/evidence/2026-09-08-host-client-unblocking-attempt-01/client-discovery-cli-source-01.json": "b68f35f899c5ef68bbfd9bb6515fd0025f66467ec381b7a297ed0286532a27d6",
    "verification/current-h100x4-rental-adjudications.json": "5098bd147e59d1b749d35d072be554beca90c0926ed6467f4aaf21c2cb6895d7",
}
OLD_FAILS = {"/host/first-24-hours": "MCL-323c8fb8180f5f62", "/host/vms": "MCL-dfebca7edafe9c59"}
ALLOWED = {
    "/host/first-24-hours": {59: ("```text", "```bash"), 60: ("vastai show machines", "vastai search offers 'machine_id=<machine_id> verified=any' --limit 200")},
    "/host/vms": {48: ("| `off` | VM support is disabled or a previous test failed. |", "| `off` | VM support is disabled, a previous test failed, or the status helper could not read its configuration. |")} }
REPLACEMENTS = {
    "/host/first-24-hours": {"id": "COR-01-MCL-323c8fb8180f5f62-REPLACEMENT", "span": (59, 61), "heading": "Test Like A Client", "text": "```bash\nvastai search offers 'machine_id=<machine_id> verified=any' --limit 200\n```", "classification": "RUNTIME_BEHAVIOR", "required": ["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"], "owner": "Vast CLI source owner; authorized client/API operator", "rationale": "The bounded source inspection supports the renter offer-search spelling and verified=any handling only. It does not execute search, establish offer visibility, or establish a successful rental workflow.", "next": "Retain the focused source signature/semantic check. An authorized client-context observation is still required before treating this instruction as a successful workflow.", "source_refs": [{"repository": "vast-ai/vast-cli", "revision": "18c4f2ccd6da587d5352f8741c71805a9a18e1ae", "path": "vastai/cli/commands/offers.py", "locator": "search__offers decorator/options lines 21-37 and query assembly lines 133-185", "source_kind": "CANONICAL_IMPLEMENTATION_SOURCE"}, {"repository": "vast-ai/vast-cli", "revision": "18c4f2ccd6da587d5352f8741c71805a9a18e1ae", "path": "vastai/api/query.py", "locator": "offers_fields lines 109-166; parse_query wildcard lines 329-336", "source_kind": "CANONICAL_IMPLEMENTATION_SOURCE"}], "evidence": [{"id": "CLI-QUERY-SOURCE-INSPECTION-01", "role": "CANONICAL_CLI_SIGNATURE_AND_SEMANTIC_RETEST", "limit": "Safe source inspection only: accepts --limit, default verified handling, and verified=any wildcard removal. No CLI/API command or renter workflow was run.", "artifact_ref": f"{ATTEMPT}/cli-query-source-inspection-01.json"}, {"id": "CLI-QUERY-SEMANTIC-RETEST-01", "role": "LOCAL_PINNED_AST_QUERY_SEMANTIC_RETEST", "limit": "Synthetic local parse only with machine_id=999999; no CLI dispatch, credentials, API, offer visibility, or rental workflow.", "artifact_ref": f"{ATTEMPT}/cli-query-semantic-retest-01.json"}]},
    "/host/vms": {"id": "COR-02-MCL-dfebca7edafe9c59-REPLACEMENT", "span": (48, 48), "heading": "Check VM Status", "text": "| `off` | VM support is disabled, a previous test failed, or the status helper could not read its configuration. |", "classification": "IMPLEMENTATION_OR_CONCEPT", "required": ["CANONICAL_IMPLEMENTATION_SOURCE"], "owner": "VM platform and Host integration source owner", "rationale": "The retained installed-helper source catches configuration-read failures before printing off, and the retained status observation records an unreadable configuration with off. This bounded correction does not identify or prove upstream VM health.", "next": "Retain the installed-helper/source counterexample and bind an identified upstream VM implementation before making any broader VM-state claim.", "source_refs": [], "evidence": [{"id": "VM-HELPER-SOURCE-RETEST-02", "role": "RETAINED_INSTALLED_HELPER_SOURCE", "limit": "Installed helper digest/source only; not upstream implementation identity or VM health proof.", "artifact_ref": "verification/evidence/2026-09-08-host-client-unblocking-attempt-01/vm-helper-source-retest-02.json"}, {"id": "VM-STATUS-01", "role": "RETAINED_CONFIGURATION_READ_COUNTEREXAMPLE", "limit": "One retained unreadable-configuration/off observation only; not a general VM runtime result.", "artifact_ref": "verification/evidence/2026-09-08-host-client-unblocking-attempt-01/vm-status-01.json"}]}, }


def _sha(value: bytes) -> str: return hashlib.sha256(value).hexdigest()
def _canon(value: Any) -> str: return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
def _require(condition: bool, message: str) -> None:
    if not condition: raise ValueError(f"two-defect transition: {message}")


def _read(repo: Path, relative: str) -> bytes:
    root, candidate = repo.resolve(strict=True), Path(relative)
    _require(not candidate.is_absolute() and ".." not in candidate.parts, "unsafe artifact path")
    path = root
    for part in candidate.parts:
        path /= part
        _require(not path.is_symlink(), "artifact path contains symlink")
    _require(path.is_file(), "unsafe or missing artifact")
    resolved = path.resolve(strict=True)
    _require(resolved.is_relative_to(root), "artifact path escapes repository")
    return resolved.read_bytes()


def _json(data: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            _require(key not in result, "duplicate JSON key"); result[key] = value
        return result
    result = json.loads(data, object_pairs_hook=unique)
    _require(isinstance(result, dict), "expected JSON object")
    return result


def _artifact_pins(repo: Path) -> None:
    for path, expected in EXPECTED_ARTIFACT_HASHES.items():
        _require(_sha(_read(repo, path)) == expected, f"artifact digest drift: {path}")


def _baseline(repo: Path) -> dict[str, dict[str, Any]]:
    data = _read(repo, BASELINE)
    _require(_sha(data) == BASELINE_SHA256, "baseline model digest drift")
    model = _json(data); _require(model.get("record_type") == "HOST_DOCS_CURRENT_REVIEW", "baseline model type")
    pages = {page.get("route"): page for page in model.get("pages", []) if isinstance(page, dict)}
    _require(set(OLD_FAILS).issubset(pages) and len(pages) == 44, "baseline page inventory drift")
    return {route: pages[route] for route in OLD_FAILS}


def _literal(repo: Path, source: str, start: int, end: int) -> str:
    lines = _read(repo, source).decode().splitlines(); _require(1 <= start <= end <= len(lines), "invalid source span")
    return "\n".join(lines[start - 1:end])


def _heading(source: bytes, line: int) -> str:
    import re
    answer = "Introduction"
    for number, value in enumerate(source.decode().splitlines(), 1):
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", value)
        if match and number <= line: answer = match.group(1)
    return answer


def _sources(repo: Path, old_pages: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for route, old_page in old_pages.items():
        source = old_page["source_file"]
        snapshot = f"{ATTEMPT}/transition-baseline/{source.rsplit('/', 1)[0]}/{Path(source).stem}.pre-two-defects.mdx"
        old, new = _read(repo, snapshot), _read(repo, source)
        _require(_sha(old) == old_page["source_sha256"], f"old snapshot digest drift: {route}")
        _require(_sha(new) == CURRENT_PAGE_SHA256[route], f"current page digest drift: {route}")
        before, after = old.decode().splitlines(), new.decode().splitlines()
        _require(len(before) == len(after), f"line-count drift: {route}")
        changed = {n: (a, b) for n, (a, b) in enumerate(zip(before, after), 1) if a != b}
        _require(changed == ALLOWED[route], f"unapproved source change: {route}")
        result[route] = {"source_file": source, "sha256": _sha(new), "snapshot": snapshot, "snapshot_sha256": _sha(old), "allowed_changes": [{"line": n, "old": a, "new": b} for n, (a, b) in changed.items()]}
    return result


def _cli_source_proof(repo: Path) -> None:
    proof = _json(_read(repo, f"{ATTEMPT}/cli-query-source-inspection-01.json"))
    _require(proof.get("exit_code") == 0 and proof.get("source_identity_unchanged") is True, "CLI source proof execution identity")
    observed = json.loads(proof.get("stdout", "{}"))
    rows = observed.get("rows") if isinstance(observed, dict) else None
    _require(isinstance(rows, list) and [(row.get("path"), row.get("sha256")) for row in rows] == [
        ("vastai/cli/commands/offers.py", "aaccded130adec54b95d7b68d4d13d466b3bcca885d130ef11f0fe5ee13ccf4c"),
        ("vastai/cli/commands/offers.py", "aaccded130adec54b95d7b68d4d13d466b3bcca885d130ef11f0fe5ee13ccf4c"),
        ("vastai/api/query.py", "40be0f69f1e0b2128eb81ba8b366a57856f9013ddb68db091995124de9a3869b")], "CLI source proof path/hash")
    excerpts = [row.get("excerpt") for row in rows]
    _require("argument(\"--limit\"" in excerpts[0] and "query = {\"verified\": {\"eq\": True}" in excerpts[1] and 'value in ["?", "*", "any"]' in excerpts[2], "CLI source proof semantics")


def _cli_semantic_proof(repo: Path) -> None:
    proof = _json(_read(repo, f"{ATTEMPT}/cli-query-semantic-retest-01.json"))
    _require(proof.get("exit_code") == 0 and proof.get("source_identity_unchanged") is True, "CLI semantic proof execution identity")
    observed = json.loads(proof.get("stdout", "{}"))
    _require(isinstance(observed, dict) and observed.get("repository") == "vast-ai/vast-cli" and observed.get("revision") == "18c4f2ccd6da587d5352f8741c71805a9a18e1ae" and observed.get("path") == "vastai/api/query.py" and observed.get("source_sha256") == "40be0f69f1e0b2128eb81ba8b366a57856f9013ddb68db091995124de9a3869b", "CLI semantic source pin")
    _require(observed.get("method") == "Execute only the pinned offers_fields assignment and parse_query function AST locally; no CLI client, credentials, network or Host operation" and observed.get("fields_locator") == {"start": 109, "end": 166} and observed.get("input") == "machine_id=999999 verified=any" and observed.get("synthetic_placeholder_substitution") == "999999 replaces <machine_id> for a local parser test; no such machine was contacted" and observed.get("recognized_fields") == ["machine_id", "verified"] and observed.get("parsed_query") == {"external": {"eq": False}, "rentable": {"eq": True}, "machine_id": {"eq": "999999"}} and observed.get("status") == "PASS" and observed.get("stderr") == "", "CLI semantic proof payload")


def _rental(repo: Path, old_page: dict[str, Any]) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("rental_transition", Path(__file__).with_name("current_h100x4_rental_adjudications.py"))
    module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    registry = module.validate_transition_baseline(repo)
    synthetic = [{"route": "/host/first-24-hours", "source_file": "host/first-24-hours.mdx", "source_sha256": old_page["source_sha256"], "claims": [copy.deepcopy(item["previous_claim"]) for item in registry["adjudications"]]}]
    module.apply_transition_baseline_adjudications(synthetic, repo)
    expected = {claim["id"]: claim for claim in synthetic[0]["claims"]}
    actual = {claim["id"]: claim for claim in old_page["claims"] if claim["id"] in expected}
    _require(actual == expected and len(actual) == 4, "historical rental result differs from pinned baseline")
    return {"registry": registry, "claims": expected}


def _claims(old_page: dict[str, Any], raw: list[dict[str, Any]], route: str, repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source = _read(repo, old_page["source_file"]); old_id = OLD_FAILS[route]
    inventory, carried = [], []
    for claim in old_page["claims"]:
        if claim["id"] == old_id: continue
        span = claim["spans"]
        _require(len(span) == 1 and _literal(repo, old_page["source_file"], span[0]["start"], span[0]["end"]) == claim["text"] and _sha(claim["text"].encode()) == span[0]["text_sha256"] and _heading(source, span[0]["start"]) == claim["headings"][0], f"unmodified literal drift: {claim['id']}")
        inventory.append({"id": claim["id"], "text": claim["text"], "headings": claim["headings"], "spans": span, "historical_status": claim["status"], "historical_claim_sha256": _canon(claim)})
        updated = copy.deepcopy(claim); updated["coverage_state"] = "CHANGED"; updated["history"] = {**updated["history"], "carry_decision": "TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL", "reason": updated["history"]["reason"] + " Exact unchanged literal and heading were rebound through the two-defect transition; no whole-page PASS transfer occurred."}; carried.append(updated)
    old = next(claim for claim in old_page["claims"] if claim["id"] == old_id); spec = REPLACEMENTS[route]
    spans = [spec["span"]]
    matches = [claim for claim in raw if [(item.get("start"), item.get("end")) for item in claim.get("spans", [])] == spans and claim.get("headings") == [spec["heading"]]]
    _require(len(matches) == 1, f"replacement literal inventory drift: {route}")
    replacement = copy.deepcopy(matches[0])
    _require(replacement["text"] == spec["text"], f"replacement text drift: {route}")
    replacement.update({"id": spec["id"], "status": "UNVALIDATED", "classification": spec["classification"], "required_evidence_types": spec["required"], "owner_role": spec["owner"], "rationale": spec["rationale"], "next_action": spec["next"], "source_refs": spec["source_refs"], "evidence_refs": [*spec["evidence"], {"id": spec["id"], "role": "TWO_DEFECT_CORRECTION_SOURCE_RETEST", "limit": "Static source/counterexample retest only; no runtime, owner approval, or workflow success is implied.", "artifact_ref": REGISTRY}], "history": {"baseline_claim_id": old["id"], "baseline_source_text_sha256": old["spans"][0]["text_sha256"], "carry_decision": "TWO_DEFECT_REPLACEMENT_UNVALIDATED", "reason": "Replaces the retained historical FAIL occurrence after the exact bounded source correction. The replacement remains UNVALIDATED."}, "coverage_state": "CHANGED"})
    return carried + [replacement], inventory, {"old_fail_claim": old, "replacement": replacement}


def apply_current_two_defect_transition(pages: list[dict[str, Any]], repo: Path = REPO) -> list[dict[str, str]]:
    _require(_sha(_read(repo, FINDINGS)) == FINDINGS_SHA256, "historical FAIL registry drift")
    _artifact_pins(repo)
    old_pages = _baseline(repo); current = _sources(repo, old_pages); _cli_source_proof(repo); _cli_semantic_proof(repo); rental = _rental(repo, old_pages["/host/first-24-hours"])
    selected = {page.get("route"): page for page in pages if page.get("route") in OLD_FAILS}
    _require(set(selected) == set(OLD_FAILS) and len(selected) == 2, "current page target set")
    proposed: dict[str, list[dict[str, Any]]] = {}
    for route, page in selected.items():
        _require(page.get("source_file") == old_pages[route]["source_file"] and page.get("source_sha256") == current[route]["sha256"] and page.get("coverage_state") == "CHANGED", "current page identity")
        _require(all(item.get("status") == "STALE" for item in page.get("procedures", []) if item.get("id", "").startswith("TS-")), "changed historical procedures must remain stale")
        proposed[route], _inventory, _records = _claims(old_pages[route], page["claims"], route, repo)
    for claim_id, expected in rental["claims"].items():
        actual = next(claim for claim in proposed["/host/first-24-hours"] if claim["id"] == claim_id)
        _require(actual["status"] == expected["status"], f"rental status transition drift: {claim_id}")
    for route, page in selected.items(): page["claims"] = proposed[route]
    return [{"id": "CURRENT-TWO-DEFECT-TRANSITION-01", "scope": route, "history": f"Original FAIL {OLD_FAILS[route]} remains immutable in {FINDINGS}.", "current": "UNVALIDATED bounded replacement; each other literal was exact-rebound.", "reason": "The allowed line/caption/fence transition is source-bound; no new runtime execution occurred."} for route in OLD_FAILS]


def output_bytes(pages: list[dict[str, Any]], repo: Path = REPO) -> bytes:
    _artifact_pins(repo)
    old_pages = _baseline(repo); current = _sources(repo, old_pages); _cli_source_proof(repo); _cli_semantic_proof(repo); rental = _rental(repo, old_pages["/host/first-24-hours"])
    selected = {page.get("route"): page for page in pages if page.get("route") in OLD_FAILS}; _require(set(selected) == set(OLD_FAILS), "final transition pages missing")
    records, inventory = {}, {}
    for route, old_page in old_pages.items():
        expected, inventory[route], records[route] = _claims(old_page, selected[route]["claims"], route, repo)
        _require(selected[route]["claims"] == expected, f"final transition claim set drift: {route}")
    rentals = [{"claim_id": key, "historical_claim_sha256": _canon(value), "current_status": next(item for item in selected["/host/first-24-hours"]["claims"] if item["id"] == key)["status"]} for key, value in rental["claims"].items()]
    record = {"schema_version": 1, "artifact_type": "EXACT_TWO_DEFECT_SOURCE_TRANSITION", "id": "CURRENT-TWO-DEFECT-TRANSITION-01", "limits": "Two documentation corrections only. Static source/counterexample checks do not establish renter visibility, a rental workflow, upstream VM health, owner approval, or acceptance.", "baseline": {"model": {"path": BASELINE, "sha256": BASELINE_SHA256}, "historical_fail_registry": {"path": FINDINGS, "sha256": FINDINGS_SHA256}}, "current_pages": current, "allowed_changes": {route: current[route]["allowed_changes"] for route in OLD_FAILS}, "historical_fail_records": records, "unmodified_claim_inventory": inventory, "rental_transition_adapter": {"registry": "verification/current-h100x4-rental-adjudications.json", "purpose": rental["registry"]["purpose"], "validated_against": "immutable pre-two-defects first-24-hours page", "claims": rentals}, "artifacts": [{"path": path, "sha256": sha256} for path, sha256 in EXPECTED_ARTIFACT_HASHES.items()]}
    return (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode()
