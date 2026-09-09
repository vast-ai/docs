"""Adversarial checks for the exact two-defect source-transition adapter."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

spec = importlib.util.spec_from_file_location("transition", HERE / "current_two_defect_transition.py")
transition = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(transition)
overlay_spec = importlib.util.spec_from_file_location("overlay", HERE / "build_current_host_vv_overlay.py")
overlay = importlib.util.module_from_spec(overlay_spec)
assert overlay_spec and overlay_spec.loader
overlay_spec.loader.exec_module(overlay)


class TwoDefectTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Test the historical transition before the new connection projection;
        # keep every original 2,003-record equality assertion below intact.
        package, transition_pages = overlay._build_with_transition_projection()
        cls.package = {**package, "pages": transition_pages}
        cls.registry = json.loads(transition.output_bytes(cls.package["pages"], REPO))

    def test_actual_model_has_only_two_unvalidated_replacements_and_2003_prior_occurrences(self) -> None:
        claims = [claim for page in self.package["pages"] for claim in page["claims"]]
        self.assertEqual(len(claims), 2005)
        current = {claim["id"]: claim for claim in claims}
        self.assertNotIn("MCL-323c8fb8180f5f62", current)
        self.assertNotIn("MCL-dfebca7edafe9c59", current)
        self.assertEqual(current["COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"]["status"], "UNVALIDATED")
        self.assertEqual(current["COR-02-MCL-dfebca7edafe9c59-REPLACEMENT"]["status"], "UNVALIDATED")
        self.assertEqual([self.registry["rental_transition_adapter"]["claims"][n]["current_status"] for n in range(4)], ["PASS", "PASS", "PASS", "UNVALIDATED"])
        baseline = transition._baseline(REPO)
        self.assertEqual(sum(len(rows) for rows in self.registry["unmodified_claim_inventory"].values()),
                         sum(len(page["claims"]) - 1 for page in baseline.values()))
        self.assertEqual(sum(claim["status"] == "FAIL" for claim in claims), 149)
        self.assertFalse(any(claim["status"] == "FAIL" for page in self.package["pages"] if page["route"] in transition.OLD_FAILS for claim in page["claims"]))
        first = next(page for page in self.package["pages"] if page["route"] == "/host/first-24-hours")
        self.assertEqual(next(claim for claim in first["claims"] if claim["id"].startswith("COR-01"))["text"], "```bash\nvastai search offers 'machine_id=<machine_id> verified=any' --limit 200\n```")
        vm = next(page for page in self.package["pages"] if page["route"] == "/host/vms")
        self.assertEqual(next(claim for claim in vm["claims"] if claim["id"].startswith("COR-02"))["text"], "| `off` | VM support is disabled, a previous test failed, or the status helper could not read its configuration. |")

    def test_all_2003_unaffected_claims_match_baseline_except_exact_transition_metadata(self) -> None:
        baseline = transition._baseline(REPO)
        frozen = json.loads((REPO / transition.BASELINE).read_text())
        old_by_id = {claim["id"]: (page["route"], claim)
                     for page in frozen["pages"] for claim in page["claims"]
                     if claim["id"] not in transition.OLD_FAILS.values()}
        current_by_id = {claim["id"]: claim for page in self.package["pages"] for claim in page["claims"]
                         if not claim["id"].startswith("COR-")}
        self.assertEqual(len(old_by_id), 2003)
        self.assertEqual(set(current_by_id), set(old_by_id))
        for claim_id, (route, old) in old_by_id.items():
            expected = copy.deepcopy(old)
            if route in transition.OLD_FAILS:
                expected["coverage_state"] = "CHANGED"
                expected["history"] = {**expected["history"],
                    "carry_decision": "TWO_DEFECT_SOURCE_TRANSITION_EXACT_LITERAL",
                    "reason": expected["history"]["reason"] + " Exact unchanged literal and heading were rebound through the two-defect transition; no whole-page PASS transfer occurred."}
            self.assertEqual(current_by_id[claim_id], expected, claim_id)
        failures = [claim for claim in current_by_id.values() if claim["status"] == "FAIL"]
        self.assertEqual(len(failures), 149)
        self.assertTrue(all("AUTHORITATIVE_DOCUMENTATION_CITATION" in claim["required_evidence_types"] for claim in failures))

    def test_registry_pins_historical_fail_records_allowed_lines_and_exact_inventory(self) -> None:
        self.assertEqual(self.registry["baseline"]["model"]["sha256"], transition.BASELINE_SHA256)
        self.assertEqual(self.registry["baseline"]["historical_fail_registry"]["sha256"], transition.FINDINGS_SHA256)
        self.assertEqual([row["line"] for row in self.registry["allowed_changes"]["/host/first-24-hours"]], [59, 60])
        self.assertEqual([row["line"] for row in self.registry["allowed_changes"]["/host/vms"]], [48])
        for route, claim_id in transition.OLD_FAILS.items():
            record = self.registry["historical_fail_records"][route]
            self.assertEqual(record["old_fail_claim"]["id"], claim_id)
            self.assertEqual(record["old_fail_claim"]["status"], "FAIL")
            self.assertEqual(record["replacement"]["status"], "UNVALIDATED")
        self.assertTrue(all({"id", "text", "headings", "spans", "historical_claim_sha256"} <= set(item)
                            for rows in self.registry["unmodified_claim_inventory"].values() for item in rows))

    def test_old_whole_page_rental_gate_rejects_current_source_while_adapter_passes(self) -> None:
        rental_spec = importlib.util.spec_from_file_location("rental", HERE / "current_h100x4_rental_adjudications.py")
        rental = importlib.util.module_from_spec(rental_spec)
        assert rental_spec and rental_spec.loader
        rental_spec.loader.exec_module(rental)
        with self.assertRaisesRegex(ValueError, "source digest drift"):
            rental.validate(REPO)
        self.assertEqual(rental.validate_transition_baseline(REPO)["purpose"], "THREE_PASS_ONE_PARTIAL_FIRST_24_HOURS_RUNTIME_CLAIMS")
        replacements = {claim["id"]: claim for page in self.package["pages"] for claim in page["claims"] if claim["id"].startswith("COR-")}
        self.assertEqual([item["id"] for item in replacements["COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"]["evidence_refs"]], ["CLI-QUERY-SOURCE-INSPECTION-01", "CLI-QUERY-SEMANTIC-RETEST-01", "COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"])
        self.assertEqual([item["id"] for item in replacements["COR-02-MCL-dfebca7edafe9c59-REPLACEMENT"]["evidence_refs"]], ["VM-HELPER-SOURCE-RETEST-02", "VM-STATUS-01", "COR-02-MCL-dfebca7edafe9c59-REPLACEMENT"])

    def test_all_artifact_bytes_and_semantic_payload_are_pinned(self) -> None:
        original = transition._read
        semantic_path = f"{transition.ATTEMPT}/cli-query-semantic-retest-01.json"
        def appended(repo: Path, path: str) -> bytes:
            value = original(repo, path)
            return value + b"\n" if path == semantic_path else value
        with patch.object(transition, "_read", side_effect=appended), self.assertRaisesRegex(ValueError, "artifact digest drift"):
            transition._artifact_pins(REPO)
        payload = json.loads(original(REPO, semantic_path))
        stdout = json.loads(payload["stdout"])
        stdout["recognized_fields"] = ["machine_id"]
        payload["stdout"] = json.dumps(stdout)
        mutated = (json.dumps(payload, indent=2) + "\n").encode()
        def replaced(repo: Path, path: str) -> bytes:
            return mutated if path == semantic_path else original(repo, path)
        with patch.object(transition, "_read", side_effect=replaced), patch.dict(transition.EXPECTED_ARTIFACT_HASHES, {semantic_path: transition._sha(mutated)}), self.assertRaisesRegex(ValueError, "CLI semantic proof payload"):
            transition._cli_semantic_proof(REPO)

    def test_unapproved_literal_and_baseline_byte_drift_fail_closed(self) -> None:
        old_read = transition._read
        def altered(repo: Path, path: str) -> bytes:
            value = old_read(repo, path)
            if path == "host/first-24-hours.mdx":
                return value.replace(b"Create a test instance", b"Create a different instance", 1)
            return value
        changed = altered(REPO, "host/first-24-hours.mdx")
        with patch.object(transition, "_read", side_effect=altered), patch.dict(transition.CURRENT_PAGE_SHA256, {"/host/first-24-hours": transition._sha(changed)}), self.assertRaisesRegex(ValueError, "unapproved source change"):
            transition._sources(REPO, transition._baseline(REPO))
        def baseline_drift(repo: Path, path: str) -> bytes:
            value = old_read(repo, path)
            return value + b" " if path == transition.BASELINE else value
        with patch.object(transition, "_read", side_effect=baseline_drift), self.assertRaisesRegex(ValueError, "baseline model digest drift"):
            transition._baseline(REPO)
        def newline_drift(repo: Path, path: str) -> bytes:
            value = old_read(repo, path)
            return value + b"\n" if path == "host/vms.mdx" else value
        with patch.object(transition, "_read", side_effect=newline_drift), self.assertRaisesRegex(ValueError, "current page digest drift"):
            transition._sources(REPO, transition._baseline(REPO))

    def test_final_unmodified_or_replacement_drift_is_rejected(self) -> None:
        pages = copy.deepcopy(self.package["pages"])
        first = next(page for page in pages if page["route"] == "/host/first-24-hours")
        next(claim for claim in first["claims"] if claim["id"] == "MCL-7d10fc61bf9a884b")["text"] = "drift"
        with self.assertRaisesRegex(ValueError, "final transition claim set drift"):
            transition.output_bytes(pages, REPO)
        pages = copy.deepcopy(self.package["pages"])
        vm = next(page for page in pages if page["route"] == "/host/vms")
        next(claim for claim in vm["claims"] if claim["id"].startswith("COR-02"))["status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "final transition claim set drift"):
            transition.output_bytes(pages, REPO)

    def test_symlinked_parent_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "outside").mkdir()
            os.symlink(root / "outside", root / "linked")
            with self.assertRaisesRegex(ValueError, "contains symlink"):
                transition._read(root, "linked/file.json")

    def test_current_static_transition_attempt_cannot_be_overwritten(self) -> None:
        original = overlay.static_evidence
        def drift(package: dict) -> dict:
            value = original(package)
            value["method"] = "drift"
            return value
        with patch.object(overlay, "static_evidence", side_effect=drift), self.assertRaisesRegex(ValueError, "Two-defect static evidence differs"):
            overlay.outputs()


if __name__ == "__main__":
    unittest.main()
