#!/usr/bin/env python3
"""Repository-local regressions for the active 40-page Host V&V package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest


REPO = Path(__file__).resolve().parents[1]
SETS = json.loads((REPO / "verification/host-docs-test-sets.json").read_text())
RESULTS = json.loads((REPO / "verification/host-docs-test-results.json").read_text())


class ReconciledHostVvTests(unittest.TestCase):
    @staticmethod
    def _claim_source_text(claim: dict) -> str:
        lines = (REPO / claim["scope"]["source_file"]).read_text().splitlines()
        return "\n".join(
            "\n".join(lines[span["start"] - 1:span["end"]])
            for span in claim["scope"]["source_spans"]
        )

    def test_all_attempt_artifacts_are_manifest_bound(self) -> None:
        manifest = {row["path"]: row for row in RESULTS["evidence_artifact_manifest"]}
        self.assertEqual(len(manifest), len({row["evidence_ref"] for row in RESULTS["attempts"]}))
        for attempt in RESULTS["attempts"]:
            path = attempt["evidence_ref"]
            self.assertIn(path, manifest)
            artifact = REPO / path
            self.assertTrue(artifact.is_file())
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertEqual(attempt["evidence_ref_sha256"], digest)
            self.assertEqual(manifest[path]["sha256"], digest)
        baseline = next(
            row for row in RESULTS["attempts"]
            if row["attempt_id"] == "ATTEMPT-2026-09-03-HOST-WORKING-TREE-BASELINE-01"
        )
        self.assertEqual(baseline["summary"]["retained_lines"], 254)
        public_baseline = REPO / baseline["evidence_ref"]
        self.assertEqual(len(public_baseline.read_text().splitlines()), 254)
        source = SETS["source"]
        self.assertNotIn("reconciled_docs_head", source)
        self.assertNotIn("reconciled_docs_head_tree", source)
        self.assertEqual(
            source["reconciled_identity_method"],
            "PRIMARY_AND_RENDERED_SOURCE_SHA256_PLUS_FINAL_GIT_TREE",
        )
        for field in ("reconciled_primary_source_sha256", "reconciled_rendered_source_sha256"):
            self.assertRegex(source[field], r"^[0-9a-f]{64}$")
        evidence_dir = REPO / "verification/evidence/2026-09-02-host-self-test-attempt-01"
        plan = (evidence_dir / "plan.md").read_text()
        result = (evidence_dir / "result.md").read_text()
        for text in (plan, result):
            self.assertIn("<authorized_machine_id>", text)
            self.assertNotRegex(
                text,
                r"(?m)^- Target: authorized Host machine `\d+`$",
            )
        self.assertIn(
            "534f608dd342aba81707ebce710f2f51a72ffaf15e52c275a1e16e2e383dd734",
            plan,
        )
        self.assertIn(
            "79cb9a4db6dbb0601bf0a40586fc374782dd011d1384623040477c8181b6b78b",
            result,
        )
        install_plan = (
            REPO / "verification/evidence/2026-09-02-cli-install-attempt-02/plan.md"
        ).read_text()
        self.assertIn("<disposable-venv>/bin/vastai", install_plan)
        self.assertNotIn("/private/tmp/", install_plan)
        self.assertIn(
            "b55f056538b287ccd6a8057a76fde433221321283c535cc5f54d177befd49dda",
            install_plan,
        )
        repository_rebase = (
            REPO
            / "verification/evidence/2026-09-03-host-repository-rebase-01/result.md"
        ).read_text()
        self.assertIn("browser-review-status-empty-retest-01.png", repository_rebase)
        self.assertIn(
            "2b913ec083af972fa6345f4ac021e0b5d35c3804ac76e8ae0f0e39fbae404ab0",
            repository_rebase,
        )
        self.assertNotIn("[`browser-review-status.png`]", repository_rebase)
        self.assertTrue((
            REPO
            / "verification/evidence/2026-09-03-host-repository-rebase-01/"
              "browser-review-status-empty-retest-01.png"
        ).is_file())

    def test_retained_p1_baseline_is_unchanged(self) -> None:
        baseline = REPO / "verification/procedure-baseline-p1.json"
        self.assertEqual(
            hashlib.sha256(baseline.read_bytes()).hexdigest(),
            "45fa27a8f6570e9cf8df15d486ac89ccf2c1420d8e38709150bd2a08ae647a38",
        )

    def test_self_test_commands_are_owned_by_their_exact_action_steps(self) -> None:
        page = next(
            row for row in SETS["pages"] if row["route"] == "/host/how-to-self-test"
        )
        test_set = next(
            row for row in page["test_sets"] if row["test_set_id"] == "TS-ST-E01"
        )
        steps = {
            (branch["branch_id"], step["step_id"]): step
            for branch in test_set["branches"]
            for step in branch["steps"]
        }
        expected = {
            "CLM-b3cd48630e5f2b0c": (
                "ST-E01-normal", "ST-E01-normal-s01", "setup",
                "Before You Run It", 29, 29, "FAIL",
            ),
            "CLM-3ba3b25f5c3ddac1": (
                "ST-E01-normal", "ST-E01-normal-s03", "action",
                "Run The Test", 79, 79, "UNVALIDATED",
            ),
            "CLM-3fa5d5948b34fc6a": (
                "ST-E01-bundle-dir", "ST-E01-bundle-dir-s02", "action",
                "Run The Test", 85, 86, "BLOCKED",
            ),
        }
        found = {}
        for (branch_id, step_id), step in steps.items():
            for command in step["commands"]:
                if command["command_id"] not in expected:
                    continue
                self.assertNotIn(command["command_id"], found)
                found[command["command_id"]] = (branch_id, step_id)
                exp_branch, exp_step, role, section, start, end, status = expected[
                    command["command_id"]
                ]
                self.assertEqual((branch_id, step_id), (exp_branch, exp_step))
                self.assertEqual(step["role"], role)
                self.assertEqual(command["source"]["section"], section)
                self.assertEqual(command["source"]["line_start"], start)
                self.assertEqual(command["source"]["line_end"], end)
                self.assertEqual(command["treatment"], "EXECUTABLE_TEMPLATE_REQUIRED")
                self.assertEqual(command["execution_status"], status)
                self.assertTrue(any(
                    span["start"] <= start and span["end"] >= end
                    for span in step["source_lines"]
                ))
        self.assertEqual(set(found), set(expected))
        checkpoint = steps[("ST-E01-normal", "ST-E01-normal-s02")]
        self.assertEqual(checkpoint["commands"], [])
        self.assertEqual(checkpoint["source_sections"], ["What Self-Test Checks"])
        self.assertEqual(checkpoint["source_lines"], [{"start": 33, "end": 64}])
        self.assertEqual(checkpoint["execution_classification"], "MANUAL_OR_CONTEXT")
        self.assertEqual(checkpoint["blocker_ids"], [])
        self.assertEqual(SETS["counts"]["command_carriers"], 179)
        self.assertEqual(SETS["counts"]["command_bearing_steps"], 121)

    def test_self_test_topology_correction_preserves_history_and_rekeys_indexes(self) -> None:
        correction_attempt = "ATTEMPT-2026-09-03-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"
        correction_evidence = "EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"
        attempts = {row["attempt_id"]: row for row in RESULTS["attempts"]}
        self.assertIn(correction_attempt, attempts)
        self.assertEqual(attempts[correction_attempt]["status"], "PASS")
        self.assertEqual(attempts[correction_attempt]["summary"], {
            "command_carriers_relocated": 3,
            "current_projection_command_keys_rekeyed": 3,
            "historical_procedure_bindings_rekeyed": 9,
            "affected_attempt_accounting_chains": 5,
            "status_reclassification_targets": 4,
            "status_basis_rebound_targets": 7,
            "new_host_executions": 0,
            "new_command_results": 0,
        })
        expected_chains = {
            "ATTEMPT-2026-09-01-HOST-COMMAND-ASSESSMENT-01": correction_attempt,
            "ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-01":
                "ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-02",
            "ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-02": correction_attempt,
            "ATTEMPT-2026-09-02-HOST-SELF-TEST-01": correction_attempt,
            "ATTEMPT-2026-09-02-CLI-SET-API-KEY-PERMISSIONS-01": correction_attempt,
            "ATTEMPT-2026-09-03-HOST-REPOSITORY-REBASE-01": correction_attempt,
        }
        for attempt_id, successor in expected_chains.items():
            self.assertEqual(attempts[attempt_id]["accounting_corrected_by"], successor)

        expected_locations = {
            "CLM-b3cd48630e5f2b0c": ("ST-E01-normal", "ST-E01-normal-s01"),
            "CLM-3ba3b25f5c3ddac1": ("ST-E01-normal", "ST-E01-normal-s03"),
            "CLM-3fa5d5948b34fc6a": ("ST-E01-bundle-dir", "ST-E01-bundle-dir-s02"),
        }
        expected_binding_counts = {
            "EV-HOST-COMMAND-ASSESSMENT-01": 3,
            "EV-HOST-CURRENT-RECONCILIATION-01": 3,
            "EV-HOST-SELF-TEST-PROCEDURE-01": 1,
            "EV-CLI-SET-API-KEY-PERMISSIONS-PROCEDURE-01": 1,
            "EV-HOST-REPOSITORY-LOCAL-STATUS-REBASE-01": 1,
        }
        actual_counts = {evidence_id: 0 for evidence_id in expected_binding_counts}
        retained_statuses = {evidence_id: [] for evidence_id in expected_binding_counts}
        for result in RESULTS["procedure_results"]:
            if result["evidence_id"] in {
                correction_evidence,
                "EV-HOST-COMMAND-PROOF-REVIEWER-01",
                "EV-HOST-COMMAND-PROOF-REVIEWER-02",
            }:
                continue
            for target in result["targets"]:
                command_id = target["target"].get("command_id")
                if command_id not in expected_locations:
                    continue
                self.assertIn(result["evidence_id"], expected_binding_counts)
                actual_counts[result["evidence_id"]] += 1
                retained_statuses[result["evidence_id"]].append(
                    (command_id, target["vv_status"])
                )
                self.assertEqual(
                    (target["target"]["branch_id"], target["target"]["step_id"]),
                    expected_locations[command_id],
                )
        self.assertEqual(actual_counts, expected_binding_counts)
        self.assertEqual(
            {key: sorted(value) for key, value in retained_statuses.items()},
            {
                "EV-HOST-COMMAND-ASSESSMENT-01": sorted([
                    ("CLM-b3cd48630e5f2b0c", "UNVALIDATED"),
                    ("CLM-3ba3b25f5c3ddac1", "UNVALIDATED"),
                    ("CLM-3fa5d5948b34fc6a", "UNVALIDATED"),
                ]),
                "EV-HOST-CURRENT-RECONCILIATION-01": sorted([
                    ("CLM-b3cd48630e5f2b0c", "BLOCKED"),
                    ("CLM-3ba3b25f5c3ddac1", "BLOCKED"),
                    ("CLM-3fa5d5948b34fc6a", "BLOCKED"),
                ]),
                "EV-HOST-SELF-TEST-PROCEDURE-01": [
                    ("CLM-3fa5d5948b34fc6a", "BLOCKED"),
                ],
                "EV-CLI-SET-API-KEY-PERMISSIONS-PROCEDURE-01": [
                    ("CLM-b3cd48630e5f2b0c", "FAIL"),
                ],
                "EV-HOST-REPOSITORY-LOCAL-STATUS-REBASE-01": [
                    ("CLM-3ba3b25f5c3ddac1", "UNVALIDATED"),
                ],
            },
        )

        correction = next(
            row for row in RESULTS["procedure_results"]
            if row["evidence_id"] == correction_evidence
        )
        self.assertEqual(len(correction["targets"]), 11)
        roles = [row["basis_role"] for row in correction["targets"]]
        self.assertEqual(roles.count("STATUS_RECLASSIFICATION"), 4)
        self.assertEqual(roles.count("STATUS_BASIS_REBOUND"), 7)

    def test_self_test_topology_rollups_and_command_proof_boundaries(self) -> None:
        fields = {
            "PAGE": ("page_id",),
            "TEST_SET": ("page_id", "test_set_id"),
            "BRANCH": ("page_id", "test_set_id", "branch_id"),
            "STEP": ("page_id", "test_set_id", "branch_id", "step_id"),
            "COMMAND": (
                "page_id", "test_set_id", "branch_id", "step_id", "command_id",
            ),
        }
        projection = {
            (row["level"], *(row["target"][field] for field in fields[row["level"]])): row
            for row in RESULTS["current_status_projection"]["records"]
        }
        prefix = ("PAGE-host-how-to-self-test", "TS-ST-E01")
        expected_statuses = {
            ("PAGE", prefix[0]): "FAIL",
            ("TEST_SET", *prefix): "FAIL",
            ("BRANCH", *prefix, "ST-E01-normal"): "FAIL",
            ("BRANCH", *prefix, "ST-E01-bundle-dir"): "BLOCKED",
            ("STEP", *prefix, "ST-E01-normal", "ST-E01-normal-s01"): "FAIL",
            ("STEP", *prefix, "ST-E01-normal", "ST-E01-normal-s02"): "UNVALIDATED",
            ("STEP", *prefix, "ST-E01-normal", "ST-E01-normal-s03"): "UNVALIDATED",
            ("STEP", *prefix, "ST-E01-bundle-dir", "ST-E01-bundle-dir-s02"): "BLOCKED",
            ("COMMAND", *prefix, "ST-E01-normal", "ST-E01-normal-s01",
             "CLM-b3cd48630e5f2b0c"): "FAIL",
            ("COMMAND", *prefix, "ST-E01-normal", "ST-E01-normal-s03",
             "CLM-3ba3b25f5c3ddac1"): "UNVALIDATED",
            ("COMMAND", *prefix, "ST-E01-bundle-dir", "ST-E01-bundle-dir-s02",
             "CLM-3fa5d5948b34fc6a"): "BLOCKED",
        }
        for key, status in expected_statuses.items():
            self.assertEqual(projection[key]["current_status"], status, key)

        self.assertEqual(RESULTS["current_status_projection"]["counts"]["statuses"], {
            "PASS": 128,
            "FAIL": 5,
            "BLOCKED": 97,
            "UNVALIDATED": 747,
            "NOT_APPLICABLE": 27,
        })
        set_key = projection[(
            "COMMAND", *prefix, "ST-E01-normal", "ST-E01-normal-s01",
            "CLM-b3cd48630e5f2b0c",
        )]
        normal = projection[(
            "COMMAND", *prefix, "ST-E01-normal", "ST-E01-normal-s03",
            "CLM-3ba3b25f5c3ddac1",
        )]
        bundle = projection[(
            "COMMAND", *prefix, "ST-E01-bundle-dir", "ST-E01-bundle-dir-s02",
            "CLM-3fa5d5948b34fc6a",
        )]
        self.assertEqual(set_key["evidence_ids"], ["EV-CLI-SET-API-KEY-PERMISSIONS-01"])
        self.assertEqual(normal["evidence_ids"], ["EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"])
        self.assertEqual(bundle["evidence_ids"], ["EV-HOST-SELF-TEST-01"])
        self.assertEqual(normal["status_basis"]["basis_kind"], "NO_CLAIM_SUITABLE_EVIDENCE")
        self.assertEqual(bundle["status_basis"]["basis_kind"], "UNAVAILABLE_PREREQUISITE")
        self.assertIn("Host-owner credential", bundle["status_basis"]["next_action"])
        self.assertIn("numeric exit status", bundle["status_basis"]["next_action"])
        self.assertNotIn(
            "unavailable_prerequisite.components",
            bundle["status_basis"]["next_action"],
        )
        for row in projection.values():
            if row["current_status"] != "BLOCKED":
                continue
            self.assertNotIn(
                "unavailable_prerequisite.components",
                row["status_basis"]["next_action"],
                row["target"],
            )
        vm_reboot = projection[(
            "COMMAND", "PAGE-host-vms", "TS-VM-E02", "VM-E02-B-intel",
            "VM-E02-S02", "CLM-1e2f077efd167bfd",
        )]
        self.assertIn("Explicit operator authorization", vm_reboot["status_basis"]["next_action"])
        self.assertIn("controlled disposable or idle VM-capable Host", vm_reboot["status_basis"]["next_action"])

    def test_exact_command_evidence_contracts_name_missing_runtime_work(self) -> None:
        fields = {
            "PAGE": ("page_id",),
            "TEST_SET": ("page_id", "test_set_id"),
            "BRANCH": ("page_id", "test_set_id", "branch_id"),
            "STEP": ("page_id", "test_set_id", "branch_id", "step_id"),
            "COMMAND": (
                "page_id", "test_set_id", "branch_id", "step_id", "command_id",
            ),
        }
        projection = {
            (row["level"], *(row["target"][field] for field in fields[row["level"]])): row
            for row in RESULTS["current_status_projection"]["records"]
        }
        plain = projection[(
            "COMMAND", "PAGE-host-how-to-self-test", "TS-ST-E01",
            "ST-E01-normal", "ST-E01-normal-s03", "CLM-3ba3b25f5c3ddac1",
        )]
        vm_off = projection[(
            "COMMAND", "PAGE-host-vms", "TS-VM-E01", "VM-E01-B-disable",
            "VM-E01-S02", "CLM-9cba75bbdc780804",
        )]

        self.assertEqual(plain["current_status"], "UNVALIDATED")
        self.assertEqual(
            plain["attempt_id"],
            "ATTEMPT-2026-09-03-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01",
        )
        self.assertEqual(
            plain["evidence_ids"],
            ["EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"],
        )
        self.assertEqual(
            plain["status_basis"]["required_evidence_types"],
            ["RUNTIME_OR_UI_OBSERVATION"],
        )
        self.assertIn("representative idle listed Host", plain["status_basis"]["next_action"])
        self.assertIn("without `--support-bundle-dir`", plain["status_basis"]["next_action"])
        self.assertIn("verified cleanup", plain["status_basis"]["next_action"])
        cli_checks = json.loads((REPO / "host-docs-cli-command-check.json").read_text())
        plain_signature = next(
            row for row in cli_checks["records"] if row["id"] == "cli-4caeeed44e"
        )
        self.assertEqual(plain_signature["status"], "pass")

        self.assertEqual(vm_off["current_status"], "UNVALIDATED")
        self.assertEqual(
            vm_off["attempt_id"],
            "ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-01",
        )
        self.assertEqual(vm_off["evidence_ids"], ["EV-HOST-CURRENT-RECONCILIATION-01"])
        self.assertEqual(
            vm_off["status_basis"]["required_evidence_types"],
            ["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"],
        )
        self.assertIn("immutable canonical helper source", vm_off["status_basis"]["next_action"])
        self.assertIn(
            "`check → off → check → on -f → check`",
            vm_off["status_basis"]["next_action"],
        )
        self.assertIn("safely restored", vm_off["status_basis"]["next_action"])

    def test_command_proof_reviewer_attempts_are_registered_without_status_promotion(self) -> None:
        attempt_ids = (
            "ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-01",
            "ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-02",
            "ATTEMPT-2026-09-04-HOST-PR-READY-PACKAGING-01",
        )
        evidence_ids = (
            "EV-HOST-COMMAND-PROOF-REVIEWER-01",
            "EV-HOST-COMMAND-PROOF-REVIEWER-02",
            "EV-HOST-PR-READY-PACKAGING-01",
        )
        evidence_refs = (
            "verification/evidence/2026-09-03-host-command-proof-reviewer-attempt-01/result.md",
            "verification/evidence/2026-09-03-host-command-proof-reviewer-attempt-02/result.md",
            "verification/evidence/2026-09-04-host-pr-ready-packaging-attempt-01/result.md",
        )
        attempt_rows = [
            row for row in RESULTS["attempts"]
            if row["attempt_id"] in attempt_ids
        ]
        manifest_rows = [
            row for row in RESULTS["evidence_artifact_manifest"]
            if row["path"] in evidence_refs
        ]
        self.assertEqual(
            {attempt_id: sum(
                row["attempt_id"] == attempt_id for row in attempt_rows
            ) for attempt_id in attempt_ids},
            {attempt_id: 1 for attempt_id in attempt_ids},
        )
        self.assertEqual(
            {evidence_ref: sum(
                row["path"] == evidence_ref for row in manifest_rows
            ) for evidence_ref in evidence_refs},
            {evidence_ref: 1 for evidence_ref in evidence_refs},
        )
        self.assertEqual(
            {evidence_ref: sum(
                row["evidence_ref"] == evidence_ref for row in attempt_rows
            ) for evidence_ref in evidence_refs},
            {evidence_ref: 1 for evidence_ref in evidence_refs},
        )
        attempts = {row["attempt_id"]: row for row in attempt_rows}
        manifest = {row["path"]: row for row in manifest_rows}
        for attempt_id, evidence_ref in zip(attempt_ids, evidence_refs):
            attempt = attempts[attempt_id]
            artifact = REPO / evidence_ref
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertEqual(attempt["status"], "PASS")
            self.assertEqual(attempt["execution_state"], "EXECUTED")
            self.assertEqual(attempt["evidence_ref"], evidence_ref)
            self.assertEqual(attempt["evidence_ref_sha256"], digest)
            self.assertEqual(manifest[evidence_ref], {
                "path": evidence_ref,
                "sha256": digest,
                "role": "RETAINED_ATTEMPT_EVIDENCE",
            })
        self.assertEqual(
            attempts[attempt_ids[0]]["qualification_superseded_by"],
            attempt_ids[1],
        )
        self.assertEqual(
            attempts[attempt_ids[1]]["qualification_superseded_by"],
            attempt_ids[2],
        )
        self.assertEqual(attempts[attempt_ids[0]]["summary"]["completed_at"],
                         "2026-09-03T20:27:25Z")
        self.assertEqual(attempts[attempt_ids[1]]["summary"]["completed_at"],
                         "2026-09-03T21:01:48Z")
        self.assertEqual(attempts[attempt_ids[2]]["summary"]["completed_at"],
                         "2026-09-04T16:23:35Z")
        self.assertEqual(
            {
                key: attempts[attempt_ids[2]]["summary"][key]
                for key in (
                    "registration_focused_tests_passed",
                    "registration_focused_tests_total",
                    "registration_reconciler_tests_passed",
                    "registration_reconciler_tests_total",
                    "repository_python_tests_passed",
                    "repository_python_tests_total",
                    "retained_status_evidence_records",
                    "status_bearing_procedure_results",
                )
            },
            {
                "registration_focused_tests_passed": 4,
                "registration_focused_tests_total": 4,
                "registration_reconciler_tests_passed": 42,
                "registration_reconciler_tests_total": 42,
                "repository_python_tests_passed": 97,
                "repository_python_tests_total": 97,
                "retained_status_evidence_records": 96,
                "status_bearing_procedure_results": 42,
            },
        )
        for attempt_id in attempt_ids:
            self.assertEqual(attempts[attempt_id]["summary"]["support_layers"], 33)
            self.assertEqual(attempts[attempt_id]["summary"]["cli_support_layers"], 18)
            self.assertEqual(attempts[attempt_id]["summary"]["sdk_support_layers"], 15)

        expected_statuses = {
            "CLM-b3cd48630e5f2b0c": "FAIL",
            "CLM-3ba3b25f5c3ddac1": "UNVALIDATED",
            "CLM-3fa5d5948b34fc6a": "BLOCKED",
            "CLM-ca44522b22c4c5ee": "PASS",
            "CLM-9cba75bbdc780804": "UNVALIDATED",
        }
        for attempt_id in attempt_ids:
            self.assertEqual(
                attempts[attempt_id]["summary"]["target_statuses"],
                expected_statuses,
            )

        # The reviewer attempts prove presentation/linkage only. Registering
        # them as status-bearing procedure results would inflate the retained
        # evidence count and make the review artifact selectable as proof for
        # the commands it merely describes.
        self.assertEqual(len(RESULTS["procedure_results"]), 42)
        self.assertTrue(set(evidence_ids).isdisjoint(
            row["evidence_id"] for row in RESULTS["procedure_results"]
        ))
        retained_status_evidence = {
            row["evidence_id"] for group in (
                RESULTS["command_results"],
                RESULTS["procedure_results"],
                RESULTS["material_claim_results"],
                RESULTS["support_layer_results"],
            ) for row in group
        }
        self.assertEqual(len(retained_status_evidence), 96)

        status_payload = json.dumps({
            "current_status_projection": RESULTS["current_status_projection"],
            "direct_proof_ceilings": RESULTS["direct_proof_ceilings"],
            "material_claim_results": RESULTS["material_claim_results"],
            "support_layer_results": RESULTS["support_layer_results"],
        }, sort_keys=True)
        scores_payload = (
            REPO / "verification/host-docs-command-scores.json"
        ).read_text()
        for presentation_id in (*attempt_ids, *evidence_ids):
            self.assertNotIn(presentation_id, status_payload)
            self.assertNotIn(presentation_id, scores_payload)
        self.assertEqual(RESULTS["current_status_projection"]["counts"]["statuses"], {
            "PASS": 128,
            "FAIL": 5,
            "BLOCKED": 97,
            "UNVALIDATED": 747,
            "NOT_APPLICABLE": 27,
        })
        self.assertEqual(SETS["counts"], {
            "pages": 40,
            "test_sets": 101,
            "branches": 207,
            "steps": 477,
            "command_carriers": 179,
            "command_bearing_steps": 121,
        })

        initial_text = (REPO / evidence_refs[0]).read_text()
        post_change_text = (REPO / evidence_refs[1]).read_text()
        final_text = (REPO / evidence_refs[2]).read_text()
        traceability_text = (REPO / "REVIEW-TRACEABILITY.md").read_text()
        for scope_link in (
            "/host/how-to-self-test#before-you-run-it",
            "/host/how-to-self-test#run-the-test",
            "/host/vms#check-vm-status",
            "/host/vms#disable-vm-support",
        ):
            self.assertIn(scope_link, traceability_text)
        self.assertNotRegex(
            traceability_text,
            r"\]\(\./verification/evidence/",
        )
        self.assertGreaterEqual(
            traceability_text.count(
                "https://github.com/vast-ai/docs/pull/185/files#diff-"
            ),
            7,
        )
        self.assertIn("Completed: `2026-09-03T20:27:25Z`", initial_text)
        self.assertNotIn("Completed: `2026-09-03T20:48:44Z`", initial_text)
        for required in (
            "33 support layers (18 CLI, 15 SDK)",
            "`2/4`",
            "`4/4`",
            "`17/24`",
            "`23/24`",
            "`24/24`",
            "`3/3`",
            "`41/41`",
        ):
            self.assertIn(required, post_change_text)
        for required in (
            "40 primary Host pages",
            "33 support layers (18 CLI, 15 SDK)",
            "`97/97`",
            "`24/24`",
            "58 retained attempts",
            "57 unique attempt-artifact references",
            "42 status-bearing procedure results",
        ):
            self.assertIn(required, final_text)
        artifact_rows = re.findall(
            r"\| `([^`]+)` \| `([a-f0-9]{64})` \|",
            final_text,
        )
        artifact_paths = [path for path, _digest in artifact_rows]
        self.assertEqual(set(artifact_paths), {
            "review-server.mjs",
            "scripts/review-context.test.mjs",
            "scripts/reconcile_host_vv_repository.py",
            "scripts/test_reconcile_host_vv_repository.py",
            "host-docs-cli-command-check.json",
            "host-docs-command-access.json",
            "host-docs-verification-inventory.json",
            "verification/host-docs-test-sets.json",
            "verification/host-docs-command-scores.json",
            "verification/runtime-operator-blockers.md",
            "verification/source-owner-blockers.md",
            "HOST-DOCS-VV-HANDOFF.md",
            "REVIEW-TRACEABILITY.md",
            "verification/evidence/2026-09-03-host-repository-rebase-01/pre-edit-working-tree-baseline-sanitized.txt",
            "verification/evidence/2026-09-01-host-install-retained-record-audit-01/result.md",
            "verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-05/result.md",
            "verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-06/result.md",
            "verification/evidence/2026-09-01-host-third-party-remediation-attempt-01/result.md",
            "verification/evidence/2026-09-02-host-inventory-reconciliation-attempt-07/result.md",
            "verification/evidence/2026-09-03-host-reviewer-clarity-attempt-01/result.md",
        })
        self.assertEqual(len(artifact_paths), len(set(artifact_paths)))
        self.assertNotIn("verification/host-docs-test-results.json", artifact_paths)
        self.assertNotIn(evidence_refs[1], artifact_paths)
        supplemental_history = {
            "verification/evidence/2026-09-01-host-install-retained-record-audit-01/result.md",
            "verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-05/result.md",
            "verification/evidence/2026-09-01-host-inventory-reconciliation-attempt-06/result.md",
            "verification/evidence/2026-09-01-host-third-party-remediation-attempt-01/result.md",
            "verification/evidence/2026-09-02-host-inventory-reconciliation-attempt-07/result.md",
            "verification/evidence/2026-09-03-host-reviewer-clarity-attempt-01/result.md",
        }
        self.assertTrue(supplemental_history.issubset(artifact_paths))
        self.assertIn("supplementary historical records", final_text)
        for path in supplemental_history:
            self.assertNotRegex(
                (REPO / path).read_text(),
                r"(?:/Users/|/private/tmp/|/var/folders/|github\.com/(?!vast-ai/)[^/\s]+/(?:docs|vast-python|self-test)(?=[\s)/#]|$))",
                f"{path}: workstation-private path leaked into retained history",
            )
        # The table records the September 4 packaging snapshot. Compare it to
        # the immutable commit that sealed those bytes, not to a later working
        # tree where independently validated reviewer UI changes may exist.
        packaging_commit = "3e1e30e2221b65d7ce1e901d9ae305f63af5b64b"
        for path, digest in artifact_rows:
            self.assertTrue((REPO / path).is_file())
            packaged_bytes = subprocess.run(
                ["git", "show", f"{packaging_commit}:{path}"],
                cwd=REPO,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
            self.assertEqual(
                hashlib.sha256(packaged_bytes).hexdigest(),
                digest,
            )
        final_results_hash = hashlib.sha256(
            (REPO / "verification/host-docs-test-results.json").read_bytes()
        ).hexdigest()
        for text in (initial_text, final_text):
            self.assertNotIn(final_results_hash, text)
            self.assertNotRegex(
                text,
                r"verification/host-docs-test-results\.json`\s*\|\s*`[a-f0-9]{64}`",
            )

    def test_inline_code_literals_are_lossless_in_generic_claims(self) -> None:
        for claim in SETS["material_claims"]:
            if not claim["claim_id"].startswith("MCL-"):
                continue
            source = (REPO / claim["scope"]["source_file"]).read_text().splitlines()
            spans = claim["scope"]["source_spans"]
            raw = "\n".join(
                "\n".join(source[span["start"] - 1:span["end"]])
                for span in spans
            )
            if claim["claim"]["text"].startswith("["):
                continue
            for literal in re.findall(r"`([^`\n]+)`", raw):
                normalized = re.sub(r"\s+", " ", literal).strip()
                self.assertIn(f"`{normalized}`", claim["claim"]["text"])

    def test_every_material_claim_hashes_its_literal_declared_source_spans(self) -> None:
        for claim in SETS["material_claims"]:
            literal = self._claim_source_text(claim)
            self.assertEqual(
                claim["scope"]["source_text_sha256"],
                hashlib.sha256(literal.encode()).hexdigest(),
                claim["claim_id"],
            )

    def test_fragment_only_references_are_local(self) -> None:
        fragment_refs = [
            ref
            for claim in SETS["material_claims"]
            for ref in claim["citation"]["refs"]
            if ref["href"].startswith("#")
        ]
        self.assertTrue(fragment_refs)
        self.assertTrue(all(ref["kind"] == "LOCAL_DOCUMENTATION" for ref in fragment_refs))

    def test_material_result_roles_disclose_partial_evidence(self) -> None:
        bindings = RESULTS["material_claim_results"][0]["bindings"]
        for binding in bindings:
            if binding["status"] == "PASS":
                self.assertEqual(binding["evidence_role"], "CLAIM_SUITABLE_BOUNDED_SUPPORT")
                self.assertEqual(
                    set(binding["required_evidence_types"]),
                    set(binding["satisfied_evidence_types"]),
                )
            if binding["status"] == "UNVALIDATED" and binding["supporting_evidence_ids"]:
                self.assertEqual(
                    binding["evidence_role"],
                    "PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED",
                )

    def test_unresolved_authority_summaries_match_lane_roles(self) -> None:
        for claim in SETS["material_claims"]:
            requirements = claim["authority"].get("unresolved_evidence_requirements", [])
            if not requirements:
                continue
            expected = "; ".join(dict.fromkeys(
                requirement["responsible_role"] for requirement in requirements
            ))
            self.assertEqual(claim["authority"]["unresolved_owner_role"], expected)

    def test_technical_contract_ids_are_not_legal_citation_failures(self) -> None:
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        for claim_id in ("MCL-fb9d0cf28b4ac252", "MCL-ca4a7dafc0b99270"):
            claim = claims[claim_id]
            self.assertEqual(claim["citation"]["state"], "NOT_REQUIRED")
            self.assertEqual(claim["current"]["status"], "UNVALIDATED")
            self.assertNotIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
        cleanup = claims["MCL-af67e230dba3c369"]
        self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", cleanup["evidence_requirement"]["types"])
        self.assertIn("Product, Finance, and Legal owner", cleanup["authority"]["unresolved_owner_role"])

    def test_policy_and_commercial_claims_require_exact_authority(self) -> None:
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        for claim_id in (
            "MCL-1a4146b033bd9b88",
            "MCL-2c3f7082e2c7fdf2",
            "MCL-c4c4bfc59eb7b49f",
            "MCL-2c877a0f252279dd",
            "MCL-399798a3c4946b5f",
            "MCL-633317ca7ebecfef",
            "MCL-fe3eccd1cd40b4bd",
            "MCL-e2b956d14494e470",
            "MCL-9aed4b65c749baae",
            "MCL-b7440bdb3eb40fa1",
            "MCL-dcb653ae3a927dae",
        ):
            claim = claims[claim_id]
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")
            if claim["scope"]["source_file"] == "host/workload-policy.mdx":
                self.assertIn(
                    "Product, Trust, and Legal policy owner",
                    claim["authority"]["unresolved_owner_role"],
                )

    def test_local_documentation_links_do_not_satisfy_policy_citations(self) -> None:
        for claim in SETS["material_claims"]:
            if not claim["citation"]["required"]:
                continue
            has_authoritative_candidate = any(
                ref["kind"] == "AUTHORITATIVE_SOURCE_CANDIDATE"
                for ref in claim["citation"]["refs"]
            )
            self.assertEqual(
                claim["citation"]["state"],
                "PRESENT_UNVERIFIED" if has_authoritative_candidate else "ABSENT",
            )

    def test_direct_static_pass_targets_repeat_exact_source_refs(self) -> None:
        result_targets = {}
        for result in RESULTS["procedure_results"]:
            for target in result["targets"]:
                key = (target["level"], tuple(target["target"].items()), result["evidence_id"])
                result_targets[key] = target
        for row in RESULTS["current_status_projection"]["records"]:
            basis = row["status_basis"]
            refs = basis["authority"]["source_refs"]
            if row["current_status"] != "PASS" or basis["basis_kind"] != "STATIC_SOURCE_CONFORMANCE":
                continue
            self.assertTrue(refs)
            self.assertTrue(any(
                result_targets.get((row["level"], tuple(row["target"].items()), evidence_id), {}).get("source_refs") == refs
                for evidence_id in row["evidence_ids"]
            ))

    def test_bounded_local_navigation_index_is_fully_bound(self) -> None:
        navigation = next(
            row for row in RESULTS["material_claim_results"]
            if row["method"] == "STATIC_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION"
        )
        self.assertEqual(len(navigation["bindings"]), 140)
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        descriptive = claims["MCL-868db06c756ae224"]
        self.assertEqual(descriptive["current"]["status"], "UNVALIDATED")
        self.assertEqual(descriptive["citation"]["state"], "NOT_REQUIRED")
        self.assertNotIn(
            "ACCOUNTABLE_OWNER_CONFIRMATION",
            descriptive["evidence_requirement"]["types"],
        )
        semantic_row = claims["MCL-76404b5eca27a2be"]
        self.assertEqual(semantic_row["current"]["status"], "FAIL")
        self.assertNotEqual(semantic_row["claim"]["kind"], "NAVIGATION_CONTRACT")

    def test_rendered_snippet_claims_and_dependency_are_hash_bound(self) -> None:
        page = next(row for row in SETS["pages"] if row["route"] == "/host/notifications")
        self.assertEqual(len(page["rendered_dependencies"]), 1)
        dependency = page["rendered_dependencies"][0]
        self.assertEqual(dependency["component"], "NotificationChannels")
        self.assertEqual(dependency["source_file"], "snippets/notifications/channels.mdx")
        self.assertEqual(dependency["import_line"], 13)
        self.assertEqual(dependency["insertion_line"], 35)
        self.assertEqual(
            dependency["source_sha256"],
            hashlib.sha256((REPO / dependency["source_file"]).read_bytes()).hexdigest(),
        )
        dependency_claims = [
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == dependency["source_file"]
        ]
        self.assertEqual(len(dependency_claims), 5)
        self.assertTrue(all(
            claim["scope"]["route"] == "/host/notifications"
            and claim["scope"]["rendered_via"] == {
                "component": "NotificationChannels",
                "host_source_file": "host/notifications.mdx",
                "import_line": 13,
                "insertion_line": 35,
            }
            for claim in dependency_claims
        ))
        mandatory = next(
            claim for claim in dependency_claims
            if "mandatory" in claim["claim"]["text"].casefold()
        )
        self.assertEqual(mandatory["current"]["status"], "FAIL")
        self.assertEqual(mandatory["citation"]["state"], "ABSENT")
        self.assertIn(
            "AUTHORITATIVE_DOCUMENTATION_CITATION",
            mandatory["evidence_requirement"]["types"],
        )

    def test_every_page_render_snapshot_includes_all_declared_dependencies(self) -> None:
        rendered_rows = []
        for page in SETS["pages"]:
            rows = [
                f"PRIMARY\0{page['source_file']}\0{page['source_sha256']}\n"
            ]
            rows.extend(
                f"DEPENDENCY\0{item['component']}\0{item['source_file']}\0"
                f"{item['source_sha256']}\0{item['import_line']}\0{item['insertion_line']}\n"
                for item in page["rendered_dependencies"]
            )
            digest = hashlib.sha256("".join(rows).encode()).hexdigest()
            self.assertEqual(page["rendered_source_sha256"], digest, page["route"])
            rendered_rows.append(f"{page['route']}\0{digest}\n")
        self.assertEqual(
            SETS["source"]["reconciled_rendered_source_sha256"],
            hashlib.sha256("".join(rendered_rows).encode()).hexdigest(),
        )

    def test_material_manifest_repeats_render_origin_exactly(self) -> None:
        material = next(
            row for row in RESULTS["material_claim_results"]
            if row["method"] == "MATERIAL_CLAIM_OCCURRENCE_AND_DISPOSITION_MANIFEST"
        )
        bindings = {row["claim_id"]: row for row in material["bindings"]}
        self.assertEqual(len(bindings), len(SETS["material_claims"]))
        for claim in SETS["material_claims"]:
            self.assertEqual(
                bindings[claim["claim_id"]]["rendered_via"],
                claim["scope"]["rendered_via"],
            )

    def test_visible_frame_captions_are_runtime_ui_claims(self) -> None:
        captions = [
            claim for claim in SETS["material_claims"]
            if "<Frame" in self._claim_source_text(claim)
            and "caption=" in self._claim_source_text(claim)
        ]
        self.assertEqual(len(captions), 24)
        self.assertTrue(all(
            "RUNTIME_OR_UI_OBSERVATION" in claim["evidence_requirement"]["types"]
            for claim in captions
        ))

    def test_non_rendered_mdx_comments_are_not_material_claims(self) -> None:
        self_test_claims = [
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/self-test-reference.mdx"
        ]
        self.assertFalse(any(
            span["start"] <= 18 and span["end"] >= 13
            for claim in self_test_claims
            for span in claim["scope"]["source_spans"]
        ))

    def test_volume_atomic_manifest_accounts_for_all_four_prior_gaps(self) -> None:
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        for claim_id, line, status in (
            ("VOL-C36", 29, "PASS"),
            ("VOL-C37", 47, "PASS"),
            ("VOL-C38", 60, "UNVALIDATED"),
            ("VOL-C39", 71, "UNVALIDATED"),
        ):
            claim = claims[claim_id]
            self.assertEqual(claim["current"]["status"], status)
            self.assertTrue(any(
                span["start"] <= line <= span["end"]
                for span in claim["scope"]["source_spans"]
            ))
        self.assertEqual(
            len([claim for claim in SETS["material_claims"] if claim["page_id"] == "PAGE-host-volume-offers"]),
            39,
        )

    def test_runtime_register_contains_every_blocked_runtime_claim(self) -> None:
        register = (REPO / "verification/runtime-operator-blockers.md").read_text()
        material_section = register.split("## Blocked root procedure", 1)[0]
        expected = {
            claim["claim_id"]
            for claim in SETS["material_claims"]
            if claim["current"]["status"] == "BLOCKED"
            and "RUNTIME_OR_UI_OBSERVATION" in claim["evidence_requirement"]["types"]
        }
        observed = set(re.findall(r"`((?:MCL-[a-f0-9]{16})|(?:VOL-C\d{2}))`\)", material_section))
        self.assertEqual(observed, expected)
        bundle_row = next(
            line for line in register.splitlines()
            if "`CLM-3fa5d5948b34fc6a`" in line
        )
        self.assertIn("Host-owner credential", bundle_row)
        self.assertIn("numeric exit status", bundle_row)
        self.assertNotIn("unavailable_prerequisite.components", bundle_row)

    def test_explicit_ui_claims_require_retained_ui_observation(self) -> None:
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        for claim_id in (
            "MCL-c097d0beccbacad9",
            "MCL-ec0258710264c66e",
            "MCL-54f7239ba5c24fb9",
            "MCL-e1813d2faa5f9e24",
            "MCL-6d79e88ee4c5f4dd",
            "MCL-c36ab6f175970d56",
            "MCL-50ed1c5e647babcc",
            "MCL-9a18ba75267890e1",
            "MCL-07471963000a0522",
            "MCL-d4514d6f3c4833d7",
            "MCL-d25abfa50ad31f49",
            "MCL-5fc7c9ad95aa0671",
            "MCL-cce20356707a167a",
            "MCL-1b07f76a63e37580",
            "MCL-e0dd6d7d2ad0d108",
            "MCL-c31e94ebcc90e832",
            "MCL-2298ff57212a6824",
        ):
            self.assertIn(
                "RUNTIME_OR_UI_OBSERVATION",
                claims[claim_id]["evidence_requirement"]["types"],
                claim_id,
            )

    def test_external_action_links_do_not_mask_missing_authority(self) -> None:
        claims = {row["claim_id"]: row for row in SETS["material_claims"]}
        for claim_id in (
            "MCL-d0ce5b7f8787cda6",
            "MCL-bb42b9952d115f51",
            "MCL-edbf5dd77539fa66",
            "MCL-0eeef126e388e068",
            "MCL-b7862fc23da77b56",
            "MCL-790d76c6e2bea8fa",
            "MCL-fe93aa337bb543bf",
        ):
            claim = claims[claim_id]
            self.assertEqual(claim["current"]["status"], "FAIL", claim_id)
            self.assertEqual(claim["citation"]["state"], "ABSENT", claim_id)
            self.assertTrue(any(
                ref["kind"] == "EXTERNAL_ACTION_OR_UI_DESTINATION"
                for ref in claim["citation"]["refs"]
            ), claim_id)
        for claim_id in (
            "MCL-8ce33b81e4e0134c",
            "MCL-33e039957eabfb0c",
            "MCL-f48f7f89c7355a3f",
        ):
            claim = claims[claim_id]
            self.assertEqual(claim["citation"]["state"], "PRESENT_UNVERIFIED")
            self.assertTrue(all(
                ref["kind"] in {"AUTHORITATIVE_SOURCE_CANDIDATE", "LOCAL_DOCUMENTATION"}
                for ref in claim["citation"]["refs"]
            ))

    def test_list_leadins_are_bound_to_items_not_dangling_claims(self) -> None:
        claims = SETS["material_claims"]
        hosting = [
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/hosting-overview.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 18, "end": 18}
        ]
        workload = [
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/workload-policy.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 23, "end": 23}
        ]
        self.assertEqual(len(hosting), 4)
        self.assertEqual(len(workload), 6)
        self.assertTrue(all(len(claim["scope"]["source_spans"]) == 2 for claim in hosting + workload))
        self.assertTrue(all(claim["current"]["status"] == "FAIL" for claim in hosting + workload))
        self.assertFalse(any(
            len(claim["scope"]["source_spans"]) == 1
            and (
                (
                    claim["scope"]["source_file"] == "host/hosting-overview.mdx"
                    and claim["scope"]["source_spans"][0] == {"start": 18, "end": 18}
                )
                or (
                    claim["scope"]["source_file"] == "host/workload-policy.mdx"
                    and claim["scope"]["source_spans"][0] == {"start": 23, "end": 23}
                )
            )
            for claim in claims
        ))
        support_context = next(
            claim for claim in claims
            if claim["claim_id"] == "MCL-1e28623cfe82e85b"
        )
        self.assertEqual(support_context["current"]["status"], "UNVALIDATED")
        self.assertEqual(support_context["citation"]["state"], "NOT_REQUIRED")
        handoff = next(
            claim for claim in claims
            if claim["claim_id"] == "MCL-e9c7af0148732c9b"
        )
        self.assertEqual(handoff["current"]["status"], "PASS")
        self.assertEqual(handoff["claim"]["kind"], "NAVIGATION_CONTRACT")

    def test_payment_provider_leadin_is_bound_to_each_provider(self) -> None:
        providers = [
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/payment.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 31, "end": 31}
        ]
        self.assertEqual(len(providers), 3)
        self.assertEqual(
            {claim["scope"]["source_spans"][1]["start"] for claim in providers},
            {33, 34, 35},
        )
        for claim in providers:
            self.assertEqual(len(claim["scope"]["source_spans"]), 2)
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")

    def test_plural_finance_and_responsibility_claims_require_authority(self) -> None:
        claims = SETS["material_claims"]

        def at_line(source_file: str, line: int) -> dict:
            matches = [
                claim for claim in claims
                if claim["scope"]["source_file"] == source_file
                and any(
                    span["start"] <= line <= span["end"]
                    for span in claim["scope"]["source_spans"]
                )
            ]
            self.assertEqual(len(matches), 1, (source_file, line))
            return matches[0]

        for source_file, line in (
            ("host/payment.mdx", 101),
            ("host/guide-to-taxes.mdx", 51),
            ("host/common-errors-diagnostics.mdx", 221),
            ("host/community.mdx", 18),
        ):
            claim = at_line(source_file, line)
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")

    def test_rental_dedication_rule_requires_policy_authority(self) -> None:
        claim = next(
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/supported-hardware.mdx"
            and claim["scope"]["source_spans"] == [{"start": 78, "end": 78}]
        )
        self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
        self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
        self.assertEqual(claim["citation"]["state"], "ABSENT")
        self.assertEqual(claim["current"]["status"], "FAIL")

    def test_operational_contract_and_page_routing_text_are_not_policy_claims(self) -> None:
        cases = (
            ("host/notifications.mdx", 33, 29),
            ("host/workload-policy.mdx", 90, 90),
            ("host/account-hosting-agreement.mdx", 15, 15),
            ("host/hosting-overview.mdx", 31, 31),
        )
        for source_file, line, first_span in cases:
            matches = [
                claim for claim in SETS["material_claims"]
                if claim["scope"]["source_file"] == source_file
                and any(
                    span["start"] <= line <= span["end"]
                    for span in claim["scope"]["source_spans"]
                )
            ]
            self.assertEqual(len(matches), 1, (source_file, line))
            claim = matches[0]
            self.assertEqual(claim["scope"]["source_spans"][0]["start"], first_span)
            self.assertNotIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertNotIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "NOT_REQUIRED")
            self.assertEqual(claim["current"]["status"], "UNVALIDATED")

    def test_agreement_context_and_citation_are_bound_to_each_consequence(self) -> None:
        for source_file, context_line, item_lines in (
            ("host/hosting-agreement.mdx", 31, {33, 34, 35, 36}),
            ("host/hosting-overview.mdx", 72, {74, 75, 76, 77}),
        ):
            claims = [
                claim for claim in SETS["material_claims"]
                if claim["scope"]["source_file"] == source_file
                and claim["scope"]["source_spans"][0] == {
                    "start": context_line, "end": context_line
                }
            ]
            children = [claim for claim in claims if len(claim["scope"]["source_spans"]) == 2]
            own = [claim for claim in claims if len(claim["scope"]["source_spans"]) == 1]
            self.assertEqual(len(children), 4)
            self.assertEqual(len(own), 1)
            self.assertEqual(
                {claim["scope"]["source_spans"][1]["start"] for claim in children},
                item_lines,
            )
            for claim in claims:
                self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
                self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
                self.assertEqual(claim["citation"]["state"], "PRESENT_UNVERIFIED")
                self.assertEqual(claim["current"]["status"], "UNVALIDATED")

    def test_datacenter_program_requirements_have_exact_owner_and_citation_lane(self) -> None:
        claims = SETS["material_claims"]
        requirements = [
            next(
                claim for claim in claims
                if claim["scope"]["source_file"] == "host/datacenter-status.mdx"
                and claim["scope"]["source_spans"] == [{"start": line, "end": line}]
            )
            for line in range(24, 30)
        ]
        application = [
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/datacenter-status.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 33, "end": 33}
        ]
        self.assertEqual(len(requirements), 6)
        self.assertEqual(len(application), 5)
        self.assertEqual(
            {claim["scope"]["source_spans"][1]["start"] for claim in application},
            {35, 36, 37, 38, 39},
        )
        for claim in requirements + application:
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertIn(
                "Datacenter Product, Trust/Security, and Legal program owner",
                claim["authority"]["unresolved_owner_role"],
            )
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")
        application_link = next(
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/datacenter-status.mdx"
            and claim["scope"]["source_spans"] == [{"start": 41, "end": 41}]
        )
        self.assertNotIn(
            "ACCOUNTABLE_OWNER_CONFIRMATION",
            application_link["evidence_requirement"]["types"],
        )
        self.assertEqual(application_link["citation"]["state"], "NOT_REQUIRED")
        self.assertEqual(application_link["current"]["status"], "UNVALIDATED")

    def test_negated_pricing_comparison_remains_a_diagnostic_claim(self) -> None:
        claim = next(
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/machine-errors.mdx"
            and claim["scope"]["source_spans"] == [{"start": 196, "end": 196}]
        )
        self.assertEqual(claim["claim"]["kind"], "RUNTIME_BEHAVIOR")
        self.assertNotIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
        self.assertNotIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
        self.assertEqual(claim["citation"]["state"], "NOT_REQUIRED")

    def test_mixed_commercial_contract_claims_name_all_owner_domains(self) -> None:
        for source_file, line in (
            ("host/hosting-overview.mdx", 62),
            ("host/hosting-overview.mdx", 91),
            ("host/fleet-operations.mdx", 38),
            ("host/glossary.mdx", 87),
        ):
            claim = next(
                claim for claim in SETS["material_claims"]
                if claim["scope"]["source_file"] == source_file
                and any(
                    span["start"] <= line <= span["end"]
                    for span in claim["scope"]["source_spans"]
                )
            )
            role = claim["authority"]["unresolved_owner_role"]
            self.assertIn("Product", role)
            self.assertIn("Legal", role)
            if re.search(r"\b(?:price|pricing)\b", claim["claim"]["text"], re.IGNORECASE):
                self.assertIn("Finance", role)

    def test_procedure_fail_chain_names_the_exact_retained_discrepancy(self) -> None:
        failed = [
            row for row in RESULTS["current_status_projection"]["records"]
            if row["current_status"] == "FAIL"
        ]
        self.assertEqual(len(failed), 5)
        for row in failed:
            basis = row["status_basis"]
            self.assertIn("CLM-b3cd48630e5f2b0c", row["rationale"])
            self.assertIn("mode 0644", row["rationale"])
            self.assertIn("CLM-b3cd48630e5f2b0c", basis["claim_impact"])
            self.assertIn("mode 0644", basis["claim_impact"])
            self.assertIn("synthetic no-network permission check", basis["next_action"])
            self.assertIn("macOS", basis["limitations"])
            self.assertIn("Linux", basis["limitations"])
            self.assertIn("Windows", basis["limitations"])

    def test_tax_responsibility_context_is_bound_without_false_source_lane(self) -> None:
        claims = [
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/guide-to-taxes.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 23, "end": 23}
        ]
        own = [claim for claim in claims if len(claim["scope"]["source_spans"]) == 1]
        children = [claim for claim in claims if len(claim["scope"]["source_spans"]) == 2]
        self.assertEqual(len(own), 1)
        self.assertEqual(len(children), 3)
        self.assertNotIn(
            "CANONICAL_IMPLEMENTATION_SOURCE",
            own[0]["evidence_requirement"]["types"],
        )
        self.assertEqual(
            {claim["scope"]["source_spans"][1]["start"] for claim in children},
            {25, 26, 27},
        )
        for claim in claims:
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")

    def test_account_security_leadins_bind_normative_owner_and_runtime_lanes(self) -> None:
        claims = SETS["material_claims"]
        two_factor = [
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/account-security-for-hosts.mdx"
            and claim["scope"]["source_spans"][:2] == [
                {"start": 21, "end": 21}, {"start": 23, "end": 23}
            ]
        ]
        key_guidance = [
            claim for claim in claims
            if claim["scope"]["source_file"] == "host/account-security-for-hosts.mdx"
            and claim["scope"]["source_spans"][0] == {"start": 38, "end": 38}
        ]
        self.assertEqual(len(two_factor), 4)
        self.assertEqual(len(key_guidance), 4)
        self.assertEqual(
            {claim["scope"]["source_spans"][2]["start"] for claim in two_factor},
            {25, 26, 27, 28},
        )
        self.assertEqual(
            {claim["scope"]["source_spans"][1]["start"] for claim in key_guidance},
            {40, 41, 42, 43},
        )
        self.assertFalse(any(
            claim["scope"]["source_file"] == "host/account-security-for-hosts.mdx"
            and claim["scope"]["source_spans"] == [{"start": 23, "end": 23}]
            for claim in claims
        ))
        self.assertFalse(any(
            claim["scope"]["source_file"] == "host/account-security-for-hosts.mdx"
            and claim["scope"]["source_spans"] == [{"start": 38, "end": 38}]
            for claim in claims
        ))
        for claim in two_factor + key_guidance:
            self.assertIn("RUNTIME_OR_UI_OBSERVATION", claim["evidence_requirement"]["types"])
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertNotIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "NOT_REQUIRED")
            self.assertEqual(claim["current"]["status"], "UNVALIDATED")

    def test_revenue_component_claims_require_product_finance_authority(self) -> None:
        claims = [
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/earning.mdx"
            and claim["scope"]["heading"] == "Revenue Components"
            and (
                claim["scope"]["source_spans"] == [{"start": 25, "end": 25}]
                or claim["scope"]["source_spans"] == [{"start": 27, "end": 33}]
                or claim["scope"]["source_spans"][0]["start"] in {37, 38, 39, 40}
            )
        ]
        self.assertEqual(len(claims), 6)
        for claim in claims:
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("Product and Finance owner", claim["authority"]["unresolved_owner_role"])

    def test_live_action_paths_require_runtime_or_ui_observation(self) -> None:
        for source_file, line in (
            ("host/datacenter-status.mdx", 41),
            ("host/community.mdx", 23),
            ("host/guide-to-taxes.mdx", 37),
        ):
            claim = next(
                claim for claim in SETS["material_claims"]
                if claim["scope"]["source_file"] == source_file
                and any(
                    span["start"] <= line <= span["end"]
                    for span in claim["scope"]["source_spans"]
                )
            )
            self.assertIn("RUNTIME_OR_UI_OBSERVATION", claim["evidence_requirement"]["types"])
        datacenter = next(
            claim for claim in SETS["material_claims"]
            if claim["scope"]["source_file"] == "host/datacenter-status.mdx"
            and claim["scope"]["source_spans"] == [{"start": 41, "end": 41}]
        )
        self.assertNotIn("ACCOUNTABLE_OWNER_CONFIRMATION", datacenter["evidence_requirement"]["types"])
        self.assertEqual(datacenter["citation"]["state"], "NOT_REQUIRED")

    def test_account_and_datacenter_program_claims_require_owner_citations(self) -> None:
        cases = (
            ("host/account-hosting-agreement.mdx", 20),
            ("host/datacenter-status.mdx", 13),
            ("host/datacenter-status.mdx", 18),
            ("host/datacenter-status.mdx", 19),
            ("host/datacenter-status.mdx", 20),
        )
        for source_file, line in cases:
            claim = next(
                claim for claim in SETS["material_claims"]
                if claim["scope"]["source_file"] == source_file
                and claim["scope"]["source_spans"] == [{"start": line, "end": line}]
            )
            self.assertIn("RUNTIME_OR_UI_OBSERVATION", claim["evidence_requirement"]["types"])
            self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", claim["evidence_requirement"]["types"])
            self.assertIn("AUTHORITATIVE_DOCUMENTATION_CITATION", claim["evidence_requirement"]["types"])
            self.assertEqual(claim["citation"]["state"], "ABSENT")
            self.assertEqual(claim["current"]["status"], "FAIL")
            if source_file == "host/datacenter-status.mdx":
                self.assertIn(
                    "Datacenter Product, Trust/Security, and Legal program owner",
                    claim["authority"]["unresolved_owner_role"],
                )

    def test_current_reviewer_narratives_match_canonical_material_projection(self) -> None:
        expected = {
            "HOST-DOCS-QA-SUMMARY.md": (
                "1,687-item material-claim register contains 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED",
                "citation states are 153 required-and-absent, 19 required-and-present-but-unverified, and 1,515 not required",
                "page rollup is 3 BLOCKED, 26 FAIL, and 11 UNVALIDATED",
            ),
            "HOST-DOCS-VV-HANDOFF.md": (
                "Material-claim status: 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED across 1,687 claims",
                "One hundred fifty-three required citations are absent; 19 required citations are present but not yet verified; 1,515 claims do not require one",
                "owner input is retained as non-promoting context and no owner acceptance is inferred",
            ),
            "verification/README.md": (
                "Material-claim status: 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED across 1,687 claims",
                "Citation status is 153 required-and-absent, 19 required-and-present-but-unverified, and 1,515 not required",
            ),
            "verification/summary.md": (
                "material-claim register contains 1,687 claims: 167 PASS, 153 FAIL, 23 BLOCKED, and 1,344 UNVALIDATED",
                "Citation status is 153 required-and-absent, 19 required-and-present-but-unverified, and 1,515 not required",
            ),
        }
        for relative, snippets in expected.items():
            text = re.sub(r"\s+", " ", (REPO / relative).read_text())
            for snippet in snippets:
                self.assertIn(snippet, text, f"{relative}: stale current material projection")
            self.assertNotIn("1,692", text, f"{relative}: stale material denominator")
            self.assertNotRegex(
                text,
                r"(?:/Users/|/private/tmp/|/var/folders/|github\.com/(?!vast-ai/)[^/\s]+/(?:docs|vast-python|self-test)(?=[\s)/#]|$))",
                f"{relative}: workstation-private path leaked into reviewer document",
            )
        result = (REPO / "verification/evidence/2026-09-03-host-repository-rebase-01/result.md").read_text()
        for row in (
            "| Material claims | 1,687 |", "| PASS | 167 |", "| FAIL | 153 |",
            "| BLOCKED | 23 |", "| UNVALIDATED | 1,344 |",
            "| Pages by material-claim disposition | 3 BLOCKED, 26 FAIL, 11 UNVALIDATED |",
            "| Required citation absent | 153 |",
            "| Citation present but authority unverified | 19 |",
            "| Citation not required by claim semantics | 1,515 |",
        ):
            self.assertIn(row, result)
        command_coverage = (REPO / "verification/HOST-DOCS-COMMAND-COVERAGE.md").read_text()
        self.assertIn("1,687 material-claim dispositions", command_coverage)


if __name__ == "__main__":
    unittest.main()
