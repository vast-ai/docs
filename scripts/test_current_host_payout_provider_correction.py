#!/usr/bin/env python3
"""Focused regression tests for the actual Payout Account correction inputs."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("current_host_payout_provider_correction.py")
SPEC = importlib.util.spec_from_file_location("payout", SCRIPT)
assert SPEC and SPEC.loader
payout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(payout)
ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"MCL-77f72f0e0ac77e54", "MCL-a04f3ef2f5a7d5fd", "MCL-cc62439b0f816902", "MCL-9826b26393329d27"}
TERMS_BEFORE = "verification/evidence/2026-09-14-payout-terms-correction-attempt-01/pre-correction-payment.mdx"
RAW_PINNED = payout.pinned

def frozen_pinned(root: Path, ref: str, wanted: str) -> bytes:
    return RAW_PINNED(root, TERMS_BEFORE, "95e6585980cb936f72c657a0ef508abf917361b210faa8b86b4b5af5896ad0a9") if ref == payout.SOURCE else RAW_PINNED(root, ref, wanted)

def project_frozen() -> dict:
    with patch.object(payout, "pinned", side_effect=frozen_pinned):
        return payout.project(ROOT)


class PayoutProviderCorrectionTests(unittest.TestCase):
    def test_actual_before_model_and_source_fail_before_while_projection_passes_after(self) -> None:
        before = json.loads((ROOT / payout.BASELINE).read_text())
        before_claims = {claim["id"]: claim for page in before["pages"] for claim in page["claims"]}
        self.assertEqual({before_claims[item]["status"] for item in TARGETS}, {"FAIL"})
        self.assertIn("ACH, wire, and SWIFT payouts are not available", (ROOT / payout.BEFORE_SOURCE).read_text())
        after = project_frozen()
        claims = {claim["id"]: claim for page in after["pages"] for claim in page["claims"]}
        self.assertEqual({claims[item]["status"] for item in TARGETS}, {"PASS"})
        self.assertEqual(after["counts"]["claim_statuses"], {"BLOCKED": 23, "FAIL": 31, "NOT_APPLICABLE": 87, "PASS": 312, "UNVALIDATED": 1560})
        faq = claims["MCL-9826b26393329d27"]
        self.assertEqual([item["id"] for item in faq["evidence_refs"]], ["EV-PAYOUT-PROVIDER-SOURCE-LINK-01", "EV-PAYOUT-UI-PAYPAL-01", "EV-PAYOUT-UI-STRIPE-01", "EV-PAYOUT-UI-WISE-01"])
        self.assertNotIn("PAYOUT-UI-DIRECT-01", [item["id"] for item in faq["evidence_refs"]])

    def test_tampered_observation_stale_source_unsupported_prohibition_and_unrelated_claim_fail_closed(self) -> None:
        original_pinned = payout.pinned
        with self.assertRaises(ValueError):
            payout.pinned(ROOT, payout.OBSERVATION, "0" * 64)
        def stale_source(root: Path, ref: str, wanted: str) -> bytes:
            value = original_pinned(root, TERMS_BEFORE, "95e6585980cb936f72c657a0ef508abf917361b210faa8b86b4b5af5896ad0a9") if ref == payout.SOURCE else original_pinned(root, ref, wanted)
            return value.replace(b"Stripe, PayPal or Wise", b"Stripe, PayPal, Wise and ACH") if ref == payout.SOURCE else value
        with patch.object(payout, "pinned", side_effect=stale_source):
            with self.assertRaises(ValueError):
                payout.project(ROOT)
        original_loads = payout.json.loads
        registry = original_loads((ROOT / payout.REGISTRY).read_text())
        registry["transitions"][-1]["observation_ids"] = ["PAYOUT-UI-DIRECT-01"]
        with patch.object(payout, "pinned", side_effect=lambda root, ref, wanted: json.dumps(registry).encode() if ref == payout.REGISTRY else (original_pinned(root, TERMS_BEFORE, "95e6585980cb936f72c657a0ef508abf917361b210faa8b86b4b5af5896ad0a9") if ref == payout.SOURCE else original_pinned(root, ref, wanted))):
            with self.assertRaises(ValueError):
                payout.project(ROOT)
        model = project_frozen()
        unselected = next(claim for page in model["pages"] for claim in page["claims"] if claim["id"] not in TARGETS)
        unselected["rationale"] += " tampered"
        with self.assertRaises(ValueError):
            with patch.object(payout, "pinned", side_effect=frozen_pinned):
                payout.validate_model(model, ROOT)


if __name__ == "__main__":
    unittest.main()
