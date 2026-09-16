"""One reviewed source-lane correction, never a general claim promotion facility.

validate_product_publications(repo) validates the retained registry and capture.
apply_product_publications(pages, repo) validates first, changes the exact original
claim in place, and returns one correction summary for the builder to append.
Neither function performs network access or writes files. Reapplication fails.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


CLAIM_ID = "MCL-e12ac9f6be2ce502"
CLAIM_TEXT = "Vast is a GPU marketplace. Hosts provide machines; renters run workloads on them."
ROUTE = "/host/hosting-overview"
SOURCE_FILE = "host/hosting-overview.mdx"
# Historical public API retained for existing focused tests and the preserved
# registry occurrence.  The authority transition adds one separately pinned
# current page hash below.
SOURCE_SHA256 = "0893d15921f55e4fae9a0aef5110336877d63d2698fe4c418bb4456fae686c7e"
# The authority-binding transition changes other, independently reviewed
# occurrences on this page.  It preserves this line byte-for-byte and pins the
# complete changed-page transition separately; this bounded adjudication never
# accepts an arbitrary third page revision.
SOURCE_SHA256S = {
    SOURCE_SHA256,
    "3d64b0bcfba203133725d654d1bb4c462b7ab8cfb577e94fcba3c37ffcf80ec3",
}
TEXT_SHA256 = "954df89cf6ab91b44b2ba20337c482bc6fa1a60f5ee6a252791e9102da7c7934"
PRIOR_CLAIM_SHA256 = "c9724dc3aa583b87d695e1eba6ba3b693e52d6e3315958adb34754f806887a24"
# The exact post-publication record from the frozen authority-transition input.
# It is not a generic already-PASS exception.
AUTHORITY_TRANSITION_CLAIM_SHA256 = "db08fba542604fe57b73527aa66a8fb5fe7fa1a160dce3f340ace92e2f183e62"
REGISTRY_PATH = "verification/current-host-product-publications.json"
CAPTURE_PATH = "verification/evidence/2026-09-08-host-live-readonly-attempt-01/product-source-capture-02.json"
CAPTURE_SHA256 = "50402fe4c97a54f9ac89d2f003b1c42329f708162a4691de214a3aa6bd3eac12"
DECISION = "CURRENT_PRODUCT_PUBLICATION_ADJUDICATION"
LANE = "PRODUCT_PUBLICATION_SOURCE"
SCOPE = "PASS supports only Vast's published high-level marketplace, Host supply and customer workload capability description."
LIMITS = "Not runtime observation, individual owner confirmation, a specific rental, machine ownership, health, provisioning or cleanup proof. No Finance, Legal, pricing, security, account or contractual promise is approved. Full HTML bodies are not retained; body hashes are provenance metadata, not replayable page evidence. No human acceptance is inferred."
REASON = "Deliberate reviewed correction of an over-demanding runtime-only lane for this exact introductory product description; three independent-of-docs official public pages jointly support its three parts."
SOURCE_ROWS = (
    ("marketplace", "https://vast.ai/article/vast-ai-startup-program",
     "Compute credits apply across Vast.ai's global GPU marketplace",
     "81b53a106f778c7067c2a5cc02867c1283f82508cb2e6cdf59547937e98eccb3"),
    ("host_supply", "https://vast.ai/hosting", "Your machines appear on the platform",
     "ef48fca97aade234030dd6a86170297fb2c775f17a65b43643799eb13c480af7"),
    ("workload_capability", "https://vast.ai/products/gpu-cloud",
     "Deploy AI models, run intensive compute jobs",
     "c2f880ab0b7343001e5c1c84fe7fcfb11f85ed5304edd420cf60ee3948e18340"),
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"product publication adjudication: {message}")


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
    result = json.loads(data, object_pairs_hook=_unique_object)
    _require(isinstance(result, dict), "expected a JSON object")
    return result


def _read_bytes(repo: Path, relative: str) -> bytes:
    root = Path(repo).resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    _require(path.is_relative_to(root) and path.is_file(), "artifact escaped repository or is not a file")
    return path.read_bytes()


def _sources() -> list[dict[str, str]]:
    return [{"part": part, "url": url, "excerpt": excerpt,
             "excerpt_sha256": _sha(excerpt.encode()), "body_sha256": body_hash}
            for part, url, excerpt, body_hash in SOURCE_ROWS]


def _validate_capture(capture: dict[str, Any], sources: list[dict[str, str]]) -> None:
    _require(set(capture) == {"schema_version", "claim_id", "claim_text", "status", "proof_kind",
                             "captures", "correction", "source_review", "retention"}, "capture fields changed")
    _require(type(capture["schema_version"]) is int and capture["schema_version"] == 1,
             "unsupported capture schema")
    _require(capture["claim_id"] == CLAIM_ID and capture["claim_text"] == CLAIM_TEXT,
             "capture claim mismatch")
    _require(capture["status"] == "PASS" and capture["proof_kind"] == LANE,
             "capture is not passing publication evidence")
    rows = capture["captures"]
    _require(isinstance(rows, list) and len(rows) == 3, "exactly three captures required")
    _require(sources == _sources(), "publication source allowlist changed")
    fields = {"part", "url", "final_url", "started_at", "ended_at", "http_status", "body_bytes",
              "body_sha256", "excerpt", "excerpt_sha256", "excerpt_found_in_normalized_body", "status"}
    for row, source in zip(rows, sources):
        _require(isinstance(row, dict) and set(row) == fields, "capture row fields changed")
        _require(all(row[key] == value for key, value in source.items()), "capture source, part or hash mismatch")
        _require(row["final_url"] == source["url"], "capture redirect is not the approved public URL")
        _require(type(row["http_status"]) is int and row["http_status"] == 200 and row["status"] == "PASS",
                 "unsuccessful public capture")
        _require(row["excerpt_found_in_normalized_body"] is True, "excerpt was not observed in captured body")
        _require(type(row["body_bytes"]) is int and row["body_bytes"] > 0, "empty capture body")
        _require(_sha(row["excerpt"].encode()) == row["excerpt_sha256"], "excerpt digest mismatch")
        try:
            _require(all(isinstance(row[key], str) and row[key].endswith("Z")
                         for key in ("started_at", "ended_at")), "capture timestamps must be UTC")
            start, end = (datetime.fromisoformat(row[key].replace("Z", "+00:00"))
                          for key in ("started_at", "ended_at"))
            _require(start <= end, "capture timestamps reversed")
        except (TypeError, ValueError) as exc:
            raise ValueError("product publication adjudication: invalid capture timestamps") from exc
    # All prose and the original failure/retest record are also bound by the
    # fixed capture artifact digest checked before this semantic validation.


def validate_product_publications(repo: Path) -> dict[str, Any]:
    """Return the single validated registry; raise on any occurrence/evidence drift."""
    registry = _json(_read_bytes(repo, REGISTRY_PATH))
    _require(set(registry) == {"schema_version", "artifact_type", "adjudication_id", "claim_id", "occurrence",
                              "previous_claim", "previous_claim_sha256", "classification", "status",
                              "required_evidence_types", "proof_scope", "limits", "reason", "capture", "sources"},
             "registry fields changed")
    _require(type(registry["schema_version"]) is int and registry["schema_version"] == 1,
             "unsupported registry schema")
    _require(registry["artifact_type"] == "BOUNDED_PRODUCT_PUBLICATION_ADJUDICATION"
             and registry["adjudication_id"] == "PRODUCT-PUBLICATION-MCL-e12ac9f6be2ce502-01"
             and registry["claim_id"] == CLAIM_ID, "only the exact approved claim is supported")
    _require(registry["occurrence"] == {"route": ROUTE, "source_file": SOURCE_FILE,
                                       "source_sha256": "0893d15921f55e4fae9a0aef5110336877d63d2698fe4c418bb4456fae686c7e", "start": 16, "end": 16,
                                       "text_sha256": TEXT_SHA256, "text": CLAIM_TEXT,
                                       "headings": ["Introduction"]}, "approved occurrence changed")
    _require(registry["previous_claim_sha256"] == PRIOR_CLAIM_SHA256
             and _canonical_sha(registry["previous_claim"]) == PRIOR_CLAIM_SHA256,
             "original assessment/history changed")
    _require(registry["classification"] == "PRODUCT_DESCRIPTION" and registry["status"] == "PASS"
             and registry["required_evidence_types"] == [LANE], "only the product-publication lane may pass")
    _require(registry["proof_scope"] == SCOPE and registry["limits"] == LIMITS
             and registry["reason"] == REASON, "bounded adjudication meaning changed")
    _require(registry["capture"] == {"artifact_ref": CAPTURE_PATH, "sha256": CAPTURE_SHA256},
             "capture artifact or digest changed")
    _require(registry["sources"] == _sources(), "exact three public source parts required")
    source = _read_bytes(repo, SOURCE_FILE)
    _require(_sha(source) in SOURCE_SHA256S, "current source file drift")
    lines = source.decode("utf-8").splitlines()
    _require(len(lines) >= 16 and lines[15] == CLAIM_TEXT
             and _sha(lines[15].encode()) == TEXT_SHA256, "current occurrence drift")
    capture_bytes = _read_bytes(repo, CAPTURE_PATH)
    _require(_sha(capture_bytes) == CAPTURE_SHA256, "retained capture artifact digest mismatch")
    _validate_capture(_json(capture_bytes), registry["sources"])
    return registry


def apply_product_publications(pages: list[dict[str, Any]], repo: Path) -> dict[str, Any]:
    """Mutate only the exact original target after validation; return one summary.

    Call after historical/current claim extraction, before computing counts.
    The registry preserves the full previous claim; the current claim keeps the
    established schema, including only the existing four history fields.
    """
    registry = validate_product_publications(repo)
    matches = [(page, claim) for page in pages for claim in page["claims"] if claim["id"] == CLAIM_ID]
    _require(len(matches) == 1, "exactly one current target claim required")
    page, claim = matches[0]
    _require(page["route"] == ROUTE and page["source_file"] == SOURCE_FILE
             and page["source_sha256"] in SOURCE_SHA256S, "target page identity changed")
    if page["source_sha256"] != "0893d15921f55e4fae9a0aef5110336877d63d2698fe4c418bb4456fae686c7e":
        _require(_canonical_sha(claim) == AUTHORITY_TRANSITION_CLAIM_SHA256
                 and claim["history"].get("carry_decision") == "CURRENT_PRODUCT_PUBLICATION_ADJUDICATION",
                 "authority-transition product claim drift")
        return {"id": registry["adjudication_id"], "scope": CLAIM_ID,
                "history": "The exact pre-existing post-publication record was source-transition rebound.",
                "current": "PASS / PRODUCT_DESCRIPTION / PRODUCT_PUBLICATION_SOURCE (published description only).",
                "reason": f"{REASON} {LIMITS}"}
    _require(claim == registry["previous_claim"], "current claim differs from preserved original assessment")
    updated = copy.deepcopy(claim)
    updated.update({
        "status": "PASS", "classification": "PRODUCT_DESCRIPTION", "required_evidence_types": [LANE],
        "owner_role": "Documentation product-description source reviewer",
        "rationale": f"{REASON} {SCOPE} {LIMITS}",
        "next_action": "Re-review this bounded source adjudication if the exact occurrence or retained sources change; no rental or human acceptance is asserted.",
        "source_refs": [{"repository": "vast-ai/public-website", "revision": f"sha256:{source['body_sha256']}",
                         "path": source["url"], "locator": f"{source['part']}: {source['excerpt']}",
                         "source_kind": LANE} for source in registry["sources"]],
        "evidence_refs": [
            {"id": registry["adjudication_id"], "role": DECISION, "limit": f"{SCOPE} {LIMITS}",
             "artifact_ref": REGISTRY_PATH},
            {"id": "PRODUCT-SOURCE-CAPTURE-02", "role": "PRODUCT_PUBLICATION_CITATION",
             "limit": f"Retained short excerpts and capture metadata only. {LIMITS}", "artifact_ref": CAPTURE_PATH},
        ],
    })
    updated["history"].update({"carry_decision": DECISION,
                               "reason": f"{REASON} Full original assessment/history preserved in {REGISTRY_PATH}."})
    claim.clear()
    claim.update(updated)
    return {"id": registry["adjudication_id"], "scope": CLAIM_ID,
            "history": "UNVALIDATED / RUNTIME_BEHAVIOR / RUNTIME_OR_UI_OBSERVATION; original full claim retained in registry.",
            "current": "PASS / PRODUCT_DESCRIPTION / PRODUCT_PUBLICATION_SOURCE (published description only).",
            "reason": f"{REASON} {LIMITS}"}
