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
from scripts.test_current_host_authority_scan import frozen_before_model, frozen_source_reader, historical_overlay

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
AUTHORITY_BASELINE = REPO / "verification/evidence/2026-09-09-host-authority-correction-attempt-01/pre-authority-current-host-docs-review.json"

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
        # Keep the immutable pre-connection registry separate from the public
        # package, whose connection projection is the current review model.
        global overlay
        overlay=historical_overlay()
        # This fixture is deliberately before the later Terms and jurisdiction
        # source edits.  Its retained frozen source bytes must select the
        # original dated path rather than a later phase whose pins expect the
        # live Tax or datacenter source bytes.
        (overlay.REPO/'verification/current-host-terms-binding.json').unlink(missing_ok=True)
        (overlay.REPO/'verification/current-host-jurisdiction.json').unlink(missing_ok=True)
        (overlay.REPO/'verification/current-host-review-cleanup.json').unlink(missing_ok=True)
        fixture_read=patch.object(transition,'_read',side_effect=frozen_source_reader(transition._read))
        fixture_read.start()
        cls.addClassCleanup(fixture_read.stop)
        package=frozen_before_model()
        transition_pages=copy.deepcopy(package['pages'])
        connection=json.loads((REPO/'verification/current-host-connection-adjudications.json').read_text())
        previous={e['claim_id']:e['previous_claim'] for e in connection['adjudications']}
        for page in transition_pages:
            page['claims']=[copy.deepcopy(previous.get(c['id'],c)) for c in page['claims']]
        cls.package = package
        cls.transition_pages = transition_pages
        cls.registry = json.loads(transition.output_bytes(transition_pages, REPO))

    def test_actual_model_retains_2005_prior_occurrences_and_eight_explicit_new_ids(self) -> None:
        claims = [claim for page in self.package["pages"] for claim in page["claims"]]
        self.assertEqual(len(claims), 2013)
        current = {claim["id"]: claim for claim in claims}
        self.assertNotIn("MCL-323c8fb8180f5f62", current)
        self.assertNotIn("MCL-dfebca7edafe9c59", current)
        self.assertEqual(current["COR-01-MCL-323c8fb8180f5f62-REPLACEMENT"]["status"], "PASS")
        self.assertEqual(current["COR-02-MCL-dfebca7edafe9c59-REPLACEMENT"]["status"], "UNVALIDATED")
        self.assertEqual([self.registry["rental_transition_adapter"]["claims"][n]["current_status"] for n in range(4)], ["PASS", "PASS", "PASS", "UNVALIDATED"])
        baseline = transition._baseline(REPO)
        self.assertEqual(sum(len(rows) for rows in self.registry["unmodified_claim_inventory"].values()),
                         sum(len(page["claims"]) - 1 for page in baseline.values()))
        self.assertEqual(sum(claim["status"] == "FAIL" for claim in claims), 151)
        self.assertFalse(any(claim["status"] == "FAIL" for page in self.package["pages"] if page["route"] in transition.OLD_FAILS for claim in page["claims"]))
        first = next(page for page in self.package["pages"] if page["route"] == "/host/first-24-hours")
        self.assertEqual(next(claim for claim in first["claims"] if claim["id"].startswith("COR-01"))["text"], "```bash\nvastai search offers 'machine_id=<machine_id> verified=any' --limit 200\n```")
        vm = next(page for page in self.package["pages"] if page["route"] == "/host/vms")
        self.assertEqual(next(claim for claim in vm["claims"] if claim["id"].startswith("COR-02"))["text"], "| `off` | VM support is disabled, a previous test failed, or the status helper could not read its configuration. |")

    def test_all_1993_unaffected_claim_proof_and_status_fields_match_pre_authority_baseline(self) -> None:
        frozen = json.loads(AUTHORITY_BASELINE.read_text())
        old_by_id = {claim["id"]: claim for page in frozen["pages"] for claim in page["claims"]}
        current_by_id = {claim["id"]: claim for page in self.package["pages"] for claim in page["claims"]
                         }
        authority_changes = {
            "MCL-508003945b6ef934", "MCL-c85a4e96752730ab", "MCL-437e58c77dcafecc", "MCL-943ba22ec56a356a",
            "MCL-805ef8a72833f2b8", "MCL-3cfe1a3c265f0223", "MCL-1a4146b033bd9b88", "MCL-f855ff5e92cfbec1",
            "MCL-181b0127498ba639", "MCL-ed68c47bda19e986", "MCL-8fe2020c0e7efe26", "MCL-399798a3c4946b5f",
        }
        added = {
            "AUTH-DATA-SECURITY-01", "CUR-2b941108a664d7e6", "CUR-5de4ad29d7f8a40f", "CUR-8f84c54760a2a448",
            "CUR-9a254ad0dbc63699", "CUR-c5c5c961094767f1", "CUR-d83c946956b9328a", "CUR-fac8a624c979a233",
        }
        self.assertEqual(len(old_by_id), 2005)
        self.assertTrue(set(old_by_id) <= set(current_by_id))
        self.assertEqual(set(current_by_id) - set(old_by_id), added)
        fields = ("text", "status", "classification", "required_evidence_types", "owner_role", "rationale",
                  "next_action", "evidence_refs", "source_refs")
        unchanged = set(old_by_id) - authority_changes
        self.assertEqual(len(unchanged), 1993)
        for claim_id in unchanged:
            prior = {field: old_by_id[claim_id][field] for field in fields}
            current = {field: current_by_id[claim_id][field] for field in fields}
            self.assertEqual(json.dumps(current, sort_keys=True, separators=(",", ":")),
                             json.dumps(prior, sort_keys=True, separators=(",", ":")), claim_id)
        for claim_id in authority_changes:
            self.assertNotEqual(
                {field: current_by_id[claim_id][field] for field in fields},
                {field: old_by_id[claim_id][field] for field in fields}, claim_id,
            )
        self.assertEqual({claim_id for claim_id in added if current_by_id[claim_id]["status"] == "PASS"},
                         {"AUTH-DATA-SECURITY-01"})
        failures = [claim for claim in current_by_id.values() if claim["status"] == "FAIL"]
        self.assertEqual(len(failures), 151)
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
        replacements = {claim["id"]: claim for page in self.transition_pages for claim in page["claims"] if claim["id"].startswith("COR-")}
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
        historical = overlay.STATIC_EVIDENCE.read_bytes()
        authority = overlay.AUTHORITY_STATIC_EVIDENCE.read_bytes()
        output = overlay.outputs()
        self.assertEqual(output[overlay.STATIC_EVIDENCE], historical)
        self.assertEqual(output[overlay.AUTHORITY_STATIC_EVIDENCE], authority)
        original = overlay.static_evidence
        def drift(package: dict) -> dict:
            value = original(package)
            value["method"] = "drift"
            return value
        with patch.object(overlay, "static_evidence", side_effect=drift), self.assertRaisesRegex(ValueError, "Authority static evidence differs"):
            overlay.outputs()


if __name__ == "__main__":
    unittest.main()
