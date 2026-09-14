"""Focused fail-closed contracts for the bounded Host authority adapter."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.test_current_host_authority_scan import frozen_before_model, frozen_source_reader


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("authority", HERE / "current_host_authority_adjudications.py")
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class AuthorityAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_read=patch.object(gate,'_read',side_effect=frozen_source_reader(gate._read))
        fixture_read.start()
        cls.addClassCleanup(fixture_read.stop)
        cls.registry, cls.baseline = gate.validate()
        cls.model = frozen_before_model()

    def test_pinned_registry_and_source_artifacts_reject_tampering(self) -> None:
        original = gate._read
        registry = copy.deepcopy(self.registry)
        registry["artifacts"][0]["sha256"] = "0" * 64
        with patch.object(gate, "_read", side_effect=lambda repo, path: json.dumps(registry).encode() if path == gate.REGISTRY else original(repo, path)), self.assertRaises(ValueError):
            gate.validate()
        agreement_path = self.registry["artifacts"][0]["path"]
        tampered = json.loads(original(gate.REPO, agreement_path))
        tampered["sections"][0]["text_sha256"] = "0" * 64
        with patch.object(gate, "_read", side_effect=lambda repo, path: json.dumps(tampered).encode() if path == agreement_path else original(repo, path)), self.assertRaises(ValueError):
            gate.validate()

    def test_joint_registry_and_agreement_tamper_cannot_replace_code_pins(self) -> None:
        """A mutually consistent mutable capture/registry still loses to code pins."""
        original = gate._read
        registry = copy.deepcopy(self.registry)
        agreement_path = registry["artifacts"][0]["path"]
        agreement = json.loads(original(gate.REPO, agreement_path))
        agreement["sections"][0]["text_sha256"] = "a" * 64
        replacement = json.dumps(agreement, sort_keys=True).encode()
        registry["artifacts"][0]["sha256"] = gate._sha(replacement)
        registry_bytes = json.dumps(registry, sort_keys=True).encode()
        with patch.object(gate, "_read", side_effect=lambda repo, path: registry_bytes if path == gate.REGISTRY else replacement if path == agreement_path else original(repo, path)), self.assertRaises(ValueError):
            gate.validate()

    def test_current_bound_records_preserve_partial_lanes_and_direct_proof(self) -> None:
        claims = {claim["id"]: claim for page in self.model["pages"] for claim in page["claims"]}
        for claim_id in gate.TECHNICAL:
            claim = claims[claim_id]
            self.assertEqual(claim["status"], "PASS")
            self.assertEqual(claim["required_evidence_types"], ["CANONICAL_IMPLEMENTATION_SOURCE"])
            self.assertEqual(len(claim["evidence_refs"]), 6)
        for claim_id in gate.AGREEMENT_PARTIAL:
            prior = next(claim for page in self.baseline["pages"] for claim in page["claims"] if claim["id"] == claim_id)
            claim = claims[claim_id]
            self.assertEqual(claim["status"], "FAIL")
            self.assertEqual(claim["required_evidence_types"], prior["required_evidence_types"])
            self.assertEqual(claim["owner_role"], prior["owner_role"])
            self.assertIn("Citation covers only", claim["rationale"])
        data_security = claims["AUTH-DATA-SECURITY-01"]
        self.assertEqual(data_security["status"], "PASS")
        self.assertTrue(any(ref["artifact_ref"].endswith("agreement-source-01.json") for ref in data_security["evidence_refs"]))

    def test_rebinding_preserves_same_text_distinct_span_identities(self) -> None:
        pages = copy.deepcopy(self.model["pages"])
        gate.apply_current_host_authority_adjudications(pages)
        for page in pages:
            if page["route"] not in gate.PAGES:
                continue
            keys = [tuple((span["source_file"], span["start"], span["end"], span["text_sha256"]) for span in claim["spans"]) for claim in page["claims"]]
            self.assertEqual(len(keys), len(set(keys)))

    def test_wrong_current_page_digest_is_rejected_before_rebinding(self) -> None:
        pages = copy.deepcopy(self.model["pages"])
        target = next(page for page in pages if page["route"] == "/host/hosting-overview")
        target["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "current page drift"):
            gate.apply_current_host_authority_adjudications(pages)


if __name__ == "__main__":
    unittest.main()
