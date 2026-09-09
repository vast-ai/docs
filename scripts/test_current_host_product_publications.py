"""Offline positive and fail-closed checks for the one product-source correction."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import current_host_product_publications as product


REPO = Path(__file__).resolve().parents[1]


class ProductPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = product.validate_product_publications(REPO)
        cls.capture = json.loads((REPO / product.CAPTURE_PATH).read_bytes())
        cls.page = {"route": product.ROUTE, "source_file": product.SOURCE_FILE,
                    "source_sha256": product.SOURCE_SHA256, "claims": [cls.registry["previous_claim"]]}

    def validate_registry(self, value: dict) -> dict:
        original_read = product._read_bytes
        def read(repo: Path, path: str) -> bytes:
            if path == product.REGISTRY_PATH:
                return json.dumps(value).encode()
            return original_read(repo, path)
        with patch.object(product, "_read_bytes", side_effect=read):
            return product.validate_product_publications(REPO)

    def test_positive_only_exact_target_changes_and_existing_schema_is_preserved(self) -> None:
        unrelated = copy.deepcopy(self.registry["previous_claim"])
        unrelated["id"] = "ANOTHER-CLAIM"
        pages = [copy.deepcopy(self.page), {"route": "/unrelated", "claims": [unrelated]}]
        before = copy.deepcopy(pages)
        summary = product.apply_product_publications(pages, REPO)
        claim = pages[0]["claims"][0]
        self.assertEqual(pages[1], before[1])
        self.assertEqual(set(claim), set(before[0]["claims"][0]))
        self.assertEqual(set(claim["history"]), set(before[0]["claims"][0]["history"]))
        self.assertEqual(claim["status"], "PASS")
        self.assertEqual(claim["classification"], "PRODUCT_DESCRIPTION")
        self.assertEqual(claim["required_evidence_types"], [product.LANE])
        self.assertEqual(claim["history"]["carry_decision"], product.DECISION)
        for field in ("id", "text", "headings", "spans", "coverage_state"):
            self.assertEqual(claim[field], before[0]["claims"][0][field])
        self.assertEqual(self.registry["previous_claim"], before[0]["claims"][0])
        self.assertEqual(summary["scope"], product.CLAIM_ID)
        self.assertEqual(len(claim["source_refs"]), 3)
        self.assertEqual({r["path"] for r in claim["source_refs"]}, {r["url"] for r in self.registry["sources"]})
        for ref in claim["source_refs"]:
            self.assertEqual(set(ref), {"repository", "revision", "path", "locator", "source_kind"})
            self.assertEqual(ref["source_kind"], product.LANE)
        for ref in claim["evidence_refs"]:
            self.assertEqual(set(ref), {"id", "role", "limit", "artifact_ref"})
            self.assertIn("Not runtime observation", ref["limit"])
            self.assertIn("not replayable page evidence", ref["limit"])
        with self.assertRaises(ValueError):
            product.apply_product_publications(pages, REPO)

    def test_registry_rejects_altered_identity_lanes_meaning_and_history(self) -> None:
        mutations = {
            "other_claim": lambda r: r.update(claim_id="ANOTHER-CLAIM"),
            "runtime_classification": lambda r: r.update(classification="RUNTIME_BEHAVIOR"),
            "runtime_lane": lambda r: r.update(required_evidence_types=["RUNTIME_OR_UI_OBSERVATION"]),
            "owner_lane": lambda r: r.update(required_evidence_types=["ACCOUNTABLE_OWNER_CONFIRMATION"]),
            "extra_lane": lambda r: r["required_evidence_types"].append("RUNTIME_OR_UI_OBSERVATION"),
            "missing_lane": lambda r: r.update(required_evidence_types=[]),
            "extra_field": lambda r: r.update(approved_all_claims=True),
            "scope_expansion": lambda r: r.update(proof_scope="A renter workload executed successfully."),
            "removed_limits": lambda r: r.update(limits=""),
            "prior_promotion": lambda r: r["previous_claim"].update(status="PASS"),
            "prior_history_change": lambda r: r["previous_claim"]["history"].update(carry_decision="OVERRIDDEN"),
            "span_drift": lambda r: r["occurrence"].update(start=17),
            "text_drift": lambda r: r["occurrence"].update(text="Changed claim"),
            "file_hash_drift": lambda r: r["occurrence"].update(source_sha256="0" * 64),
            "capture_substitution": lambda r: r["capture"].update(artifact_ref="owner-confirmation.json"),
            "capture_hash_drift": lambda r: r["capture"].update(sha256="0" * 64),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.registry)
                mutate(value)
                with self.assertRaises(ValueError):
                    self.validate_registry(value)

    def test_registry_rejects_missing_duplicate_extra_and_docs_sources(self) -> None:
        mutations = {
            "missing": lambda r: r["sources"].pop(),
            "extra": lambda r: r["sources"].append(copy.deepcopy(r["sources"][0])),
            "duplicate_part": lambda r: r["sources"][1].update(part="marketplace"),
            "duplicate_source": lambda r: r["sources"].__setitem__(1, copy.deepcopy(r["sources"][0])),
            "docs_self_proof": lambda r: r["sources"][0].update(url="https://docs.vast.ai/host/hosting-overview"),
            "non_official": lambda r: r["sources"][0].update(url="https://example.com/"),
            "extra_source_field": lambda r: r["sources"][0].update(runtime_verified=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.registry)
                mutate(value)
                with self.assertRaises(ValueError):
                    self.validate_registry(value)

    def test_capture_requires_successful_exact_sources_and_observed_excerpts(self) -> None:
        mutations = {
            "failed_attempt": lambda c: c.update(status="FAIL"),
            "other_claim": lambda c: c.update(claim_id="ANOTHER-CLAIM"),
            "runtime_substitution": lambda c: c.update(proof_kind="RUNTIME_OR_UI_OBSERVATION"),
            "owner_substitution": lambda c: c.update(proof_kind="ACCOUNTABLE_OWNER_CONFIRMATION"),
            "missing_part": lambda c: c["captures"].pop(),
            "duplicate_part": lambda c: c["captures"].__setitem__(1, copy.deepcopy(c["captures"][0])),
            "extra_part": lambda c: c["captures"].append(copy.deepcopy(c["captures"][0])),
            "http_failure": lambda c: c["captures"][0].update(http_status=403),
            "capture_failure": lambda c: c["captures"][0].update(status="FAIL"),
            "missing_excerpt": lambda c: c["captures"][0].update(excerpt_found_in_normalized_body=False),
            "excerpt_drift": lambda c: c["captures"][0].update(excerpt="Different words"),
            "excerpt_hash_drift": lambda c: c["captures"][0].update(excerpt_sha256="0" * 64),
            "body_hash_drift": lambda c: c["captures"][0].update(body_sha256="0" * 64),
            "docs_redirect": lambda c: c["captures"][0].update(final_url="https://docs.vast.ai/host/hosting-overview"),
            "empty_body": lambda c: c["captures"][0].update(body_bytes=0),
            "boolean_body_size": lambda c: c["captures"][0].update(body_bytes=True),
            "invalid_time": lambda c: c["captures"][0].update(started_at="not a timestamp"),
            "reversed_time": lambda c: c["captures"][0].update(started_at="2026-09-09T00:00:00Z"),
        }
        product._validate_capture(self.capture, self.registry["sources"])
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.capture)
                mutate(value)
                with self.assertRaises(ValueError):
                    product._validate_capture(value, self.registry["sources"])

    def test_source_or_capture_byte_drift_fails_without_mutating_any_claim(self) -> None:
        original_read = product._read_bytes
        for target in (product.SOURCE_FILE, product.CAPTURE_PATH):
            with self.subTest(path=target):
                def read(repo: Path, path: str) -> bytes:
                    value = original_read(repo, path)
                    return value + b"\n" if path == target else value
                pages = [copy.deepcopy(self.page)]
                before = copy.deepcopy(pages)
                with patch.object(product, "_read_bytes", side_effect=read), self.assertRaises(ValueError):
                    product.apply_product_publications(pages, REPO)
                self.assertEqual(pages, before)

    def test_target_absence_duplication_page_identity_or_prior_drift_fails_atomically(self) -> None:
        mutations = {
            "missing": lambda p: p[0].update(claims=[]),
            "unrelated_only": lambda p: p[0]["claims"][0].update(id="ANOTHER-CLAIM"),
            "duplicate": lambda p: p.append(copy.deepcopy(p[0])),
            "wrong_route": lambda p: p[0].update(route="/host/another-page"),
            "wrong_source": lambda p: p[0].update(source_file="host/another-page.mdx"),
            "wrong_page_hash": lambda p: p[0].update(source_sha256="0" * 64),
            "current_status": lambda p: p[0]["claims"][0].update(status="BLOCKED"),
            "current_lane": lambda p: p[0]["claims"][0].update(required_evidence_types=[product.LANE]),
            "current_text": lambda p: p[0]["claims"][0].update(text="A changed claim"),
            "current_span": lambda p: p[0]["claims"][0]["spans"][0].update(start=17),
            "current_evidence": lambda p: p[0]["claims"][0]["evidence_refs"].append({"id": "UNREVIEWED"}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                pages = [copy.deepcopy(self.page)]
                mutate(pages)
                before = copy.deepcopy(pages)
                with self.assertRaises(ValueError):
                    product.apply_product_publications(pages, REPO)
                self.assertEqual(pages, before)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            product._json(b'{"claim_id":"first", "claim_id":"second"}')


if __name__ == "__main__":
    unittest.main()
