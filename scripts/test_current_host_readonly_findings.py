"""Fail-closed tests for the two exact current read-only documentation findings."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import current_host_readonly_findings as findings


REPO = Path(__file__).resolve().parents[1]


class CurrentReadonlyFindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live_read = findings._read
        def pre_transition_read(repo: Path, path: str) -> bytes:
            snapshots = {
                "host/first-24-hours.mdx": "verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/transition-baseline/host/first-24-hours.pre-two-defects.mdx",
                "host/vms.mdx": "verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/transition-baseline/host/vms.pre-two-defects.mdx",
            }
            return cls.live_read(repo, snapshots.get(path, path))
        # This legacy FAIL-only gate intentionally targets the immutable old
        # occurrence.  Keep it strict and test the edited current source as a
        # negative case instead of pretending the historical finding applies.
        findings._read = pre_transition_read
        cls.registry = findings.validate_current_readonly_findings(REPO)
        cls.pages = []
        for row in cls.registry["findings"]:
            occurrence = row["occurrence"]
            cls.pages.append({"route": occurrence["route"], "source_file": occurrence["source_file"],
                              "source_sha256": occurrence["source_sha256"], "claims": [copy.deepcopy(row["previous_claim"])]})

    @classmethod
    def tearDownClass(cls) -> None:
        findings._read = cls.live_read

    def test_edited_current_sources_are_rejected_by_the_old_findings_gate(self) -> None:
        with patch.object(findings, "_read", type(self).live_read), self.assertRaisesRegex(ValueError, "current page hash drift"):
            findings.validate_current_readonly_findings(REPO)

    def validate_registry(self, value: dict) -> None:
        original = findings._read
        def read(repo: Path, path: str) -> bytes:
            if path == findings.REGISTRY_PATH:
                return json.dumps(value).encode()
            return original(repo, path)
        with patch.object(findings, "_read", side_effect=read):
            findings.validate_current_readonly_findings(REPO)

    def test_positive_applies_only_the_two_preserved_original_claims_as_fail(self) -> None:
        pages = copy.deepcopy(self.pages)
        unrelated = copy.deepcopy(pages[0]["claims"][0])
        unrelated["id"] = "UNRELATED"
        pages.append({"route": "/unrelated", "claims": [unrelated]})
        before = copy.deepcopy(pages)
        summaries = findings.apply_current_readonly_findings(pages, REPO)
        self.assertEqual(len(summaries), 2)
        self.assertEqual(pages[-1], before[-1])
        for page, original in zip(pages[:2], before[:2]):
            claim, prior = page["claims"][0], original["claims"][0]
            self.assertEqual(set(claim), set(prior))
            self.assertEqual(set(claim["history"]), set(prior["history"]))
            self.assertEqual(claim["status"], "FAIL")
            self.assertEqual(claim["classification"], "CONFIRMED_DOCUMENTATION_DEFECT")
            self.assertEqual(claim["required_evidence_types"], ["CANONICAL_IMPLEMENTATION_SOURCE"])
            self.assertEqual(claim["history"]["carry_decision"], findings.DECISION)
            self.assertIn("full original claim retained", claim["history"]["reason"])
            self.assertEqual(claim["id"], prior["id"])
            self.assertEqual(claim["text"], prior["text"])
            self.assertEqual(claim["spans"], prior["spans"])
        self.assertEqual(pages[1]["claims"][0]["source_refs"][0]["repository"], "vast-ai/vast-cli")
        self.assertEqual(pages[0]["claims"][0]["source_refs"], [])
        with self.assertRaises(ValueError):
            findings.apply_current_readonly_findings(pages, REPO)

    def test_registry_rejects_extra_target_promotion_lane_or_unbounded_meaning(self) -> None:
        mutations = {
            "extra_target": lambda r: r["findings"].append(copy.deepcopy(r["findings"][0])),
            "swapped_target": lambda r: r["findings"][0].update(claim_id="OTHER"),
            "pass": lambda r: r["findings"][0].update(status="PASS"),
            "blocked": lambda r: r["findings"][0].update(status="BLOCKED"),
            "runtime_lane": lambda r: r["findings"][0].update(required_evidence_types=["RUNTIME_OR_UI_OBSERVATION"]),
            "extra_lane": lambda r: r["findings"][0]["required_evidence_types"].append("RUNTIME_OR_UI_OBSERVATION"),
            "approval_claim": lambda r: r.update(limits="Human approval is recorded."),
            "wrong_occurrence": lambda r: r["findings"][0]["occurrence"].update(start=49),
            "prior_promotion": lambda r: r["findings"][0]["previous_claim"].update(status="PASS"),
            "prior_hash": lambda r: r["findings"][0].update(previous_claim_sha256="0" * 64),
            "extra_field": lambda r: r["findings"][0].update(all_claims_approved=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.registry)
                mutate(value)
                with self.assertRaises(ValueError):
                    self.validate_registry(value)

    def test_evidence_allowlists_and_bytes_are_required(self) -> None:
        mutations = {
            "vm_missing": lambda r: r["findings"][0]["evidence"].pop(),
            "vm_extra": lambda r: r["findings"][0]["evidence"].append(copy.deepcopy(r["findings"][0]["evidence"][0])),
            "vm_digest": lambda r: r["findings"][0]["evidence"][0].update(sha256="0" * 64),
            "cli_substitution": lambda r: r["findings"][1]["evidence"][0].update(artifact_ref=findings.VM_STATUS),
            "cli_digest": lambda r: r["findings"][1]["evidence"][0].update(sha256="0" * 64),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                value = copy.deepcopy(self.registry)
                mutate(value)
                with self.assertRaises(ValueError):
                    self.validate_registry(value)
        original = findings._read
        for target in (findings.VM_SOURCE, findings.VM_STATUS, findings.CLI_CAPTURE):
            with self.subTest(byte_drift=target):
                def read(repo: Path, path: str) -> bytes:
                    value = original(repo, path)
                    return value + b"\n" if path == target else value
                with patch.object(findings, "_read", side_effect=read), self.assertRaises(ValueError):
                    findings.validate_current_readonly_findings(REPO)

    def test_validation_requires_no_workstation_checkout_or_subprocess(self) -> None:
        # The full-file digest and source provenance are immutable retained pins
        # in the docs repository. Validation must work in any review checkout.
        source = Path(findings.__file__).read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("/Users/", source)
        with patch("subprocess.check_output", side_effect=AssertionError("must not execute")):
            findings.validate_current_readonly_findings(REPO)

    def test_apply_is_atomic_when_page_or_claim_identity_has_drifted(self) -> None:
        mutations = {
            "missing": lambda p: p.pop(),
            "duplicate": lambda p: p.append(copy.deepcopy(p[0])),
            "page": lambda p: p[0].update(route="/host/other"),
            "claim_status": lambda p: p[0]["claims"][0].update(status="FAIL"),
            "claim_text": lambda p: p[1]["claims"][0].update(text="changed"),
            "claim_evidence": lambda p: p[1]["claims"][0]["evidence_refs"].append({"id": "drift"}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                pages = copy.deepcopy(self.pages)
                mutate(pages)
                before = copy.deepcopy(pages)
                with self.assertRaises(ValueError):
                    findings.apply_current_readonly_findings(pages, REPO)
                self.assertEqual(pages, before)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            findings._json(b'{"claim_id":"first", "claim_id":"second"}')


if __name__ == "__main__":
    unittest.main()
