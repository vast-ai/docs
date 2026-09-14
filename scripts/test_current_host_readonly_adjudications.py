"""Focused positive and negative checks for the strict readonly command gate."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.test_current_host_authority_scan import frozen_before_model, frozen_source_reader

SCRIPT = Path(__file__).with_name("current_host_readonly_adjudications.py")
SPEC = importlib.util.spec_from_file_location("readonly_adjudications", SCRIPT)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ReadonlyAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_read=patch.object(gate,'_read',side_effect=frozen_source_reader(gate._read))
        fixture_read.start()
        cls.addClassCleanup(fixture_read.stop)
        cls.registry = gate.validate()
        overlay_spec = importlib.util.spec_from_file_location("overlay", Path(__file__).with_name("build_current_host_vv_overlay.py"))
        assert overlay_spec and overlay_spec.loader
        cls.overlay = importlib.util.module_from_spec(overlay_spec)
        overlay_spec.loader.exec_module(cls.overlay)

    def changed(self, mutate) -> None:
        original = gate._read
        value = copy.deepcopy(self.registry)
        mutate(value)
        def read(path: str):
            return __import__("json").dumps(value).encode() if path == gate.REGISTRY else original(path)
        with patch.object(gate, "_read", side_effect=read), self.assertRaises(ValueError):
            gate.validate()

    def test_exact_ten_passes_and_the_unaffected_blocker_refresh_remain_strict(self) -> None:
        package = frozen_before_model()
        claims = {claim["id"]: claim for page in package["pages"] for claim in page["claims"]}
        passing = {"CUR-142629d88fb18726", "CUR-705da5057d7f3360", "CUR-2c04f5e4d6ef0b20", "MCL-f0b9b724554ce68a", "MCL-aa735864a1cb734d", "MCL-96ee15f730e698d8", "MCL-728ef13be833d21e", "MCL-a54378e7f20b92e9", "MCL-e7db8b5148b63289", "MCL-50f964a1bb6a2e95"}
        self.assertTrue(all(claims[item]["status"] == "PASS" for item in passing))
        self.assertEqual(claims["MCL-aa735864a1cb734d"]["required_evidence_types"], ["CANONICAL_IMPLEMENTATION_SOURCE"])
        # MCL-ee is deliberately superseded later by the independently pinned
        # normal-preflight connection adjudication.  This readonly module still
        # owns the untouched MCL-3aca blocker refresh.
        for item in ("MCL-3aca6b1f291d4d0c",):
            prior = next(row for row in self.registry["blocker_refreshes"] if row["claim_id"] == item)["previous_claim"]
            self.assertEqual(claims[item]["status"], "BLOCKED")
            self.assertEqual(claims[item]["rationale"], gate.BLOCKER_RATIONALE)
            self.assertNotIn("credential with permission to select and create", claims[item]["rationale"])
            self.assertIn("create permission", claims[item]["next_action"])
            self.assertEqual(claims[item]["history"], prior["history"])
            self.assertEqual(claims[item]["evidence_refs"][:-1], prior["evidence_refs"])
        self.assertEqual(claims["MCL-eeaf6da83da9eca7"]["status"], "BLOCKED")
        self.assertEqual(claims["MCL-eeaf6da83da9eca7"]["history"]["carry_decision"], "CURRENT_HOST_CONNECTION_RUNTIME_ADJUDICATION")
        self.assertIn("0.8506588", claims["MCL-eeaf6da83da9eca7"]["rationale"])
        self.assertEqual(claims["MCL-eeaf6da83da9eca7"]["evidence_refs"][0]["artifact_ref"], "verification/current-host-connection-adjudications.json")

    def test_rejects_changed_text_span_heading_lane_source_capture_argv_and_nonzero(self) -> None:
        cases = {
            "text": lambda r: r["adjudications"][0].update(literal="different"),
            "span": lambda r: r["adjudications"][0]["span"].update(start=78),
            "heading": lambda r: r["adjudications"][0].update(headings=["Other"]),
            "lane": lambda r: r["adjudications"][0]["required_evidence_types"].append("ACCOUNTABLE_OWNER_CONFIRMATION"),
            "source": lambda r: r["adjudications"][0]["source_binding"][0].update(path="host/market-metrics.mdx"),
            "capture": lambda r: r["artifacts"][0].update(sha256="0" * 64),
            "argv": lambda r: r["adjudications"][0]["checks"][0].update(argv=["metrics", "wrong"]),
            "missing_check": lambda r: r["adjudications"][0].update(checks=[]),
            "partial_check_set": lambda r: r["adjudications"][0]["checks"].pop(),
            "empty_output_predicate": lambda r: r["adjudications"][0]["checks"][0].update(required_output={}),
            "trivial_output_predicate": lambda r: r["adjudications"][0]["checks"][0].update(required_output={"exit_code": 0}),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name): self.changed(mutate)

    def test_rejects_wrong_route_borrowed_proof_and_stale_blocker(self) -> None:
        cases = {
            "route": lambda r: r["adjudications"][0].update(route="/host/fleet-operations"),
            "borrowed": lambda r: r["adjudications"][1]["checks"][0].update(check_id="D06"),
            "blocked": lambda r: r["blocker_refreshes"][0].update(rationale="Host key unavailable"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name): self.changed(mutate)


if __name__ == "__main__":
    unittest.main()
