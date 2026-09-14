"""Focused contract tests for H100x4 direct-route runtime-only evidence."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.test_current_host_authority_scan import frozen_before_model, frozen_source_reader


SCRIPT = Path(__file__).with_name("current_h100x4_direct_postinstall_adjudications.py")
SPEC = importlib.util.spec_from_file_location("h100x4_postinstall", SCRIPT)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class H100x4PostinstallAdjudicationTests(unittest.TestCase):
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

    def changed_registry_rejected(self, mutate) -> None:
        original = gate._read
        value = copy.deepcopy(self.registry)
        mutate(value)
        def read(repo, relative):
            return json.dumps(value).encode() if relative == gate.REGISTRY else original(repo, relative)
        with patch.object(gate, "_read", side_effect=read), self.assertRaises(ValueError):
            gate.validate()

    def test_exact_four_runtime_claims_pass_without_source_proof(self) -> None:
        package = frozen_before_model()
        claims = {claim["id"]: claim for page in package["pages"] for claim in page["claims"]}
        self.assertEqual(set(gate.TARGETS), {row["claim_id"] for row in self.registry["adjudications"]})
        for claim_id in gate.TARGETS:
            claim = claims[claim_id]
            self.assertEqual(claim["status"], "PASS")
            self.assertEqual(claim["required_evidence_types"], ["RUNTIME_OR_UI_OBSERVATION"])
            self.assertEqual(claim["source_refs"], [])
            self.assertEqual(claim["history"]["carry_decision"], gate.DECISION)
            self.assertEqual(claim["evidence_refs"][0]["artifact_ref"], gate.REGISTRY)
            self.assertEqual(claim["evidence_refs"][1]["id"], gate.TARGETS[claim_id][3])
            self.assertEqual(claim["evidence_refs"][1]["artifact_ref"], gate.ATTEMPT)
            self.assertIn("transient bandwidth-test", claim["evidence_refs"][0]["limit"])

    def test_rejects_target_lane_literal_selector_and_prior_claim_drift(self) -> None:
        cases = {
            "target": lambda r: r["adjudications"].reverse(),
            "lane": lambda r: r["adjudications"][0]["required_evidence_types"].append("CANONICAL_IMPLEMENTATION_SOURCE"),
            "literal": lambda r: r["adjudications"][0].update(literal="different"),
            "selector": lambda r: r["adjudications"][0]["selector"].update(observation_id="POST-01"),
            "prior": lambda r: r["adjudications"][0]["previous_claim"].update(status="PASS"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                self.changed_registry_rejected(mutate)

    def test_rejects_artifact_digest_and_failed_project_quota_predicate(self) -> None:
        original = gate._read
        with patch.object(gate, "_read", side_effect=lambda repo, relative: b"{}" if relative == gate.ATTEMPT else original(repo, relative)), self.assertRaises(ValueError):
            gate.validate()

    def predicate_mutation_rejected(self, claim_id: str, mutate) -> None:
        original = gate._read
        registry = copy.deepcopy(self.registry)
        artifact = json.loads(original(gate.REPO, gate.ATTEMPT))
        entry = next(row for row in registry["adjudications"] if row["claim_id"] == claim_id)
        observation = next(row for row in artifact["observations"] if row["id"] == entry["selector"]["observation_id"])
        mutate(observation)
        observation["stdout_sha256"] = hashlib.sha256(observation["stdout"].encode()).hexdigest()
        entry["selector"]["stdout_sha256"] = observation["stdout_sha256"]
        mutated = json.dumps(artifact).encode()
        registry["artifact"]["sha256"] = hashlib.sha256(mutated).hexdigest()
        def read(repo, relative):
            if relative == gate.REGISTRY:
                return json.dumps(registry).encode()
            if relative == gate.ATTEMPT:
                return mutated
            return original(repo, relative)
        with patch.object(gate, "_read", side_effect=read), patch.object(gate, "ATTEMPT_SHA256", hashlib.sha256(mutated).hexdigest()), self.assertRaises(ValueError):
            gate.validate()

    def test_rejects_each_required_runtime_predicate(self) -> None:
        cases = {
            "three-gpus": ("MCL-ead93c85c2ff4168", lambda row: row.update(stdout="\n".join(row["stdout"].splitlines()[:3]) + "\n")),
            "three-services": ("MCL-82fa8860fe3ef124", lambda row: row.update(stdout="active\nactive\nactive\n")),
            "non-xfs": ("MCL-2f9f572d80e1e8f9", lambda row: row.update(stdout=row["stdout"].replace(" xfs", " ext4"))),
            "accounting-off": ("MCL-aa383ba37f55f306", lambda row: row.update(stdout=row["stdout"].replace("Project quota state on /var/lib/docker (/dev/md127)\n  Accounting: ON", "Project quota state on /var/lib/docker (/dev/md127)\n  Accounting: OFF"))),
            "enforcement-off": ("MCL-aa383ba37f55f306", lambda row: row.update(stdout=row["stdout"].replace("Project quota state on /var/lib/docker (/dev/md127)\n  Accounting: ON\n  Enforcement: ON", "Project quota state on /var/lib/docker (/dev/md127)\n  Accounting: ON\n  Enforcement: OFF"))),
        }
        for name, (claim_id, mutate) in cases.items():
            with self.subTest(name=name):
                self.predicate_mutation_rejected(claim_id, mutate)

    def test_rejects_symlink_components_and_lexical_escape(self) -> None:
        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root, outside = Path(root_name), Path(outside_name)
            (outside / "artifact.json").write_text("outside")
            os.symlink(outside / "artifact.json", root / "leaf.json")
            os.symlink(outside, root / "dir-link")
            with self.assertRaises(ValueError):
                gate._read(root, "leaf.json")
            with self.assertRaises(ValueError):
                gate._read(root, "dir-link/artifact.json")
            with self.assertRaises(ValueError):
                gate._read(root, "../" + outside.name + "/artifact.json")

    def test_apply_is_atomic_on_first_pass_drift_and_rejects_reapplication(self) -> None:
        pages = [{"route": "/host/installing-host-software", "source_file": "host/installing-host-software.mdx",
                  "source_sha256": self.registry["adjudications"][0]["source_sha256"],
                  "claims": [copy.deepcopy(row["previous_claim"]) for row in self.registry["adjudications"]]}]
        pages[0]["claims"][-1]["text"] = "drift"
        before = copy.deepcopy(pages)
        with self.assertRaises(ValueError):
            gate.apply_current_h100x4_direct_postinstall_adjudications(pages)
        self.assertEqual(pages, before)
        pages[0]["claims"][-1] = copy.deepcopy(self.registry["adjudications"][-1]["previous_claim"])
        summaries = gate.apply_current_h100x4_direct_postinstall_adjudications(pages)
        self.assertEqual(len(summaries), 4)
        self.assertTrue(all(claim["status"] == "PASS" for claim in pages[0]["claims"]))
        with self.assertRaises(ValueError):
            gate.apply_current_h100x4_direct_postinstall_adjudications(pages)
        self.assertNotEqual(pages, before)

    def test_duplicate_target_id_is_rejected_without_mutation(self) -> None:
        pages = [{"route": "/host/installing-host-software", "source_file": "host/installing-host-software.mdx",
                  "source_sha256": self.registry["adjudications"][0]["source_sha256"],
                  "claims": [copy.deepcopy(row["previous_claim"]) for row in self.registry["adjudications"]]}]
        pages[0]["claims"].append(copy.deepcopy(pages[0]["claims"][0]))
        before = copy.deepcopy(pages)
        with self.assertRaises(ValueError):
            gate.apply_current_h100x4_direct_postinstall_adjudications(pages)
        self.assertEqual(pages, before)


if __name__ == "__main__":
    unittest.main()
