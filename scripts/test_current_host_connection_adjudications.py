"""Focused contracts for bounded current Host connection evidence."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.test_current_host_authority_scan import frozen_source_reader


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("connection", HERE / "current_host_connection_adjudications.py")
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class ConnectionAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_read=patch.object(gate,'_read',side_effect=frozen_source_reader(gate._read))
        fixture_read.start()
        cls.addClassCleanup(fixture_read.stop)
        cls.registry = gate.validate()
        # The builder's output is intentionally post-binding.  Exercise the
        # importer against the registry's immutable pre-binding projection so
        # this focused test stays valid after a normal --write regeneration.
        pages: dict[str, dict] = {}
        for entry in cls.registry["adjudications"]:
            page = pages.setdefault(entry["route"], {
                "route": entry["route"], "source_file": entry["source_file"],
                "source_sha256": entry["source_sha256"], "claims": [],
            })
            page["claims"].append(entry["previous_claim"])
        cls.model = {"pages": list(pages.values())}

    def pages(self) -> list[dict]:
        return copy.deepcopy(self.model["pages"])

    def changed_registry_rejected(self, mutate) -> None:
        registry = copy.deepcopy(self.registry)
        mutate(registry)
        original = gate._read
        def read(repo, relative):
            return json.dumps(registry).encode() if relative == gate.REGISTRY else original(repo, relative)
        with patch.object(gate, "_read", side_effect=read), self.assertRaises(ValueError):
            gate.validate()

    def test_exact_six_apply_with_only_two_bounded_passes(self) -> None:
        pages = self.pages()
        summaries = gate.apply_current_host_connection_adjudications(pages)
        claims = {claim["id"]: claim for page in pages for claim in page["claims"]}
        self.assertEqual([item["scope"] for item in summaries], list(gate.TARGETS))
        self.assertEqual(claims["COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"]["status"], "PASS")
        self.assertEqual(claims["MCL-4c49eaf437cfa29e"]["status"], "PASS")
        self.assertEqual(claims["MCL-1ebb3e6e2b370757"]["status"], "BLOCKED")
        self.assertEqual(claims["MCL-eeaf6da83da9eca7"]["status"], "BLOCKED")
        self.assertEqual(claims["MCL-3fb43d8a410371df"]["status"], "UNVALIDATED")
        self.assertEqual(claims["MCL-da591d84b7d08317"]["status"], "UNVALIDATED")
        for claim_id in ("MCL-4c49eaf437cfa29e", "MCL-1ebb3e6e2b370757", "MCL-3fb43d8a410371df"):
            self.assertEqual(claims[claim_id]["classification"], "RUNTIME_BEHAVIOR")
            self.assertEqual(claims[claim_id]["required_evidence_types"], ["RUNTIME_OR_UI_OBSERVATION"])
        self.assertEqual(claims["MCL-da591d84b7d08317"]["required_evidence_types"], ["RUNTIME_OR_UI_OBSERVATION"])
        self.assertIn("0.8506588", claims["MCL-eeaf6da83da9eca7"]["rationale"])
        self.assertIn("browser", claims["MCL-1ebb3e6e2b370757"]["rationale"].lower())
        self.assertEqual(claims["MCL-1ebb3e6e2b370757"]["history"]["carry_decision"], gate.DECISION)
        self.assertEqual(claims["MCL-eeaf6da83da9eca7"]["text"].splitlines()[2], "  --support-bundle-dir /path/to/output")
        self.assertNotIn("CUR-bfa0f979eb4ccc00", gate.TARGETS)
        self.assertEqual(
            claims["COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"]["evidence_refs"][:3],
            self.registry["adjudications"][0]["previous_claim"]["evidence_refs"],
        )
        for claim_id in ("MCL-4c49eaf437cfa29e", "MCL-1ebb3e6e2b370757", "MCL-3fb43d8a410371df"):
            self.assertEqual(claims[claim_id]["owner_role"], "Authorized client/browser/network operator")

    def test_prior_claim_artifact_digest_taxonomy_and_reapplication_fail_closed(self) -> None:
        self.changed_registry_rejected(lambda value: value["adjudications"].reverse())
        self.changed_registry_rejected(lambda value: value["artifacts"][0].update(sha256="0" * 64))
        self.changed_registry_rejected(lambda value: value["adjudications"][1]["taxonomy"].update(outcome_classification="IMPLEMENTATION_OR_CONCEPT"))
        self.changed_registry_rejected(lambda value: value["adjudications"][4]["previous_claim"].update(status="PASS"))
        pages = self.pages()
        gate.apply_current_host_connection_adjudications(pages)
        with self.assertRaisesRegex(ValueError, "current claim drift or reapplication"):
            gate.apply_current_host_connection_adjudications(pages)

    def test_source_occurrence_and_browser_blocker_are_not_bypassable(self) -> None:
        original = gate._read
        artifact = gate.ARTIFACTS["JUPYTER_HTTPS"]
        path = f"{gate.EVIDENCE_ROOT}/{artifact}"
        with patch.object(gate, "_read", side_effect=lambda repo, relative: b"{}" if relative == path else original(repo, relative)), self.assertRaises(ValueError):
            gate.validate()
        registry = copy.deepcopy(self.registry)
        registry["adjudications"][2]["outcome_status"] = "PASS"
        registry["adjudications"][2]["previous_claim_sha256"] = gate._canonical(registry["adjudications"][2]["previous_claim"])
        def read(repo, relative):
            return json.dumps(registry).encode() if relative == gate.REGISTRY else original(repo, relative)
        with patch.object(gate, "_read", side_effect=read), self.assertRaisesRegex(ValueError, "outcome drift"):
            gate.validate()


if __name__ == "__main__":
    unittest.main()
