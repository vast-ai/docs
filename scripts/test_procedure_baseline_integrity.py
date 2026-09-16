#!/usr/bin/env python3
"""Fail-closed integrity regressions for the Host Docs P1 procedure baseline.

This suite is deliberately local-only. It loads the retained historical draft, confirms
that current-source drift is reported, then mutates deep copies of the draft. It does not execute any
documented Host procedure, network operation, credentialed action, or live test.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
from typing import Any, Callable


SCRIPT_PATH = Path(__file__).resolve().with_name("assemble_procedure_baseline.py")
REPO = SCRIPT_PATH.parent.parent
BASELINE_PATH = REPO / "verification" / "procedure-baseline-p1.json"


def load_assembler() -> Any:
    spec = importlib.util.spec_from_file_location(
        "host_docs_procedure_baseline_assembler", SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import assembler from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ASSEMBLER = load_assembler()


def reseal(baseline: dict[str, Any]) -> None:
    """Recompute the immutable-plan seal after a test mutation.

    Every rejection test uses this helper so a stale digest cannot be the sole reason
    that the validator rejects a forged record.
    """

    payload = ASSEMBLER.plan_identity_payload(baseline)
    digest = ASSEMBLER.sha256_text(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    baseline["plan_baseline_sha256"] = digest
    state_label = {
        "DRAFT_NOT_FROZEN": "DRAFT",
        "FROZEN_P1": "FROZEN",
    }.get(baseline.get("state"), "INVALID")
    target = str(baseline.get("source_identity", {}).get("docs_target_revision", ""))
    baseline["baseline_id"] = (
        f"P1-{state_label}-{target[:12]}-{digest[:12]}"
    )


class ProcedureBaselineIntegrityTests(unittest.TestCase):
    """Mutation tests for lifecycle, schema, traceability, privacy, and freeze gates."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = ASSEMBLER.load_json(BASELINE_PATH)

    def rejected_copy(
        self,
        mutation: Callable[[dict[str, Any]], None],
        expected_errors: tuple[str, ...],
        *,
        repository_aware: bool = False,
    ) -> list[str]:
        candidate = copy.deepcopy(self.baseline)
        mutation(candidate)
        reseal(candidate)
        errors = ASSEMBLER.validate(candidate, REPO if repository_aware else None)
        self.assertTrue(errors, "mutated and resealed baseline was unexpectedly accepted")
        self.assertNotIn(
            "plan baseline digest mismatch",
            errors,
            "mutation test was rejected only because it was not correctly resealed",
        )
        for expected in expected_errors:
            self.assertTrue(
                any(expected in error for error in errors),
                f"expected rejection containing {expected!r}; got: {errors[:12]!r}",
            )
        return errors

    def test_00_historical_canonical_draft_is_retained_and_reports_current_drift(self) -> None:
        self.assertEqual(self.baseline.get("state"), "DRAFT_NOT_FROZEN")
        errors = ASSEMBLER.validate(self.baseline, REPO)
        self.assertTrue(errors)
        self.assertIn("plan baseline digest mismatch", errors)
        self.assertTrue(
            any("current docs.json differs from the pinned target" in error for error in errors)
        )
        self.assertTrue(
            any("primary page source changed or is missing" in error for error in errors)
        )

    def test_01_arbitrary_lifecycle_state_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value.__setitem__("state", "RELEASE_CANDIDATE"),
            ("invalid baseline lifecycle state",),
        )

    def test_02_lifecycle_and_freeze_state_mismatch_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["freeze"].__setitem__("state", "FROZEN"),
            ("baseline lifecycle state and freeze state are inconsistent",),
        )

    def test_03_forged_evidence_package_completion_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["completion_and_acceptance"].__setitem__(
                "evidence_package_complete", True
            ),
            ("P1 baseline cannot claim evidence-package completion",),
        )

    def test_04_forged_acceptance_candidacy_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["completion_and_acceptance"].__setitem__(
                "target_acceptance_candidate", True
            ),
            ("P1 baseline cannot claim target-acceptance candidacy",),
        )

    def test_05_forged_human_acceptance_is_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["completion_and_acceptance"]["human_acceptance"] = {
                "owner": "Deterministic Test Owner",
                "role": "Test Role",
                "decision": "ACCEPTED",
                "date": "2030-01-01",
                "conditions": [],
                "closure_evidence": ["EVIDENCE-DUMMY-001"],
            }

        self.rejected_copy(
            mutate,
            ("P1 baseline must keep human acceptance explicitly undecided",),
        )

    def test_06_unknown_nested_page_field_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["pages"][0].__setitem__(
                "unreviewed_test_field", "deterministic-dummy"
            ),
            ("has unknown fields",),
        )

    def test_07_unknown_nested_claim_field_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["claims"][0].__setitem__(
                "unreviewed_test_field", "deterministic-dummy"
            ),
            ("has unknown fields",),
        )

    def test_08_empty_procedure_goal_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("goal", ""),
            (".goal must be nonempty",),
        )

    def test_09_empty_procedure_prerequisites_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("prerequisites", []),
            (".prerequisites must be a nonempty list",),
        )

    def test_10_empty_procedure_access_classes_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("access_classes", []),
            (".access_classes must be a nonempty list",),
        )

    def test_11_empty_procedure_safety_constraints_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__(
                "safety_constraints", []
            ),
            (".safety_constraints must be a nonempty list",),
        )

    def test_12_empty_procedure_expected_observables_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__(
                "expected_final_observables", []
            ),
            (".expected_final_observables must be a nonempty list",),
        )

    def test_13_empty_procedure_failure_behavior_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("failure_behavior", []),
            (".failure_behavior must be a nonempty list",),
        )

    def test_14_empty_procedure_limitations_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("limitations", []),
            (".limitations must be a nonempty list",),
        )

    def test_15_empty_procedure_cleanup_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__("cleanup", []),
            (".cleanup must be a nonempty list",),
        )

    def test_16_empty_procedure_redaction_rules_are_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__(
                "public_redaction_rules", []
            ),
            (".public_redaction_rules must be a nonempty list",),
        )

    def test_17_empty_step_instruction_is_rejected(self) -> None:
        step = self._first_step
        self.rejected_copy(
            lambda value: step(value).__setitem__("instruction_summary", ""),
            (".instruction_summary must be nonempty",),
        )

    def test_18_empty_step_expected_observables_are_rejected(self) -> None:
        step = self._first_step
        self.rejected_copy(
            lambda value: step(value).__setitem__("expected_observables", []),
            (".expected_observables must be a nonempty list",),
        )

    def test_19_empty_step_failure_behavior_is_rejected(self) -> None:
        step = self._first_step
        self.rejected_copy(
            lambda value: step(value).__setitem__("failure_behavior", []),
            (".failure_behavior must be a nonempty list",),
        )

    def test_20_changed_crosswalk_source_is_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["legacy_crosswalk"][0]["source"]["section"] = (
                "Deterministic Altered Section"
            )

        self.rejected_copy(
            mutate,
            ("is not a canonical claim projection for source",),
        )

    def test_21_changed_crosswalk_kind_is_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            row = value["legacy_crosswalk"][0]
            row["legacy_kind"] = (
                "command" if row["legacy_kind"] != "command" else "behavior-claim"
            )

        self.rejected_copy(
            mutate,
            ("is not a canonical claim projection for legacy_kind",),
        )

    def test_22_changed_crosswalk_rendered_route_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["legacy_crosswalk"][0]["rendered_context_refs"][
                0
            ].__setitem__("route", "/host/deterministic-dummy-route"),
            ("is not a canonical claim projection for rendered_context_refs",),
        )

    def test_23_changed_crosswalk_rationale_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["legacy_crosswalk"][0].__setitem__(
                "rationale", "Deterministic altered rationale."
            ),
            ("is not a canonical claim projection for rationale",),
        )

    def test_24_unrelated_existing_heading_is_rejected(self) -> None:
        target_step_id = "ACC-E01-S01"
        unrelated_heading = "How to accept the hosting agreement"

        source_text = (REPO / "host/account-hosting-agreement.mdx").read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            source_text,
            rf"(?m)^#+\s+{re.escape(unrelated_heading)}\s*$",
            "test fixture heading must exist in the source page",
        )

        def mutate(value: dict[str, Any]) -> None:
            procedure, step = self._find_step(value, target_step_id)
            page = next(
                item for item in value["pages"] if item["id"] == procedure["page_id"]
            )
            step["source_sections"] = [unrelated_heading]
            source_path = REPO / page["source_file"]
            step["source_context_validation"] = ASSEMBLER.source_context_validation(
                source_path, step
            )
            self.assertEqual(
                step["source_context_validation"]["heading_match"],
                "REVIEW_REQUIRED",
            )
            self.assertIn(
                unrelated_heading,
                step["source_context_validation"]["unmatched_headings"],
            )

        self.rejected_copy(
            mutate,
            ("source alignment is not recomputed from its source and step",),
            repository_aware=True,
        )

    def test_25_forged_target_commit_pin_is_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            forged = "0" * 40
            value["source_identity"]["docs_target_revision"] = forged
            value["source_identity"]["repository_head_at_assembly"] = forged

        self.rejected_copy(
            mutate,
            ("docs target revision is not available in the repository",),
            repository_aware=True,
        )

    def test_25b_existing_old_commit_cannot_retarget_current_sources(self) -> None:
        # Find the nearest real ancestor at which at least one declared primary
        # source exists but has different bytes.  An immediate ancestor whose
        # in-scope sources are byte-identical is a legitimate historical target,
        # so it must not be treated as a forgery merely because unrelated files
        # changed later.
        revisions = ASSEMBLER.git(
            REPO,
            "rev-list",
            "--first-parent",
            self.baseline["source_identity"]["docs_target_revision"],
        ).splitlines()[1:]
        old_commit = ""
        for revision in revisions:
            for page in self.baseline["pages"]:
                try:
                    historical_sha = ASSEMBLER.git_blob_sha256(
                        REPO, revision, page["source_file"]
                    )
                except RuntimeError:
                    continue
                if historical_sha != page["source_sha256"]:
                    old_commit = revision
                    break
            if old_commit:
                break
        self.assertTrue(old_commit, "no docs-bearing changed ancestor found")
        self.assertRegex(old_commit, r"^[0-9a-f]{40}$")
        self.assertNotEqual(
            old_commit,
            self.baseline["source_identity"]["docs_target_revision"],
        )

        def mutate(value: dict[str, Any]) -> None:
            value["source_identity"]["docs_target_revision"] = old_commit
            value["source_identity"]["repository_head_at_assembly"] = old_commit
            value["source_identity"]["repository_tree_at_assembly"] = ASSEMBLER.git(
                REPO, "rev-parse", old_commit + "^{tree}"
            )

        self.rejected_copy(
            mutate,
            ("primary page source is not bound to target commit",),
            repository_aware=True,
        )

    def test_26_forged_target_tree_pin_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["source_identity"].__setitem__(
                "repository_tree_at_assembly", "1" * 40
            ),
            ("assembly tree does not match the exact docs target commit",),
            repository_aware=True,
        )

    def test_27_forged_branch_pin_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["source_identity"].__setitem__(
                "branch", "deterministic-forged-review-branch"
            ),
            ("current checkout branch differs from the assembly branch",),
            repository_aware=True,
        )

    def test_28_forged_inventory_pins_are_rejected(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            inventory = value["source_identity"]["legacy_inventory"]
            inventory["sha256"] = "2" * 64
            inventory["source_revision"] = "3" * 40
            inventory["content_fingerprint"] = "sha256:" + "4" * 64

        self.rejected_copy(
            mutate,
            ("current legacy inventory differs from the pinned target",),
            repository_aware=True,
        )

    def test_29_raw_target_coordinate_in_free_text_is_rejected(self) -> None:
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__(
                "goal", "Verify machine_id: 424242 using dummy evidence only."
            ),
            ("canonical non-source evidence contains restricted coordinates",),
        )

    def test_30_key_like_value_in_free_text_is_rejected(self) -> None:
        dummy_key = "a" * 64
        self.rejected_copy(
            lambda value: value["procedures"][0].__setitem__(
                "goal", f"Deterministic dummy key value: {dummy_key}"
            ),
            ("canonical non-source evidence contains restricted coordinates",),
        )

    def test_31_forged_freeze_cannot_bypass_unresolved_gates(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["state"] = "FROZEN_P1"
            value["freeze"]["state"] = "FROZEN"
            value["freeze"]["reconciler"] = {
                "reviewer": "Deterministic Independent Reviewer",
                "role": "Test Reconciler",
                "reviewed_at": "2030-01-01T00:00:00Z",
                "evidence_refs": ["EVIDENCE-DUMMY-001"],
            }
            value["freeze"]["frozen_at"] = "2030-01-01T00:00:00Z"
            value["freeze"]["blocking_checks"] = []
            value["reconciliation"]["independent_second_pass"] = "COMPLETE"

        self.rejected_copy(
            mutate,
            (
                "has unresolved branch semantics",
                "frozen baseline retains unresolved safe executable forms",
                "frozen baseline has unreviewed primary rendered contexts",
                "frozen baseline has unreviewed support/render contracts",
            ),
        )

    @staticmethod
    def _first_step(value: dict[str, Any]) -> dict[str, Any]:
        return value["procedures"][0]["branches"][0]["steps"][0]

    @staticmethod
    def _find_step(
        value: dict[str, Any], step_id: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        for procedure in value["procedures"]:
            for branch in procedure["branches"]:
                for step in branch["steps"]:
                    if step["id"] == step_id:
                        return procedure, step
        raise AssertionError(f"missing deterministic step fixture: {step_id}")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ProcedureBaselineIntegrityTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(
        json.dumps(
            {
                "errors": len(result.errors),
                "failures": len(result.failures),
                "skipped": len(result.skipped),
                "status": "PASS" if result.wasSuccessful() else "FAIL",
                "tests_run": result.testsRun,
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
