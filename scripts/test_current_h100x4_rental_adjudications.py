"""Focused adversarial tests for the four-claim H100x4 rental adjudicator."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parent
FIXTURE_ROOT = Path(os.environ.get("H100X4_RENTAL_FIXTURE_ROOT", WORKTREE)).resolve()
spec = importlib.util.spec_from_file_location("rental", HERE / "current_h100x4_rental_adjudications.py")
rental = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(rental)


class RentalAdjudicationTests(unittest.TestCase):
    def fixture(self) -> tempfile.TemporaryDirectory[str]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "host").mkdir()
        (root / "verification").mkdir()
        # The original rental registry intentionally pins the whole pre-fix
        # page.  Its positive fixture must therefore use that immutable page;
        # the transition tests cover rejection of the edited current page.
        shutil.copy2(FIXTURE_ROOT / "verification/evidence/2026-09-09-host-two-defects-citation-review-attempt-01/transition-baseline/host/first-24-hours.pre-two-defects.mdx", root / "host/first-24-hours.mdx")
        shutil.copy2(FIXTURE_ROOT / "verification/current-host-docs-review.json", root / "verification/current-host-docs-review.json")
        shutil.copy2(WORKTREE / rental.REGISTRY, root / rental.REGISTRY)
        for relative in rental.ARTIFACTS.values():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(FIXTURE_ROOT / relative, target)
        registry = self.load(root, rental.REGISTRY)
        pinned = {entry["claim_id"]: entry["previous_claim"] for entry in registry["adjudications"]}
        model = self.load(root, "verification/current-host-docs-review.json")
        for page in model["pages"]:
            if page["route"] == "/host/first-24-hours":
                page["source_sha256"] = registry["adjudications"][0]["source_sha256"]
            for index, claim in enumerate(page["claims"]):
                if claim["id"] in pinned:
                    page["claims"][index] = copy.deepcopy(pinned[claim["id"]])
        self.dump(root, "verification/current-host-docs-review.json", model)
        return temp

    @staticmethod
    def load(root: Path, relative: str) -> dict:
        return json.loads((root / relative).read_text())

    @staticmethod
    def dump(root: Path, relative: str, value: dict) -> None:
        (root / relative).write_text(json.dumps(value, indent=2) + "\n")

    def artifact_mutation(self, root: Path, artifact_id: str, mutate) -> None:
        registry = self.load(root, rental.REGISTRY)
        artifact = next(item for item in registry["artifacts"] if item["id"] == artifact_id)
        payload = self.load(root, artifact["path"])
        mutate(payload)
        self.dump(root, artifact["path"], payload)
        artifact["sha256"] = hashlib.sha256((root / artifact["path"]).read_bytes()).hexdigest()
        self.dump(root, rental.REGISTRY, registry)

    def pages(self, root: Path) -> list[dict]:
        return self.load(root, "verification/current-host-docs-review.json")["pages"]

    def test_actual_shared_fixture_validates_and_applies_exactly_four(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            registry = rental.validate(root)
            pages = self.pages(root)
            summaries = rental.apply_current_h100x4_rental_adjudications(pages, root)
            self.assertEqual([item["scope"] for item in summaries], list(rental.TARGETS))
            changed = [claim for page in pages for claim in page["claims"] if claim["id"] in rental.TARGETS]
            self.assertEqual([claim["status"] for claim in changed], [rental.OUTCOMES[claim["id"]] for claim in changed])
            self.assertEqual(sum(claim["status"] == "PASS" for claim in changed), 3)
            destroy = next(claim for claim in changed if claim["id"] == "MCL-da591d84b7d08317")
            self.assertEqual(destroy["status"], "UNVALIDATED")
            self.assertIn("SSH/Jupyter troubleshooting", destroy["rationale"])
            self.assertEqual(registry["purpose"], "THREE_PASS_ONE_PARTIAL_FIRST_24_HOURS_RUNTIME_CLAIMS")
            for claim in changed:
                self.assertGreaterEqual(len(claim["evidence_refs"]), 3)
                self.assertEqual(claim["evidence_refs"][0]["artifact_ref"], rental.REGISTRY)

    def test_source_drift_and_artifact_digest_drift_fail_closed(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            with (root / "host/first-24-hours.mdx").open("a") as handle:
                handle.write("\n")
            with self.assertRaisesRegex(ValueError, "source digest drift"):
                rental.validate(root)
        with self.fixture() as temp:
            root = Path(temp)
            target = root / rental.ARTIFACTS["CREATE_RESPONSE"]
            target.write_text(target.read_text().replace("true", "false", 1))
            with self.assertRaisesRegex(ValueError, "artifact digest drift"):
                rental.validate(root)

    def test_duplicate_target_and_duplicate_json_key_fail_closed(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            pages = self.pages(root)
            page = next(page for page in pages if page["route"] == "/host/first-24-hours")
            page["claims"].append(copy.deepcopy(next(claim for claim in page["claims"] if claim["id"] == "MCL-fabfbad844e625b4")))
            with self.assertRaisesRegex(ValueError, "duplicate target claim id"):
                rental.apply_current_h100x4_rental_adjudications(pages, root)
        with self.fixture() as temp:
            root = Path(temp)
            path = root / rental.REGISTRY
            path.write_text(path.read_text().replace('"purpose": "THREE_PASS_ONE_PARTIAL_FIRST_24_HOURS_RUNTIME_CLAIMS",', '"purpose": "bad", "purpose": "THREE_PASS_ONE_PARTIAL_FIRST_24_HOURS_RUNTIME_CLAIMS",', 1))
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                rental.validate(root)

    def test_selected_proof_substitution_is_rejected(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            registry = self.load(root, rental.REGISTRY)
            registry["adjudications"][0]["artifact_ids"] = ["CLEANUP"]
            self.dump(root, rental.REGISTRY, registry)
            with self.assertRaisesRegex(ValueError, "claim binding drift"):
                rental.validate(root)

    def test_registry_outcome_substitution_is_rejected(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            registry = self.load(root, rental.REGISTRY)
            registry["adjudications"][3]["outcome_status"] = "PASS"
            self.dump(root, rental.REGISTRY, registry)
            with self.assertRaisesRegex(ValueError, "claim binding drift"):
                rental.validate(root)

    def test_wrong_machine_instance_gpu_and_label_each_fail_predicate(self) -> None:
        cases = [
            ("FRESH_OFFER", lambda item: item["offer"].update({"machine_id": 1})),
            ("CREATE_RESPONSE", lambda item: item["body"].update({"new_contract": 1})),
            ("INSTANCE_READ", lambda item: item["instance"].update({"num_gpus": 3})),
            ("INSTANCE_READ", lambda item: item["instance"].update({"label": "borrowed"})),
        ]
        for artifact_id, mutate in cases:
            with self.subTest(artifact_id=artifact_id):
                with self.fixture() as temp:
                    root = Path(temp)
                    self.artifact_mutation(root, artifact_id, mutate)
                    with self.assertRaises(ValueError):
                        rental.validate(root)

    def test_create_failure_destroying_other_id_absence_before_delete_and_failed_delete_reject(self) -> None:
        cases = [
            ("CREATE_RESPONSE", lambda item: item["body"].update({"success": False})),
            ("CLEANUP", lambda item: item["attempts"][0]["delete"].update({"endpoint": "/instances/1/"})),
            ("CLEANUP", lambda item: item["attempts"][1].update({"absent": False})),
            ("CLEANUP", lambda item: item["attempts"][0]["delete"].update({"http_status": 500})),
        ]
        for artifact_id, mutate in cases:
            with self.subTest(artifact_id=artifact_id):
                with self.fixture() as temp:
                    root = Path(temp)
                    self.artifact_mutation(root, artifact_id, mutate)
                    with self.assertRaises(ValueError):
                        rental.validate(root)

    def test_borrowed_previous_claim_rejected_and_rejected_apply_is_atomic(self) -> None:
        with self.fixture() as temp:
            root = Path(temp)
            registry = self.load(root, rental.REGISTRY)
            registry["adjudications"][0]["previous_claim"] = copy.deepcopy(registry["adjudications"][1]["previous_claim"])
            registry["adjudications"][0]["previous_claim_sha256"] = rental._canonical(registry["adjudications"][0]["previous_claim"])
            self.dump(root, rental.REGISTRY, registry)
            with self.assertRaisesRegex(ValueError, "claim binding drift"):
                rental.apply_current_h100x4_rental_adjudications(self.pages(root), root)
        with self.fixture() as temp:
            root = Path(temp)
            pages = self.pages(root)
            target = next(claim for page in pages for claim in page["claims"] if claim["id"] == "MCL-da591d84b7d08317")
            target["rationale"] = "drift"
            before = json.dumps(pages, sort_keys=True)
            with self.assertRaisesRegex(ValueError, "current claim drift"):
                rental.apply_current_h100x4_rental_adjudications(pages, root)
            self.assertEqual(json.dumps(pages, sort_keys=True), before)


if __name__ == "__main__":
    unittest.main()
