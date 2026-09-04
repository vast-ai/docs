#!/usr/bin/env python3
"""Reconcile the active Host V&V package to the current repository.

This generator is deliberately repository-local.  It reads documentation and
retained evidence, updates the current procedure/status projections, and writes
deterministic JSON/Markdown views.  It never invokes a documented command,
network endpoint, credential, Host, paid resource, privileged operation, or
workload.

The 39-page P1 draft remains an immutable historical input.  The active
``host-docs-test-sets.json`` package is the current 40-page baseline.
"""

from __future__ import annotations

import argparse
from collections import Counter
import copy
import html
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
SETS_PATH = REPO / "verification/host-docs-test-sets.json"
RESULTS_PATH = REPO / "verification/host-docs-test-results.json"
SCORES_PATH = REPO / "verification/host-docs-command-scores.json"
RUNTIME_REGISTER_PATH = REPO / "verification/runtime-operator-blockers.md"
OWNER_REGISTER_PATH = REPO / "verification/source-owner-blockers.md"
EVIDENCE_REF = "verification/evidence/2026-09-03-host-repository-rebase-01/result.md"
BASELINE_EVIDENCE_REF = "verification/evidence/2026-09-03-host-repository-rebase-01/pre-edit-working-tree-baseline-sanitized.txt"

BASELINE_ATTEMPT = "ATTEMPT-2026-09-03-HOST-WORKING-TREE-BASELINE-01"
PRECHECK_ATTEMPT = "ATTEMPT-2026-09-03-HOST-REPOSITORY-PRECHECK-01"
CURRENT_ATTEMPT = "ATTEMPT-2026-09-03-HOST-REPOSITORY-REBASE-01"
TOPOLOGY_CORRECTION_ATTEMPT = "ATTEMPT-2026-09-03-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"
PRECHECK_EVIDENCE = "EV-HOST-REPOSITORY-PRECHECK-01"
REBASE_EVIDENCE = "EV-HOST-REPOSITORY-LOCAL-STATUS-REBASE-01"
TOPOLOGY_CORRECTION_EVIDENCE = "EV-HOST-SELF-TEST-TOPOLOGY-CORRECTION-01"
TOPOLOGY_CORRECTION_EVIDENCE_REF = (
    "verification/evidence/2026-09-03-host-self-test-topology-correction-01/result.md"
)
COMMAND_PROOF_REVIEWER_ATTEMPT_01 = (
    "ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-01"
)
COMMAND_PROOF_REVIEWER_ATTEMPT_02 = (
    "ATTEMPT-2026-09-03-HOST-COMMAND-PROOF-REVIEWER-02"
)
COMMAND_PROOF_REVIEWER_EVIDENCE_01 = "EV-HOST-COMMAND-PROOF-REVIEWER-01"
COMMAND_PROOF_REVIEWER_EVIDENCE_02 = "EV-HOST-COMMAND-PROOF-REVIEWER-02"
COMMAND_PROOF_REVIEWER_EVIDENCE_REF_01 = (
    "verification/evidence/2026-09-03-host-command-proof-reviewer-attempt-01/result.md"
)
COMMAND_PROOF_REVIEWER_EVIDENCE_REF_02 = (
    "verification/evidence/2026-09-03-host-command-proof-reviewer-attempt-02/result.md"
)
PR_READY_PACKAGING_ATTEMPT = (
    "ATTEMPT-2026-09-04-HOST-PR-READY-PACKAGING-01"
)
PR_READY_PACKAGING_EVIDENCE = "EV-HOST-PR-READY-PACKAGING-01"
PR_READY_PACKAGING_EVIDENCE_REF = (
    "verification/evidence/2026-09-04-host-pr-ready-packaging-attempt-01/result.md"
)
COMMAND_PROOF_REVIEWER_ATTEMPTS = {
    COMMAND_PROOF_REVIEWER_ATTEMPT_01, COMMAND_PROOF_REVIEWER_ATTEMPT_02,
    PR_READY_PACKAGING_ATTEMPT,
}
COMMAND_PROOF_REVIEWER_EVIDENCE = {
    COMMAND_PROOF_REVIEWER_EVIDENCE_01, COMMAND_PROOF_REVIEWER_EVIDENCE_02,
    PR_READY_PACKAGING_EVIDENCE,
}
VOLUME_EVIDENCE = "EV-HOST-VOLUME-OFFERS-STATIC-SOURCE-01"
SUPPORT_EVIDENCE = "EV-HOST-CENTRAL-REFERENCE-SUPPORT-LAYERS-01"
CLAIM_MANIFEST_EVIDENCE = "EV-HOST-MATERIAL-CLAIM-DISPOSITIONS-01"
NAVIGATION_EVIDENCE = "EV-HOST-LOCAL-NAVIGATION-RESOLUTION-01"
COMMAND_CLAIM_MANIFEST_EVIDENCE = "EV-HOST-EXACT-COMMAND-CLAIM-BINDINGS-01"
COMMAND_COVERAGE_EVIDENCE = "EV-HOST-COMMAND-OCCURRENCE-RECONCILIATION-01"
SOURCE_BINDING_EVIDENCE = "EV-HOST-PINNED-CANONICAL-SOURCE-BINDING-01"
GENERATED_ATTEMPTS = {
    BASELINE_ATTEMPT, PRECHECK_ATTEMPT, CURRENT_ATTEMPT,
    TOPOLOGY_CORRECTION_ATTEMPT, *COMMAND_PROOF_REVIEWER_ATTEMPTS,
}
GENERATED_EVIDENCE = {
    PRECHECK_EVIDENCE, TOPOLOGY_CORRECTION_EVIDENCE, VOLUME_EVIDENCE,
    COMMAND_COVERAGE_EVIDENCE, SOURCE_BINDING_EVIDENCE,
    *COMMAND_PROOF_REVIEWER_EVIDENCE,
}

CLI_REVISION = "ecf32efa1d8d2f110f7de4118c30698bb7ae2fbd"
SELF_TEST_CLI_REVISION = "d4316fb06631cea759f5a36542e6196450e897f2"
SELF_TEST_IMAGE_REVISION = "6f93fc4ba8ec61e3360b28829e91665f3ba7ade6"

TARGET_FIELDS = {
    "PAGE": ("page_id",),
    "TEST_SET": ("page_id", "test_set_id"),
    "BRANCH": ("page_id", "test_set_id", "branch_id"),
    "STEP": ("page_id", "test_set_id", "branch_id", "step_id"),
    "COMMAND": ("page_id", "test_set_id", "branch_id", "step_id", "command_id"),
}
STATUS_ORDER = ("PASS", "FAIL", "BLOCKED", "UNVALIDATED", "STALE", "NOT_APPLICABLE")
COMMAND_PROOF_REVIEWER_TARGET_STATUSES = {
    "CLM-b3cd48630e5f2b0c": "FAIL",
    "CLM-3ba3b25f5c3ddac1": "UNVALIDATED",
    "CLM-3fa5d5948b34fc6a": "BLOCKED",
    "CLM-ca44522b22c4c5ee": "PASS",
    "CLM-9cba75bbdc780804": "UNVALIDATED",
}
API_KEY_PERMISSION_COMMAND_ID = "CLM-b3cd48630e5f2b0c"
API_KEY_PERMISSION_OBSERVATION = (
    "Vast CLI 1.5.6 on macOS arm64 with Python 3.14.6 and umask 022 wrote the "
    "synthetic API-key file with mode 0644."
)
API_KEY_PERMISSION_LIMITATION = (
    "The retained no-network check used a synthetic value in an isolated disposable "
    "configuration. It establishes the unsafe file mode only for that macOS arm64, "
    "Python 3.14.6, Vast CLI 1.5.6 environment; Linux, Windows, real credentials, Host "
    "operations, and later CLI versions were not tested."
)
API_KEY_PERMISSION_ACTION = (
    "Harden the Vast CLI credential writer to create and retain platform-appropriate "
    "user-only access, then rerun the synthetic no-network permission check on macOS, "
    "Linux, and Windows and retain the exact modes or ACLs; preserve the failed attempt."
)

# Four retained command checks name an exact unavailable prerequisite.  All
# other old command BLOCKED records merely said an input/evidence bucket was
# missing and are therefore UNVALIDATED.
ROOT_BLOCKED_COMMANDS = {
    "CLM-645eb90e744fd6f7": (
        "PERMISSION",
        "An authorized Host-owner API credential with permission to select and create the temporary self-test workload is unavailable.",
    ),
    "CLM-3fa5d5948b34fc6a": (
        "PERMISSION",
        "An authorized Host-owner API credential with permission to select and create the temporary self-test workload is unavailable.",
    ),
    "CLM-1112ca628ad4639f": (
        "AUTHORIZATION",
        "An authorized idle workload-capable Host and explicit approval to run GPU burn are unavailable under this task scope.",
    ),
    "CLM-c48a9b18342902bb": (
        "PERMISSION",
        "The retained account credential lacks the machine-read permission required by the metrics endpoint.",
    ),
    "CLM-2872a25df6add3a5": (
        "AUTHORIZATION",
        "Explicit operator authorization and a controlled disposable or idle Host are unavailable for changing the bootloader configuration.",
    ),
    "CLM-1e2f077efd167bfd": (
        "AUTHORIZATION",
        "Explicit operator authorization and a controlled disposable or idle VM-capable Host are unavailable for changing the bootloader configuration and rebooting it.",
    ),
    "CLM-0fa4c0088a41c909": (
        "ENVIRONMENT",
        "A representative authorized VM-capable Host in the post-enable state is unavailable for checking VM state, GPU visibility, and Host service health together.",
    ),
}


# These three authored fenced blocks were present in the 193-command static
# inventory but absent from the procedure topology.  Their IDs are stable
# hashes of the exact command text; inventory_id preserves the independent
# inventory identity used to detect the omission.
RECONCILED_WORKFLOW_COMMANDS = (
    {
        "command_id": "CLM-2872a25df6add3a5",
        "inventory_id": "com-10c8e6f115",
        "page_id": "PAGE-host-headless-install",
        "step_id": "HDL-E01-S26",
        "file": "host/headless-install.mdx",
        "section": "Step 8: Configure GRUB Only When Needed",
        "line_start": 256,
        "line_end": 256,
        "text": "sudo update-grub",
        "treatment": "PRIVILEGED_HOST_REQUIRED",
        "applicability": "Shared apply step after either the AMD or Intel GRUB option; represented once as one authored command occurrence.",
    },
    {
        "command_id": "CLM-1e2f077efd167bfd",
        "inventory_id": "com-81ab748278",
        "page_id": "PAGE-host-vms",
        "step_id": "VM-E02-S02",
        "file": "host/vms.mdx",
        "section": "Kernel Options",
        "line_start": 92,
        "line_end": 93,
        "text": "sudo update-grub\nsudo reboot",
        "treatment": "DESTRUCTIVE_OR_MUTATING_REQUIRED",
        "applicability": "Shared apply-and-reboot block after either the Intel or AMD kernel option; represented once as one authored command occurrence.",
    },
    {
        "command_id": "CLM-0fa4c0088a41c909",
        "inventory_id": "com-b345adca68",
        "page_id": "PAGE-host-vms",
        "step_id": "VM-E02-S08",
        "file": "host/vms.mdx",
        "section": "Retry Enablement",
        "line_start": 117,
        "line_end": 119,
        "text": "python3 /var/lib/vastai_kaalia/enable_vms.py check\nnvidia-smi -L\nsystemctl is-active vastai.service docker.service",
        "treatment": "PRIVILEGED_HOST_REQUIRED",
        "applicability": "Post-enable state and health observation block.",
    },
)
RETIRED_RECONCILIATION_COMMAND_IDS = {
    "CLM-1825500456154028", "CLM-1776e44ff635ab14", "CLM-efc71b1a7b674331",
}
TEAM_CATALOG_COMMAND_IDS = {
    "CLM-1b189d051c9468e5", "CLM-1cb07ec233c461b2", "CLM-38257bb7c2529187",
    "CLM-40b2f1682f7e1b79", "CLM-46d0c5ce2153a004", "CLM-4f08d5cc9817690b",
    "CLM-5f1ad892e6c8e34c", "CLM-6a6993c68a1f04e4", "CLM-923d7604e486acd4",
    "CLM-961b4271992ad45f", "CLM-965828ea630d32ff", "CLM-b10173dc22deecd2",
    "CLM-bb31da6105c31a7c", "CLM-c6370bac1c24cf5d", "CLM-da373c4653a28e82",
    "CLM-e6bffefe839b663c", "CLM-fa287335656da956",
}
SELF_TEST_PARITY_STEP_IDS = {"STR-C01-parity-s01", "STR-C01-parity-s02"}

# These three exact command occurrences were incorrectly attached to the
# narrative checkpoint ST-E01-normal-s02.  The correction is intentionally
# declared here rather than patched into the generated JSON: the reconciler is
# the owner of the active topology, while procedure-baseline-p1.json and the
# retained attempt artifacts remain historical inputs.
SELF_TEST_COMMAND_PLACEMENTS = (
    {
        "command_id": "CLM-b3cd48630e5f2b0c",
        "text": "vastai set api-key <API_KEY>",
        "branch_id": "ST-E01-normal",
        "step_id": "ST-E01-normal-s01",
        "step_role": "setup",
        "line_start": 29,
        "line_end": 29,
        "section": "Before You Run It",
        "execution_status": "FAIL",
    },
    {
        "command_id": "CLM-3ba3b25f5c3ddac1",
        "text": "vastai self-test machine <machine_id>",
        "branch_id": "ST-E01-normal",
        "step_id": "ST-E01-normal-s03",
        "step_role": "action",
        "line_start": 79,
        "line_end": 79,
        "section": "Run The Test",
        "execution_status": "UNVALIDATED",
    },
    {
        "command_id": "CLM-3fa5d5948b34fc6a",
        "text": (
            "vastai self-test machine <machine_id> \\\n"
            "  --support-bundle-dir /path/to/output"
        ),
        "branch_id": "ST-E01-bundle-dir",
        "step_id": "ST-E01-bundle-dir-s02",
        "step_role": "action",
        "line_start": 85,
        "line_end": 86,
        "section": "Run The Test",
        "execution_status": "BLOCKED",
    },
)
SELF_TEST_PAGE_ID = "PAGE-host-how-to-self-test"
SELF_TEST_SET_ID = "TS-ST-E01"
SELF_TEST_LEGACY_BRANCH_ID = "ST-E01-normal"
SELF_TEST_LEGACY_STEP_ID = "ST-E01-normal-s02"
SELF_TEST_CORRECTED_STEP_OWN_STATUSES = {
    "ST-E01-normal-s01": "UNVALIDATED",
    "ST-E01-normal-s02": "UNVALIDATED",
    "ST-E01-normal-s03": "UNVALIDATED",
    "ST-E01-bundle-dir-s02": "UNVALIDATED",
}
SELF_TEST_HISTORICAL_BINDING_COUNTS = {
    "EV-HOST-COMMAND-ASSESSMENT-01": 3,
    "EV-HOST-CURRENT-RECONCILIATION-01": 3,
    "EV-HOST-SELF-TEST-PROCEDURE-01": 1,
    "EV-CLI-SET-API-KEY-PERMISSIONS-PROCEDURE-01": 1,
    REBASE_EVIDENCE: 1,
}

# These exact command subjects need evidence contracts that are independent of
# whichever retained accounting record currently supplies their status basis.
# In particular, a static topology/reconciliation method must not turn a
# missing runtime check into a REPOSITORY_STATIC_CHECK requirement.
EXACT_COMMAND_EVIDENCE_CONTRACTS = {
    (
        "COMMAND", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-bundle-dir",
        "ST-E01-bundle-dir-s02", "CLM-3fa5d5948b34fc6a",
    ): {
        "command_text": (
            "vastai self-test machine <machine_id> \\\n"
            "  --support-bundle-dir /path/to/output"
        ),
        "required_evidence_types": ("RUNTIME_OR_UI_OBSERVATION",),
        "next_action": (
            "Provide an explicitly authorized Host-owner credential that can inspect the "
            "representative idle listed Host, select its offer, and create the bounded "
            "temporary self-test workload. Then rerun the exact "
            "`vastai self-test machine <machine_id> --support-bundle-dir /path/to/output` "
            "form and retain the CLI and self-test revisions, image digest, machine, offer, "
            "contract, and instance identities, invocation, timestamps, numeric exit status, "
            "terminal result, requested bundle path and contents, lifecycle observations, "
            "and verified cleanup."
        ),
    },
    (
        "COMMAND", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-normal",
        "ST-E01-normal-s03", "CLM-3ba3b25f5c3ddac1",
    ): {
        "command_text": "vastai self-test machine <machine_id>",
        "required_evidence_types": ("RUNTIME_OR_UI_OBSERVATION",),
        "next_action": (
            "On an explicitly authorized representative idle listed Host, run the exact "
            "`vastai self-test machine <machine_id>` default form without "
            "`--support-bundle-dir`, using a role-correct Host-owner credential, an "
            "approved runtime/spend bound, and cleanup authority. Retain the exact CLI "
            "and self-test revisions, image digest, machine/offer/contract/instance "
            "identities, invocation, timestamps, exit status, terminal result, lifecycle "
            "observations, and verified cleanup."
        ),
    },
    (
        "COMMAND", "PAGE-host-vms", "TS-VM-E01", "VM-E01-B-disable",
        "VM-E01-S02", "CLM-9cba75bbdc780804",
    ): {
        "command_text": "sudo python3 /var/lib/vastai_kaalia/enable_vms.py off",
        "required_evidence_types": (
            "CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION",
        ),
        "next_action": (
            "First bind the exact immutable canonical helper source and its privilege and "
            "state-transition contract. Then, on an explicitly authorized, idle, unlisted, "
            "representative VM-capable Host that begins with VM support `on` and has no "
            "active rentals or workloads, retain the controlled "
            "`check → off → check → on -f → check` sequence, every exit status, "
            "output, timestamp, and Host/service/GPU health observation, and proof that "
            "the original enabled state and workload availability were safely restored."
        ),
    },
}

# These records have a target-specific retained authorization, parameter, or
# representative-environment prerequisite.  The two child-derived blockers are
# intentionally absent and are recomputed from their command children.
ROOT_BLOCKED_STEPS = {
    "DIA-E02-B02-S02", "DIA-E03-B01-S03", "DIA-E03-B03-S02",
    "ERR-T01-B02-S02", "ERR-T02-B01-S02", "FLT-E03-B01-S02",
    "HDL-E01-S09", "HDL-E01-S16", "HDL-E01-S17", "HDL-E01-S18",
    "HDL-E01-S21", "HDL-E01-S25", "HDL-E01-S29", "HWP-C01-S01",
    "HWP-C01-S04", "INS-E02-S03", "MET-E02-setup-s01",
    "MNT-E02-B01-S02", "NET-E03-S01", "NET-E03-S02", "NET-E03-S05",
    "NET-E03-S07", "NET-E03-S08", "NET-E03-S11", "STO-E03-S03",
    "STO-E03-S08",
}

VOLUME_COMMANDS = (
    ("CLM-881b5228b0d09b54", "VOL-E01-S01", 54, 57,
     "vastai list machine <machine-id> \\\n  --vol_size <capacity-gb> \\\n  --vol_price <usd-per-gb-month> \\\n  --end_date <date>", "EXECUTABLE_TEMPLATE_REQUIRED"),
    ("CLM-f05355ac5fc0ec73", "VOL-E02-S01", 65, 68,
     "vastai list volume <machine-id> \\\n  --size <capacity-gb> \\\n  --price_disk <usd-per-gb-month> \\\n  --end_date <date>", "EXECUTABLE_TEMPLATE_REQUIRED"),
    ("CLM-1c1bc04791804074", "VOL-E02-S02", 71, 71,
     "vastai list volumes", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-219274fbd05ee481", "VOL-C02-S01", 101, 101,
     "vastai list machine", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-d29496bf33bc175d", "VOL-C02-S01", 102, 102,
     "vastai list volume", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-cc0a0209572d051a", "VOL-C02-S01", 104, 104,
     "vastai unlist volume", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-ba4388c51f05e7e7", "VOL-C02-S02", 105, 105,
     "vastai search volumes", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-cb2e22b99b179d61", "VOL-C02-S02", 106, 106,
     "vastai create volume", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-d3e7a361fea7f9e3", "VOL-C02-S02", 107, 107,
     "vastai show volumes", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-b2dda57cc9a45ea5", "VOL-C02-S02", 108, 108,
     "vastai create instance", "NON_EXECUTABLE_DISPLAY"),
    ("CLM-815c031ba9fdea94", "VOL-C02-S02", 109, 109,
     "vastai delete volume", "NON_EXECUTABLE_DISPLAY"),
)


class ReconciliationError(RuntimeError):
    """The current repository cannot be reconciled without ambiguity."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReconciliationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: top level must be an object")
    return value


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def target_key(level: str, target: dict[str, str]) -> tuple[str, ...]:
    return (level, *(target[field] for field in TARGET_FIELDS[level]))


def target_dict(key: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(TARGET_FIELDS[key[0]], key[1:], strict=True))


def correct_self_test_command_topology(sets: dict[str, Any]) -> list[dict[str, Any]]:
    """Relocate three known self-test command carriers to their action steps.

    Accept only the exact legacy layout or the exact corrected layout.  This
    makes the rewrite idempotent while failing closed if a future topology or
    source edit needs a new reviewed mapping.
    """
    pages = [page for page in sets["pages"] if page["page_id"] == SELF_TEST_PAGE_ID]
    require(len(pages) == 1, "expected exactly one How to Self-Test page")
    page = pages[0]
    require(
        page["route"] == "/host/how-to-self-test"
        and page["source_file"] == "host/how-to-self-test.mdx",
        "How to Self-Test page identity changed",
    )
    test_sets = [
        test_set for test_set in page["test_sets"]
        if test_set["test_set_id"] == SELF_TEST_SET_ID
    ]
    require(len(test_sets) == 1, "expected exactly one TS-ST-E01 test set")
    test_set = test_sets[0]

    steps: dict[tuple[str, str], dict[str, Any]] = {}
    locations: dict[str, list[tuple[str, str, dict[str, Any]]]] = {
        spec["command_id"]: [] for spec in SELF_TEST_COMMAND_PLACEMENTS
    }
    for candidate_page in sets["pages"]:
        for candidate_set in candidate_page["test_sets"]:
            for branch in candidate_set["branches"]:
                for step in branch["steps"]:
                    if candidate_set is test_set:
                        key = (branch["branch_id"], step["step_id"])
                        require(key not in steps, f"duplicate self-test step: {key}")
                        steps[key] = step
                    for command in step["commands"]:
                        if command["command_id"] in locations:
                            locations[command["command_id"]].append(
                                (branch["branch_id"], step["step_id"], command)
                            )

    legacy_key = (SELF_TEST_LEGACY_BRANCH_ID, SELF_TEST_LEGACY_STEP_ID)
    legacy_step = steps.get(legacy_key)
    require(legacy_step is not None, "missing legacy self-test checkpoint step")
    legacy_spans = tuple(
        (span["start"], span["end"]) for span in legacy_step["source_lines"]
    )
    require(
        legacy_spans in {
            ((29, 29), (33, 64), (79, 79), (85, 86)),
            ((33, 64),),
        },
        f"unexpected self-test checkpoint source spans: {legacy_spans}",
    )
    require(
        tuple(legacy_step["source_sections"]) in {
            ("What Self-Test Checks", "Run The Test", "Before You Run It"),
            ("What Self-Test Checks",),
        },
        "unexpected self-test checkpoint source sections",
    )
    require(
        legacy_step["execution_classification"] in {
            "SOURCE_DEFECT_BLOCKED", "MANUAL_OR_CONTEXT",
        },
        "unexpected self-test checkpoint execution classification",
    )

    # Validate the list-valued legacy blocker separately and then normalize the
    # generator-owned checkpoint metadata back to its original narrative scope.
    require(
        legacy_step["blocker_ids"] in (
            ["SAFEFORM-SOURCE-DEFECT-ST-E01-NORMAL-S02"], []
        ),
        "unexpected self-test checkpoint blocker identity",
    )
    legacy_step["source_sections"] = ["What Self-Test Checks"]
    legacy_step["source_lines"] = [{"start": 33, "end": 64}]
    legacy_step["execution_classification"] = "MANUAL_OR_CONTEXT"
    legacy_step["blocker_ids"] = []

    source_lines = (REPO / page["source_file"]).read_text(encoding="utf-8").splitlines()
    bindings: list[dict[str, Any]] = []
    for spec in SELF_TEST_COMMAND_PLACEMENTS:
        command_id = spec["command_id"]
        command_locations = locations[command_id]
        require(
            len(command_locations) == 1,
            f"expected one active carrier for {command_id}, found {len(command_locations)}",
        )
        branch_id, step_id, command = command_locations[0]
        require(
            (branch_id, step_id) in {
                legacy_key, (spec["branch_id"], spec["step_id"]),
            },
            f"{command_id} is attached to an unreviewed step {branch_id}/{step_id}",
        )
        destination_key = (spec["branch_id"], spec["step_id"])
        destination = steps.get(destination_key)
        require(destination is not None, f"missing destination step for {command_id}")
        require(
            destination["role"] == spec["step_role"]
            and spec["section"] in destination["source_sections"]
            and any(
                span["start"] <= spec["line_start"]
                and span["end"] >= spec["line_end"]
                for span in destination["source_lines"]
            ),
            f"destination step no longer owns the source action for {command_id}",
        )
        expected_source = {
            "file": "host/how-to-self-test.mdx",
            "line_end": spec["line_end"],
            "line_start": spec["line_start"],
            "section": spec["section"],
            "source_type": "authored",
            "text_sha256": sha256_bytes(spec["text"].encode()),
        }
        require(command["text"] == spec["text"], f"command text changed for {command_id}")
        require(command["source"] == expected_source, f"command source changed for {command_id}")
        require(
            command["execution_status"] == spec["execution_status"],
            f"preserved command status changed for {command_id}",
        )
        require(
            command["treatment"] in {
                "SOURCE_DEFECT_BLOCKED", "EXECUTABLE_TEMPLATE_REQUIRED",
            },
            f"unexpected command treatment for {command_id}",
        )
        raw = "\n".join(source_lines[spec["line_start"] - 1:spec["line_end"]])
        require(raw == spec["text"], f"authored source occurrence changed for {command_id}")

        if (branch_id, step_id) != destination_key:
            source_step = steps[(branch_id, step_id)]
            source_step["commands"].remove(command)
            destination["commands"].append(command)
        command["treatment"] = "EXECUTABLE_TEMPLATE_REQUIRED"
        bindings.append({
            "command_id": command_id,
            "legacy_branch_id": SELF_TEST_LEGACY_BRANCH_ID,
            "legacy_step_id": SELF_TEST_LEGACY_STEP_ID,
            "branch_id": spec["branch_id"],
            "step_id": spec["step_id"],
            "step_role": spec["step_role"],
            "source_file": expected_source["file"],
            "heading": spec["section"],
            "line_start": spec["line_start"],
            "line_end": spec["line_end"],
            "text_sha256": expected_source["text_sha256"],
            "preserved_execution_status": spec["execution_status"],
            "treatment": command["treatment"],
        })

    expected_commands = {
        (SELF_TEST_LEGACY_BRANCH_ID, SELF_TEST_LEGACY_STEP_ID): set(),
        **{
            (spec["branch_id"], spec["step_id"]): {spec["command_id"]}
            for spec in SELF_TEST_COMMAND_PLACEMENTS
        },
    }
    for key, expected_ids in expected_commands.items():
        actual_ids = {command["command_id"] for command in steps[key]["commands"]}
        require(actual_ids == expected_ids, f"unexpected command set for {key}: {actual_ids}")
        steps[key]["commands"].sort(
            key=lambda command: (
                command["source"]["line_start"], command["source"]["line_end"],
                command["command_id"],
            )
        )
    return bindings


def command_key_index(
    entities: dict[tuple[str, ...], dict[str, Any]],
) -> dict[str, tuple[str, ...]]:
    index: dict[str, tuple[str, ...]] = {}
    for key in entities:
        if key[0] != "COMMAND":
            continue
        require(key[-1] not in index, f"duplicate command id in topology: {key[-1]}")
        index[key[-1]] = key
    return index


def rekey_self_test_command_target(
    level: str, target: dict[str, str], command_keys: dict[str, tuple[str, ...]],
) -> dict[str, str]:
    """Return the current coordinate for a known self-test command target."""
    command_id = target.get("command_id")
    specs = {spec["command_id"]: spec for spec in SELF_TEST_COMMAND_PLACEMENTS}
    if command_id not in specs:
        return copy.deepcopy(target)
    require(level == "COMMAND", f"{command_id} is bound at non-command level {level}")
    require(set(target) == set(TARGET_FIELDS["COMMAND"]), f"malformed target for {command_id}")
    spec = specs[command_id]
    expected = target_dict(command_keys[command_id])
    legacy = {
        "page_id": SELF_TEST_PAGE_ID,
        "test_set_id": SELF_TEST_SET_ID,
        "branch_id": SELF_TEST_LEGACY_BRANCH_ID,
        "step_id": SELF_TEST_LEGACY_STEP_ID,
        "command_id": command_id,
    }
    declared = {
        "page_id": SELF_TEST_PAGE_ID,
        "test_set_id": SELF_TEST_SET_ID,
        "branch_id": spec["branch_id"],
        "step_id": spec["step_id"],
        "command_id": command_id,
    }
    require(expected == declared, f"active topology disagrees with declared placement for {command_id}")
    require(target in (legacy, declared), f"unreviewed retained target coordinate for {command_id}")
    return expected


def normalize_preserved_projection_command_keys(
    records: list[dict[str, Any]], command_keys: dict[str, tuple[str, ...]],
) -> list[dict[str, Any]]:
    """Rekey only the three active current-projection rows; retain their data."""
    normalized: list[dict[str, Any]] = []
    seen = Counter()
    relevant = {spec["command_id"] for spec in SELF_TEST_COMMAND_PLACEMENTS}
    for original in records:
        row = copy.deepcopy(original)
        command_id = row["target"].get("command_id")
        if command_id in relevant:
            row["target"] = rekey_self_test_command_target(
                row["level"], row["target"], command_keys
            )
            seen[command_id] += 1
        normalized.append(row)
    require(
        seen == Counter({command_id: 1 for command_id in relevant}),
        f"unexpected preserved current-projection command rows: {dict(seen)}",
    )
    return normalized


def normalize_historical_self_test_bindings(
    results: dict[str, Any], command_keys: dict[str, tuple[str, ...]],
) -> set[str]:
    """Rekey active index pointers while preserving every observation/status.

    The evidence files and attempt records remain intact.  Their accounting
    correction chain points to the new retained topology-correction record.
    """
    counts = Counter()
    affected_attempts: set[str] = set()
    relevant = {spec["command_id"] for spec in SELF_TEST_COMMAND_PLACEMENTS}
    for result in results.get("procedure_results", []):
        if result["evidence_id"] == TOPOLOGY_CORRECTION_EVIDENCE or (
            result["evidence_id"] in COMMAND_PROOF_REVIEWER_EVIDENCE
        ):
            continue
        for target in result["targets"]:
            command_id = target["target"].get("command_id")
            if command_id not in relevant:
                continue
            require(
                result["evidence_id"] in SELF_TEST_HISTORICAL_BINDING_COUNTS,
                f"unreviewed historical self-test binding: {result['evidence_id']}",
            )
            target["target"] = rekey_self_test_command_target(
                target["level"], target["target"], command_keys
            )
            counts[result["evidence_id"]] += 1
            affected_attempts.add(result["attempt_id"])
    require(
        counts == Counter(SELF_TEST_HISTORICAL_BINDING_COUNTS),
        f"unexpected historical self-test binding population: {dict(counts)}",
    )
    return affected_attempts


def link_topology_accounting_correction(
    results: dict[str, Any], affected_attempt_ids: set[str],
) -> set[str]:
    """Append the correction to each affected attempt's accounting chain."""
    attempts = {row["attempt_id"]: row for row in results["attempts"]}
    require(len(attempts) == len(results["attempts"]), "duplicate V&V attempt id")
    expected_affected = {
        "ATTEMPT-2026-09-01-HOST-COMMAND-ASSESSMENT-01",
        "ATTEMPT-2026-09-01-HOST-CURRENT-RECONCILIATION-01",
        "ATTEMPT-2026-09-02-HOST-SELF-TEST-01",
        "ATTEMPT-2026-09-02-CLI-SET-API-KEY-PERMISSIONS-01",
        CURRENT_ATTEMPT,
    }
    require(
        affected_attempt_ids == expected_affected,
        f"unexpected attempts owning corrected bindings: {sorted(affected_attempt_ids)}",
    )
    linked_terminals: set[str] = set()
    for attempt_id in sorted(affected_attempt_ids):
        cursor_id = attempt_id
        seen: set[str] = set()
        while cursor_id != TOPOLOGY_CORRECTION_ATTEMPT:
            require(cursor_id not in seen, f"cyclic accounting correction at {cursor_id}")
            seen.add(cursor_id)
            cursor = attempts.get(cursor_id)
            require(cursor is not None, f"missing affected attempt {cursor_id}")
            next_id = cursor.get("accounting_corrected_by")
            if next_id is None:
                cursor["accounting_corrected_by"] = TOPOLOGY_CORRECTION_ATTEMPT
                linked_terminals.add(cursor_id)
                break
            require(next_id in attempts, f"missing accounting successor {next_id}")
            cursor_id = next_id
    return linked_terminals


def source_title(path: Path) -> str:
    match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', path.read_text(), re.MULTILINE)
    return match.group(1) if match else path.stem.replace("-", " ").title()


def normalize_text(value: str) -> str:
    inline_code: list[str] = []

    def protect_inline_code(match: re.Match[str]) -> str:
        token = f"\x00INLINE_CODE_{len(inline_code)}\x00"
        inline_code.append(f"`{normalize_code_text(match.group(1))}`")
        return token

    # CLI placeholders such as <machine_id> are literal content inside inline
    # code, not MDX/HTML tags. Protect code spans before removing actual markup.
    value = re.sub(r"`([^`\n]+)`", protect_inline_code, value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    for index, literal in enumerate(inline_code):
        value = value.replace(f"\x00INLINE_CODE_{index}\x00", literal)
    return value.strip()


def normalize_code_text(value: str) -> str:
    """Collapse code whitespace without treating CLI placeholders as MDX tags."""
    return re.sub(r"\s+", " ", value).strip()


def heading_index(lines: list[str]) -> list[tuple[int, str]]:
    headings = [(1, "Introduction")]
    fence: tuple[str, int] | None = None
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append((number, re.sub(r"`([^`]+)`", r"\1", match.group(1))))
    return headings


def heading_at(headings: list[tuple[int, str]], line: int) -> str:
    return next(title for number, title in reversed(headings) if number <= line)


def mask_mdx_comments(value: str) -> str:
    """Mask non-rendered MDX comments while preserving bytes-per-line geometry.

    Comment-looking text inside fenced code remains literal code.  Outside a
    fence, every non-newline character from ``{/*`` through ``*/}`` becomes a
    space so subsequent source spans still address the original file exactly.
    """
    output: list[str] = []
    in_comment = False
    fence: tuple[str, int] | None = None
    for line in value.splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if not in_comment and marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            output.append(line)
            continue
        if fence:
            output.append(line)
            continue
        masked: list[str] = []
        cursor = 0
        while cursor < len(line):
            if in_comment:
                end = line.find("*/}", cursor)
                if end < 0:
                    masked.append("\n" if line[cursor:] == "\n" else re.sub(r"[^\r\n]", " ", line[cursor:]))
                    cursor = len(line)
                else:
                    masked.append(re.sub(r"[^\r\n]", " ", line[cursor:end + 3]))
                    cursor = end + 3
                    in_comment = False
                continue
            start = line.find("{/*", cursor)
            if start < 0:
                masked.append(line[cursor:])
                cursor = len(line)
            else:
                masked.append(line[cursor:start])
                masked.append("   ")
                cursor = start + 3
                in_comment = True
        output.append("".join(masked))
    require(not in_comment, "unterminated MDX comment in material-claim source")
    return "".join(output)


def material_blocks(route: str, path: Path) -> list[dict[str, Any]]:
    """Conservatively inventory current material source blocks.

    A block is an auditable occurrence denominator, not proof that every sentence
    in it is true.  Volume Offers is replaced by a finer 39-claim reviewed map.
    """
    source_text = path.read_text(encoding="utf-8")
    raw_lines = source_text.splitlines()
    lines = mask_mdx_comments(source_text).splitlines()
    require(len(lines) == len(raw_lines), f"MDX comment masking changed line count: {path}")
    headings = heading_index(lines)
    blocks: list[tuple[int, int, str, str]] = []
    paragraph: list[tuple[int, str]] = []
    frontmatter = bool(lines and lines[0].strip() == "---")
    fence: tuple[str, int, int, list[str]] | None = None

    def flush() -> None:
        if not paragraph:
            return
        start, end = paragraph[0][0], paragraph[-1][0]
        raw = "\n".join(item[1] for item in paragraph)
        text = normalize_text(raw)
        paragraph.clear()
        # Standalone image alt text is an accessibility description, not an
        # independent product assertion.  Images are covered by the dedicated
        # accessibility/static checks instead of inflating the claim count.
        if re.fullmatch(r"\s*!\[[^\]]*\]\([^)]*\)\s*", raw):
            return
        if text and not re.fullmatch(r"[{}()[\],.;:'\"`/*_ -]+", text):
            blocks.append((start, end, heading_at(headings, start), text))

    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        if frontmatter:
            if index > 1 and stripped == "---":
                frontmatter = False
            continue
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= fence[1]:
                language, start, content = fence[2], fence[3], fence[4]
                text = normalize_code_text("\n".join(content))
                if text:
                    blocks.append((start, index, heading_at(headings, start), f"[{language or 'code'}] {text}"))
                fence = None
            else:
                fence[4].append(line)
            continue
        if marker:
            flush()
            fence = [marker.group(1)[0], len(marker.group(1)), marker.group(2).strip(), index, []]  # type: ignore[assignment]
            continue
        if re.match(r"^#{1,6}\s+", line):
            flush()
            continue
        if not stripped:
            flush()
            continue
        if re.match(r"^(?:import|export)\s+", stripped) or "persona-chips" in stripped:
            flush()
            continue
        frame_caption = re.fullmatch(
            r"<Frame\b[^>]*\bcaption=(?P<quote>['\"])(?P<caption>.*?)(?P=quote)[^>]*>",
            stripped,
        )
        if frame_caption:
            flush()
            text = normalize_text(frame_caption.group("caption"))
            if text:
                blocks.append((index, index, heading_at(headings, index), text))
            continue
        if re.fullmatch(r"</?[A-Za-z][^>]*>", stripped):
            flush()
            continue
        if re.fullmatch(r"\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?", stripped):
            flush()
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush()
            # A table header followed by its delimiter labels fields; it does
            # not itself assert product behavior.
            if index < len(lines) and re.fullmatch(
                r"\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?", lines[index].strip()
            ):
                continue
            text = normalize_text(" | ".join(cell.strip() for cell in stripped.strip("|").split("|")))
            if text:
                blocks.append((index, index, heading_at(headings, index), text))
            continue
        if re.match(r"^(?:[-*+] |\d+[.)] )", stripped):
            flush()
            text = normalize_text(re.sub(r"^(?:[-*+] |\d+[.)] )", "", stripped))
            if text:
                blocks.append((index, index, heading_at(headings, index), text))
            continue
        paragraph.append((index, line))
    flush()

    records: list[dict[str, Any]] = []
    page_id = f"PAGE-{route.lstrip('/').replace('/', '-')}"
    source_file = path.relative_to(REPO).as_posix()
    contextual_list_leadins = {
        "host/account-security-for-hosts.mdx": {
            23: {25, 26, 27, 28},
            38: {40, 41, 42, 43},
        },
        "host/datacenter-status.mdx": {33: {35, 36, 37, 38, 39}},
        "host/guide-to-taxes.mdx": {23: {25, 26, 27}},
        "host/hosting-agreement.mdx": {31: {33, 34, 35, 36}},
        "host/hosting-overview.mdx": {
            18: {20, 21, 22, 23},
            72: {74, 75, 76, 77},
        },
        "host/notifications.mdx": {29: {33}},
        "host/payment.mdx": {31: {33, 34, 35}},
        "host/workload-policy.mdx": {23: {25, 26, 27, 28, 29, 30}},
    }.get(source_file, {})
    retained_leadin_text = {
        "host/hosting-agreement.mdx": {
            31: "Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), listing a machine creates offers that clients can accept as rental contracts.",
        },
        "host/guide-to-taxes.mdx": {
            23: "Depending on your payout method, your payment provider may issue a tax form if you meet their reporting threshold.",
        },
        "host/hosting-overview.mdx": {
            72: "Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), existing contracts cannot be changed by editing the offer.",
        },
    }.get(source_file, {})
    contextual_text_overrides = {
        "host/account-security-for-hosts.mdx": {
            23: "Enable two-factor authentication on these accounts; it is especially important for:",
        },
        "host/guide-to-taxes.mdx": {
            23: "It is your responsibility to:",
        },
        "host/hosting-agreement.mdx": {
            31: "Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), for each active rental contract you commit to:",
        },
        "host/hosting-overview.mdx": {
            72: "Under the [Hosting Agreement](https://cloud.vast.ai/host/agreement), that means:",
        },
    }.get(source_file, {})
    contextual_source_lines = {
        "host/account-security-for-hosts.mdx": {
            23: [21, 23],
        },
    }.get(source_file, {})
    leadin_lines = set(contextual_list_leadins)
    context_by_item_line = {
        item_line: context_line
        for context_line, item_lines in contextual_list_leadins.items()
        for item_line in item_lines
    }
    for start, end, heading, text in blocks:
        if start in leadin_lines and start not in retained_leadin_text:
            # These incomplete lead-ins qualify the following list items; they
            # are not independent assertions.  Bind the context to each exact
            # item instead of manufacturing a dangling citation defect.
            continue
        raw = "\n".join(raw_lines[start - 1:end])
        if start in retained_leadin_text:
            text = retained_leadin_text[start]
        source_spans = [{"start": start, "end": end}]
        context_line = context_by_item_line.get(start)
        if context_line is not None:
            context_lines = contextual_source_lines.get(context_line, [context_line])
            context_raw = "\n".join(raw_lines[line - 1] for line in context_lines)
            context_text = contextual_text_overrides.get(context_line, context_raw)
            raw = f"{context_raw}\n{raw}"
            text = f"{normalize_text(context_text)} {text}"
            source_spans = [
                {"start": line, "end": line} for line in context_lines
            ] + source_spans
        if not text.startswith("["):
            for inline_literal in re.findall(r"`([^`\n]+)`", raw):
                require(
                    f"`{normalize_code_text(inline_literal)}`" in text,
                    f"inline-code literal lost during material-claim serialization: "
                    f"{path.relative_to(REPO)}:{start}-{end}",
                )
        basis = (
            f"{route}\0{heading}\0{start}\0{end}\0{sha256_bytes(raw.encode())}"
            if len(source_spans) == 1
            else f"{route}\0{heading}\0"
                 + ",".join(f"{span['start']}-{span['end']}" for span in source_spans)
                 + f"\0{sha256_bytes(raw.encode())}"
        )
        claim_id = "MCL-" + sha256_bytes(basis.encode())[:16]
        kind, lanes, citation_required = classify_claim(source_file, heading, text, raw)
        citation = citation_contract(raw, citation_required)
        owner_source_file = (
            f"{route.lstrip('/')}.mdx"
            if source_file.startswith("snippets/")
            else source_file
        )
        owner = owner_for(owner_source_file, kind)
        unresolved = unresolved_evidence_requirements(
            claim_id, route, source_file, text, lanes, owner
        )
        status = "FAIL" if citation["state"] == "ABSENT" else "UNVALIDATED"
        if status == "FAIL":
            for requirement in unresolved:
                if requirement["evidence_type"] == "AUTHORITATIVE_DOCUMENTATION_CITATION":
                    requirement["current_status"] = "FAIL"
        rationale = (
            "CONFIRMED_CITATION_DEFECT: this owner-governed claim requires an authoritative citation, and no citation is present in the exact source occurrence."
            if status == "FAIL"
            else "No claim-suitable retained source, runtime observation, or accountable-owner confirmation is bound to this exact current occurrence. Missing evidence alone is UNVALIDATED."
        )
        next_action = " ".join(item["next_action"] for item in unresolved)
        records.append({
            "claim_id": claim_id,
            "page_id": page_id,
            "scope": {
                "route": route, "source_file": source_file, "heading": heading,
                "source_spans": source_spans,
                "source_text_sha256": sha256_bytes(raw.encode()),
                "rendered_via": None,
            },
            "claim": {"text": text, "kind": kind,
                      "claim_limit": "This record identifies the current assertion; documentation text is not evidence for itself."},
            "evidence_requirement": {
                "types": lanes, "citation_required": citation_required,
                "rationale": evidence_requirement_rationale(lanes),
            },
            "citation": citation,
            "authority": {
                "source_refs": [], "state": "UNRESOLVED",
                "unresolved_owner_role": "; ".join(dict.fromkeys(
                    item["responsible_role"] for item in unresolved
                )),
                "unresolved_evidence_requirements": unresolved,
                "unresolved_question": "Which exact source, runtime environment/permission, owner decision, or citation listed by evidence lane supports this occurrence?",
            },
            "current": {
                "status": status,
                "rationale": rationale,
                "evidence_ids": [],
                "limitations": [
                    "Repository occurrence coverage is complete, but semantic validation remains open."
                    if status == "UNVALIDATED"
                    else "The failure establishes only that the required citation is absent; it does not decide whether the underlying claim is true."
                ],
            },
            "next_action": next_action,
        })
    return records


def rendered_dependencies(path: Path) -> list[dict[str, Any]]:
    """Return exact local MDX components rendered by one primary Host page."""
    source_file = path.relative_to(REPO).as_posix()
    text = path.read_text(encoding="utf-8")
    import_re = re.compile(
        r"^import\s+(?P<component>[A-Za-z][A-Za-z0-9_]*)\s+from\s+"
        r"(?P<quote>['\"])(?P<path>/snippets/[A-Za-z0-9._/-]+\.mdx)(?P=quote)[ \t]*;?[ \t]*$",
        re.MULTILINE,
    )
    dependencies: list[dict[str, Any]] = []
    for match in import_re.finditer(text):
        component = match.group("component")
        relative = match.group("path").lstrip("/")
        dependency = (REPO / relative).resolve()
        require(
            dependency.is_relative_to((REPO / "snippets").resolve()) and dependency.is_file(),
            f"invalid rendered MDX dependency in {source_file}: {relative}",
        )
        usage_re = re.compile(
            rf"^[ \t]*<{re.escape(component)}[ \t]*/>[ \t]*$", re.MULTILINE
        )
        usages = list(usage_re.finditer(text))
        require(
            len(usages) == 1,
            f"expected one rendered use of {component} in {source_file}, found {len(usages)}",
        )
        dependencies.append({
            "component": component,
            "source_file": relative,
            "source_sha256": sha256_path(dependency),
            "import_line": text.count("\n", 0, match.start()) + 1,
            "insertion_line": text.count("\n", 0, usages[0].start()) + 1,
        })
    dependencies.sort(key=lambda item: (item["insertion_line"], item["component"]))
    return dependencies


def rendered_page_sha256(page: dict[str, Any]) -> str:
    """Bind a primary page and every local component contributing rendered prose."""
    rows = [f"PRIMARY\0{page['source_file']}\0{page['source_sha256']}\n"]
    rows.extend(
        f"DEPENDENCY\0{item['component']}\0{item['source_file']}\0{item['source_sha256']}\0"
        f"{item['import_line']}\0{item['insertion_line']}\n"
        for item in page["rendered_dependencies"]
    )
    return sha256_bytes("".join(rows).encode())


def citation_ref_kind(href: str) -> str:
    if href.startswith(("/", "#")):
        return "LOCAL_DOCUMENTATION"
    normalized = href.casefold().split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if normalized in {
        "https://cloud.vast.ai/host/agreement",
        "https://vast.ai/terms",
        "https://www.vast.ai/terms",
    }:
        return "AUTHORITATIVE_SOURCE_CANDIDATE"
    if href.startswith(("https://", "http://")):
        if any(token in normalized for token in (
            "cloud.vast.ai/", "vastai.app.box.com/", "s3.amazonaws.com/vast.ai/",
        )):
            return "EXTERNAL_ACTION_OR_UI_DESTINATION"
        return "EXTERNAL_REFERENCE"
    return "EXTERNAL_CONTACT_OR_REFERENCE"


def citation_contract(raw: str, required: bool) -> dict[str, Any]:
    hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)", raw)
    hrefs.extend(re.findall(r"<((?:https?://|mailto:)[^>]+)>", raw))
    refs = [
        {"href": href, "kind": citation_ref_kind(href)}
        for href in dict.fromkeys(hrefs)
    ]
    authoritative_candidates = [
        ref for ref in refs
        if ref["kind"] == "AUTHORITATIVE_SOURCE_CANDIDATE"
    ]
    if not required:
        state = "NOT_REQUIRED"
        assessment = "This occurrence does not assert owner-governed Product, Finance, Legal, policy, contract, or account meaning requiring an authoritative citation."
    elif authoritative_candidates:
        state = "PRESENT_UNVERIFIED"
        assessment = "An authoritative-source candidate is linked, but its authority and exact support for the claim remain unvalidated until source-owner review."
    else:
        state = "ABSENT"
        assessment = (
            "The required authoritative citation is absent from this exact source occurrence. "
            "Repository-local documentation, action/UI destinations, upload/download links, "
            "and owner-contact links do not prove the claim."
        )
    return {"required": required, "state": state, "refs": refs, "assessment": assessment}


def classify_claim(source_file: str, heading: str, text: str, raw: str) -> tuple[str, list[str], bool]:
    lower = f"{heading} {text}".lower()
    body_lower = text.lower()
    # Code identifiers and instance/volume "contract IDs" are technical API
    # nouns, not legal or commercial assertions. Remove those narrow forms
    # only for policy detection; retain the original text and runtime/source
    # lanes unchanged. A separate term such as billing still selects the
    # accountable Product/Finance lane.
    policy_lower = re.sub(r"`[^`]+`", " ", lower)
    policy_body_lower = re.sub(r"`[^`]+`", " ", body_lower)
    technical_contract = (
        r"\b(?:new|temporary|volume|instance|the)\s+contract(?:\s+(?:id|identifier))?\b"
    )
    policy_lower = re.sub(technical_contract, " instance identifier ", policy_lower)
    policy_body_lower = re.sub(
        technical_contract, " instance identifier ", policy_body_lower
    )
    policy_lower = re.sub(r"\boffer/contract context\b", " rental context ", policy_lower)
    policy_body_lower = re.sub(
        r"\boffer/contract context\b", " rental context ", policy_body_lower
    )
    # These narrow operational phrases use contract/agreement as a runtime or
    # documentation-routing noun. They do not themselves assert the meaning
    # of a legal agreement or commercial contract.
    policy_lower = re.sub(r"\bhost-side contract events\b", " host lifecycle events ", policy_lower)
    policy_body_lower = re.sub(
        r"\bhost-side contract events\b", " host lifecycle events ", policy_body_lower
    )
    policy_lower = re.sub(r"\bexpired contract\b", " expired rental ", policy_lower)
    policy_body_lower = re.sub(r"\bexpired contract\b", " expired rental ", policy_body_lower)
    policy_lower = re.sub(
        r"\bnot a pricing or marketplace issue\b", " not a diagnostic category mismatch ", policy_lower
    )
    policy_body_lower = re.sub(
        r"\bnot a pricing or marketplace issue\b", " not a diagnostic category mismatch ", policy_body_lower
    )
    lanes: list[str] = []
    hrefs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)", text)
    navigation_index_row = bool(
        raw.strip().startswith("|")
        and not text.startswith("Honoring active contracts first |")
        and (
            heading.casefold() == "related pages"
            or source_file == "host/common-host-questions.mdx"
            or (
                source_file == "host/persona-decision-guide.mdx"
                and heading == "Common Questions"
            )
        )
    )
    navigation_handoff = bool(
        re.fullmatch(
            r"(?:For [^.,]+, see \[[^\]]+\]\([^)]+\)\.?(?:\s+|$))+",
            text,
            flags=re.IGNORECASE,
        )
    )
    # Only a whole-line local link is safe to close as a bounded route
    # contract. Rows and paragraphs that also make implementation, runtime,
    # policy, or topical-suitability assertions go through the normal claim
    # classifier even when they contain links.
    navigation = bool(
        hrefs
        and all(href.startswith(("/", "#")) for href in hrefs)
        and (
            navigation_index_row
            or navigation_handoff
            or re.fullmatch(
                r"(?:\[[^\]]+\]\([^)]+\)(?:[,;]\s*|\s+)?)+[.!]?",
                text,
            )
        )
    )
    workload_policy_subject = (
        source_file == "host/workload-policy.mdx"
        and bool(re.search(
            r"\b(?:do not|should not|illegal|abusive|malware|spam|attack|security bypass|"
            r"intellectual[- ]property|export[- ]controlled|sanctioned|restricted|mining|"
            r"terms|allowed|private renter data)\b",
            policy_lower,
        ))
    )
    commercial_contract_subject = (
        (source_file == "host/payment.mdx" and heading == "Payout Schedule")
        or (source_file == "host/pricing-your-listing.mdx" and heading == "Changing Price Later")
    )
    datacenter_program_requirement = (
        source_file == "host/datacenter-status.mdx"
        and (
            heading == "Requirements"
            or (heading == "Apply" and not body_lower.startswith("apply at "))
        )
    )
    datacenter_program_benefit = (
        source_file == "host/datacenter-status.mdx"
        and (
            heading == "Introduction"
            or body_lower.startswith((
                "secure cloud search eligibility",
                "better reliability/search signals",
                "direct discord or slack channel with vast",
            ))
        )
    )
    dedicated_host_account_policy = (
        source_file == "host/account-hosting-agreement.mdx"
        and heading == "Do I need a separate host account?"
        and body_lower.startswith("yes. use a dedicated account for hosting.")
    )
    account_security_guidance = (
        source_file == "host/account-security-for-hosts.mdx"
        and heading in {"Two-Factor Authentication", "API Keys"}
        and bool(re.search(
            r"\b(?:enable two-factor authentication|two-factor authentication on these accounts|"
            r"treat host automation keys like production secrets)\b",
            policy_lower,
        ))
    )
    revenue_component_subject = (
        source_file == "host/earning.mdx"
        and heading == "Revenue Components"
        and body_lower.startswith((
            "gross host revenue", "[text]", "gpu compute", "storage |",
            "bandwidth |", "volumes |",
        ))
    )
    rental_dedication_subject = bool(re.search(
        r"\b(?:gaming|workstation)\b.*\bduring rentals?\b.*\brented machines? should be dedicated\b",
        policy_lower,
    ))
    page_scope_statement = (
        source_file == "host/account-hosting-agreement.mdx"
        and heading == "Introduction"
        and body_lower.startswith("use this page when ")
    )
    docs_routing_statement = (
        source_file == "host/hosting-overview.mdx"
        and body_lower.startswith("after signup, use this docs path ")
    )
    policy = not navigation and not page_scope_statement and not docs_routing_statement and (
        bool(re.search(
            r"\b(?:agreement|contracts?|commitment|legal|policy|terms of service|tax(?:es|ation)?|"
            r"payouts?|payment|invoices?|billing|earnings?|pricing|prices?|fee|responsib(?:le|ility|ilities)|"
            r"must not|prohibited|permitted|allowed|account status|provider policy)\b",
            policy_lower,
        ))
        or workload_policy_subject
        or commercial_contract_subject
        or rental_dedication_subject
        or datacenter_program_requirement
        or datacenter_program_benefit
        or dedicated_host_account_policy
        or account_security_guidance
        or revenue_component_subject
    )
    citation_required = policy and not account_security_guidance and (
        bool(re.search(
            r"\b(?:agreement|contracts?|legal|terms of service|tax(?:es|ation)?|tax form|vat|invoices?|"
            r"provider policy|regulat(?:ion|ory)|prohibited|not permitted|must not|do not|should not|"
            r"illegal|abusive|malware|spam|attack|security bypass|intellectual[- ]property|"
            r"export[- ]controlled|sanctioned|restricted|mining|"
            r"required by|responsible for|responsibilit(?:y|ies)|liable|mandatory|cannot be fully disabled|"
            r"account access|paid means|pending means|"
            r"direct bank transfer|ach|swift|wire transfer|wise|paypal|stripe)\b",
            policy_body_lower,
        ))
        or bool(re.search(r"\b\d+\s+(?:business\s+)?(?:days?|weeks?)\b", policy_body_lower))
        or bool(re.search(r"(?:at least|minimum(?:\s+payout)?(?: of)?)[^$]{0,24}\$\s*\d+", policy_body_lower))
        or commercial_contract_subject
        or rental_dedication_subject
        or datacenter_program_requirement
        or datacenter_program_benefit
        or dedicated_host_account_policy
    )
    fenced_command = text.startswith("[")
    provider_tax_policy_statement = (
        source_file == "host/guide-to-taxes.mdx"
        and heading == "United States Hosts"
        and body_lower.startswith("depending on your payout method")
    )
    implementation = (
        bool(re.search(r"\b(?:vastai|api|cli|sdk|command|option|flag|field|config|daemon|installer|endpoint|error|threshold)\b", lower))
        and not provider_tax_policy_statement
    )
    frame_caption = bool(re.search(r"<Frame\b[^>]*\bcaption=", raw))
    ui_heading = bool(re.search(
        r"\b(?:earnings|payout|members|machines|billing|notifications?|settings|market)\b.*"
        r"\b(?:page|console|dashboard)\b",
        heading.casefold(),
    ))
    ui_observable = bool(
        ui_heading
        or re.search(
            r"\b(?:console|dashboard|dialog|tabs?|menus?|buttons?|settings(?:\s+page)?|"
            r"controls?|user interface|ui)\b",
            lower,
        )
        or re.search(r"\b(?:account|earnings)\s*>\s*[a-z]", body_lower)
        or re.match(
            r"^(?:open|click|select|save|view|download|switch|enter|assign|send|"
            r"go\s+to|turn\s+(?:on|off))\b",
            body_lower,
        )
    )
    live_action_path = (
        (source_file == "host/datacenter-status.mdx" and body_lower.startswith("apply at "))
        or (source_file == "host/community.mdx" and body_lower.startswith("join [discord]"))
        or (source_file == "host/guide-to-taxes.mdx" and "submit your w9 here" in body_lower)
    )
    runtime = (
        frame_caption or ui_observable or fenced_command or account_security_guidance
        or datacenter_program_benefit
        or live_action_path
        or bool(re.search(r"\b(?:run|returns?|appears?|creates?|deletes?|mount|attach|install|restart|reboot|rent|workload|network|port|gpu|machine|instance|volume|verify|fails?|passes?)\b", lower))
    )
    if navigation:
        return "NAVIGATION_CONTRACT", ["REPOSITORY_STATIC_CHECK"], False
    if implementation:
        lanes.append("CANONICAL_IMPLEMENTATION_SOURCE")
    if runtime:
        lanes.append("RUNTIME_OR_UI_OBSERVATION")
    if policy:
        lanes.append("ACCOUNTABLE_OWNER_CONFIRMATION")
    if citation_required:
        lanes.append("AUTHORITATIVE_DOCUMENTATION_CITATION")
    if not lanes:
        lanes.append("CANONICAL_IMPLEMENTATION_SOURCE")
    kind = "POLICY_OR_COMMERCIAL" if policy else "RUNTIME_BEHAVIOR" if runtime else "IMPLEMENTATION_OR_CONCEPT"
    return kind, list(dict.fromkeys(lanes)), citation_required


def owner_for(source_file: str, kind: str) -> str:
    stem = Path(source_file).stem
    if kind == "NAVIGATION_CONTRACT":
        return "Host Docs information-architecture owner"
    if stem in {"guide-to-taxes", "hosting-agreement", "account-hosting-agreement", "workload-policy"}:
        return "Product and Legal policy owner"
    if stem in {"earning", "payment", "pricing-your-listing", "optimization-guide", "market-metrics"}:
        return "Product and Finance owner"
    if stem == "datacenter-status":
        return "Datacenter program implementation, Product, Trust/Security, and Legal source owner"
    if stem in {"machine-errors", "common-errors-diagnostics"}:
        return "Backend and Host-daemon source owner"
    if stem == "network-ports":
        return "Backend and Networking source owner"
    if stem in {"how-to-self-test", "self-test-reference", "understanding-verification", "verification-stages", "supported-hardware"}:
        return "Self-Test and Verification source owner"
    if stem in {"host-teams", "account-security-for-hosts", "cli-api-sdk"}:
        return "Teams and account engineering owner"
    if stem in {
        "first-24-hours", "fleet-operations", "hardware-prep", "headless-install",
        "installing-host-software", "maintenance-windows", "quickstart",
        "reliability-uptime", "removing-recreating-machines", "storage-setup",
    }:
        return "Host installer and operations engineering owner"
    if stem == "vms":
        return "VM platform and Host integration source owner"
    if stem in {"common-host-questions", "community", "glossary", "hosting-overview", "persona-decision-guide"}:
        return "Host Product and Documentation content owner"
    if stem == "not-in-search":
        return "Marketplace search and Host listing backend owner"
    if stem == "notifications":
        return "Notifications backend and Product owner"
    if kind == "POLICY_OR_COMMERCIAL":
        return "Accountable Product policy owner"
    return f"Host implementation source owner for {stem}"


def unresolved_evidence_requirements(
    claim_id: str, route: str, source_file: str, claim_text: str,
    lanes: list[str], source_owner_role: str,
) -> list[dict[str, str]]:
    """Name the distinct actor/source needed for every unresolved lane."""
    source_stem = Path(route).stem
    policy_text = claim_text.casefold()
    if source_stem == "workload-policy":
        accountable_owner_role = "Product, Trust, and Legal policy owner"
    elif source_stem == "datacenter-status":
        accountable_owner_role = "Datacenter Product, Trust/Security, and Legal program owner"
    elif source_stem == "payment":
        accountable_owner_role = "Product, Finance, and Legal payout owner"
    elif source_stem == "earning":
        accountable_owner_role = (
            "Product, Finance, and Legal owner"
            if re.search(
                r"\b(?:agreement|contracts?|commitment|legal|tax(?:es|ation)?|tax form|vat|liable)\b",
                policy_text,
            )
            else "Product and Finance owner"
        )
    elif source_stem in {"pricing-your-listing", "optimization-guide"}:
        accountable_owner_role = "Product, Finance, and Legal marketplace owner"
    else:
        tax_domain = bool(re.search(r"\b(?:tax|taxes|taxation|tax form|vat)\b", policy_text))
        finance_domain = bool(re.search(
            r"\b(?:payouts?|payment|billing|invoices?|earnings?|revenue|pricing|prices?|fee|credit)\b",
            policy_text,
        ))
        legal_domain = bool(re.search(
            r"\b(?:agreement|contracts?|commitment|legal|terms of service|liable)\b",
            policy_text,
        ))
        trust_domain = bool(re.search(
            r"\b(?:security|trust|prohibited|not permitted|must not|policy|workload|data protection)\b",
            policy_text,
        ))
        roles = ["Product"]
        if finance_domain or tax_domain:
            roles.append("Finance")
        if trust_domain:
            roles.append("Trust/Security")
        if legal_domain or tax_domain or trust_domain:
            roles.append("Legal")
        if roles == ["Product"]:
            accountable_owner_role = "Accountable Host Product policy owner"
        else:
            accountable_owner_role = f"{', '.join(roles[:-1])}, and {roles[-1]} owner" if len(roles) > 2 else f"{roles[0]} and {roles[1]} owner"
    records: list[dict[str, str]] = []
    for lane in lanes:
        if lane == "CANONICAL_IMPLEMENTATION_SOURCE":
            records.append({
                "evidence_type": lane, "prerequisite_kind": "SOURCE",
                "responsible_role": source_owner_role,
                "required_input": (
                    f"An immutable canonical code, API-schema, configuration, generator, or generated-reference locator that supports {claim_id} on {route}."
                ),
                "next_action": (
                    f"The {source_owner_role} supplies the exact repository, revision, path, and symbol/operation locator; bind it to {claim_id} and retain the focused source check."
                ),
            })
        elif lane == "RUNTIME_OR_UI_OBSERVATION":
            records.append({
                "evidence_type": lane, "prerequisite_kind": "ENVIRONMENT_OR_PERMISSION",
                "responsible_role": "Authorized Host/API operator",
                "required_input": (
                    f"A representative authorized environment, least-privilege permission where needed, expected observable, and cleanup boundary for the runtime behavior asserted by {claim_id} on {route}."
                ),
                "next_action": (
                    f"An authorized Host/API operator runs only an approved representative check for {claim_id} and retains inputs, outputs/UI state, environment identity, timestamps, and cleanup evidence."
                ),
            })
        elif lane == "ACCOUNTABLE_OWNER_CONFIRMATION":
            records.append({
                "evidence_type": lane, "prerequisite_kind": "OWNER_CONFIRMATION",
                "responsible_role": accountable_owner_role,
                "required_input": f"A dated accountable-owner decision supporting the exact policy/commercial meaning of {claim_id} on {route}.",
                "next_action": f"The {accountable_owner_role} confirms, narrows, or rejects {claim_id} in a dated authoritative source, then the page and evidence binding are updated.",
            })
        elif lane == "AUTHORITATIVE_DOCUMENTATION_CITATION":
            records.append({
                "evidence_type": lane, "prerequisite_kind": "AUTHORITATIVE_CITATION",
                "responsible_role": accountable_owner_role,
                "required_input": f"A stable authoritative citation that supports the exact owner-governed statement in {claim_id}.",
                "next_action": f"Obtain the source from the {accountable_owner_role}, add the exact citation without broadening the claim, and retain a link/source-binding retest.",
            })
        elif lane == "REPOSITORY_STATIC_CHECK":
            records.append({
                "evidence_type": lane, "prerequisite_kind": "REPOSITORY_STATE",
                "responsible_role": "Host Docs information-architecture owner",
                "required_input": f"The exact current route, fragment, and destination source for {claim_id}.",
                "next_action": f"Resolve the route and fragment for {claim_id} against the current repository and retain the exact destination hash.",
            })
        else:
            raise ReconciliationError(f"unknown evidence lane for {claim_id}: {lane}")
    for record in records:
        record["current_status"] = "UNVALIDATED"
    return records


def evidence_requirement_rationale(lanes: list[str]) -> str:
    labels = {
        "CANONICAL_IMPLEMENTATION_SOURCE": "implementation claims require canonical Vast code, API schema, configuration, or generated source",
        "RUNTIME_OR_UI_OBSERVATION": "runtime behavior requires retained execution or UI evidence",
        "ACCOUNTABLE_OWNER_CONFIRMATION": "product, financial, policy, account, or legal meaning requires accountable-owner authority",
        "AUTHORITATIVE_DOCUMENTATION_CITATION": "the page must cite the authoritative source; its own prose cannot prove itself",
        "REPOSITORY_STATIC_CHECK": "navigation and repository structure require an exact retained local check",
    }
    return "; ".join(labels[item] for item in lanes) + "."


def canonical_ref(
    repository: str, revision: str, path: str, locator: str, source_kind: str,
) -> dict[str, str]:
    """Return one exact, machine-checkable canonical-source reference."""
    return {
        "repository": repository,
        "revision": revision,
        "path": path,
        "locator": locator,
        "source_kind": source_kind,
    }


def local_source_ref(path: str, locator: str, source_kind: str) -> dict[str, str]:
    source = REPO / path
    require(source.is_file(), f"missing local authority source: {path}")
    return canonical_ref(
        "vast-ai/docs",
        f"sha256:{sha256_path(source)}",
        path,
        locator,
        source_kind,
    )


def heading_fragment_ids(path: Path) -> set[str]:
    """Return explicit IDs and conservative GitHub/Mint-style heading slugs."""
    text = path.read_text(encoding="utf-8")
    identifiers = set(re.findall(r"\bid=['\"]([^'\"]+)['\"]", text))
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        label = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(1))
        label = re.sub(r"<[^>]+>", "", label)
        label = html.unescape(label).replace("&", " and ")
        label = re.sub(r"[`*_~]", "", label).casefold()
        slug = re.sub(r"[^a-z0-9]+", "-", label).strip("-")
        if slug:
            identifiers.add(slug)
    return identifiers


def resolve_local_doc_href(source_file: str, href: str) -> dict[str, Any]:
    """Resolve one repository-local documentation route without network I/O."""
    require(href.startswith(("/", "#")), f"not a local documentation href: {href}")
    target, separator, fragment = href.partition("#")
    target = target.split("?", 1)[0]
    if not target:
        destination = REPO / source_file
        route = "/" + str(Path(source_file).with_suffix(""))
    else:
        route = target.rstrip("/") or "/"
        relative = target.lstrip("/").rstrip("/")
        candidates = [REPO / f"{relative}.mdx", REPO / relative / "index.mdx"]
        destination = next((candidate for candidate in candidates if candidate.is_file()), None)
        require(destination is not None, f"missing local documentation route {href} from {source_file}")
    resolved = destination.resolve()
    require(resolved.is_relative_to(REPO.resolve()), f"local documentation route escapes repository: {href}")
    if separator and fragment:
        require(fragment in heading_fragment_ids(resolved),
                f"missing local documentation fragment #{fragment} in {resolved.relative_to(REPO)}")
    relative_path = resolved.relative_to(REPO).as_posix()
    return {
        "href": href,
        "route": route,
        "fragment": fragment or None,
        "target_file": relative_path,
        "target_sha256": sha256_path(resolved),
        "source_ref": local_source_ref(
            relative_path,
            f"route {route}" + (f" fragment #{fragment}" if fragment else ""),
            "ROUTE_DESTINATION_SOURCE",
        ),
    }


def bind_pure_local_navigation_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Close only whole-line local-link claims with exact route/fragment proof."""
    bindings: list[dict[str, Any]] = []
    for claim in claims:
        if claim["claim"]["kind"] != "NAVIGATION_CONTRACT":
            continue
        refs = claim["citation"]["refs"]
        require(refs and all(ref["kind"] == "LOCAL_DOCUMENTATION" for ref in refs),
                f"navigation claim is not entirely local: {claim['claim_id']}")
        destinations = [
            resolve_local_doc_href(claim["scope"]["source_file"], ref["href"])
            for ref in refs
        ]
        claim["evidence_requirement"] = {
            "types": ["REPOSITORY_STATIC_CHECK"],
            "citation_required": False,
            "rationale": "This whole-line navigation claim requires exact local route and fragment resolution; linked-page semantic truth remains separately governed.",
        }
        claim["authority"] = {
            "source_refs": [destination["source_ref"] for destination in destinations],
            "state": "BOUND",
            "unresolved_owner_role": None,
            "unresolved_evidence_requirements": [],
            "unresolved_question": None,
        }
        claim["current"] = {
            "status": "PASS",
            "rationale": "Every local destination in this whole-line navigation occurrence resolves to an exact current repository file and fragment where applicable.",
            "evidence_ids": [NAVIGATION_EVIDENCE],
            "limitations": [
                "PASS is limited to local route/fragment existence; it does not validate the linked page's implementation, runtime, policy, pricing, contract, account, or legal claims."
            ],
        }
        claim["claim"]["claim_limit"] = (
            "This atomic claim is limited to the whole-line local navigation destination; documentation text does not prove linked-page semantics."
        )
        claim["next_action"] = None
        bindings.append({
            "claim_id": claim["claim_id"],
            "page_id": claim["page_id"],
            "status": "PASS",
            "source_file": claim["scope"]["source_file"],
            "heading": claim["scope"]["heading"],
            "source_spans": claim["scope"]["source_spans"],
            "source_text_sha256": claim["scope"]["source_text_sha256"],
            "destinations": [{key: value for key, value in destination.items() if key != "source_ref"}
                             for destination in destinations],
            "evidence_role": "EXACT_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION",
        })
    require(len(bindings) == 140, f"expected 140 bounded local navigation claims, found {len(bindings)}")
    return bindings


def bind_exact_command_claims(
    claims: list[dict[str, Any]], sets: dict[str, Any], scores: dict[str, Any],
) -> list[dict[str, Any]]:
    """Bind exact fenced-command occurrences to their carrier evidence.

    Score-3 PASS is accepted only for the bounded exact command occurrence.
    Score-2 PASS remains UNVALIDATED because its retained support is partial.
    Concrete command FAIL/BLOCKED dispositions propagate to the exact fenced
    occurrence but never to unrelated prose or to a parent semantic rollup.
    """
    command_by_location: dict[tuple[str, int, int], list[dict[str, Any]]] = {}
    for page in sets["pages"]:
        for test_set in page["test_sets"]:
            for branch in test_set["branches"]:
                for step in branch["steps"]:
                    for command in step["commands"]:
                        source = command["source"]
                        key = (source["file"], source["line_start"], source["line_end"])
                        command_by_location.setdefault(key, []).append(command)
    score_by_id = {row["command_id"]: row for row in scores["records"]}
    for spec in RECONCILED_WORKFLOW_COMMANDS:
        score_by_id.setdefault(spec["command_id"], {
            "command_id": spec["command_id"], "score": 2,
            "execution_status": "BLOCKED",
            "direct_evidence_ids": [COMMAND_COVERAGE_EVIDENCE],
            "rationale": "Exact authored occurrence and safety gate only; Host behavior did not run.",
        })

    bindings: list[dict[str, Any]] = []
    for claim in claims:
        if not claim["claim"]["text"].startswith("[") or len(claim["scope"]["source_spans"]) != 1:
            continue
        span = claim["scope"]["source_spans"][0]
        matches = [
            command
            for (source_file, start, end), commands in command_by_location.items()
            if source_file == claim["scope"]["source_file"]
            and span["start"] <= start <= end <= span["end"]
            and start - span["start"] <= 2 and span["end"] - end <= 2
            for command in commands
            if normalize_code_text(command["text"]) in claim["claim"]["text"]
        ]
        if not matches:
            continue
        require(len(matches) == 1, f"ambiguous exact command claim: {claim['claim_id']}")
        command = matches[0]
        score = score_by_id.get(command["command_id"])
        require(score is not None, f"exact command claim lacks score record: {command['command_id']}")
        execution_status = score["execution_status"]
        direct_ids = list(score.get("direct_evidence_ids", []))
        prior_status = claim["current"]["status"]
        decision = "PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED"
        for requirement in claim["authority"].get("unresolved_evidence_requirements", []):
            if requirement["evidence_type"] != "RUNTIME_OR_UI_OBSERVATION" or not direct_ids:
                continue
            requirement["bound_evidence_ids"] = direct_ids
            if execution_status == "PASS" and score["score"] == 3:
                requirement["current_status"] = "PASS"
                requirement["evidence_state"] = "SATISFIED_FOR_EXACT_COMMAND_CEILING"
            elif execution_status == "BLOCKED":
                requirement["current_status"] = "BLOCKED"
                requirement["evidence_state"] = "BLOCKER_CONFIRMED_RUNTIME_NOT_EXECUTED"
            elif execution_status == "FAIL":
                requirement["current_status"] = "UNVALIDATED"
                requirement["evidence_state"] = "ADVERSE_RESULT_OUTSIDE_LITERAL_SYNTAX_CLAIM"
            else:
                requirement["current_status"] = "UNVALIDATED"
                requirement["evidence_state"] = "PARTIAL"
        required_lanes = set(claim["evidence_requirement"]["types"])
        execution_supported_lanes = {"RUNTIME_OR_UI_OBSERVATION"}
        if (execution_status == "PASS" and score["score"] == 3
                and required_lanes <= execution_supported_lanes):
            require(direct_ids, f"score-3 command lacks direct evidence: {command['command_id']}")
            claim["current"] = {
                "status": "PASS",
                "rationale": "The exact fenced-command occurrence is bound to a score-3 PASS carrier with current non-superseded direct retained evidence.",
                "evidence_ids": direct_ids,
                "limitations": [
                    "PASS is limited to the exact fenced command and the carrier's recorded direct-proof ceiling; no surrounding prose or parent procedure inherits it."
                ],
            }
            claim["authority"].update({
                "state": "EVIDENCE_BOUND", "unresolved_owner_role": None,
                "unresolved_evidence_requirements": [], "unresolved_question": None,
            })
            claim["next_action"] = None
            decision = "BOUNDED_PASS_FROM_SCORE_3_DIRECT_EVIDENCE"
        elif execution_status == "FAIL":
            require(direct_ids, f"failed command lacks direct evidence: {command['command_id']}")
            claim["current"]["evidence_ids"] = direct_ids
            claim["current"]["limitations"] = [
                "The retained adverse command result concerns a security/output property not asserted by the literal fenced syntax alone; the exact documentation claim remains UNVALIDATED rather than being falsely contradicted."
            ]
            claim["next_action"] = (
                f"Correct the retained defect for {command['command_id']} without erasing history, explicitly define the expected safety/output contract, and retain both syntax/source and behavioral retests."
            )
            decision = "ADVERSE_EVIDENCE_BOUND_WITHOUT_OVERBROAD_CLAIM_FAIL"
        elif execution_status == "BLOCKED":
            require(command["command_id"] in ROOT_BLOCKED_COMMANDS,
                    f"blocked exact command lacks a concrete root prerequisite: {command['command_id']}")
            kind, description = ROOT_BLOCKED_COMMANDS[command["command_id"]]
            claim["current"] = {
                "status": "BLOCKED",
                "rationale": f"UNAVAILABLE_PREREQUISITE {kind}: {description}",
                "evidence_ids": direct_ids,
                "limitations": ["Static or partial evidence does not establish the prohibited or unavailable runtime behavior."],
                "unavailable_prerequisite": {"kind": kind, "description": description},
            }
            for requirement in claim["authority"].get("unresolved_evidence_requirements", []):
                requirement["current_status"] = (
                    "BLOCKED"
                    if requirement["evidence_type"] == "RUNTIME_OR_UI_OBSERVATION"
                    else "UNVALIDATED"
                )
            claim["next_action"] = (
                f"Under explicit authorization, provide this prerequisite for {command['command_id']}: {description} Then retain the exact observation and cleanup."
            )
            decision = "EXACT_BLOCKER_PROPAGATED"
        else:
            claim["current"]["evidence_ids"] = direct_ids
            if direct_ids:
                claim["current"]["limitations"] = [
                    (
                        "The runtime lane has score-3 direct support, but at least one separately required canonical-source lane remains UNVALIDATED."
                        if score["score"] == 3 and execution_status == "PASS"
                        else "Direct carrier evidence is retained but its score is partial; it does not validate the full exact command claim."
                    )
                ]
                claim["next_action"] = (
                    f"Close every still-UNVALIDATED evidence lane for {command['command_id']}; current carrier context: {score['rationale']} Retain a claim-suitable source or runtime retest before changing the overall status."
                )
        binding = {
            "claim_id": claim["claim_id"], "command_id": command["command_id"],
            "page_id": claim["page_id"], "source_file": claim["scope"]["source_file"],
            "heading": claim["scope"]["heading"], "source_spans": claim["scope"]["source_spans"],
            "source_text_sha256": claim["scope"]["source_text_sha256"],
            "command_source": command["source"], "score": score["score"],
            "command_execution_status": execution_status,
            "prior_claim_status": prior_status, "current_claim_status": claim["current"]["status"],
            "direct_evidence_ids": direct_ids, "decision": decision,
        }
        claim["current"]["command_evidence_binding"] = copy.deepcopy(binding)
        bindings.append(binding)
    require(len(bindings) == 104,
            f"expected 104 exact fenced-command claim bindings, found {len(bindings)}")
    bounded_passes = sum(
        item["decision"] == "BOUNDED_PASS_FROM_SCORE_3_DIRECT_EVIDENCE"
        for item in bindings
    )
    require(bounded_passes == 8,
            f"expected eight runtime-only score-3 fenced-command bounded PASS bindings, found {bounded_passes}")
    return bindings


def volume_source_refs(claim_id: str) -> list[dict[str, str]]:
    """Exact authority refs for bounded PASS claims on Volume Offers.

    The refs intentionally name files and symbols/operations.  A directory,
    generated evidence record, or the prose under review is not an authority.
    """
    cli_storage = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/cli/commands/storage.py",
        "search__volumes, create__volume, delete__volume, show__volumes, list__volume, list__volumes, and unlist__volume command registrations",
        "CANONICAL_CLI_SOURCE",
    )
    cli_instance = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/cli/commands/instances.py",
        "create__instance volume-link arguments and request delegation",
        "CANONICAL_CLI_SOURCE",
    )
    api_storage = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/api/storage.py",
        "show_volumes, create_volume, delete_volume, list_volume, list_volumes, and unlist_volume request builders",
        "CANONICAL_API_CLIENT_SOURCE",
    )
    cli_machine = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/cli/commands/machines.py",
        "list_machine_impl, list__machine, and list__machines volume-offer arguments",
        "CANONICAL_CLI_SOURCE",
    )
    api_machine = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/api/machines.py",
        "list_machine request payload fields vol_size and vol_price",
        "CANONICAL_API_CLIENT_SOURCE",
    )
    api_instance = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/api/instances.py",
        "build_volume_info and build_create_instance_payload",
        "CANONICAL_API_CLIENT_SOURCE",
    )
    cli_clone = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/cli/commands/storage.py",
        "clone__volume registration and source/destination volume syntax",
        "CANONICAL_CLI_SOURCE",
    )
    api_clone = canonical_ref(
        "vast-ai/vast-cli", CLI_REVISION,
        "vastai/api/storage.py",
        "clone_volume source owned-volume ID and destination offer ID request builder",
        "CANONICAL_API_CLIENT_SOURCE",
    )
    openapi_volume = local_source_ref(
        "api-reference/openapi/yaml/list_volume.yaml",
        "list_volume and list_volumes request schemas",
        "OPENAPI_SOURCE",
    )
    openapi_machine = local_source_ref(
        "api-reference/openapi/yaml/list_machine.yaml",
        "list machine request schema fields vol_size and vol_price",
        "OPENAPI_SOURCE",
    )
    nav_source = local_source_ref(
        "docs.json", "Host, CLI, SDK, and guide route declarations", "ROUTE_CONFIGURATION"
    )
    renter_volume_page = resolve_local_doc_href(
        "host/volume-offers.mdx", "/guides/instances/storage/volumes"
    )["source_ref"]
    mapping: dict[str, list[dict[str, str]]] = {
        "VOL-C04": [cli_machine, api_machine],
        "VOL-C05": [cli_storage, api_storage, openapi_volume],
        "VOL-C06": [api_instance],
        "VOL-C07": [cli_storage, cli_machine, cli_instance],
        "VOL-C08": [cli_storage, api_storage],
        "VOL-C09": [cli_storage, api_storage, openapi_volume],
        "VOL-C10": [cli_storage, api_storage, api_instance, cli_clone, api_clone],
        "VOL-C12": [cli_machine, api_machine, cli_storage, api_storage],
        "VOL-C14": [cli_storage, api_storage, openapi_volume],
        "VOL-C16": [api_instance],
        "VOL-C20": [cli_storage, api_storage],
        "VOL-C21": [cli_machine, api_machine, openapi_machine],
        "VOL-C22": [cli_storage, api_storage, openapi_volume],
        "VOL-C23": [cli_storage, api_storage, openapi_volume],
        "VOL-C24": [cli_storage, api_storage, openapi_volume],
        "VOL-C34": [nav_source],
        "VOL-C35": [nav_source],
        "VOL-C36": [cli_storage, api_storage, cli_machine, api_machine, api_instance],
        "VOL-C37": [renter_volume_page],
    }
    return copy.deepcopy(mapping.get(claim_id, []))


def volume_unresolved_requirements(
    claim_id: str, claim_text: str, lanes: list[str], aggregate_owner: str,
) -> list[dict[str, str]]:
    """Separate Volume source, runtime, and decision prerequisites by lane."""
    source_roles = {
        "VOL-C01": "Volumes backend lifecycle source owner",
        "VOL-C02": "Volumes and scheduler backend source owner",
        "VOL-C03": "Instances and Volumes backend source owners",
        "VOL-C11": "Shipped Host installer source owner",
        "VOL-C13": "Volumes allocation backend source owner",
        "VOL-C15": "Volumes and Instances ownership/cascade source owner",
        "VOL-C18": "Instances and Volumes cascade source owner",
        "VOL-C19": "Volumes enforcement and error-contract source owner",
        "VOL-C25": "Host daemon and storage-accounting source owner",
        "VOL-C26": "Volumes and storage-allocation source owner",
        "VOL-C27": "Storage-accounting implementation source owner",
        "VOL-C29": "Volumes placement and migration source owner",
        "VOL-C30": "Volumes and scheduler constraint source owner",
        "VOL-C31": "Volumes lifecycle source owner",
        "VOL-C32": "Volumes and VM compatibility source owner",
        "VOL-C33": "Volumes durability, replication, and recovery source owner",
    }
    decision_roles = {
        "VOL-C11": "Host SRE and Product owner",
        "VOL-C27": "Storage Product and SRE owner",
        "VOL-C28": "Product, SRE, Support, and Trust policy owner",
        "VOL-C31": "Volumes Product owner",
        "VOL-C33": "Volumes Product and SRE owner",
    }
    requirements: list[dict[str, str]] = []
    for lane in lanes:
        if lane == "CANONICAL_IMPLEMENTATION_SOURCE":
            role = source_roles.get(claim_id, aggregate_owner)
            requirements.append({
                "evidence_type": lane, "prerequisite_kind": "SOURCE",
                "responsible_role": role,
                "required_input": f"The exact immutable implementation revision and locator governing {claim_id}: {claim_text}",
                "next_action": f"The {role} supplies repository, revision, path, and symbol/operation locators for {claim_id}; bind and retest them.",
            })
        elif lane == "RUNTIME_OR_UI_OBSERVATION":
            role = "Authorized Volumes Host/renter operator"
            requirements.append({
                "evidence_type": lane, "prerequisite_kind": "ENVIRONMENT_AND_AUTHORIZATION",
                "responsible_role": role,
                "required_input": f"Explicit paid/mutating/destructive authorization where applicable and a disposable representative environment for {claim_id}: {claim_text}",
                "next_action": f"The {role} retains target IDs, environment/revisions, inputs, positive/adverse observations, costs where applicable, and cleanup for {claim_id}.",
            })
        elif lane in {"ACCOUNTABLE_OWNER_CONFIRMATION", "AUTHORITATIVE_DOCUMENTATION_CITATION"}:
            role = decision_roles.get(claim_id, aggregate_owner)
            kind = "OWNER_CONFIRMATION" if lane == "ACCOUNTABLE_OWNER_CONFIRMATION" else "AUTHORITATIVE_CITATION"
            requirements.append({
                "evidence_type": lane, "prerequisite_kind": kind,
                "responsible_role": role,
                "required_input": f"A dated authoritative decision/source supporting the exact owner-governed meaning of {claim_id}: {claim_text}",
                "next_action": f"The {role} confirms, narrows, or rejects {claim_id}; cite the dated authority and retain a focused source/link retest.",
            })
        elif lane == "REPOSITORY_STATIC_CHECK":
            requirements.append({
                "evidence_type": lane, "prerequisite_kind": "REPOSITORY_STATE",
                "responsible_role": "Host Docs information-architecture owner",
                "required_input": f"Exact current local route and fragment resolution for {claim_id}.",
                "next_action": f"Retain route, fragment, destination file, and hash for {claim_id}.",
            })
        else:
            raise ReconciliationError(f"unknown Volume evidence lane for {claim_id}: {lane}")
    for requirement in requirements:
        requirement["current_status"] = "UNVALIDATED"
    return requirements


def volume_claims(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return the reviewed 39-claim Volume map and two retired claim defects."""
    lines = path.read_text(encoding="utf-8").splitlines()
    route = "/host/volume-offers"
    page_id = "PAGE-host-volume-offers"
    # id, spans, heading, claim, status, evidence requirement, owner/source,
    # rationale, limitation, next action, evidence lanes.
    seeds = [
        ("VOL-C01", [(15,15)], "Introduction", "A local volume is persistent storage.", "BLOCKED", "Backend lifecycle source plus retained create/write/destroy/re-attach/read execution.", "Volumes backend owner and authorized renter operator", "The backend lifecycle source and the paid, mutating representative run are unavailable under this task authorization.", "CLI terminology does not prove persistence.", "Obtain the exact backend lifecycle revision and explicit paid/mutation authorization, then retain the lifecycle run.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C02", [(15,15)], "Introduction", "A volume is backed by one physical Host and may attach only on that machine.", "BLOCKED", "Scheduling enforcement source plus same-machine success and cross-machine rejection.", "Volumes and scheduler backend owner", "The enforcement source and authorized representative runtime are unavailable.", "Machine-id fields corroborate identity but do not prove enforcement.", "Bind the scheduler constraint and retain positive/adverse runs.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C03", [(15,15)], "Introduction", "Volume storage is separate from the container disk; destroying the instance keeps the volume.", "BLOCKED", "Backend ownership/cascade source plus destructive before/after evidence.", "Instances and Volumes backend owners", "The cascade source and destructive lifecycle authorization are unavailable.", "Separate client endpoints are indirect evidence only.", "Inspect cascade policy and retain create/write/destroy/re-attach/read evidence.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C04", [(19,19)], "Introduction", "A Host can publish capacity and price as a volume offer.", "PASS", "Exact CLI/API request construction.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned client source constructs the host volume-offer request.", "Static interface conformance only; marketplace appearance was not tested.", "Retain an authorized before/after marketplace observation if runtime validation is required.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C05", [(20,20)], "Introduction", "A renter accepts an offer ID to create an owned volume; the CLI/API also use volume-contract terminology.", "PASS", "Exact command/API schema and terminology source.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned command/API sources distinguish offer creation from an owned volume.", "Static contract only; ownership and billing policy were not validated.", "Obtain Product/Finance authority for billing language before adding it.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C06", [(21,21),(36,36)], "Introduction / Identifiers And Values", "The renter supplies a chosen mount path during instance creation.", "PASS", "CLI registration, request construction, and pure payload tests.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned client code emits mount_path for volume attachment.", "No container was mounted.", "Run an authorized paid create/attach and inspect the path for runtime validation.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C07", [(24,24),(101,109)], "Introduction / Command Map", "The command map assigns Host offer tasks to list machine, list volume(s), and unlist volume, and renter tasks to search, create, show, attach, and delete volume interfaces.", "PASS", "Exact command registration and role separation.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned command registration supports every Host/renter role mapping.", "No account action or runtime effect was exercised.", "Keep runtime effects separately classified.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C08", [(33,33)], "Identifiers And Values", "list volume takes a machine ID.", "PASS", "CLI positional registration and API payload.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned source registers and sends the machine identifier.", "Does not establish storage-pool semantics.", "No further repository action is required for the bounded interface claim.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C09", [(34,34)], "Identifiers And Values", "Search results expose a volume-offer ID and unlist volume consumes a listing ID.", "PASS", "Search schema plus unlist request construction.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned sources expose and consume the listing identifier.", "Marketplace removal was not observed.", "Retain authorized before/after evidence for runtime removal.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C10", [(35,35)], "Identifiers And Values", "An owned-volume ID is returned by show volumes and accepted by instance-link, volume-clone, and delete interfaces.", "PASS", "Schema and exact request construction.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned show, link, clone, and delete sources expose and consume the owned-volume identifier.", "Fixed-size and lifecycle behavior are separate unresolved claims.", "Validate lifecycle constraints separately.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C11", [(40,40)], "Volume Lifecycle", "Hosts should place Docker storage on fast SSD/NVMe with XFS project quotas.", "BLOCKED", "Canonical shipped installer/config source, owner decision, and representative runtime.", "Host Installer, SRE, and Product owner", "The shipped installer revision and accountable applicability decision are unavailable.", "The local wizard corroborates the gate but is not the full installer/backend.", "Obtain the shipped installer source/revision and owner decision, then retain a disposable-Host observation.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION","ACCOUNTABLE_OWNER_CONFIRMATION"]),
        ("VOL-C12", [(41,41)], "Volume Lifecycle", "An offer can be created with a machine listing or separately.", "PASS", "Exact request construction for both paths.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned source contains both request paths.", "No marketplace action ran.", "Retain authorized publication evidence if end-to-end validation is required.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C13", [(41,41),(77,77)], "Volume Lifecycle / Shared Disk Capacity", "Published size is a maximum aggregate rentable capacity and publication alone creates no renter volume.", "BLOCKED", "Backend allocation transaction source and capacity-boundary runs.", "Volumes backend owner", "The backend enforcement source and mutating capacity-boundary run are unavailable.", "Client help is a contract hint, not enforcement proof.", "Bind the allocation implementation and retain offer-only, partial, exact, and over-capacity observations.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C14", [(42,42)], "Volume Lifecycle", "A renter searches offers and selects a size.", "PASS", "Search/create registration and request schema.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned sources expose search and size selection.", "Does not prove persistence or charging.", "Keep persistence and billing as separate claims.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C15", [(42,42)], "Volume Lifecycle", "The allocated volume persists independently of an instance.", "BLOCKED", "Backend ownership source and destructive lifecycle run.", "Volumes and Instances backend owner plus authorized renter operator", "The source and destructive representative run are unavailable.", "Separate endpoints are indirect evidence.", "Bind the exact backend ownership/cascade source, then retain create/write/attach/destroy/re-attach/read runtime evidence under explicit authorization.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C16", [(43,43)], "Volume Lifecycle", "A new or existing volume is linked in the create-instance request.", "PASS", "Pure payload implementation and tests.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned source and payload tests distinguish new and existing volume forms.", "No instance was created.", "Run both paths only under paid/mutation authorization.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C17", [(43,43)], "Volume Lifecycle", "The linked volume appears at the selected path in a running Docker instance.", "BLOCKED", "Representative paid runtime inspection.", "Authorized renter operator with paid instance and volume", "Paid/mutating runtime is explicitly outside this task authorization.", "Static payload construction cannot prove a working mount.", "Retain target IDs, revision, cost, mount/read/write observation, and cleanup.", ["RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C18", [(44,44)], "Volume Lifecycle", "Destroying an instance leaves its volume intact.", "BLOCKED", "Backend cascade source and destructive before/after evidence.", "Instances and Volumes backend owner plus authorized disposable target", "The cascade source and destructive run are unavailable.", "No retained volume lifecycle run exists.", "Inspect cascade policy and execute the preservation test under explicit authorization.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C19", [(44,44)], "Volume Lifecycle", "Every attached instance must be destroyed before the volume can be deleted.", "BLOCKED", "Backend enforcement/error contract plus attached rejection and unattached success.", "Volumes backend owner", "Backend enforcement source and destructive adverse/positive runs are unavailable.", "CLI/API docstrings state the prerequisite but do not prove enforcement.", "Confirm the error contract and retain both outcomes.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C20", [(45,45)], "Volume Lifecycle", "Unlisting an offer is distinct from deleting an owned volume.", "PASS", "Separate endpoint contracts.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned source implements separate unlist and delete operations.", "Marketplace effects were not observed.", "Retain authorized listing-removal evidence if runtime validation is required.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C21", [(51,60)], "Publish Local Storage", "list machine accepts --vol_size, --vol_price, and --end_date; zero disables the volume offer.", "PASS", "Multiline CLI signature plus exact request construction.", f"vast-ai/vast-cli@{CLI_REVISION}", "The corrected multiline verifier and pinned source validate every option spelling and request field.", "Runtime zero/nonzero behavior was not exercised.", "Retain an authorized before/after listing observation for runtime semantics.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C22", [(62,69)], "Publish Local Storage", "list volume accepts machine ID, --size, --price_disk, and --end_date.", "PASS", "Multiline CLI signature, request construction, and OpenAPI request parity.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "The corrected verifier and semantic OpenAPI drift check validate the complete request form.", "No marketplace mutation ran.", "Retain authorized publication evidence if runtime validation is required.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C23", [(71,71)], "Publish Local Storage", "list volumes applies one size, price, and end-date tuple to several machine IDs.", "PASS", "CLI positional registration and API payload.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned source and current OpenAPI support the multi-machine request shape.", "No multi-machine mutation ran.", "Retain before/after evidence only with explicit account-mutation authorization.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C24", [(71,71)], "Publish Local Storage", "--end_date sets the volume offer expiration.", "PASS", "CLI registration/request source and OpenAPI request field.", f"vast-ai/vast-cli@{CLI_REVISION} and current OpenAPI", "Pinned source supports an independent volume-offer expiration field.", "No claim is made that it must match a GPU-offer commitment window.", "No repository-local action remains for this bounded interface claim.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C25", [(75,75)], "Shared Disk Capacity", "Local volumes, instance disks, stopped instances, cached images, and other allocations use one machine pool.", "BLOCKED", "Canonical Host storage/accounting implementation plus before/after observations.", "Host daemon and storage backend owner", "The daemon/accounting source and representative Host environment are unavailable.", "Installer wording does not prove marketplace accounting.", "Bind storage-accounting source and retain per-allocation before/after values.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C26", [(77,77)], "Shared Disk Capacity", "Renter-created size is allocated from the offer and shared pool.", "BLOCKED", "Backend allocation implementation plus capacity evidence.", "Volumes and storage backend owner", "The allocation source and mutating runtime are unavailable.", "Client help does not expose the backend transaction.", "Inspect allocation code and retain offer capacity before/after create/delete.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C27", [(79,79)], "Shared Disk Capacity", "A 200 GB volume drawn from a 500 GB offer must be included in storage planning; headroom is needed.", "UNVALIDATED", "Confirmed allocation premise plus accountable capacity guidance.", "Storage Product and SRE owner", "Arithmetic is clear, but no claim-suitable accounting evidence or required-headroom decision is retained.", "The example is not proof of platform accounting.", "After capacity accounting is confirmed, source a headroom rule or label it non-normative advice.", ["CANONICAL_IMPLEMENTATION_SOURCE","ACCOUNTABLE_OWNER_CONFIRMATION"]),
        ("VOL-C28", [(82,82)], "Shared Disk Capacity", "Hosts should not manually remove renter files and should use normal lifecycle/support paths for reconciliation failures.", "BLOCKED", "Authoritative security, operations, and support policy.", "Product, SRE, Support, and Trust policy owner", "The required handling/support policy owner decision is unavailable.", "Prudent advice and docs prose are not authoritative policy.", "Obtain and cite the exact approved runbook without retaining renter content.", ["ACCOUNTABLE_OWNER_CONFIRMATION","AUTHORITATIVE_DOCUMENTATION_CITATION"]),
        ("VOL-C29", [(89,89)], "Local Volume Limits", "A local volume stays on its creation machine.", "BLOCKED", "Backend placement/migration source plus lifecycle observation.", "Volumes and scheduler backend owner", "Placement source and representative runtime are unavailable.", "machine_id fields do not prove non-migration.", "Bind the exact placement/migration implementation source, then retain a representative create/attach/reuse lifecycle observation on the same and a different machine.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C30", [(90,90)], "Local Volume Limits", "Attachment is restricted to instances on the same machine.", "BLOCKED", "Backend constraint plus same-machine success and cross-machine rejection.", "Volumes and scheduler backend owner", "Constraint source and paid/mutating runs are unavailable.", "Client/OpenAPI fields do not encode equality enforcement.", "Bind the constraint and retain positive/adverse outcomes.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C31", [(91,91)], "Local Volume Limits", "Volume size is fixed after creation.", "BLOCKED", "Backend lifecycle contract and resize attempt.", "Volumes backend and Product owner", "The lifecycle source/owner decision and representative resize behavior are unavailable.", "Absence of a public resize endpoint is not proof.", "Obtain the lifecycle contract and retain supported/unsupported resize evidence.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION","ACCOUNTABLE_OWNER_CONFIRMATION"]),
        ("VOL-C32", [(92,92)], "Local Volume Limits", "Local volumes work with Docker instances, not VM instances.", "BLOCKED", "Backend compatibility constraint plus Docker success and VM rejection.", "Volumes, VM backend, and Product owner", "The compatibility source and paid/mutating positive/adverse runs are unavailable.", "The current public schema has no mutual-exclusion rule.", "Confirm the backend rule, update the schema if applicable, and retain Docker-positive/VM-negative evidence.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION"]),
        ("VOL-C33", [(93,93)], "Local Volume Limits", "A local volume is persistent storage but not an off-machine backup.", "BLOCKED", "Lifecycle evidence plus authoritative resilience/backup definition.", "Volumes Product and SRE owner", "Persistence, locality, and recovery semantics require unavailable source/owner/runtime evidence.", "The warning derives from unresolved premises.", "Bind the exact durability/replication/recovery implementation source, obtain the dated Volumes Product and SRE failure-domain decision, and retain representative persistence and machine-loss runtime observations.", ["CANONICAL_IMPLEMENTATION_SOURCE","RUNTIME_OR_UI_OBSERVATION","ACCOUNTABLE_OWNER_CONFIRMATION"]),
        ("VOL-C34", [(95,95)], "Local Volume Limits", "The page routes storage maintenance to the Maintenance Windows workflow.", "PASS", "Repository-local destination and rendered-link check.", "Current docs navigation", "The unsupported hosting-commitment statement was removed; the current sentence is a bounded navigation handoff whose destination exists.", "This PASS does not validate the linked page's operational or contract claims.", "Validate the linked workflow under its own claim contracts.", ["REPOSITORY_STATIC_CHECK"]),
        ("VOL-C35", [(111,118)], "Related Pages", "All local Related Pages and command-reference destinations exist.", "PASS", "Repository-local link existence and rendered navigation.", "Current docs tree", "All current local targets resolve in the repository and Host link analysis has no finding.", "Linked-page semantic claims are outside this link-existence result.", "Retain browser click evidence in the rendered review pass.", ["REPOSITORY_STATIC_CHECK"]),
        ("VOL-C36", [(29,29)], "Identifiers And Values", "Machine, volume-offer, owned-volume, and mount-path identifiers have distinct interface roles and are not interchangeable.", "PASS", "Exact CLI/API registration and request-construction roles for every identifier.", f"vast-ai/vast-cli@{CLI_REVISION}", "Pinned client sources consume each identifier in a distinct operation or payload field.", "Static interface separation does not establish backend ownership, scheduling, or lifecycle enforcement.", "Keep the unresolved lifecycle and enforcement claims separate.", ["CANONICAL_IMPLEMENTATION_SOURCE"]),
        ("VOL-C37", [(47,47)], "Volume Lifecycle", "The renter workflow link resolves to the central Volumes guide.", "PASS", "Exact repository-local route resolution.", "Current docs tree", "The local renter Volumes destination resolves to its exact current source file.", "This PASS establishes navigation only; it does not validate the renter workflow semantics.", "Validate the linked workflow under its own claim contracts.", ["REPOSITORY_STATIC_CHECK"]),
        ("VOL-C38", [(60,60)], "Publish Local Storage", "Hosts should pass an explicit volume size and price so advertised capacity is intentional.", "UNVALIDATED", "A dated accountable Product decision for this publishing guidance.", "Volumes Product owner", "No dated accountable-owner decision is retained for the guidance.", "The CLI fields prove the inputs exist, not that this recommendation is universally appropriate.", "The Volumes Product owner confirms, narrows, or removes the guidance and the decision is retained.", ["ACCOUNTABLE_OWNER_CONFIRMATION"]),
        ("VOL-C39", [(71,71)], "Publish Local Storage", "Hosts should review a volume-offer expiration date before publishing.", "UNVALIDATED", "A dated accountable Product decision for this publishing guidance.", "Volumes Product owner", "No dated accountable-owner decision is retained for the guidance.", "The expiration field proves the input exists, not the scope or necessity of this recommendation.", "The Volumes Product owner confirms, narrows, or removes the guidance and the decision is retained.", ["ACCOUNTABLE_OWNER_CONFIRMATION"]),
    ]
    records: list[dict[str, Any]] = []
    for claim_id, spans, heading, text, status, requirement, authority, rationale, limitation, action, lanes in seeds:
        raw = "\n".join("\n".join(lines[start - 1:end]) for start, end in spans)
        citation = citation_contract(raw, "AUTHORITATIVE_DOCUMENTATION_CITATION" in lanes)
        if citation["state"] == "ABSENT":
            status = "FAIL"
            rationale = "CONFIRMED_CITATION_DEFECT: the exact owner-governed Volume claim requires an authoritative citation, and no citation is present."
            limitation = "The failure establishes the missing citation only; it does not establish whether the underlying policy advice is true."
            action = f"Obtain the authoritative source or dated decision from {authority}, add the exact citation, and retain the focused source/link retest."
        source_refs = volume_source_refs(claim_id)
        is_source = bool(source_refs)
        require(is_source == (status == "PASS"),
                f"{claim_id}: bounded PASS claims require exact refs; unresolved claims must name an owner")
        unresolved = [] if is_source else volume_unresolved_requirements(
            claim_id, text, lanes, authority
        )
        unresolved_owner_role = (
            None if is_source
            else "; ".join(dict.fromkeys(
                requirement["responsible_role"] for requirement in unresolved
            ))
        )
        for unresolved_item in unresolved:
            unresolved_item["current_status"] = (
                "FAIL"
                if status == "FAIL" and unresolved_item["evidence_type"] == "AUTHORITATIVE_DOCUMENTATION_CITATION"
                else "BLOCKED" if status == "BLOCKED"
                else "UNVALIDATED"
            )
        records.append({
            "claim_id": claim_id, "page_id": page_id,
            "scope": {"route": route, "source_file": "host/volume-offers.mdx", "heading": heading,
                      "source_spans": [{"start": start, "end": end} for start, end in spans],
                      "source_text_sha256": sha256_bytes(raw.encode()),
                      "rendered_via": None},
            "claim": {"text": text, "kind": "VOLUME_ATOMIC_CLAIM",
                      "claim_limit": limitation},
            "evidence_requirement": {"types": lanes,
                                     "citation_required": "AUTHORITATIVE_DOCUMENTATION_CITATION" in lanes,
                                     "rationale": requirement},
            "citation": citation,
            "authority": {"source_refs": source_refs,
                          "state": "BOUND" if is_source else "UNRESOLVED",
                          "unresolved_owner_role": unresolved_owner_role,
                          "unresolved_evidence_requirements": unresolved,
                          "unresolved_question": None if is_source else f"Provide each exact source, runtime authorization/environment, decision, or citation listed by evidence lane for {claim_id}."},
            "current": {"status": status, "rationale": rationale,
                        "evidence_ids": [VOLUME_EVIDENCE] if status in {"PASS", "BLOCKED", "FAIL"} else [],
                        "limitations": [limitation]},
            "next_action": action,
        })
    retired = [
        {
            "claim_id": "VOL-C24-HISTORICAL", "status": "FAIL",
            "source": "host/volume-offers.mdx:71 at pre-edit SHA-256 2be619b3d1ff66014a4301fa8a40ab17dcd13e48af5f78eed2d50e90fd1d37ad",
            "claim": "Volume-offer end date should use the same commitment window as GPU offers.",
            "failure": "A required Product/Legal source was absent; documentation text and client code could not authorize the contract claim.",
            "correction": "The sentence now states only the source-supported expiration-field behavior.",
            "retest_evidence_id": VOLUME_EVIDENCE,
        },
        {
            "claim_id": "VOL-C34-HISTORICAL", "status": "FAIL",
            "source": "host/volume-offers.mdx:95 at pre-edit SHA-256 2be619b3d1ff66014a4301fa8a40ab17dcd13e48af5f78eed2d50e90fd1d37ad",
            "claim": "Disk health and availability are part of the Host commitment and maintenance must not interrupt active volume contracts.",
            "failure": "A required Product/Legal/Operations source was absent.",
            "correction": "The sentence is now a bounded navigation handoff to the separately governed maintenance workflow.",
            "retest_evidence_id": VOLUME_EVIDENCE,
        },
    ]
    return records, retired


def command_record(command: tuple[str, str, int, int, str, str], source_lines: list[str]) -> dict[str, Any]:
    command_id, _step, start, end, text, treatment = command
    raw = "\n".join(source_lines[start - 1:end])
    require(text in raw, f"Volume command {command_id} no longer matches lines {start}-{end}")
    return {
        "command_id": command_id, "text": text,
        "source": {"file": "host/volume-offers.mdx", "line_end": end, "line_start": start,
                   "section": "Publish Local Storage" if start < 97 else "Command Map",
                   "source_type": "authored", "text_sha256": sha256_bytes(text.encode())},
        "treatment": treatment, "execution_status": "UNVALIDATED", "attempt_ids": [],
        "evidence_ids": [], "behavior_score": None, "score_rationale": None, "finding_ids": [],
    }


def add_reconciled_workflow_commands(sets: dict[str, Any]) -> list[dict[str, Any]]:
    """Add the three independently inventoried authored command occurrences.

    The active generated topology is also this function's next input, so first
    remove only these generator-owned carriers.  Historical evidence and every
    other command carrier remain untouched.
    """
    generated_ids = (
        {spec["command_id"] for spec in RECONCILED_WORKFLOW_COMMANDS}
        | RETIRED_RECONCILIATION_COMMAND_IDS
    )
    step_index: dict[tuple[str, str], dict[str, Any]] = {}
    for page in sets["pages"]:
        for test_set in page["test_sets"]:
            for branch in test_set["branches"]:
                for step in branch["steps"]:
                    step["commands"] = [
                        command for command in step["commands"]
                        if command["command_id"] not in generated_ids
                    ]
                    step_index[(page["page_id"], step["step_id"])] = step

    bindings: list[dict[str, Any]] = []
    for spec in RECONCILED_WORKFLOW_COMMANDS:
        step = step_index.get((spec["page_id"], spec["step_id"]))
        require(step is not None, f"missing target step for {spec['command_id']}")
        source = REPO / spec["file"]
        lines = source.read_text(encoding="utf-8").splitlines()
        raw = "\n".join(lines[spec["line_start"] - 1:spec["line_end"]])
        require(raw == spec["text"], (
            f"authored command occurrence {spec['inventory_id']} changed at "
            f"{spec['file']}:{spec['line_start']}-{spec['line_end']}"
        ))
        step["commands"].append({
            "command_id": spec["command_id"],
            "text": spec["text"],
            "source": {
                "file": spec["file"], "line_start": spec["line_start"],
                "line_end": spec["line_end"], "section": spec["section"],
                "source_type": "authored", "text_sha256": sha256_bytes(spec["text"].encode()),
            },
            "inventory_id": spec["inventory_id"],
            "applicability": spec["applicability"],
            "treatment": spec["treatment"], "execution_status": "BLOCKED",
            "attempt_ids": [CURRENT_ATTEMPT],
            "evidence_ids": [COMMAND_COVERAGE_EVIDENCE],
            "behavior_score": 2,
            "score_rationale": (
                "Exact authored occurrence and conservative safety classification are retained; "
                "the prohibited representative Host operation was not executed."
            ),
            "finding_ids": ["F-HOST-PROCEDURE-COMMAND-COVERAGE"],
        })
        bindings.append({
            "command_id": spec["command_id"], "inventory_id": spec["inventory_id"],
            "page_id": spec["page_id"], "step_id": spec["step_id"],
            "source_file": spec["file"], "heading": spec["section"],
            "line_start": spec["line_start"], "line_end": spec["line_end"],
            "text_sha256": sha256_bytes(spec["text"].encode()),
            "status": "BLOCKED", "treatment": spec["treatment"],
            "applicability": spec["applicability"],
        })
    return bindings


def normalize_procedure_source_scopes(sets: dict[str, Any]) -> int:
    """Make each parent scope contain every exact child command occurrence."""
    adjusted = 0
    for page in sets["pages"]:
        for test_set in page["test_sets"]:
            context = test_set["source_context"]
            require(context["file"] == page["source_file"],
                    f"test-set source does not match page: {test_set['test_set_id']}")
            set_spans: list[dict[str, int]] = []
            headings = list(context["headings"])
            for branch in test_set["branches"]:
                for step in branch["steps"]:
                    for command in step["commands"]:
                        source = command["source"]
                        require(source["file"] == context["file"],
                                f"cross-file command carrier in {step['step_id']}")
                        if not any(
                            span["start"] <= source["line_start"]
                            and span["end"] >= source["line_end"]
                            for span in step["source_lines"]
                        ):
                            step["source_lines"].append({
                                "start": source["line_start"], "end": source["line_end"]
                            })
                            step["source_lines"].sort(key=lambda span: (span["start"], span["end"]))
                            adjusted += 1
                        if source["section"] not in step["source_sections"]:
                            step["source_sections"].append(source["section"])
                        if source["section"] not in headings:
                            headings.append(source["section"])
                    set_spans.extend(step["source_lines"])
            require(set_spans, f"test set has no exact source spans: {test_set['test_set_id']}")
            context["line_start"] = min(span["start"] for span in set_spans)
            context["line_end"] = max(span["end"] for span in set_spans)
            context["headings"] = headings
            for branch in test_set["branches"]:
                for step in branch["steps"]:
                    for command in step["commands"]:
                        source = command["source"]
                        require(context["line_start"] <= source["line_start"] <= source["line_end"] <= context["line_end"],
                                f"command outside normalized test-set scope: {command['command_id']}")
    return adjusted


def make_volume_page() -> dict[str, Any]:
    path = REPO / "host/volume-offers.mdx"
    lines = path.read_text(encoding="utf-8").splitlines()
    commands_by_step: dict[str, list[dict[str, Any]]] = {}
    for command in VOLUME_COMMANDS:
        commands_by_step.setdefault(command[1], []).append(command_record(command, lines))

    def step(step_id: str, instruction: str, sections: list[str], spans: list[tuple[int, int]],
             dependencies: list[str], expected: str) -> dict[str, Any]:
        return {
            "step_id": step_id, "instruction": instruction, "role": "checkpoint", "required": True,
            "dependencies": dependencies, "source_sections": sections,
            "source_lines": [{"start": start, "end": end} for start, end in spans],
            "expected_observables": [expected],
            "failure_behavior": ["Record FAIL for an observed discrepancy, UNVALIDATED for missing proof, or BLOCKED only for a named unavailable prerequisite."],
            "cleanup_required": False, "execution_classification": "STATIC_REPOSITORY_INSPECTION",
            "execution_status": "UNVALIDATED", "blocker_ids": [],
            "commands": commands_by_step.get(step_id, []),
        }

    set_specs = [
        ("TS-VOL-C01", "VOL-C01", "Volume lifecycle and authority map",
         "Bind every volume concept, identifier, lifecycle, capacity, limit, and policy claim to suitable source, runtime evidence, or an exact unresolved owner.",
         ["Introduction", "Identifiers And Values", "Volume Lifecycle", "Shared Disk Capacity", "Local Volume Limits"], 15, 95,
         "VOL-C01-B-source-owner", [
             step("VOL-C01-S01", "Trace the offer/owned-volume distinction, identifier semantics, and lifecycle assertions to canonical implementation, retained runtime evidence, or an explicitly unresolved owner role.", ["Introduction","Identifiers And Values","Volume Lifecycle"], [(15,24),(27,36),(40,47)], [], "Every claim has an exact evidence requirement and source/owner disposition."),
             step("VOL-C01-S02", "Trace shared-pool allocation, headroom, renter-file safety, and support claims to storage implementation/runtime or authoritative policy.", ["Shared Disk Capacity"], [(75,82)], ["VOL-C01-S01"], "Storage-accounting and policy claims name their exact unavailable prerequisites."),
             step("VOL-C01-S03", "Trace locality, attachment, fixed-size, Docker-only, backup, and maintenance claims to suitable evidence without treating documentation as evidence for itself.", ["Local Volume Limits"], [(87,95)], ["VOL-C01-S02"], "Limits are separated into bounded static, runtime, and owner-confirmation claims."),
         ]),
        ("TS-VOL-E01", "VOL-E01", "Machine-offer volume options",
         "Verify the exact list-machine volume-option form and zero-size semantics against pinned CLI registration and request construction.",
         ["Publish Local Storage"], 49, 60, "VOL-E01-B-machine-offer", [
             step("VOL-E01-S01", "Verify the full multiline list-machine form and every continuation option.", ["Publish Local Storage"], [(54,57)], [], "All three option spellings and the positional machine ID match pinned CLI source."),
             step("VOL-E01-S02", "Verify that zero disables the machine volume offer and explicit size/price values are represented by the canonical interface.", ["Publish Local Storage"], [(60,60)], ["VOL-E01-S01"], "The bounded static interface statement matches pinned CLI registration/request code."),
         ]),
        ("TS-VOL-E02", "VOL-E02", "Separate and multi-machine volume offers",
         "Verify separate and multi-machine forms, OpenAPI request parity, and the narrowed expiration-field statement.",
         ["Publish Local Storage"], 62, 71, "VOL-E02-B-separate-offer", [
             step("VOL-E02-S01", "Verify the full multiline list-volume form and every continuation option.", ["Publish Local Storage"], [(65,68)], [], "Every option matches pinned CLI registration and request construction."),
             step("VOL-E02-S02", "Verify the multi-machine interface and expiration field against pinned CLI code and the current OpenAPI request contract.", ["Publish Local Storage"], [(71,71)], ["VOL-E02-S01"], "The multi-machine request and expiration field match both sources; no contract-alignment policy is claimed."),
         ]),
        ("TS-VOL-C02", "VOL-C02", "Host and renter command-role map",
         "Verify every task-to-command mapping and Related Pages destination without claiming runtime execution.",
         ["Command Map", "Related Pages"], 97, 118, "VOL-C02-B-role-map", [
             step("VOL-C02-S01", "Verify Host task-to-command mappings; do not duplicate the list-volumes carrier already selected on line 71.", ["Command Map"], [(101,104)], [], "Each Host role mapping resolves to pinned command registration and request code."),
             step("VOL-C02-S02", "Verify renter task-to-command mappings and every Related Pages destination.", ["Command Map","Related Pages"], [(105,109),(111,118)], [], "Each renter command exists and every repository-local destination resolves."),
         ]),
    ]
    test_sets = []
    for set_id, procedure_id, title, goal, headings, start, end, branch_id, steps in set_specs:
        test_sets.append({
            "test_set_id": set_id, "procedure_id": procedure_id, "title": title, "goal": goal,
            "context": {"environment": "Current local docs tree and pinned canonical source objects",
                        "intended_user": "Host documentation reviewer",
                        "representativeness_limit": "Static inspection cannot validate marketplace, persistence, scheduling, billing, contract, mount, or cleanup behavior."},
            "prerequisites": ["Current Volume page bytes", f"Pinned Vast CLI revision {CLI_REVISION}", "Current OpenAPI source and generated contract"],
            "access_classes": ["source-inspection", "documentation-citation", "source-owner"],
            "safety_constraints": ["Do not invoke credentialed, paid, mutating, destructive, privileged, WAN, Host, or workload operations."],
            "expected_final_observables": ["Every scoped claim has an evidence type, source or owner, status rationale, limitation, and next action."],
            "failure_behavior": ["Preserve discrepancies as FAIL; do not convert missing proof into a generic blocker."],
            "limitations": ["No runtime behavior or accountable-owner decision is inferred from code or documentation."],
            "cleanup": ["None; the procedure creates no external state."],
            "source_context": {"file": "host/volume-offers.mdx", "headings": headings,
                               "line_end": end, "line_start": start,
                               "rendered_route": "/host/volume-offers", "rendered_status": "UNVALIDATED"},
            "execution_status": "UNVALIDATED", "attempt_ids": [],
            "branches": [{"branch_id": branch_id,
                          "condition": "The current page and exact local/pinned sources are available for non-mutating inspection.",
                          "execution_status": "UNVALIDATED", "attempt_ids": [], "steps": steps}],
        })
    return {
        "page_id": "PAGE-host-volume-offers", "title": "Volume Offers",
        "route": "/host/volume-offers", "source_file": "host/volume-offers.mdx",
        "source_sha256": sha256_path(path), "disposition": "procedure-bearing",
        "actionable_sections": ["Introduction", "Identifiers And Values", "Volume Lifecycle", "Publish Local Storage", "Shared Disk Capacity", "Local Volume Limits", "Command Map", "Related Pages"],
        "test_sets": test_sets,
    }


def build_support_layers() -> list[dict[str, Any]]:
    records = []
    import_re = re.compile(r"import\s+\w+\s+from\s+['\"](?P<path>/snippets/host/(?:cli|sdk)/[^'\"]+\.mdx)['\"]")
    for kind, count in (("cli", 18), ("sdk", 15)):
        wrappers = sorted((REPO / "host" / kind).glob("*.mdx"))
        require(len(wrappers) == count, f"expected {count} Host {kind.upper()} wrappers")
        for wrapper in wrappers:
            text = wrapper.read_text(encoding="utf-8")
            match = import_re.search(text)
            require(match is not None, f"missing generated-fragment import: {wrapper}")
            snippet = REPO / match.group("path").lstrip("/")
            central = REPO / ("cli/reference" if kind == "cli" else "sdk/python/reference") / wrapper.name
            require(snippet.is_file() and central.is_file(), f"missing central support source for {wrapper.name}")
            slug = wrapper.stem
            records.append({
                "support_id": f"SUPPORT-{kind.upper()}-{slug}", "layer": kind.upper(),
                "route": f"/host/{kind}/{slug}", "source_file": wrapper.relative_to(REPO).as_posix(),
                "source_sha256": sha256_path(wrapper), "fragment_file": snippet.relative_to(REPO).as_posix(),
                "fragment_sha256": sha256_path(snippet), "central_reference_file": central.relative_to(REPO).as_posix(),
                "central_reference_route": f"/{'cli/reference' if kind == 'cli' else 'sdk/python/reference'}/{slug}",
                "central_reference_sha256": sha256_path(central), "classification": "CENTRAL_REFERENCE_SUPPORT_LAYER",
                "workflow": False, "status": "PASS", "evidence_ids": [SUPPORT_EVIDENCE],
                "claim_limit": "This proves wrapper/import/central-destination structure only; it does not validate command runtime or Host workflow behavior.",
            })
    return records


def attach_claims(sets: dict[str, Any], claims: list[dict[str, Any]]) -> None:
    by_page: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        by_page.setdefault(claim["page_id"], []).append(claim)

    def overlaps(claim: dict[str, Any], spans: Iterable[dict[str, int]]) -> bool:
        return any(
            left["start"] <= right["end"] and right["start"] <= left["end"]
            for left in claim["scope"]["source_spans"] for right in spans
        )

    for page in sets["pages"]:
        page_claims = by_page.get(page["page_id"], [])
        page["material_claim_ids"] = [item["claim_id"] for item in page_claims]
        require(page_claims, f"page has no material claim contract: {page['route']}")
        for test_set in page["test_sets"]:
            set_ids: list[str] = []
            for branch in test_set["branches"]:
                branch_ids: list[str] = []
                for step in branch["steps"]:
                    step_ids = [
                        item["claim_id"]
                        for item in page_claims
                        if item["scope"]["source_file"] == page["source_file"]
                        and overlaps(item, step["source_lines"])
                    ]
                    step["claim_ids"] = step_ids
                    if not step_ids:
                        step["no_material_claim_reason"] = "Structural/setup/checkpoint record whose bound span contains no independently inventoried material assertion."
                    else:
                        step.pop("no_material_claim_reason", None)
                    branch_ids.extend(step_ids)
                    for command in step["commands"]:
                        command_spans = [{"start": command["source"]["line_start"], "end": command["source"]["line_end"]}]
                        command_ids = [item["claim_id"] for item in page_claims if overlaps(item, command_spans)]
                        command["claim_ids"] = command_ids
                        if not command_ids:
                            command["no_material_claim_reason"] = "The command carrier is structural within its procedure; its semantic assertion is represented by the owning step."
                        else:
                            command.pop("no_material_claim_reason", None)
                    # Stable order with no duplicate aggregation.
                branch["claim_ids"] = list(dict.fromkeys(branch_ids))
                if not branch["claim_ids"]:
                    branch["no_material_claim_reason"] = "Branch structure contains no independent material assertion beyond its condition and child steps."
                else:
                    branch.pop("no_material_claim_reason", None)
                set_ids.extend(branch["claim_ids"])
            test_set["claim_ids"] = list(dict.fromkeys(set_ids))
            if not test_set["claim_ids"]:
                test_set["no_material_claim_reason"] = "Procedure grouping contains no material assertion beyond its goal and child records."
            else:
                test_set.pop("no_material_claim_reason", None)


def enumerate_topology(sets: dict[str, Any]) -> tuple[dict[tuple[str, ...], dict[str, Any]], dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]], dict[tuple[str, ...], dict[str, Any]]]:
    entities: dict[tuple[str, ...], dict[str, Any]] = {}
    children: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]] = {}
    context: dict[tuple[str, ...], dict[str, Any]] = {}
    for page in sets["pages"]:
        pk = ("PAGE", page["page_id"])
        entities[pk] = page
        context[pk] = {"page": page}
        children[pk] = []
        for test_set in page["test_sets"]:
            sk = ("TEST_SET", page["page_id"], test_set["test_set_id"])
            entities[sk] = test_set; context[sk] = {"page": page, "set": test_set}; children[sk] = []
            children[pk].append((sk, True))
            for branch in test_set["branches"]:
                bk = ("BRANCH", page["page_id"], test_set["test_set_id"], branch["branch_id"])
                entities[bk] = branch; context[bk] = {"page": page, "set": test_set, "branch": branch}; children[bk] = []
                children[sk].append((bk, True))
                for step in branch["steps"]:
                    stk = ("STEP", page["page_id"], test_set["test_set_id"], branch["branch_id"], step["step_id"])
                    entities[stk] = step; context[stk] = {"page": page, "set": test_set, "branch": branch, "step": step}; children[stk] = []
                    children[bk].append((stk, bool(step["required"])))
                    for command in step["commands"]:
                        ck = ("COMMAND", page["page_id"], test_set["test_set_id"], branch["branch_id"], step["step_id"], command["command_id"])
                        entities[ck] = command
                        context[ck] = {"page": page, "set": test_set, "branch": branch, "step": step, "command": command}
                        children[stk].append((ck, True))
    return entities, children, context


def count_topology(sets: dict[str, Any]) -> dict[str, int]:
    entities, _, _ = enumerate_topology(sets)
    counts = Counter(key[0] for key in entities)
    steps = [value for key, value in entities.items() if key[0] == "STEP"]
    return {"pages": counts["PAGE"], "test_sets": counts["TEST_SET"], "branches": counts["BRANCH"],
            "steps": counts["STEP"], "command_carriers": counts["COMMAND"],
            "command_bearing_steps": sum(bool(step["commands"]) for step in steps)}


def aggregate_status(statuses: list[str]) -> str | None:
    """Apply the canonical required-child severity rule."""
    if not statuses:
        return None
    for candidate in ("FAIL", "BLOCKED", "STALE", "UNVALIDATED"):
        if candidate in statuses:
            return candidate
    if all(item == "NOT_APPLICABLE" for item in statuses):
        return "NOT_APPLICABLE"
    if all(item in {"PASS", "NOT_APPLICABLE"} for item in statuses) and "PASS" in statuses:
        return "PASS"
    raise ReconciliationError(f"cannot aggregate child statuses: {statuses}")


def desired_statuses(
    entities: dict[tuple[str, ...], dict[str, Any]],
    children: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]],
    old_records: dict[tuple[str, ...], dict[str, Any]],
) -> tuple[dict[tuple[str, ...], str], dict[tuple[str, ...], str]]:
    status: dict[tuple[str, ...], str] = {}
    own_status: dict[tuple[str, ...], str] = {}
    volume_steps = {"VOL-C01-S01": "BLOCKED", "VOL-C01-S02": "BLOCKED", "VOL-C01-S03": "BLOCKED",
                    "VOL-E01-S01": "PASS", "VOL-E01-S02": "PASS", "VOL-E02-S01": "PASS",
                    "VOL-E02-S02": "PASS", "VOL-C02-S01": "PASS", "VOL-C02-S02": "PASS"}
    for key in (key for key in entities if key[0] == "COMMAND"):
        command_id = key[-1]
        if key[1] == "PAGE-host-volume-offers":
            own_status[key] = status[key] = "PASS"
            continue
        old = old_records.get(key, {}).get("current_status", "UNVALIDATED")
        own_status[key] = status[key] = (
            "BLOCKED" if command_id in ROOT_BLOCKED_COMMANDS
            else "UNVALIDATED" if old == "BLOCKED"
            else old
        )
    for key in (key for key in entities if key[0] == "STEP"):
        if key[1] == "PAGE-host-volume-offers":
            own = volume_steps[key[-1]]
        elif key[1] == SELF_TEST_PAGE_ID and key[-1] in SELF_TEST_CORRECTED_STEP_OWN_STATUSES:
            # These four targets changed child ownership.  Their preserved
            # projection status is a prior rollup, not the step's own direct
            # observation, so do not let that aggregate status become sticky
            # when the generator is run again.
            own = SELF_TEST_CORRECTED_STEP_OWN_STATUSES[key[-1]]
        else:
            old = old_records[key]["current_status"]
            own = (
                "BLOCKED" if key[-1] in ROOT_BLOCKED_STEPS
                else "UNVALIDATED" if old == "BLOCKED"
                else old
            )
        own_status[key] = own
        required = [status[child] for child, is_required in children[key] if is_required]
        # The target's own check and required command children are independent
        # inputs.  A later pure-rollup basis is used only when the child result
        # alone happens to determine the same final status.
        status[key] = aggregate_status([own, *required]) or own
    for level in ("BRANCH", "TEST_SET", "PAGE"):
        for key in (key for key in entities if key[0] == level):
            required_children = [child for child, required in children[key] if required]
            child_statuses = [status[child] for child in required_children]
            old = old_records.get(key, {}).get("current_status", "UNVALIDATED")
            own_status[key] = old
            status[key] = aggregate_status(child_statuses) or old
    return status, own_status


def build_evidence_index(
    results: dict[str, Any], entities: dict[tuple[str, ...], dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Index retained evidence by exact target and recorded status."""
    index: dict[str, dict[str, Any]] = {}
    superseded_attempts = {
        row["attempt_id"]
        for row in results.get("attempts", [])
        if row.get("qualification_superseded_by") or row.get("superseded_by")
    }
    for row in results.get("procedure_results", []):
        if row["evidence_id"] in COMMAND_PROOF_REVIEWER_EVIDENCE:
            # These records prove only the reviewer presentation and evidence
            # linkage contract. They are retained as exact-target history but
            # must never become source, runtime, or current-status evidence.
            continue
        bindings: dict[tuple[str, ...], str] = {}
        for target in row["targets"]:
            key = target_key(target["level"], target["target"])
            if key in entities:
                bindings[key] = target["vv_status"]
        index[row["evidence_id"]] = {
            "attempt_id": row["attempt_id"], "result_kind": "PROCEDURE_RESULT",
            "method": row["method"], "limitations": row["limitations"],
            "superseded": row["attempt_id"] in superseded_attempts,
            "bindings": bindings,
        }
    command_keys: dict[str, tuple[str, ...]] = {}
    for key in entities:
        if key[0] == "COMMAND":
            require(key[-1] not in command_keys, f"duplicate command id in topology: {key[-1]}")
            command_keys[key[-1]] = key
    for row in results.get("command_results", []):
        bindings = {
            command_keys[command_id]: row["vv_status"]
            for command_id in row["command_ids"] if command_id in command_keys
        }
        index[row["evidence_id"]] = {
            "attempt_id": row["attempt_id"], "result_kind": "COMMAND_RESULT",
            "method": "RETAINED_COMMAND_EXECUTION",
            "limitations": row.get("observation", "Retained command result; see its attempt record."),
            "superseded": row["attempt_id"] in superseded_attempts,
            "bindings": bindings,
        }
    return index


ACCOUNTING_ONLY_METHODS = {
    "CURRENT_SOURCE_AND_RETAINED_EVIDENCE_RECONCILIATION",
    "INDEPENDENT_PARENT_CHILD_ACCOUNTING_AUDIT",
    "STATIC_REPOSITORY_STATUS_BASIS_REBASE",
    "STATIC_SELF_TEST_COMMAND_TOPOLOGY_CORRECTION_RETEST",
}


def matching_evidence(
    key: tuple[str, ...], status: str, evidence_index: dict[str, dict[str, Any]],
    preferred: Iterable[str] = (), *, allow_accounting: bool = False,
) -> list[str]:
    """Return exact-target, same-status retained evidence in preference order."""
    ordered = list(dict.fromkeys([*preferred, *sorted(evidence_index)]))
    matches = []
    for evidence_id in ordered:
        meta = evidence_index.get(evidence_id)
        if not meta or meta["bindings"].get(key) != status:
            continue
        if meta.get("superseded"):
            continue
        if not allow_accounting and meta["method"] in ACCOUNTING_ONLY_METHODS:
            continue
        matches.append(evidence_id)
    return matches


def root_prerequisite(
    key: tuple[str, ...], ctx: dict[str, Any], evidence_ids: list[str],
) -> dict[str, Any] | None:
    if key[0] == "COMMAND" and key[-1] in ROOT_BLOCKED_COMMANDS:
        kind, description = ROOT_BLOCKED_COMMANDS[key[-1]]
        return {"kind": kind, "description": description, "evidence_ids": evidence_ids,
                "components": [{"kind": kind, "description": description,
                                "evidence_ids": evidence_ids}]}
    if key[0] == "STEP" and key[-1] in ROOT_BLOCKED_STEPS:
        instruction = ctx["step"]["instruction"]
        if "PARAMETER_REQUIRED" in str(ctx["step"].get("blocker_ids", [])) or key[-1].startswith("NET-E03") or key[-1] == "MNT-E02-B01-S02":
            kind = "INPUT"
            description = f"Approved representative target parameters required to check this exact step are unavailable: {instruction}"
        elif key[-1].endswith("S29"):
            kind = "ENVIRONMENT"
            description = f"A representative authorized target environment is unavailable for this exact step: {instruction}"
        else:
            kind = "AUTHORIZATION"
            description = f"Explicit operator authorization and a controlled disposable or idle target are unavailable for this potentially privileged, mutating, disruptive, or workload-affecting step: {instruction}"
        return {"kind": kind, "description": description, "evidence_ids": evidence_ids,
                "components": [{"kind": kind, "description": description,
                                "evidence_ids": evidence_ids}]}
    if key[1] == "PAGE-host-volume-offers" and key[0] == "STEP" and key[-1].startswith("VOL-C01"):
        component_specs = {
            "VOL-C01-S01": [
                ("SOURCE", "The exact canonical volume and scheduler lifecycle enforcement revision is unavailable."),
                ("AUTHORIZATION", "Approval for a paid, mutating, destructive volume lifecycle run is unavailable under this task scope."),
                ("ENVIRONMENT", "A representative disposable renter instance and volume are unavailable for the lifecycle run."),
            ],
            "VOL-C01-S02": [
                ("SOURCE", "The exact canonical Host storage-accounting and allocation revision is unavailable."),
                ("OWNER_CONFIRMATION", "The accountable Product/SRE/Support decision for headroom and renter-file handling is unavailable."),
                ("ENVIRONMENT", "A representative disposable Host and volume allocation environment is unavailable."),
            ],
            "VOL-C01-S03": [
                ("SOURCE", "The exact canonical placement, attachment, compatibility, resize, and lifecycle revision is unavailable."),
                ("OWNER_CONFIRMATION", "The accountable Product/SRE decision for backup, compatibility, and maintenance meaning is unavailable."),
                ("AUTHORIZATION", "Approval for the paid/mutating positive and adverse lifecycle checks is unavailable."),
            ],
        }
        components = [{"kind": kind, "description": description,
                       "evidence_ids": evidence_ids}
                      for kind, description in component_specs[key[-1]]]
        return {
            "kind": "MULTIPLE",
            "description": "Multiple independently required source, owner, authorization, or environment prerequisites are unavailable; see components.",
            "evidence_ids": evidence_ids,
            "components": components,
        }
    return None


def source_refs_for(key: tuple[str, ...], ctx: dict[str, Any], status: str) -> list[dict[str, str]]:
    if status not in {"PASS", "FAIL"}:
        return []
    if key[0] == "COMMAND" and key[-1] in TEAM_CATALOG_COMMAND_IDS and status == "PASS":
        text = ctx["command"]["text"]
        operation = text.removeprefix("vastai ")
        symbol = operation.replace("-", "_").replace(" ", "__")
        if "api-key" in operation:
            path = "vastai/cli/commands/keys.py"
        elif operation.startswith("metrics "):
            path = "vastai/cli/commands/metrics.py"
        elif operation == "show earnings":
            path = "vastai/cli/commands/billing.py"
        else:
            path = "vastai/cli/commands/teams.py"
        return [canonical_ref(
            "vast-ai/vast-cli", CLI_REVISION, path,
            f"{symbol} command registration and usage contract for `{text}`",
            "CANONICAL_CLI_SOURCE",
        )]
    if key[0] == "STEP" and key[-1] in SELF_TEST_PARITY_STEP_IDS and status == "PASS":
        return [
            local_source_ref(
                "scripts/generate_self_test_reference.py",
                "render_page source extraction and deterministic self-test reference generation",
                "CANONICAL_DOC_GENERATOR_SOURCE",
            ),
            canonical_ref(
                "vast-ai/vast-cli", SELF_TEST_CLI_REVISION,
                "vastai/cli/self_test/machine_diagnostics.py",
                "exact historical self-test requirement and failure catalogs consumed by the generator",
                "CANONICAL_CLI_SOURCE",
            ),
            canonical_ref(
                "vast-ai/self-test", SELF_TEST_IMAGE_REVISION,
                "remote.py", "exact historical EVENT_CATALOG consumed by the generator",
                "CANONICAL_SELF_TEST_SOURCE",
            ),
        ]
    if key[1] == "PAGE-host-volume-offers" and status == "PASS":
        claim_ids = (ctx.get("command") or ctx.get("step") or ctx.get("branch")
                     or ctx.get("set") or ctx["page"]).get("claim_ids", [])
        refs: list[dict[str, str]] = []
        for claim_id in claim_ids:
            refs.extend(volume_source_refs(claim_id))
        # Parent claim overlap can be empty (or intentionally broader than the
        # bounded target).  The retained static procedure remains evidence,
        # while authority refs are emitted only when exact canonical refs exist.
        unique = {tuple(item.values()): item for item in refs}
        return list(unique.values())
    return []


def prerequisite_evidence_types(prerequisite: dict[str, Any]) -> list[str]:
    mapping = {
        "SOURCE": "CANONICAL_IMPLEMENTATION_SOURCE",
        "OWNER_CONFIRMATION": "ACCOUNTABLE_OWNER_CONFIRMATION",
        "PERMISSION": "RUNTIME_OR_UI_OBSERVATION",
        "AUTHORIZATION": "RUNTIME_OR_UI_OBSERVATION",
        "ENVIRONMENT": "RUNTIME_OR_UI_OBSERVATION",
        "INPUT": "RUNTIME_OR_UI_OBSERVATION",
    }
    types = [mapping[item["kind"]] for item in prerequisite.get("components", [])
             if item["kind"] in mapping]
    if not types and prerequisite.get("kind") in mapping:
        types.append(mapping[prerequisite["kind"]])
    return list(dict.fromkeys(types or ["DECLARED_SUITABLE_CHECK"]))


def evidence_types_for(
    key: tuple[str, ...], status: str, ctx: dict[str, Any], evidence_ids: list[str],
    evidence_index: dict[str, dict[str, Any]], prerequisite: dict[str, Any] | None,
) -> list[str]:
    if status == "NOT_APPLICABLE":
        return ["APPROVED_NON_EXECUTABLE_CLASSIFICATION"]
    exact_contract = EXACT_COMMAND_EVIDENCE_CONTRACTS.get(key)
    if exact_contract:
        return list(exact_contract["required_evidence_types"])
    if status == "BLOCKED" and prerequisite:
        return prerequisite_evidence_types(prerequisite)
    if key[1] == "PAGE-host-volume-offers":
        refs = source_refs_for(key, ctx, status)
        return ["CANONICAL_IMPLEMENTATION_SOURCE"] if refs else ["REPOSITORY_STATIC_CHECK"]
    methods = [evidence_index[evidence_id] for evidence_id in evidence_ids
               if evidence_id in evidence_index]
    types: list[str] = []
    if any(item["result_kind"] == "COMMAND_RESULT" for item in methods):
        types.append("RUNTIME_OR_UI_OBSERVATION")
    for item in methods:
        method = item["method"]
        if re.search(r"SOURCE|CLI_CATALOG|MANIFEST|REGENERATION", method):
            types.append("CANONICAL_IMPLEMENTATION_SOURCE")
        elif re.search(r"STATIC|ROUTE|REDACTION|ACCOUNTING|RECONCILIATION", method):
            types.append("REPOSITORY_STATIC_CHECK")
        elif item["result_kind"] == "PROCEDURE_RESULT":
            types.append("RUNTIME_OR_UI_OBSERVATION")
    if types:
        return list(dict.fromkeys(types))
    classification = str(ctx.get("step", {}).get("execution_classification", ""))
    if re.search(r"STATIC|SOURCE", classification):
        return ["CANONICAL_IMPLEMENTATION_SOURCE"]
    if re.search(r"NON_EXECUTABLE|DISPLAY", classification):
        return ["APPROVED_NON_EXECUTABLE_CLASSIFICATION"]
    return ["DECLARED_SUITABLE_CHECK"]


def direct_basis(
    key: tuple[str, ...], status: str, ctx: dict[str, Any], evidence_ids: list[str],
    evidence_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    prerequisite = root_prerequisite(key, ctx, evidence_ids) if status == "BLOCKED" else None
    refs = source_refs_for(key, ctx, status)
    if status == "PASS":
        kind = "STATIC_SOURCE_CONFORMANCE" if refs else "DIRECT_OBSERVATION"
    elif status == "FAIL":
        kind = "CONFIRMED_DEFECT"
    elif status == "BLOCKED":
        kind = "UNAVAILABLE_PREREQUISITE"
    elif status == "NOT_APPLICABLE":
        kind = "APPROVED_NOT_APPLICABLE"
    else:
        kind = "NO_CLAIM_SUITABLE_EVIDENCE"
    if refs:
        authority_kind = "CANONICAL_SOURCE"
    elif status in {"PASS", "FAIL"} and evidence_ids:
        authority_kind = "RETAINED_EVIDENCE"
    elif status == "BLOCKED":
        authority_kind = "UNAVAILABLE_PREREQUISITE_OWNER"
    elif status == "NOT_APPLICABLE":
        authority_kind = "APPROVED_CLASSIFICATION"
    else:
        authority_kind = "NOT_IDENTIFIED"
    methods = [evidence_index[evidence_id]["method"] for evidence_id in evidence_ids
               if evidence_id in evidence_index]
    return {
        "status": status,
        "basis_kind": kind,
        "required_evidence_types": evidence_types_for(
            key, status, ctx, evidence_ids, evidence_index, prerequisite
        ),
        "authority": {
            "kind": authority_kind,
            "source_refs": refs,
            "unresolved_owner_role": owner_for(ctx["page"]["source_file"], "IMPLEMENTATION_OR_CONCEPT")
            if status in {"BLOCKED", "UNVALIDATED"} else None,
            "owner_confirmation_evidence_id": None,
        },
        "supporting_evidence_ids": evidence_ids,
        "evidence_methods": methods,
        "unavailable_prerequisite": prerequisite,
        "limitations": "Documentation is the target under review, not evidence for itself. Each retained result is limited to its exact target, method, environment, and recorded attempt.",
    }


def aggregate_blocker_prerequisite(
    key: tuple[str, ...], evidence_ids: list[str],
    inputs: list[tuple[tuple[str, ...], dict[str, Any]]],
) -> dict[str, Any]:
    components: list[dict[str, Any]] = []
    for source_key, prerequisite in inputs:
        nested = prerequisite.get("components") or [{
            "kind": prerequisite["kind"], "description": prerequisite["description"],
            "evidence_ids": prerequisite.get("evidence_ids", []),
        }]
        for component in nested:
            item = copy.deepcopy(component)
            item.setdefault("via_target", {"level": source_key[0], "target": target_dict(source_key)})
            components.append(item)
    # Stable de-duplication keeps distinct targets visible even when they share
    # the same missing permission or environment.
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in components:
        marker = json.dumps(item, sort_keys=True)
        if marker not in seen:
            seen.add(marker); unique.append(item)
    require(unique, f"BLOCKED aggregate lacks concrete descendant prerequisite: {key}")
    return {
        "kind": "DERIVED_FROM_CHILDREN",
        "description": f"{len(unique)} concrete prerequisite component(s) from required blocked child targets are unavailable; each component names its originating target.",
        "evidence_ids": evidence_ids,
        "components": unique,
    }


def status_leaf_descendants(
    key: tuple[str, ...], wanted_status: str,
    children: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]],
    statuses: dict[tuple[str, ...], str],
) -> list[tuple[str, ...]]:
    """Return the exact required leaves that carry a rolled-up status."""
    matching_children = [
        child for child, required in children.get(key, [])
        if required and statuses[child] == wanted_status
    ]
    if not matching_children:
        return [key] if statuses[key] == wanted_status else []
    leaves: list[tuple[str, ...]] = []
    for child in matching_children:
        leaves.extend(status_leaf_descendants(child, wanted_status, children, statuses))
    return list(dict.fromkeys(leaves))


def blocked_next_action(
    key: tuple[str, ...], prerequisite: dict[str, Any] | None,
    required_evidence_types: list[str],
) -> str:
    """Render a reviewer-facing action without exposing internal schema paths."""
    target_label = f"{key[0]} {key[-1]}"
    if prerequisite is None:
        return (
            f"For {target_label}, identify the unavailable permission, environment, "
            "source, owner, or input before retrying. Retain the exact prerequisite, "
            "observation, limitations, and cleanup; keep the target BLOCKED while it "
            "remains unavailable."
        )
    components = prerequisite.get("components") or [{
        "kind": prerequisite["kind"],
        "description": prerequisite["description"],
        "evidence_ids": prerequisite.get("evidence_ids", []),
    }]
    rendered_components: list[str] = []
    has_distinct_origins = False
    for component in components:
        rendered = f"[{component['kind']}] {component['description'].rstrip('.')}"
        origin = component.get("via_target")
        if origin:
            origin_level = origin["level"]
            origin_target = origin["target"]
            origin_id = origin_target[TARGET_FIELDS[origin_level][-1]]
            rendered += f" (origin: {origin_level} {origin_id})"
            has_distinct_origins = True
        rendered_components.append(rendered)
    prefix = (
        f"For {target_label}, address each missing prerequisite: "
        if len(rendered_components) > 1 or has_distinct_origins
        else f"For {target_label}, make this missing prerequisite available: "
    )
    if "CHILD_STATUS_ROLLUP" in required_evidence_types or has_distinct_origins:
        completion = (
            "Then complete each named originating check, retain its exact source, "
            "decision, or runtime evidence and limitations, and recompute the required-"
            "child rollup."
        )
    else:
        completion = (
            "Then complete the exact named verification and retain the source or "
            "decision record, or the runtime inputs, outputs/UI observation, environment "
            "and revision identities, timestamps, exit status, limitations, and cleanup, "
            "as applicable."
        )
    return (
        prefix + "; ".join(rendered_components) + ". " + completion
        + " If any prerequisite remains unavailable, keep the affected target BLOCKED."
    )


def basis_for(
    key: tuple[str, ...], status: str, own_status: str, ctx: dict[str, Any],
    children: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]],
    statuses: dict[tuple[str, ...], str], evidence_ids: list[str],
    own_evidence_ids: list[str], evidence_index: dict[str, dict[str, Any]],
    child_bases: dict[tuple[str, ...], dict[str, Any]], snapshot: str,
) -> dict[str, Any]:
    page, test_set = ctx["page"], ctx.get("set")
    entity = ctx.get("command") or ctx.get("step") or ctx.get("branch") or ctx.get("set") or page
    if key[0] == "PAGE":
        headings, spans, claim = page["actionable_sections"], [], f"The declared procedures for {page['title']} have a current execution/evidence disposition; material-claim semantic disposition is reported separately."
        claim_refs = page.get("material_claim_ids", [])
    elif key[0] == "TEST_SET":
        headings = test_set["source_context"]["headings"]
        spans = [{"start": test_set["source_context"]["line_start"], "end": test_set["source_context"]["line_end"]}]
        claim, claim_refs = test_set["goal"], test_set.get("claim_ids", [])
    elif key[0] == "BRANCH":
        steps = entity["steps"]
        headings = list(dict.fromkeys(section for step in steps for section in step["source_sections"]))
        spans = [span for step in steps for span in step["source_lines"]]
        claim, claim_refs = entity["condition"], entity.get("claim_ids", [])
    elif key[0] == "STEP":
        headings, spans, claim = entity["source_sections"], entity["source_lines"], entity["instruction"]
        claim_refs = entity.get("claim_ids", [])
    else:
        source = entity["source"]
        headings, spans, claim = [source["section"]], [{"start": source["line_start"], "end": source["line_end"]}], entity["text"]
        claim_refs = entity.get("claim_ids", [])
    no_claim = entity.get("no_material_claim_reason") if not claim_refs else None
    child_rows = [{"level": child[0], "target": target_dict(child), "current_status": statuses[child], "required": required_child}
                  for child, required_child in children.get(key, [])]
    required_child_keys = [child for child, required_child in children.get(key, []) if required_child]
    child_rollup = aggregate_status([statuses[child] for child in required_child_keys])
    target_basis = direct_basis(key, own_status, ctx, own_evidence_ids, evidence_index)
    if child_rows and child_rollup == status and target_basis["unavailable_prerequisite"] is None:
        basis_kind = "ROLLUP"
        target_basis_out = None
        required = ["CHILD_STATUS_ROLLUP"]
    elif child_rows:
        basis_kind = "COMPOSITE_TARGET_AND_CHILDREN"
        target_basis_out = target_basis
        required = list(dict.fromkeys([*target_basis["required_evidence_types"], "CHILD_STATUS_ROLLUP"]))
    else:
        basis_kind = target_basis["basis_kind"]
        target_basis_out = None
        required = target_basis["required_evidence_types"]
    prerequisite = None
    if status == "BLOCKED":
        blocker_inputs: list[tuple[tuple[str, ...], dict[str, Any]]] = []
        if basis_kind != "ROLLUP" and target_basis["unavailable_prerequisite"]:
            blocker_inputs.append((key, target_basis["unavailable_prerequisite"]))
        for child in required_child_keys:
            if statuses[child] == "BLOCKED":
                child_prerequisite = child_bases[child].get("unavailable_prerequisite")
                require(child_prerequisite is not None, f"blocked child lacks prerequisite: {child}")
                blocker_inputs.append((child, child_prerequisite))
        if len(blocker_inputs) == 1 and blocker_inputs[0][0] == key and not required_child_keys:
            prerequisite = copy.deepcopy(blocker_inputs[0][1])
        else:
            prerequisite = aggregate_blocker_prerequisite(key, evidence_ids, blocker_inputs)
    limitations = "Documentation is the target under review, not evidence for itself. Evidence applies only to the exact named target and method."
    if status == "FAIL":
        failed_leaves = status_leaf_descendants(key, "FAIL", children, statuses)
        if any(leaf[0] == "COMMAND" and leaf[-1] == API_KEY_PERMISSION_COMMAND_ID for leaf in failed_leaves):
            impact = (
                f"Required command {API_KEY_PERMISSION_COMMAND_ID} is FAIL: "
                f"{API_KEY_PERMISSION_OBSERVATION} This prevents the target and its required ancestors from passing."
            )
            limitations = API_KEY_PERMISSION_LIMITATION
            next_action = API_KEY_PERMISSION_ACTION
        else:
            impact = "A retained discrepancy prevents this target and its required ancestors from passing."
            next_action = f"Correct the observed defect for {key[0]} {key[-1]} and retain a target-specific retest; do not overwrite the failed history."
    elif status == "BLOCKED":
        impact = "The named unavailable prerequisite prevents the suitable check from completing."
        exact_contract = EXACT_COMMAND_EVIDENCE_CONTRACTS.get(key)
        if exact_contract:
            next_action = exact_contract["next_action"]
        else:
            next_action = blocked_next_action(key, prerequisite, required)
    elif status == "UNVALIDATED":
        impact = "No claim-suitable result is established for this target."
        exact_contract = EXACT_COMMAND_EVIDENCE_CONTRACTS.get(key)
        next_action = (
            exact_contract["next_action"]
            if exact_contract
            else (
                f"For {key[0]} {key[-1]}, obtain and retain {', '.join(required)} for the exact subject claim; "
                "until it is bound, missing proof alone remains UNVALIDATED."
            )
        )
    elif status == "PASS":
        impact = "Only the bounded target property described by the retained evidence is established."
        next_action = None
    else:
        impact = "The approved display-only carrier is not independently executable."
        next_action = None
    return {
        "basis_kind": basis_kind,
        "subject": {"route": page["route"], "source_file": page["source_file"],
                    "headings": headings or ["Introduction"], "source_spans": spans,
                    "claim": claim, "claim_refs": claim_refs,
                    "claim_refs_role": "SOURCE_SPAN_OVERLAP_ONLY_NOT_STATUS_INHERITANCE",
                    "no_material_claim_reason": no_claim},
        "required_evidence_types": required,
        "authority": ({"kind": ("DERIVED_FROM_CHILDREN" if basis_kind == "ROLLUP"
                                  else "COMPOSITE_TARGET_AND_CHILDREN"),
                       "source_refs": [], "unresolved_owner_role": None,
                       "owner_confirmation_evidence_id": None}
                      if child_rows else target_basis["authority"]),
        "supporting_evidence_ids": evidence_ids,
        "evidence_methods": [evidence_index[evidence_id]["method"] for evidence_id in evidence_ids
                             if evidence_id in evidence_index],
        "unavailable_prerequisite": prerequisite,
        "claim_impact": impact,
        "limitations": limitations,
        "next_action": next_action,
        "source_snapshot_sha256": snapshot,
        "derived_from": child_rows if child_rows else [],
        "target_basis": target_basis_out,
    }


def rationale_for(
    key: tuple[str, ...], status: str, own_status: str,
    children: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]],
    statuses: dict[tuple[str, ...], str], basis: dict[str, Any],
) -> str:
    required_children = [child for child, required in children.get(key, []) if required]
    failed_leaves = status_leaf_descendants(key, "FAIL", children, statuses) if status == "FAIL" else []
    api_key_permission_failure = any(
        leaf[0] == "COMMAND" and leaf[-1] == API_KEY_PERMISSION_COMMAND_ID
        for leaf in failed_leaves
    )
    if basis["basis_kind"] == "ROLLUP":
        counts = Counter(statuses[child] for child in required_children)
        summary = "Required-child rollup: " + ", ".join(f"{name}={counts[name]}" for name in STATUS_ORDER if counts[name]) + f" => {status}."
        if api_key_permission_failure:
            summary += f" Failing descendant {API_KEY_PERMISSION_COMMAND_ID}: {API_KEY_PERMISSION_OBSERVATION}"
        return summary
    if basis["basis_kind"] == "COMPOSITE_TARGET_AND_CHILDREN":
        counts = Counter(statuses[child] for child in required_children)
        child_text = ", ".join(f"{name}={counts[name]}" for name in STATUS_ORDER if counts[name]) or "none"
        summary = f"Composite target-and-child result: target={own_status}; required children={child_text} => {status}."
        if api_key_permission_failure:
            summary += f" Failing descendant {API_KEY_PERMISSION_COMMAND_ID}: {API_KEY_PERMISSION_OBSERVATION}"
        return summary
    prerequisite = basis.get("unavailable_prerequisite")
    if status == "BLOCKED" and prerequisite:
        return f"UNAVAILABLE_PREREQUISITE {prerequisite['kind']}: {prerequisite['description']}"
    if status == "FAIL":
        if api_key_permission_failure:
            return f"CONFIRMED_DEFECT {API_KEY_PERMISSION_COMMAND_ID}: {API_KEY_PERMISSION_OBSERVATION}"
        return "CONFIRMED_DEFECT: retained evidence records an observed discrepancy; no ancestor PASS is inferred."
    if status == "UNVALIDATED":
        return "NO_CLAIM_SUITABLE_EVIDENCE: missing evidence alone is UNVALIDATED; no unavailable prerequisite is asserted."
    if status == "PASS":
        return "Retained target-bound evidence supports only the bounded claim recorded in status_basis."
    return "Approved NON_EXECUTABLE_DISPLAY classification; functional execution is not applicable."


def projection_counts(records: list[dict[str, Any]]) -> dict[str, Any]:
    levels = Counter(row["level"] for row in records)
    statuses = Counter(row["current_status"] for row in records)
    by_level = {level: Counter(row["current_status"] for row in records if row["level"] == level) for level in TARGET_FIELDS}
    return {
        "targets": len(records),
        "levels": {level: levels[level] for level in TARGET_FIELDS},
        "statuses": {status: statuses[status] for status in STATUS_ORDER if statuses[status]},
        "by_level": {level: {status: by_level[level][status] for status in STATUS_ORDER if by_level[level][status]} for level in TARGET_FIELDS},
    }


def build_registers(
    claims: list[dict[str, Any]], projection_records: list[dict[str, Any]]
) -> tuple[str, str]:
    """Render confirmed blockers without relabelling missing proof as BLOCKED."""
    esc = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    runtime_kinds = {
        "PERMISSION", "INPUT", "ENVIRONMENT", "AUTHORIZATION",
        "ENVIRONMENT_AND_AUTHORIZATION", "ENVIRONMENT_OR_PERMISSION",
    }
    owner_kinds = {"SOURCE", "OWNER_CONFIRMATION", "AUTHORITATIVE_CITATION"}

    def prerequisite_text(prerequisite: dict[str, Any], allowed: set[str]) -> str:
        components = prerequisite.get("components", [])
        if components:
            rendered = []
            for component in components:
                if component["kind"] not in allowed:
                    continue
                origin = component.get("via_target")
                origin_text = ""
                if origin:
                    origin_id = origin["target"][TARGET_FIELDS[origin["level"]][-1]]
                    origin_text = f" via {origin['level']} {origin_id}"
                rendered.append(f"[{component['kind']}] {component['description']}{origin_text}")
            require(rendered, "blocker register selected a prerequisite with no components in its lane")
            return "; ".join(rendered)
        require(prerequisite["kind"] in allowed,
                f"blocker prerequisite leaked across registers: {prerequisite['kind']}")
        return f"[{prerequisite['kind']}] {prerequisite['description']}"

    def claim_requirements(
        claim: dict[str, Any], kinds: set[str], statuses: set[str] | None = None,
    ) -> list[dict[str, str]]:
        return [
            item for item in claim["authority"].get("unresolved_evidence_requirements", [])
            if item["prerequisite_kind"] in kinds
            and (statuses is None or item.get("current_status", "UNVALIDATED") in statuses)
        ]

    def render_claim_requirements(requirements: list[dict[str, str]]) -> str:
        require(requirements, "blocked claim lacks a structured prerequisite in the selected register lane")
        return "; ".join(
            f"[{item['prerequisite_kind']}] {item['responsible_role']} — {item['required_input']}"
            for item in requirements
        )

    def render_claim_actions(requirements: list[dict[str, str]]) -> str:
        return " ".join(item["next_action"] for item in requirements)
    runtime_claims = [
        claim
        for claim in claims
        if claim["current"]["status"] == "BLOCKED"
        and "RUNTIME_OR_UI_OBSERVATION" in claim["evidence_requirement"]["types"]
        and claim_requirements(claim, runtime_kinds, {"BLOCKED"})
    ]
    owner_claims = [
        claim
        for claim in claims
        if claim["current"]["status"] in {"BLOCKED", "FAIL"}
        and claim_requirements(claim, owner_kinds, {"BLOCKED", "FAIL"})
    ]
    runtime_unvalidated = sum(
        claim["current"]["status"] == "UNVALIDATED"
        and "RUNTIME_OR_UI_OBSERVATION" in claim["evidence_requirement"]["types"]
        for claim in claims
    )
    owner_unvalidated = sum(
        claim["current"]["status"] == "UNVALIDATED"
        and bool(claim_requirements(claim, owner_kinds, {"UNVALIDATED"}))
        for claim in claims
    )
    runtime_procedures: list[tuple[dict[str, Any], dict[str, Any]]] = []
    owner_procedures: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in projection_records:
        basis = row["status_basis"]
        direct = basis.get("target_basis") or basis
        prerequisite = direct.get("unavailable_prerequisite")
        if (row["level"] in {"STEP", "COMMAND"}
                and direct.get("status", row["current_status"]) == "BLOCKED"
                and direct.get("basis_kind") == "UNAVAILABLE_PREREQUISITE"
                and prerequisite
                and any(component["kind"] in runtime_kinds
                        for component in prerequisite.get("components", []))):
            runtime_procedures.append((row, direct))
        if (row["level"] in {"STEP", "COMMAND"}
                and direct.get("status", row["current_status"]) == "BLOCKED"
                and direct.get("basis_kind") == "UNAVAILABLE_PREREQUISITE"
                and prerequisite
                and any(component["kind"] in owner_kinds
                        for component in prerequisite.get("components", []))):
            owner_procedures.append((row, direct))

    runtime_lines = [
        "# Host Docs runtime/operator blocker register",
        "",
        "This register contains only confirmed runtime/operator blockers: a suitable check cannot proceed because the exact permission, input, environment, or authorization below is unavailable. It does not claim that any external work is complete.",
        "",
        f"Blocked runtime material claims: **{len(runtime_claims)}**. Blocked root procedure/command checks: **{len(runtime_procedures)}**.",
        "",
        f"A further **{runtime_unvalidated}** runtime-observation claims are `UNVALIDATED`, not blocked: suitable proof has not yet been bound, but this repository-local pass did not establish that a prerequisite is unavailable.",
        "",
        "## Blocked material claims",
        "",
        "| Page and heading | Claim | Concrete unavailable prerequisite | Claim impact / limitation | Exact next action |",
        "|---|---|---|---|---|",
    ]
    for claim in runtime_claims:
        scope, current = claim["scope"], claim["current"]
        requirements = claim_requirements(claim, runtime_kinds, {"BLOCKED"})
        line = scope["source_spans"][0]["start"]
        subject = f"`{scope['route']}` — {scope['heading']} (`{scope['source_file']}:{line}`; `{claim['claim_id']}`)"
        impact = "; ".join(current["limitations"])
        runtime_lines.append(
            f"| {esc(subject)} | {esc(claim['claim']['text'])} | {esc(render_claim_requirements(requirements))} | {esc(impact)} | {esc(render_claim_actions(requirements))} |"
        )
    runtime_lines += [
        "",
        "## Blocked root procedure and command checks",
        "",
        "Derived page, test-set, branch, and parent-step rollups are omitted here; their exact blocked child is listed instead.",
        "",
        "| Page and heading | Check target and claim | Concrete unavailable prerequisite | Claim impact / limitation | Exact next action |",
        "|---|---|---|---|---|",
    ]
    for row, direct in runtime_procedures:
        basis, target = row["status_basis"], row["target"]
        subject = basis["subject"]
        heading = " / ".join(subject["headings"])
        target_id = target[TARGET_FIELDS[row["level"]][-1]]
        page_heading = f"`{subject['route']}` — {heading} (`{target_id}`)"
        prerequisite = direct["unavailable_prerequisite"]
        lane_components = [
            component for component in prerequisite.get("components", [])
            if component["kind"] in runtime_kinds
        ]
        recorded_action = direct.get("next_action") or basis.get("next_action")
        lane_action = (
            recorded_action
            if recorded_action and "unavailable_prerequisite.components" not in recorded_action
            else (
                f"Make the following prerequisite(s) available under explicit authorization for "
                f"{row['level']} {target_id}: "
                + "; ".join(
                    f"[{item['kind']}] {item['description'].rstrip('.')}"
                    for item in lane_components
                )
                + ". Then run the exact named check and retain its inputs, outputs, environment "
                "identity, timestamps, exit status, and cleanup result."
            )
        )
        runtime_lines.append(
            f"| {esc(page_heading)} | {esc(subject['claim'])} | {esc(prerequisite_text(prerequisite, runtime_kinds))} | {esc(basis['claim_impact'])} {esc(basis['limitations'])} | {esc(lane_action)} |"
        )
    runtime_lines += [
        "",
        "Repository-local V&V does not authorize or complete these runtime/operator actions.",
        "",
    ]

    owner_lines = [
        "# Host Docs Product, Finance, Legal, and source-owner blocker register",
        "",
        "This register contains claims that are `BLOCKED` by a specifically unavailable Product, Finance, Legal, policy, support, or canonical-source owner, plus `FAIL` claims where a required authoritative citation is confirmed absent. Code alone cannot authorize owner-governed contract, pricing, policy, account, or legal meaning.",
        "",
        f"Owner/source material-claim entries: **{len(owner_claims)}** ({sum(claim['current']['status'] == 'BLOCKED' for claim in owner_claims)} `BLOCKED`; {sum(claim['current']['status'] == 'FAIL' for claim in owner_claims)} `FAIL`). Blocked root procedure/command source-owner checks: **{len(owner_procedures)}**.",
        "",
        f"A further **{owner_unvalidated}** claims have an unresolved source-owner role but remain `UNVALIDATED`, not blocked, because missing evidence alone does not establish that the owner or source is unavailable. Their exact claim contracts remain in `host-docs-test-sets.json` and the review UI.",
        "",
        "| Status | Page and heading | Claim | Unavailable source or owner / confirmed defect | Claim impact / limitation | Exact next action |",
        "|---|---|---|---|---|---|",
    ]
    for claim in owner_claims:
        scope, current, authority = claim["scope"], claim["current"], claim["authority"]
        requirements = claim_requirements(claim, owner_kinds, {"BLOCKED", "FAIL"})
        line = scope["source_spans"][0]["start"]
        subject = f"`{scope['route']}` — {scope['heading']} (`{scope['source_file']}:{line}`; `{claim['claim_id']}`)"
        impact = "; ".join(current["limitations"])
        owner_lines.append(
            f"| `{current['status']}` | {esc(subject)} | {esc(claim['claim']['text'])} | {esc(render_claim_requirements(requirements))} | {esc(impact)} | {esc(render_claim_actions(requirements))} |"
        )
    owner_lines += [
        "",
        "## Blocked root procedure and command source-owner checks",
        "",
        "Mixed procedure prerequisites are cross-listed by component: this register shows only source/owner components; runtime/operator components remain in the separate runtime register.",
        "",
        "| Status | Page and heading | Check target and claim | Unavailable source or owner | Claim impact / limitation | Exact next action |",
        "|---|---|---|---|---|---|",
    ]
    for row, direct in owner_procedures:
        basis, target = row["status_basis"], row["target"]
        subject = basis["subject"]
        heading = " / ".join(subject["headings"])
        target_id = target[TARGET_FIELDS[row["level"]][-1]]
        page_heading = f"`{subject['route']}` — {heading} (`{target_id}`)"
        prerequisite = direct["unavailable_prerequisite"]
        lane_components = [
            component for component in prerequisite.get("components", [])
            if component["kind"] in owner_kinds
        ]
        lane_action = (
            f"Provide the source/owner prerequisite(s) for {row['level']} {target_id}: "
            + "; ".join(f"[{item['kind']}] {item['description']}" for item in lane_components)
            + ". Bind each exact source or dated decision and retain a focused source review."
        )
        owner_lines.append(
            f"| `BLOCKED` | {esc(page_heading)} | {esc(subject['claim'])} | {esc(prerequisite_text(prerequisite, owner_kinds))} | {esc(basis['claim_impact'])} {esc(basis['limitations'])} | {esc(lane_action)} |"
        )
    owner_lines += [
        "",
        "## Forward integration gate",
        "",
        "The concrete missing prerequisite is a documentation-governance decision, agreed with Product, Finance, Legal, and canonical-source owners, that defines who may approve each authority class and the criterion for a verified citation. A reply, PR/Jira comment, or link is candidate evidence, not acceptance. For each exact claim, record its ID and missing prerequisite; the accountable role; a dated stable source or decision locator; the exact scope and limitations; and `supplied` or `unavailable` for source evidence, or `confirm`, `narrow`, or `reject` for owner/citation evidence.",
        "",
        "An independent reviewer must bind the record to the current source occurrence and hash. `Supplied` or `confirm` may satisfy only the named evidence lane; `narrow` or `reject` requires a documentation correction and focused retest. Every other required lane remains open. Until the reviewer schema and positive/adverse tests can represent this contract, owner input is non-promoting context. No current owner acceptance is inferred or recorded.",
        "",
        "Repository-local V&V does not invent, authorize, or complete these owner decisions.",
        "",
    ]
    return "\n".join(runtime_lines), "\n".join(owner_lines)


def reconcile() -> dict[Path, bytes]:
    sets_bytes_before = SETS_PATH.read_bytes()
    sets = load_json(SETS_PATH)
    results = load_json(RESULTS_PATH)
    scores = load_json(SCORES_PATH)
    evidence_artifact_sha256 = sha256_path(REPO / EVIDENCE_REF)
    topology_evidence_sha256 = sha256_path(REPO / TOPOLOGY_CORRECTION_EVIDENCE_REF)
    require(sets.get("record_type") == "HOST_DOCS_PAGE_TEST_SETS", "unexpected test-set package")

    prior_snapshot = sets.get("scope_reconciliation", {}).get("prior_test_set_snapshot_sha256") or sha256_bytes(sets_bytes_before)
    sets["pages"] = [page for page in sets["pages"] if page["page_id"] != "PAGE-host-volume-offers"]
    require(len(sets["pages"]) == 39, "expected the preserved 39-page active baseline before Volume append")
    for page in sets["pages"]:
        source = REPO / page["source_file"]
        require(source.is_file(), f"missing page source: {source}")
        page["source_sha256"] = sha256_path(source)
    sets["pages"].append(make_volume_page())
    sets["pages"].sort(key=lambda item: item["route"])
    for page in sets["pages"]:
        source = REPO / page["source_file"]
        page["rendered_dependencies"] = rendered_dependencies(source)
        page["rendered_source_sha256"] = rendered_page_sha256(page)
    command_coverage_bindings = add_reconciled_workflow_commands(sets)
    self_test_topology_bindings = correct_self_test_command_topology(sets)
    normalize_procedure_source_scopes(sets)
    hosting_volume_step_found = False
    for page in sets["pages"]:
        for test_set in page["test_sets"]:
            for branch in test_set["branches"]:
                for step in branch["steps"]:
                    if step["step_id"] != "HOV-C01-S03":
                        continue
                    step["instruction"] = (
                        "Check the dedicated Volume Offers handoff and retain an exact "
                        "disposition for the shared-storage behavior claim."
                    )
                    step["source_lines"] = [{"start": 105, "end": 113}]
                    step["expected_observables"] = [
                        "The dedicated Volume Offers route and CLI destinations resolve; "
                        "the separate shared-storage behavior claim keeps its evidence status."
                    ]
                    step["failure_behavior"] = [
                        "A broken destination fails locally; missing runtime or source-owner "
                        "proof does not become a documentation-derived pass."
                    ]
                    hosting_volume_step_found = True
    require(hosting_volume_step_found, "missing HOV-C01-S03 for Volume overview correction")

    claims: list[dict[str, Any]] = []
    for page in sets["pages"]:
        path = REPO / page["source_file"]
        if page["route"] != "/host/volume-offers":
            claims.extend(material_blocks(page["route"], path))
            for dependency in page["rendered_dependencies"]:
                dependency_claims = material_blocks(
                    page["route"], REPO / dependency["source_file"]
                )
                for claim in dependency_claims:
                    claim["scope"]["rendered_via"] = {
                        "component": dependency["component"],
                        "host_source_file": page["source_file"],
                        "import_line": dependency["import_line"],
                        "insertion_line": dependency["insertion_line"],
                    }
                claims.extend(dependency_claims)
    reviewed_volume_claims, retired_volume_claims = volume_claims(REPO / "host/volume-offers.mdx")
    claims.extend(reviewed_volume_claims)
    claims.sort(key=lambda item: (item["scope"]["route"], item["scope"]["source_spans"][0]["start"], item["claim_id"]))
    command_claim_bindings = bind_exact_command_claims(claims, sets, scores)
    navigation_bindings = bind_pure_local_navigation_claims(claims)
    for claim in claims:
        claim["current"]["disposition_evidence_ids"] = [CLAIM_MANIFEST_EVIDENCE]
        if "command_evidence_binding" in claim["current"]:
            claim["current"]["disposition_evidence_ids"].append(COMMAND_CLAIM_MANIFEST_EVIDENCE)
    attach_claims(sets, claims)
    support_layers = build_support_layers()
    sets["state"] = "RECONCILED_CURRENT_BASELINE"
    sets["reconciled_at"] = "2026-09-03T00:00:00Z"
    sets["scope_reconciliation"] = {
        "jira": "CON-1518", "pull_request": 185,
        "primary_host_pages": 40, "authored_primary_pages": 39, "generated_primary_pages": 1,
        "cli_support_layers": 18, "sdk_support_layers": 15, "total_host_routes": 73,
        "support_layer_rule": "CLI and SDK wrappers are central-reference support contracts, not independent Host workflows.",
        "prior_test_set_snapshot_sha256": prior_snapshot,
        "historical_p1_state": "DRAFT_NOT_FROZEN_AND_RETAINED",
        "historical_p1_check": "Expected to report drift when compared with current working-tree sources; it is not the current baseline.",
        "procedure_source_scope_reconciliation": {
            "commands_checked": 179,
            "out_of_scope_commands_after_reconciliation": 0,
            "historical_existing_carrier_scope_defects_corrected": 7,
            "newly_added_carriers_requiring_scope_expansion": 2,
            "rule": "Every command source occurrence must be contained by its owning step span and test-set source context; parent headings include every child command section.",
        },
        "command_occurrence_reconciliation": {
            "static_inventory_unique_commands": 193,
            "procedure_command_carriers": 179,
            "added_authored_fenced_occurrences": command_coverage_bindings,
            "support_rule": "The static inventory is the complete command/token occurrence ledger. Procedure carriers are the subset attached to Host workflows; generated wrappers, inline/display tokens, contextual cross-links, and duplicate occurrences remain inventory/support records rather than additional workflow carriers.",
        },
        "self_test_command_topology_correction": {
            "finding_id": "F-HOST-SELF-TEST-COMMAND-TOPOLOGY",
            "evidence_id": TOPOLOGY_CORRECTION_EVIDENCE,
            "legacy_carrier_step": SELF_TEST_LEGACY_STEP_ID,
            "corrected_bindings": self_test_topology_bindings,
            "historical_procedure_bindings_rekeyed": sum(
                SELF_TEST_HISTORICAL_BINDING_COUNTS.values()
            ),
            "rule": (
                "Each command carrier belongs to the setup/action step whose exact source "
                "span contains it; retained statuses remain command-specific and are not "
                "promoted by relocation."
            ),
        },
    }
    sets["support_layers"] = support_layers
    sets["material_claims"] = claims
    sets["retired_material_claims"] = retired_volume_claims + [{
        "claim_id": "HOV-C-VOLUME-ALIGNMENT-HISTORICAL",
        "status": "FAIL",
        "source": (
            "host/hosting-overview.mdx:109 at pre-correction source-text SHA-256 "
            "747f8ff68e10918a3d615b283da360ef576647858ca974a67b71f8a5ddc6966b"
        ),
        "claim": (
            "Volume offer end dates must align with GPU offer end dates; unlisting "
            "a machine also unlists its volume offers."
        ),
        "failure": (
            "The commitment-window assertion contradicted the deliberately narrowed "
            "Volume Offers claim and had no Product/Legal authority; the unlisting "
            "behavior also lacked claim-suitable canonical backend or runtime proof."
        ),
        "correction": (
            "Removed both unsupported behavior assertions from Hosting Overview and "
            "kept the dedicated Volume Offers and central CLI-reference handoffs."
        ),
        "retest_evidence_id": NAVIGATION_EVIDENCE,
    }]
    claim_page_dispositions = []
    for page in sets["pages"]:
        page_claims = [claim for claim in claims if claim["page_id"] == page["page_id"]]
        status_counts = Counter(claim["current"]["status"] for claim in page_claims)
        semantic_status = aggregate_status([claim["current"]["status"] for claim in page_claims])
        require(semantic_status is not None, f"page has no semantic claim disposition: {page['route']}")
        claim_page_dispositions.append({
            "page_id": page["page_id"], "route": page["route"], "title": page["title"],
            "status": semantic_status,
            "counts": {status: status_counts[status] for status in STATUS_ORDER if status_counts[status]},
            "rationale": "Material-claim semantic rollup with precedence FAIL > BLOCKED > STALE > UNVALIDATED > NOT_APPLICABLE/PASS. This is separate from procedure execution status.",
            "next_action": (
                "Resolve every confirmed claim/citation defect and retain its focused retest before semantic acceptance."
                if semantic_status == "FAIL"
                else "Supply each exact named unavailable prerequisite under authorization."
                if semantic_status == "BLOCKED"
                else "Bind claim-suitable canonical source, runtime observation, or accountable-owner evidence."
                if semantic_status == "UNVALIDATED"
                else None
            ),
        })
    sets["material_claim_coverage"] = {
        "method": "Current rendered source-block occurrence inventory for 39 pages, including imported local MDX prose and visible Frame captions, plus a reviewed 39-claim atomic Volume Offers manifest.",
        "claims": len(claims), "pages": 40,
        "statuses": dict(Counter(item["current"]["status"] for item in claims)),
        "page_dispositions": claim_page_dispositions,
        "coverage_limit": "Generic page claims are conservatively UNVALIDATED until claim-suitable source/runtime/owner evidence is bound; this is complete occurrence accounting, not semantic acceptance.",
    }
    sets["counts"] = count_topology(sets)
    require(sets["counts"] == {"pages": 40, "test_sets": 101, "branches": 207, "steps": 477,
                               "command_carriers": 179, "command_bearing_steps": 121},
            f"unexpected reconciled topology: {sets['counts']}")
    # Do not bind generated output to the current parent commit: committing that
    # output would immediately make it stale. Exact source bytes are bound below;
    # the resulting Git tree/commit seals the complete publication candidate.
    sets["source"].pop("reconciled_docs_head", None)
    sets["source"].pop("reconciled_docs_head_tree", None)
    sets["source"]["reconciled_identity_method"] = (
        "PRIMARY_AND_RENDERED_SOURCE_SHA256_PLUS_FINAL_GIT_TREE"
    )
    sets["source"]["reconciled_primary_source_sha256"] = sha256_bytes(
        "".join(f"{page['route']}\0{page['source_sha256']}\n" for page in sets["pages"]).encode()
    )
    sets["source"]["reconciled_rendered_source_sha256"] = sha256_bytes(
        "".join(
            f"{page['route']}\0{page['rendered_source_sha256']}\n"
            for page in sets["pages"]
        ).encode()
    )
    sets["source"]["safe_classification_sha256"] = sha256_path(REPO / "host-docs-command-access.json")
    sets["source"]["working_tree_state_ref"] = (
        "verification/evidence/2026-09-03-host-repository-rebase-01/result.md"
        "#pre-edit-working-tree-baseline"
    )
    entities, children, contexts = enumerate_topology(sets)
    command_keys = command_key_index(entities)
    command_proof_reviewer_keys = {
        command_id: command_keys[command_id]
        for command_id in COMMAND_PROOF_REVIEWER_TARGET_STATUSES
    }
    for key, contract in EXACT_COMMAND_EVIDENCE_CONTRACTS.items():
        require(key in entities, f"missing exact command evidence-contract target: {key}")
        require(
            entities[key]["text"] == contract["command_text"],
            f"exact command evidence-contract text drifted: {key}",
        )
    affected_attempt_ids = normalize_historical_self_test_bindings(results, command_keys)
    link_topology_accounting_correction(results, affected_attempt_ids)
    old_projection_records = normalize_preserved_projection_command_keys(
        results["current_status_projection"]["records"], command_keys
    )
    old_records = {target_key(row["level"], row["target"]): row for row in old_projection_records
                   if row["target"].get("page_id") != "PAGE-host-volume-offers"
                   and row["target"].get("command_id") not in {
                       spec["command_id"] for spec in RECONCILED_WORKFLOW_COMMANDS
                   }
                   and row["target"].get("command_id") not in RETIRED_RECONCILIATION_COMMAND_IDS}
    require(len(old_records) == 972, "expected 972 preserved pre-Volume current targets")
    require(all(
        key in old_records
        for key in entities
        if key[1] != "PAGE-host-volume-offers"
        and not (key[0] == "COMMAND" and key[-1] in {
            spec["command_id"] for spec in RECONCILED_WORKFLOW_COMMANDS
        })
    ),
            "active topology no longer matches preserved status projection")
    statuses, own_statuses = desired_statuses(entities, children, old_records)
    require(
        {
            command_id: statuses.get(key)
            for command_id, key in command_proof_reviewer_keys.items()
        } == COMMAND_PROOF_REVIEWER_TARGET_STATUSES,
        "command-proof reviewer target statuses changed unexpectedly",
    )

    self_test_command_keys = {
        command_keys[spec["command_id"]] for spec in SELF_TEST_COMMAND_PLACEMENTS
    }
    topology_correction_keys = set(self_test_command_keys)
    for command_key in self_test_command_keys:
        topology_correction_keys.update({
            ("PAGE", command_key[1]),
            ("TEST_SET", *command_key[1:3]),
            ("BRANCH", *command_key[1:4]),
            ("STEP", *command_key[1:5]),
        })
    topology_correction_keys.add((
        "STEP", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID,
        SELF_TEST_LEGACY_BRANCH_ID, SELF_TEST_LEGACY_STEP_ID,
    ))
    require(
        len(topology_correction_keys) == 11
        and topology_correction_keys <= set(entities),
        f"unexpected self-test topology-correction target set: {topology_correction_keys}",
    )
    first_topology_status_changes = {
        key for key in topology_correction_keys
        if old_records[key]["current_status"] != statuses[key]
    }
    old_topology_result = next((
        row for row in results.get("procedure_results", [])
        if row["evidence_id"] == TOPOLOGY_CORRECTION_EVIDENCE
    ), None)
    retained_topology_status_changes = {
        target_key(target["level"], target["target"])
        for target in (old_topology_result or {}).get("targets", [])
        if target.get("basis_role") == "STATUS_RECLASSIFICATION"
    }
    topology_status_reclassification_keys = (
        first_topology_status_changes | retained_topology_status_changes
    )
    expected_topology_status_changes = {
        ("BRANCH", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-bundle-dir"),
        ("STEP", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-normal", "ST-E01-normal-s01"),
        ("STEP", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-normal", "ST-E01-normal-s02"),
        ("STEP", SELF_TEST_PAGE_ID, SELF_TEST_SET_ID, "ST-E01-bundle-dir", "ST-E01-bundle-dir-s02"),
    }
    require(
        topology_status_reclassification_keys == expected_topology_status_changes,
        "self-test topology correction produced an unexpected status reclassification",
    )

    first_rebase_keys = {key for key, row in old_records.items() if statuses[key] != row["current_status"]}
    old_rebase_result = next((row for row in results.get("procedure_results", [])
                              if row["evidence_id"] == REBASE_EVIDENCE), None)
    retained_status_rebase_keys: set[tuple[str, ...]] = set()
    if old_rebase_result:
        old_targets = old_rebase_result["targets"]
        for target in old_targets:
            if target.get("basis_role") == "STATUS_RECLASSIFICATION" or (
                "basis_role" not in target and len(old_targets) == 525
            ):
                retained_status_rebase_keys.add(target_key(target["level"], target["target"]))
    status_rebased_keys = first_rebase_keys | retained_status_rebase_keys
    require(len(status_rebased_keys) == 531,
            f"expected 531 retained status-reclassification targets, found {len(status_rebased_keys)}")

    # The topology file is the active baseline, so its nested status fields
    # must mirror the canonical projection rather than retain a conflicting
    # pre-reconciliation value. Historical attempts and the P1 draft preserve
    # the earlier dispositions separately.
    for key, entity in entities.items():
        entity["execution_status"] = statuses[key]
        if key[0] == "TEST_SET":
            entity["source_context"]["rendered_status"] = statuses[key]
    sets["scope_reconciliation"]["nested_execution_status_semantics"] = (
        "MIRROR_OF_CURRENT_STATUS_PROJECTION; evidence and rationale are in host-docs-test-results.json"
    )
    sets_bytes = json_bytes(sets)
    snapshot = sha256_bytes(sets_bytes)

    evidence_index = build_evidence_index(results, entities)
    canonical_source_binding_keys = {
        key for key in entities
        if (key[0] == "COMMAND" and key[-1] in TEAM_CATALOG_COMMAND_IDS)
        or (key[0] == "STEP" and key[-1] in SELF_TEST_PARITY_STEP_IDS)
    }
    require(len(canonical_source_binding_keys) == 19,
            f"expected 19 pinned canonical-source bindings, found {len(canonical_source_binding_keys)}")
    evidence_index[SOURCE_BINDING_EVIDENCE] = {
        "attempt_id": CURRENT_ATTEMPT, "result_kind": "PROCEDURE_RESULT",
        "method": "PINNED_CANONICAL_SOURCE_CONFORMANCE",
        "limitations": "This supports only exact command registration/catalog existence and deterministic historical-source regeneration; runtime account behavior and current self-test product behavior remain outside the proof ceiling.",
        "superseded": False,
        "bindings": {key: "PASS" for key in canonical_source_binding_keys},
    }
    reconciled_command_keys = {
        key for key in entities
        if key[0] == "COMMAND"
        and key[-1] in {spec["command_id"] for spec in RECONCILED_WORKFLOW_COMMANDS}
    }
    require(len(reconciled_command_keys) == 3,
            f"expected three reconciled command targets, found {len(reconciled_command_keys)}")
    evidence_index[COMMAND_COVERAGE_EVIDENCE] = {
        "attempt_id": CURRENT_ATTEMPT, "result_kind": "PROCEDURE_RESULT",
        "method": "STATIC_COMMAND_OCCURRENCE_AND_SAFETY_CLASSIFICATION_RETEST",
        "limitations": "This proves exact authored occurrence, topology binding, and conservative safety gating only; none of the privileged, rebooting, mutating, or representative-Host behavior ran.",
        "superseded": False,
        "bindings": {key: "BLOCKED" for key in reconciled_command_keys},
    }
    score_by_command_before = {row["command_id"]: row for row in scores["records"]}
    na_by_command = {row["command_id"]: row for row in scores["not_applicable_records"]}

    def preferred_evidence(key: tuple[str, ...], status: str) -> list[str]:
        preferred: list[str] = []
        if key in topology_correction_keys:
            preferred.append(TOPOLOGY_CORRECTION_EVIDENCE)
        if key in canonical_source_binding_keys and status == "PASS":
            preferred.append(SOURCE_BINDING_EVIDENCE)
        if key[0] == "COMMAND":
            source = (na_by_command.get(key[-1]) if status == "NOT_APPLICABLE"
                      else score_by_command_before.get(key[-1]))
            if source:
                preferred.extend(source.get("direct_evidence_ids", source.get("evidence_ids", [])))
        old = old_records.get(key)
        if old:
            old_target_basis = old.get("status_basis", {}).get("target_basis")
            if old_target_basis and old_target_basis.get("status") == status:
                preferred.extend(old_target_basis.get("supporting_evidence_ids", []))
            preferred.extend(old.get("evidence_ids", []))
        return list(dict.fromkeys(preferred))

    child_bearing = {key for key, rows in children.items() if rows}
    root_blocked_keys = {
        key for key in entities
        if statuses[key] == "BLOCKED" and root_prerequisite(key, contexts[key], []) is not None
    }
    composite_keys = {
        key for key in child_bearing
        if (aggregate_status([statuses[child] for child, required in children[key] if required]) != statuses[key]
            or key in root_blocked_keys)
    }
    # A composite parent's current status needs a target-bound accounting row.
    # Root blockers need one only when no earlier exact blocker record exists.
    missing_root_blocker_binding = {
        key for key in root_blocked_keys
        if not matching_evidence(key, "BLOCKED", evidence_index, preferred_evidence(key, "BLOCKED"))
    }
    basis_rebound_keys = {
        key for key in (composite_keys | missing_root_blocker_binding)
        if key[1] != "PAGE-host-volume-offers"
    }
    rebase_evidence_keys = status_rebased_keys | basis_rebound_keys

    # The repository rebase result is now retained history.  Its unaffected
    # bindings must still match the current status exactly; the eleven changed
    # topology/basis targets are accounted for by a new appended correction.
    require(REBASE_EVIDENCE in evidence_index, "missing retained repository-rebase evidence")
    for key in rebase_evidence_keys - topology_correction_keys:
        require(
            evidence_index[REBASE_EVIDENCE]["bindings"].get(key) == statuses[key],
            f"retained repository-rebase binding no longer matches {key}",
        )
    evidence_index[TOPOLOGY_CORRECTION_EVIDENCE] = {
        "attempt_id": TOPOLOGY_CORRECTION_ATTEMPT,
        "result_kind": "PROCEDURE_RESULT",
        "method": "STATIC_SELF_TEST_COMMAND_TOPOLOGY_CORRECTION_RETEST",
        "limitations": (
            "Static source/topology/accounting evidence only; no credentialed Host/API, "
            "paid, WAN, privileged, mutating, destructive, or workload behavior ran."
        ),
        "superseded": False,
        "bindings": {key: statuses[key] for key in topology_correction_keys},
    }
    volume_keys = {key for key in entities if key[1] == "PAGE-host-volume-offers"}
    evidence_index[VOLUME_EVIDENCE] = {
        "attempt_id": CURRENT_ATTEMPT, "result_kind": "PROCEDURE_RESULT",
        "method": "STATIC_CANONICAL_SOURCE_CITATION_OPENAPI_AND_LINK_RETEST",
        "limitations": "Static/local only; no marketplace, persistence, scheduling, billing, contract, mount, workload, or cleanup behavior ran.",
        "bindings": {key: statuses[key] for key in volume_keys},
    }

    def exact_direct_evidence(key: tuple[str, ...], status: str) -> list[str]:
        if key[1] == "PAGE-host-volume-offers":
            return [VOLUME_EVIDENCE]
        matches = matching_evidence(
            key, status, evidence_index, preferred_evidence(key, status),
            allow_accounting=status == "UNVALIDATED",
        )
        if matches:
            return [matches[0]]
        if key in rebase_evidence_keys and status in {"BLOCKED", "UNVALIDATED"}:
            return [
                TOPOLOGY_CORRECTION_EVIDENCE
                if key in topology_correction_keys
                else REBASE_EVIDENCE
            ]
        if status in {"PASS", "FAIL", "NOT_APPLICABLE"}:
            raise ReconciliationError(
                f"{key}: {status} requires non-accounting exact-target retained evidence"
            )
        return []

    own_evidence_by_key: dict[tuple[str, ...], list[str]] = {}
    row_evidence_by_key: dict[tuple[str, ...], list[str]] = {}
    for key in entities:
        if key in composite_keys:
            row_evidence_by_key[key] = ([VOLUME_EVIDENCE] if key[1] == "PAGE-host-volume-offers"
                                        else [TOPOLOGY_CORRECTION_EVIDENCE]
                                        if key in topology_correction_keys
                                        else [REBASE_EVIDENCE])
            own_evidence_by_key[key] = exact_direct_evidence(key, own_statuses[key])
        elif key in child_bearing:
            old = old_records.get(key)
            if key[1] == "PAGE-host-volume-offers":
                row_evidence_by_key[key] = [VOLUME_EVIDENCE]
            elif key in rebase_evidence_keys:
                row_evidence_by_key[key] = [
                    TOPOLOGY_CORRECTION_EVIDENCE
                    if key in topology_correction_keys
                    else REBASE_EVIDENCE
                ]
            else:
                require(old is not None and old.get("evidence_ids"), f"rollup lacks retained accounting evidence: {key}")
                row_evidence_by_key[key] = old["evidence_ids"]
            own_evidence_by_key[key] = []
        else:
            row_evidence_by_key[key] = exact_direct_evidence(key, statuses[key])
            own_evidence_by_key[key] = row_evidence_by_key[key]

    projection_by_key: dict[tuple[str, ...], dict[str, Any]] = {}
    # Children must be materialized before parents so blocker prerequisites can
    # cite and display their exact originating targets.
    build_order = sorted(entities, key=lambda item: (-list(TARGET_FIELDS).index(item[0]), item[1:]))
    for key in build_order:
        status = statuses[key]
        old = old_records.get(key)
        evidence_ids = row_evidence_by_key[key]
        if evidence_ids:
            attempt_ids = {evidence_index[evidence_id]["attempt_id"] for evidence_id in evidence_ids}
            require(len(attempt_ids) == 1, f"projection evidence spans attempts: {key} {evidence_ids}")
            attempt_id = next(iter(attempt_ids))
        else:
            require(old is not None, f"missing current record: {key}")
            attempt_id = old["attempt_id"]
        basis = basis_for(
            key, status, own_statuses[key], contexts[key], children, statuses,
            evidence_ids, own_evidence_by_key[key], evidence_index,
            {child: projection_by_key[child]["status_basis"] for child, _required in children.get(key, [])},
            snapshot,
        )
        projection_by_key[key] = {
            "level": key[0], "target": target_dict(key), "current_status": status,
            "attempt_id": attempt_id, "evidence_ids": evidence_ids,
            "rationale": rationale_for(key, status, own_statuses[key], children, statuses, basis),
            "status_basis": basis,
        }
    projection_records = [projection_by_key[key] for key in sorted(
        entities, key=lambda item: (list(TARGET_FIELDS).index(item[0]), item[1:])
    )]

    results["attempts"] = [row for row in results["attempts"] if row["attempt_id"] not in GENERATED_ATTEMPTS]
    results["procedure_results"] = [row for row in results.get("procedure_results", []) if row["evidence_id"] not in GENERATED_EVIDENCE]
    results["direct_proof_ceilings"] = [row for row in results["direct_proof_ceilings"] if row["evidence_id"] != VOLUME_EVIDENCE]
    results["support_layer_results"] = [{
        "evidence_id": SUPPORT_EVIDENCE,
        "attempt_id": CURRENT_ATTEMPT,
        "method": "STATIC_WRAPPER_FRAGMENT_CENTRAL_REFERENCE_BINDING",
        "limitations": "This proves only exact wrapper/import/central-reference structure and current file hashes; it does not validate command runtime or a separate Host workflow.",
        "bindings": [{
            "support_id": item["support_id"], "status": item["status"],
            "layer": item["layer"], "route": item["route"],
            "source_file": item["source_file"], "source_sha256": item["source_sha256"],
            "fragment_file": item["fragment_file"], "fragment_sha256": item["fragment_sha256"],
            "central_reference_file": item["central_reference_file"],
            "central_reference_route": item["central_reference_route"],
            "central_reference_sha256": item["central_reference_sha256"],
            "evidence_role": "EXACT_STATIC_SUPPORT_LAYER_BINDING",
        } for item in support_layers],
    }]
    results["material_claim_results"] = [
        {
            "evidence_id": CLAIM_MANIFEST_EVIDENCE,
            "attempt_id": CURRENT_ATTEMPT,
            "method": "MATERIAL_CLAIM_OCCURRENCE_AND_DISPOSITION_MANIFEST",
            "limitations": "This manifest proves exact occurrence/disposition accounting. Only each binding's separately listed supporting evidence and authority refs can support semantic truth; documentation text never proves itself.",
            "bindings": [{
                "claim_id": claim["claim_id"], "page_id": claim["page_id"],
                "status": claim["current"]["status"],
                "source_file": claim["scope"]["source_file"],
                "heading": claim["scope"]["heading"],
                "source_spans": claim["scope"]["source_spans"],
                "source_text_sha256": claim["scope"]["source_text_sha256"],
                "rendered_via": claim["scope"]["rendered_via"],
                "evidence_role": (
                    "CLAIM_SUITABLE_BOUNDED_SUPPORT"
                    if claim["current"]["status"] == "PASS"
                    else "CONFIRMED_CITATION_OR_SOURCE_BINDING_DEFECT"
                    if claim["current"]["status"] == "FAIL"
                    else "UNAVAILABLE_PREREQUISITE_DISPOSITION"
                    if claim["current"]["status"] == "BLOCKED"
                    else "PARTIAL_EVIDENCE_BOUND_STATUS_UNCHANGED"
                    if claim["current"]["evidence_ids"]
                    else "OCCURRENCE_ACCOUNTING_ONLY"
                ),
                "required_evidence_types": claim["evidence_requirement"]["types"],
                "satisfied_evidence_types": (
                    claim["evidence_requirement"]["types"]
                    if claim["current"]["status"] == "PASS"
                    else sorted({
                        requirement["evidence_type"]
                        for requirement in claim["authority"].get(
                            "unresolved_evidence_requirements", []
                        )
                        if requirement.get("current_status") == "PASS"
                    })
                ),
                "partially_supported_evidence_types": sorted({
                    requirement["evidence_type"]
                    for requirement in claim["authority"].get(
                        "unresolved_evidence_requirements", []
                    )
                    if requirement.get("bound_evidence_ids")
                    and requirement.get("current_status") != "PASS"
                }),
                "supporting_evidence_ids": claim["current"]["evidence_ids"],
                "command_evidence_binding": claim["current"].get("command_evidence_binding"),
                "limitations": claim["current"]["limitations"],
            } for claim in claims],
        },
        {
            "evidence_id": NAVIGATION_EVIDENCE,
            "attempt_id": CURRENT_ATTEMPT,
            "method": "STATIC_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION",
            "limitations": "This proves only exact current local route/file and fragment existence with retained hashes. It does not support the linked page's semantic claims.",
            "bindings": navigation_bindings,
        },
        {
            "evidence_id": COMMAND_CLAIM_MANIFEST_EVIDENCE,
            "attempt_id": CURRENT_ATTEMPT,
            "method": "EXACT_FENCED_COMMAND_TO_CARRIER_EVIDENCE_BINDING",
            "limitations": "This manifest proves exact claim/carrier/source/evidence accounting. Only score-3 PASS carriers whose retained execution satisfies every declared runtime-only lane close bounded command claims; source-requiring and score-2 claims remain partial, and no parent claim inherits command status.",
            "bindings": command_claim_bindings,
        },
    ]
    results["attempts"].extend([
        {"attempt_id": BASELINE_ATTEMPT, "kind": "WORKING_TREE_BASELINE_CAPTURE", "status": "PASS",
         "execution_state": "EXECUTED",
         "summary": {
             "captured_at": "2026-09-03T16:40:46Z",
             "head": "3b7e56f0db6588953589e0692e75b7274526d5f9",
             "head_tree": "b67e225c17901b4fa82c24f070c4de966de50681",
             "upstream_ahead": 7, "upstream_behind": 0,
             "retained_lines": 254,
         },
         "reason": "The pre-edit repository identity, porcelain path/status listing, diffstat/name-status, eight selected canonical-artifact hashes, and worktree registry were retained before this completion pass. This is not a byte-for-byte content snapshot of every dirty or untracked path.",
         "evidence_ref": BASELINE_EVIDENCE_REF},
        {"attempt_id": PRECHECK_ATTEMPT, "kind": "STATIC_REPOSITORY_COMPLETION_PRECHECK", "status": "FAIL",
         "execution_state": "EXECUTED",
         "summary": {"primary_pages_before": 39, "missing_primary_pages": 1, "generic_leaf_blockers": 301,
                     "host_empty_anchor_failures": 97, "volume_repository_defects": 8,
                     "new_host_executions": 0},
         "reason": "The preserved pre-correction checks found the missing Volume baseline, incomplete claim accounting, generic blocker taxonomy, empty named anchors, multiline CLI/options gap, unsafe command classification, incomplete Volume OpenAPI contract, and two uncited normative Volume statements.",
         "evidence_ref": EVIDENCE_REF,
         "evidence_ref_sha256": evidence_artifact_sha256},
        {"attempt_id": CURRENT_ATTEMPT, "kind": "STATIC_REPOSITORY_COMPLETION_REBASE", "status": "PASS",
         "execution_state": "EXECUTED",
         "summary": {"pre_rebase_pages": 39, "post_rebase_pages": 40,
                     "old_projection_records_changed": 531, "new_volume_targets": 29,
                     "basis_rebound_targets": len(basis_rebound_keys - status_rebased_keys),
                     "rebase_binding_targets": len(rebase_evidence_keys),
                     "material_claims": len(claims), "support_layers": 33,
                     "local_navigation_claims": len(navigation_bindings),
                     "exact_command_claim_bindings": len(command_claim_bindings),
                     "material_claim_result_records": 3, "support_layer_result_records": 1,
                     "reconciled_authored_command_occurrences": len(command_coverage_bindings),
                     "pinned_canonical_source_bindings": len(canonical_source_binding_keys),
                     "new_host_executions": 0, "new_command_results": 0},
         "reason": "The authorized repository-local reconciliation and correction retests completed. Target-specific runtime/source-owner blockers, the retained CLI credential-permission defect, and external work remain open.",
         "evidence_ref": EVIDENCE_REF,
         "evidence_ref_sha256": evidence_artifact_sha256,
         "accounting_corrected_by": TOPOLOGY_CORRECTION_ATTEMPT},
        {"attempt_id": TOPOLOGY_CORRECTION_ATTEMPT,
         "kind": "CURRENT_STATUS_TOPOLOGY_CORRECTION", "status": "PASS",
         "execution_state": "EXECUTED",
         "summary": {
             "command_carriers_relocated": 3,
             "current_projection_command_keys_rekeyed": 3,
             "historical_procedure_bindings_rekeyed": sum(
                 SELF_TEST_HISTORICAL_BINDING_COUNTS.values()
             ),
             "affected_attempt_accounting_chains": 5,
             "status_reclassification_targets": len(topology_status_reclassification_keys),
             "status_basis_rebound_targets": len(
                 topology_correction_keys - topology_status_reclassification_keys
             ),
             "new_host_executions": 0,
             "new_command_results": 0,
         },
         "reason": (
             "The fail-closed repository retest attached each exact self-test command "
             "occurrence to its setup/action step, preserved its command outcome, and "
             "recomputed only the affected required-child rollups. This is topology and "
             "accounting evidence, not runtime validation."
         ),
         "evidence_ref": TOPOLOGY_CORRECTION_EVIDENCE_REF,
         "evidence_ref_sha256": topology_evidence_sha256},
        {
            "attempt_id": COMMAND_PROOF_REVIEWER_ATTEMPT_01,
            "kind": "STATIC_SOURCE_SIGNATURE_RUNTIME_EVIDENCE_UI_RECONCILIATION",
            "status": "PASS",
            "execution_state": "EXECUTED",
            "summary": {
                "completed_at": "2026-09-03T20:27:25Z",
                "pages": 2,
                "exact_command_bindings": 5,
                "target_statuses": COMMAND_PROOF_REVIEWER_TARGET_STATUSES,
                "reviewer_tests_passed": 24,
                "reviewer_tests_total": 24,
                "support_layers": 33,
                "cli_support_layers": 18,
                "sdk_support_layers": 15,
                "new_host_executions": 0,
            },
            "reason": (
                "The initial repository-local reviewer correction established exact page, "
                "heading, source-signature, runtime-evidence, status-rationale, and next-action "
                "presentation for five command examples at the retained 20:27 UTC artifact "
                "boundary. Later bytes and evidence-contract changes are covered only by the "
                "linked post-change retest."
            ),
            "evidence_ref": COMMAND_PROOF_REVIEWER_EVIDENCE_REF_01,
            "qualification_superseded_by": COMMAND_PROOF_REVIEWER_ATTEMPT_02,
        },
        {
            "attempt_id": COMMAND_PROOF_REVIEWER_ATTEMPT_02,
            "kind": "STATIC_COMMAND_PROOF_REVIEWER_POST_CHANGE_RETEST",
            "status": "PASS",
            "execution_state": "EXECUTED",
            "summary": {
                "completed_at": "2026-09-03T21:01:48Z",
                "pages": 2,
                "exact_command_bindings": 5,
                "target_statuses": COMMAND_PROOF_REVIEWER_TARGET_STATUSES,
                "focused_reconciler_tests_passed": 3,
                "focused_reconciler_tests_total": 3,
                "full_reconciler_tests_passed": 41,
                "full_reconciler_tests_total": 41,
                "reviewer_tests_passed": 24,
                "reviewer_tests_total": 24,
                "registration_focused_tests_passed": 4,
                "registration_focused_tests_total": 4,
                "registration_reconciler_tests_passed": 42,
                "registration_reconciler_tests_total": 42,
                "repository_python_tests_passed": 97,
                "repository_python_tests_total": 97,
                "retained_status_evidence_records": 96,
                "status_bearing_procedure_results": 42,
                "support_layers": 33,
                "cli_support_layers": 18,
                "sdk_support_layers": 15,
                "new_host_executions": 0,
            },
            "reason": (
                "The post-final-change repository-local retest covers the current two-lane "
                "reviewer contract, formal retained-evidence registration, plain self-test "
                "runtime-only requirement, VM-off source-plus-runtime restoration contract, "
                "and strict evidence-manifest validation without changing procedure status."
            ),
            "evidence_ref": COMMAND_PROOF_REVIEWER_EVIDENCE_REF_02,
            "qualification_superseded_by": PR_READY_PACKAGING_ATTEMPT,
        },
        {
            "attempt_id": PR_READY_PACKAGING_ATTEMPT,
            "kind": "STATIC_PR_READY_PACKAGING_REPLAY",
            "status": "PASS",
            "execution_state": "EXECUTED",
            "summary": {
                "completed_at": "2026-09-04T16:23:35Z",
                "pages": 40,
                "exact_command_bindings": 5,
                "target_statuses": COMMAND_PROOF_REVIEWER_TARGET_STATUSES,
                "registration_focused_tests_passed": 4,
                "registration_focused_tests_total": 4,
                "registration_reconciler_tests_passed": 42,
                "registration_reconciler_tests_total": 42,
                "repository_python_tests_passed": 97,
                "repository_python_tests_total": 97,
                "reviewer_tests_passed": 24,
                "reviewer_tests_total": 24,
                "inventory_routes": 73,
                "inventory_targets": 501,
                "inventory_commands": 193,
                "cli_occurrences_checked": 201,
                "retained_status_evidence_records": 96,
                "status_bearing_procedure_results": 42,
                "support_layers": 33,
                "cli_support_layers": 18,
                "sdk_support_layers": 15,
                "new_host_executions": 0,
            },
            "reason": (
                "The repository-local closeout replay binds the final reviewer, "
                "traceability, blocker-register, generator, test, inventory, and "
                "source-signature artifacts without changing any procedure or material-"
                "claim status. It performed no credentialed, paid, WAN, privileged, "
                "mutating, destructive, or workload-affecting operation."
            ),
            "evidence_ref": PR_READY_PACKAGING_EVIDENCE_REF,
        },
    ])
    precheck_targets = []
    for key in entities:
        if key[1] != "PAGE-host-volume-offers":
            continue
        if key[0] == "PAGE" or key[-1] in {"TS-VOL-C01", "TS-VOL-E02", "VOL-C01-B-source-owner", "VOL-E02-B-separate-offer", "VOL-C01-S03", "VOL-E02-S02"}:
            precheck_targets.append({"level": key[0], "target": target_dict(key), "vv_status": "FAIL"})
    results["procedure_results"].extend([
        {"evidence_id": PRECHECK_EVIDENCE, "attempt_id": PRECHECK_ATTEMPT,
         "method": "STATIC_REPOSITORY_PRECHECK_AND_SOURCE_AUDIT",
         "observation": "The original 39-page package omitted Volume Offers, two Volume statements lacked required authoritative citations, and six other repository-local V&V defects were reproduced before correction.",
         "limitations": "This is preserved pre-correction repository evidence. It did not execute Host, API, paid, privileged, mutating, WAN, destructive, or workload behavior.",
         "targets": sorted(precheck_targets, key=lambda item: (list(TARGET_FIELDS).index(item["level"]), tuple(item["target"].values())))},
        {"evidence_id": TOPOLOGY_CORRECTION_EVIDENCE,
         "attempt_id": TOPOLOGY_CORRECTION_ATTEMPT,
         "method": "STATIC_SELF_TEST_COMMAND_TOPOLOGY_CORRECTION_RETEST",
         "observation": (
             "Three exact authored command carriers were moved from the narrative "
             "ST-E01-normal-s02 checkpoint to their source-owning setup/action steps. "
             "Nine preserved procedure-result index bindings and three current-projection "
             "keys were rekeyed without changing their recorded command statuses; four "
             "affected aggregate targets changed status and seven retained status while "
             "receiving the corrected topology basis."
         ),
         "limitations": (
             "Static source/topology/accounting evidence only. Historical attempt records "
             "and retained evidence artifacts are preserved; active index coordinates were "
             "rekeyed to the current canonical topology. No credentialed Host/API, paid, "
             "WAN, privileged, mutating, destructive, or workload behavior ran."
         ),
         "targets": [
             {"level": key[0], "target": target_dict(key), "vv_status": statuses[key],
              "basis_role": (
                  "STATUS_RECLASSIFICATION"
                  if key in topology_status_reclassification_keys
                  else "STATUS_BASIS_REBOUND"
              )}
             for key in sorted(
                 topology_correction_keys,
                 key=lambda item: (list(TARGET_FIELDS).index(item[0]), item[1:]),
             )
         ]},
        {"evidence_id": VOLUME_EVIDENCE, "attempt_id": CURRENT_ATTEMPT,
         "method": "STATIC_CANONICAL_SOURCE_CITATION_OPENAPI_AND_LINK_RETEST",
         "observation": "Volume Offers now has 39 atomic claim contracts, 29 governed procedure targets, and 11 command carriers checked against pinned CLI source, corrected OpenAPI request shapes, current citations, and local destinations.",
         "limitations": "Static/local only; no marketplace, persistence, scheduling, billing, contract, mount, workload, or cleanup behavior ran.",
         "targets": [
             {"level": key[0], "target": target_dict(key), "vv_status": statuses[key]}
             | ({"source_refs": refs} if (
                 refs := source_refs_for(key, contexts[key], statuses[key])
             ) else {})
                     for key in sorted((key for key in entities if key[1] == "PAGE-host-volume-offers"), key=lambda item: (list(TARGET_FIELDS).index(item[0]), item[1:]))]},
        {"evidence_id": COMMAND_COVERAGE_EVIDENCE, "attempt_id": CURRENT_ATTEMPT,
         "method": "STATIC_COMMAND_OCCURRENCE_AND_SAFETY_CLASSIFICATION_RETEST",
         "observation": "Three authored fenced command occurrences previously present only in the static inventory are now exact procedure command carriers with source hashes, inventory cross-references, conservative safety classifications, and concrete unavailable prerequisites.",
         "limitations": "This is repository-local source/topology evidence only. The GRUB change, reboot, VM post-enable checks, and all representative Host behavior were not executed.",
         "targets": [{"level": key[0], "target": target_dict(key), "vv_status": statuses[key]}
                     for key in sorted(reconciled_command_keys, key=lambda item: item[1:])]},
        {"evidence_id": SOURCE_BINDING_EVIDENCE, "attempt_id": CURRENT_ATTEMPT,
         "method": "PINNED_CANONICAL_SOURCE_CONFORMANCE",
         "observation": "Seventeen Host Teams catalog carriers are bound to exact vast-ai/vast-cli command-registration files at the pinned revision, and both generated self-test parity steps are bound to the local generator plus the exact historical CLI/image revisions consumed by the byte-identical regeneration.",
         "limitations": "This supports only exact static registration/catalog and deterministic historical-source generation claims. It does not establish runtime account/team behavior or current self-test Product policy and workload behavior.",
         "targets": [{"level": key[0], "target": target_dict(key), "vv_status": statuses[key],
                      "source_refs": source_refs_for(key, contexts[key], statuses[key])}
                     for key in sorted(canonical_source_binding_keys,
                                       key=lambda item: (list(TARGET_FIELDS).index(item[0]), item[1:]))]},
    ])
    results["direct_proof_ceilings"].append({"evidence_id": VOLUME_EVIDENCE, "ceiling": "BOUNDED_STATIC_SUPPORT"})
    results["direct_proof_ceilings"] = [
        row for row in results["direct_proof_ceilings"]
        if row["evidence_id"] != COMMAND_COVERAGE_EVIDENCE
    ]
    results["direct_proof_ceilings"].append({
        "evidence_id": COMMAND_COVERAGE_EVIDENCE,
        "ceiling": "EXACT_OCCURRENCE_AND_SAFETY_GATE_ONLY",
    })
    # SOURCE_BINDING_EVIDENCE is status/source provenance, not command-score
    # proof.  Its exact per-target source_refs and procedure-result limitation
    # carry the ceiling; adding it to direct_proof_ceilings would leave an
    # unconsumed score-proof capability.
    results["direct_proof_ceilings"] = [
        row for row in results["direct_proof_ceilings"]
        if row["evidence_id"] != SOURCE_BINDING_EVIDENCE
    ]
    finding_ids = {
        "F-HOST-SCOPE-VOLUME-OMISSION": ("V_AND_V_SCOPE_OMISSION", "The active procedure package omitted the current 40th top-level Host page.", "CORRECTED_AND_RETESTED"),
        "F-HOST-MATERIAL-CLAIM-COVERAGE": ("HEURISTIC_CLAIM_INVENTORY_INCOMPLETE", "The 503-item regex inventory missed material assertions and could not be the claim denominator.", "CORRECTED_WITH_OCCURRENCE_CONTRACTS"),
        "F-HOST-GENERIC-BLOCKER-TAXONOMY": ("STATUS_TAXONOMY_DEFECT", "301 leaf targets used generic missing-authority/environment/evidence blockers without a target-specific unavailable prerequisite.", "CORRECTED_AND_REQUIRED_ANCESTORS_RECOMPUTED"),
        "F-HOST-NAMED-ANCHOR-A11Y": ("HOST_ACCESSIBILITY_DEFECT", "Host pages contained 97 empty named anchors reported by the accessibility checker.", "CORRECTED_TO_ARIA_HIDDEN_SPANS_AND_RETESTED"),
        "F-HOST-CLI-MULTILINE-FLAGS": ("STATIC_CLI_VERIFIER_DEFECT", "The verifier checked only the first physical line of multiline CLI commands and omitted continuation flags.", "CORRECTED_WITH_POSITIVE_AND_ADVERSE_TESTS"),
        "F-HOST-COMMAND-RISK-CLASSIFICATION": ("SAFETY_CLASSIFICATION_DEFECT", "Volume listing mutations and create-volume spend/mutation risk were understated.", "CORRECTED_WITH_UNIT_TESTS_AND_REGENERATED"),
        "F-HOST-VOLUME-OPENAPI-CONTRACT": ("OPENAPI_CONTRACT_GAP", "Host list-volume(s) POST and list-machine volume fields were absent from the public contract.", "CORRECTED_TO_PINNED_CLIENT_REQUEST_SHAPES_AND_RETESTED"),
        "F-HOST-VOLUME-REQUIRED-CITATIONS": ("DOCUMENTATION_CITATION_DEFECT", "Two normative Volume statements lacked the Product/Legal authority required to support them.", "NARROWED_TO_SOURCE_SUPPORTED_OR_NAVIGATION_TEXT_AND_RETESTED"),
        "F-HOST-WRAPPER-WORKFLOW-TAXONOMY": ("REVIEWER_TAXONOMY_DEFECT", "Generated CLI/SDK wrappers inherited Host workflow blockers while absent from workflow inventory.", "CORRECTED_TO_CENTRAL_REFERENCE_SUPPORT_LAYER"),
        "F-HOST-PROCEDURE-COMMAND-COVERAGE": ("PROCEDURE_COMMAND_COVERAGE_DEFECT", "Three authored fenced Host workflow command occurrences were inventoried but absent from the procedure topology.", "CORRECTED_WITH_EXACT_CARRIERS_AND_STATIC_RETEST; RUNTIME_REMAINS_BLOCKED_BY_NAMED_PREREQUISITES"),
        "F-HOST-PROCEDURE-SOURCE-SCOPE": ("PROCEDURE_SOURCE_SCOPE_DEFECT", "Seven existing command carriers fell outside their owning test-set line bounds; two newly reconciled VM carriers also required parent-scope expansion.", "CORRECTED_WITH_CHILD_CONTAINMENT_INVARIANT"),
        "F-HOST-SELF-TEST-COMMAND-TOPOLOGY": ("PROCEDURE_COMMAND_TOPOLOGY_DEFECT", "Three How to Self-Test command carriers were attached to the narrative preflight/runtime-basis checkpoint instead of the setup/action steps that own their exact source occurrences.", "RELOCATED_BY_FAIL_CLOSED_GENERATOR_RULE; HISTORICAL_ATTEMPTS_AND_EVIDENCE_RETAINED; ACTIVE_INDEX_KEYS_REKEYED; AFFECTED_ROLLUPS_RECOMPUTED"),
        "F-HOST-HOSTING-OVERVIEW-VOLUME-COMMITMENT": ("CONFIRMED_DOCUMENTATION_CLAIM_DEFECT", "Hosting Overview repeated an unsupported Volume commitment-window rule and coupled it to unproven machine-unlisting behavior after the dedicated Volume page had already retired the commitment claim.", "REMOVED; HISTORICAL FAIL RETAINED; LOCAL NAVIGATION RETESTED"),
        "F-HOST-STORAGE-VOLUME-HANDOFF": ("CENTRAL_REFERENCE_TAXONOMY_DEFECT", "Storage Setup routed volume behavior through Hosting Overview instead of the reconciled dedicated Volume Offers overview.", "LINKED_DIRECTLY_TO_VOLUME_OFFERS_AND_RETESTED"),
        "F-HOST-FENCED-PLACEHOLDER-SERIALIZATION": ("MATERIAL_CLAIM_SERIALIZATION_DEFECT", "Twenty-three exact fenced-command claims dropped angle-bracket CLI placeholders because prose MDX-tag normalization was applied to code.", "CODE_WHITESPACE_NORMALIZATION_PRESERVES_LITERAL_PLACEHOLDERS; EXACT_BINDINGS_RETESTED"),
        "F-HOST-INLINE-CODE-PLACEHOLDER-SERIALIZATION": ("MATERIAL_CLAIM_SERIALIZATION_DEFECT", "Inline-code CLI placeholders and diagnostic tokens were removed as if they were MDX tags, corrupting retained claim text.", "INLINE_CODE_PROTECTED_BEFORE_MARKUP_NORMALIZATION; LOSSLESS_INVARIANT_RETESTED"),
        "F-HOST-FRAGMENT-CITATION-KIND": ("SOURCE_BINDING_CLASSIFICATION_DEFECT", "Fragment-only documentation links were incorrectly labeled EXTERNAL_SOURCE even though route resolution treated them as local.", "FRAGMENT_REFS_CLASSIFIED_LOCAL_DOCUMENTATION_AND_RETESTED"),
        "F-HOST-VOLUME-AUTHORITY-SUMMARY": ("REVIEWER_AUTHORITY_SUMMARY_DEFECT", "Seventeen unresolved Volume claims used hand-written aggregate owner labels that omitted or merged exact source, operator, and accountable-owner lanes.", "SUMMARY_DERIVED_FROM_DISTINCT_PER_LANE_RESPONSIBLE_ROLES"),
        "F-HOST-TECHNICAL-CONTRACT-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Three generated self-test error rows treated technical instance contract IDs as legal contracts, creating false required-citation failures; the cleanup row's separate billing clause still needs Product/Finance confirmation.", "TECHNICAL_IDENTIFIERS_DISAMBIGUATED; RUNTIME_SOURCE_AND_FINANCE_LANES_RETESTED"),
        "F-HOST-POLICY-CITATION-UNDERCLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Imperative workload-policy rules, plural rental-contract effects, and table-form payout figures escaped the required authoritative-citation lane.", "PAGE_AND_HEADING_AWARE_POLICY_CLASSIFICATION; EXACT_CLAIMS_RETESTED"),
        "F-HOST-LOCAL-LINK-AS-AUTHORITY": ("EVIDENCE_AUTHORITY_CLASSIFICATION_DEFECT", "A repository-local documentation or owner-contact link could count as a present policy citation even though documentation text cannot prove itself.", "ONLY EXPLICIT AUTHORITATIVE_SOURCE_CANDIDATES COUNT AS PRESENT_UNVERIFIED; LOCAL LINKS RETAINED AS NAVIGATION ONLY"),
        "F-HOST-EXTERNAL-ACTION-LINK-AS-AUTHORITY": ("EVIDENCE_AUTHORITY_CLASSIFICATION_DEFECT", "Seven required-citation claims were masked by co-located external console, upload, download, setup, or uninstall action links that do not support the asserted policy meaning.", "EXTERNAL LINKS CLASSIFIED AS AUTHORITATIVE_SOURCE_CANDIDATE, ACTION_OR_UI_DESTINATION, REFERENCE, OR CONTACT; ONLY THE FIRST CAN SATISFY CITATION PRESENCE"),
        "F-HOST-NAVIGATION-INDEX-UNDERCLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "One hundred twelve bounded local route/fragment rows in Related Pages, Common Host Questions, and persona Common Questions were treated as semantic assertions instead of local navigation contracts; ten consequently appeared as false citation defects.", "EXACT ROUTE_AND_FRAGMENT EXISTENCE ONLY IS CLOSED BY STATIC EVIDENCE; TOPIC SUITABILITY AND LINKED_PAGE SEMANTICS REMAIN EXCLUDED"),
        "F-HOST-LOCAL-HANDOFF-UNDERCLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Seven exact 'For ..., see ...' local documentation handoffs were treated as semantic assertions; one became a false payout/tax citation defect from link-label text.", "EXACT ROUTE_AND_FRAGMENT EXISTENCE ONLY IS CLOSED BY STATIC EVIDENCE; TOPIC SUITABILITY AND LINKED_PAGE SEMANTICS REMAIN EXCLUDED"),
        "F-HOST-DESCRIPTIVE-DO-NOT-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "A descriptive Headless Install sentence about provider image configuration prompts was treated as policy solely because it contained 'provider' and 'do not'.", "BARE TECHNICAL PROVIDER REMOVED FROM POLICY TRIGGER; PROVIDER_POLICY AND GENUINE NORMATIVE TERMS RETAINED"),
        "F-HOST-RENDERED-SNIPPET-DENOMINATOR": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "The rendered notification-channel snippet was omitted from the primary Host-page claim denominator and its bytes could drift without staling the page render contract.", "IMPORTED LOCAL_MDX PROSE INVENTORIED UNDER THE RENDERING HOST_ROUTE WITH EXACT DEPENDENCY_AND_INSERTION HASH BINDINGS"),
        "F-HOST-FRAME-CAPTION-DENOMINATOR": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "Twenty-four visible Frame captions describing console state and controls were skipped as generic JSX even though they are reader-facing UI assertions.", "VISIBLE FRAME_CAPTIONS INVENTORIED AS EXACT RUNTIME_OR_UI CLAIM OCCURRENCES; IMAGE ALT_TEXT REMAINS EXEMPT"),
        "F-HOST-MDX-COMMENT-DENOMINATOR": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "Non-rendered MDX generator metadata and hidden comments could be inventoried as reader-facing material claims.", "COMMENTS MASKED OUTSIDE CODE_FENCES WITH LINE GEOMETRY PRESERVED; GENERATOR PROVENANCE REMAINS IN SOURCE_CONFORMANCE EVIDENCE"),
        "F-HOST-RUNTIME-REGISTER-LANE-OMISSION": ("BLOCKER_REGISTER_COVERAGE_DEFECT", "Seven blocked non-Volume material claims used the ENVIRONMENT_OR_PERMISSION prerequisite kind but were omitted from the runtime/operator blocker register.", "RUNTIME REGISTER NOW INCLUDES EVERY BLOCKED RUNTIME_LANE PREREQUISITE_KIND WITH EXACT_CLAIM COVERAGE REGRESSION"),
        "F-HOST-VOLUME-ATOMIC-DENOMINATOR": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "The hand-reviewed Volume map omitted the identifier non-interchangeability statement, renter-workflow handoff, and two operational publishing recommendations.", "EXPANDED FROM 35 TO 39 EXACT ATOMIC CLAIM CONTRACTS WITH STATIC_OR_OWNER LANES AND SOURCE SPANS"),
        "F-HOST-UI-RUNTIME-LANE-UNDERCLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Explicit console, settings, dashboard, control, and click/open UI assertions could receive only source or owner lanes and omit the required retained UI-observation lane.", "CONSERVATIVE UI_SURFACE_AND_ACTION DETECTOR ADDS RUNTIME_OR_UI_OBSERVATION WHILE PRESERVING SEPARATE SOURCE_AND_OWNER LANES"),
        "F-HOST-LIST-CONTEXT-CLAIM-SPLIT": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "Two incomplete list lead-ins appeared as dangling citation failures while their separately inventoried items omitted the responsibility or active-contract qualifier.", "LEAD_IN SOURCE SPAN AND TEXT PROPAGATED TO EACH MATERIAL LIST_ITEM; LEAD_IN NOT COUNTED AS A SEPARATE CLAIM"),
        "F-HOST-TECHNICAL-SUPPORT-CONTEXT-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "A support-evidence checklist item mentioning offer/contract context was treated as a legal contract-meaning assertion.", "NARROW OFFER_CONTRACT CONTEXT PHRASE RETAINS RUNTIME_UI LANE WITHOUT A FALSE POLICY_CITATION REQUIREMENT"),
        "F-HOST-PAYOUT-INVOICE-PLURAL-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Plural payout and invoice assertions could escape the Product/Finance/Legal owner and authoritative-citation lanes.", "PLURAL FORMS CLASSIFIED; EXACT PAYMENT_AND_TAX CLAIMS RETESTED"),
        "F-HOST-RESPONSIBILITIES-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Plural host-responsibility statements could escape the accountable-owner and authoritative-citation lanes.", "PLURAL RESPONSIBILITY FORMS CLASSIFIED; EXACT CLAIMS RETESTED"),
        "F-HOST-RENTAL-DEDICATION-POLICY": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "The supported-hardware rule that rented gaming/workstation machines should be dedicated was not classified as an owner-governed policy claim requiring a citation.", "EXACT RENTAL_DEDICATION RULE CLASSIFIED_AND_RETESTED"),
        "F-HOST-TECHNICAL-CONTRACT-EVENTS-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Operational notification and expired-rental phrases were treated as legal contract-meaning assertions solely because they contained the word contract.", "NARROW TECHNICAL_PHRASES RETAIN RUNTIME_OR_SOURCE LANES WITHOUT FALSE POLICY_CITATION REQUIREMENTS"),
        "F-HOST-PAGE-SCOPE-ROUTING-POLICY-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Two documentation scope/routing statements were treated as agreement policy assertions even though they only direct readers to troubleshooting content.", "EXACT PAGE_SCOPE_AND_DOCS_ROUTING SENTENCES EXCLUDED_FROM POLICY_CLASSIFICATION_AND_RETESTED"),
        "F-HOST-PAYMENT-PROVIDER-LIST-CONTEXT": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "The 'Vast currently supports' lead-in was detached from the Wise, PayPal, and Stripe list items, obscuring that each item is a current payout-provider assertion.", "LEAD_IN SOURCE SPAN_AND_TEXT PROPAGATED_TO_EACH_PROVIDER_ITEM; LEAD_IN NOT_COUNTED_SEPARATELY"),
        "F-HOST-AGREEMENT-COMMITMENT-LIST-CONTEXT": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "Agreement and contract qualifiers were detached from eight list-item consequences on Hosting Agreement and Hosting Overview, underclassifying their owner and citation requirements.", "COMPLETE LEAD_IN ASSERTIONS RETAINED; QUALIFIERS_AND_EXACT_AUTHORITATIVE_SOURCE_CANDIDATE PROPAGATED_TO_EACH_ITEM; EXACT CLAIMS RETESTED"),
        "F-HOST-DATACENTER-REQUIREMENT-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Datacenter eligibility and application requirements were treated as source-only concepts instead of owner-governed program rules requiring authoritative citations; the pure Prepare lead-in was detached from its items.", "DATACENTER REQUIREMENTS_AND_APPLY CLAIMS ROUTED_TO_PRODUCT_TRUST_SECURITY_LEGAL OWNER; PREPARE CONTEXT_PROPAGATED; EXACT CLAIMS RETESTED"),
        "F-HOST-NEGATED-PRICING-DIAGNOSTIC-CLASSIFICATION": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "A machine-error diagnostic statement was assigned a Finance/policy lane solely because it said the hardware-health signal was not a pricing or marketplace issue.", "NARROW NEGATED_COMPARISON RETAINS DIAGNOSTIC SOURCE_RUNTIME LANES_WITHOUT_FALSE_POLICY_AUTHORITY"),
        "F-HOST-MIXED-DOMAIN-OWNER-ROLE": ("AUTHORITY_ROLE_CLASSIFICATION_DEFECT", "First-match owner selection omitted Legal or Finance from claims spanning contract meaning and pricing, payout, or lifecycle domains.", "ACCOUNTABLE_OWNER ROLE_DERIVED_FROM_UNION_OF_SEMANTIC_DOMAINS; EXACT MIXED_CLAIMS RETESTED"),
        "F-HOST-TAX-RESPONSIBILITY-LIST-CONTEXT": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "The US-host tax responsibility qualifier was detached from its three list items, while the provider reporting-threshold sentence incorrectly gained a Vast implementation-source lane from the generic word threshold.", "COMPLETE PROVIDER_POLICY SENTENCE_RETAINED; RESPONSIBILITY_CONTEXT PROPAGATED_TO_ITEMS; FALSE_IMPLEMENTATION_LANE_REMOVED; EXACT CLAIMS_RETESTED"),
        "F-HOST-ACCOUNT-SECURITY-LIST-CONTEXT": ("MATERIAL_CLAIM_COVERAGE_DEFECT", "Two-factor and API-key security lead-ins were detached from eight dependent list items, leaving normative account-security guidance as source-only fragments and creating a false invoice-citation failure.", "EXACT ANTECEDENT_SPANS BOUND_TO_ITEMS; ACCOUNT_SECURITY_OWNER_AND_RUNTIME LANES_REQUIRED; FINANCE_NOUNS_DO_NOT_CREATE_FALSE_CITATION_FAILURE"),
        "F-HOST-REVENUE-COMPONENT-OWNER-LANE": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Gross-revenue composition and component claims on the Earnings page omitted the Product/Finance owner lane because revenue was absent from the bounded finance-domain classification.", "REVENUE_COMPONENT HEADING_SCOPE REQUIRES_PRODUCT_FINANCE_AUTHORITY; FORMULA_AND_COMPONENT CLAIMS_RETESTED"),
        "F-HOST-LIVE-ACTION-RUNTIME-LANE": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "Datacenter application, Discord account connection, and W9 submission action paths required only source or policy evidence even though they assert live UI/action behavior.", "EXACT ACTION_PATHS REQUIRE_RUNTIME_OR_UI_OBSERVATION_WITHOUT_TREATING_ACTION_LINKS_AS_AUTHORITY"),
        "F-HOST-ACCOUNT-AND-DATACENTER-POLICY-LANE": ("MATERIAL_CLAIM_CLASSIFICATION_DEFECT", "The dedicated-host-account rule and four Datacenter program eligibility/benefit claims required only runtime or source evidence, omitting accountable Product/Trust/Security/Legal authority and authoritative citations.", "EXACT ACCOUNT_AND_PROGRAM CLAIMS REQUIRE_OWNER_AND_CITATION LANES; RUNTIME_REMAINS_SEPARATE_WHERE_APPLICABLE"),
        "F-HOST-FUTURE-MULTILANE-CLOSURE-SCHEMA": ("FORWARD_EVIDENCE_INTEGRATION_LIMITATION", "The current fail-closed reviewer schema cannot yet represent a future fully satisfied multi-lane owner-governed claim or a verified authoritative citation without a schema extension.", "OPEN BEFORE ACCEPTING FUTURE OWNER EVIDENCE: ADD PER_LANE SATISFIED AUTHORITY_AND_EVIDENCE, VERIFIED_CITATION STATE, AND POSITIVE_ADVERSE FIXTURES; NO CURRENT AUTHORITY IS INVENTED"),
        "F-HOST-SUPERSEDED-EVIDENCE-SELECTION": ("EVIDENCE_QUALIFICATION_DEFECT", "Current status-basis selection could prefer evidence from a qualification-superseded attempt over its retained retest.", "CORRECTED_TO_EXCLUDE_SUPERSEDED_ATTEMPTS_FROM_CURRENT_BASIS"),
        "F-HOST-HISTORICAL-P1-DRIFT": ("HISTORICAL_BASELINE_DRIFT", "The retained 39-page P1 draft reports current-source drift and is not frozen; its historical errors are intentionally not repaired in place.", "RETAINED_AS_HISTORY; ACTIVE_40_PAGE_BASELINE_RECONCILED_SEPARATELY"),
    }
    results["findings"] = [row for row in results["findings"] if row["finding_id"] not in finding_ids]
    results["findings"].extend({"finding_id": finding_id, "classification": values[0],
                                "observation": values[1], "documentation_disposition": values[2]}
                               for finding_id, values in finding_ids.items())
    results["current_status_projection"] = {
        "schema_version": "1.1",
        "status_semantics": "PROCEDURE_EXECUTION_AND_REQUIRED_CHILDREN_ONLY",
        "material_claim_page_dispositions_ref": "verification/host-docs-test-sets.json#/material_claim_coverage/page_dispositions",
        "counts": projection_counts(projection_records), "records": projection_records,
    }
    # Integrity-bind every retained attempt artifact, not only the current
    # reconciliation record.  Artifact integrity is deliberately separate from
    # qualification/current-status semantics: historical and superseded
    # attempts remain immutable audit inputs without becoming current proof.
    evidence_artifact_manifest: dict[str, dict[str, str]] = {}
    for attempt in results["attempts"]:
        evidence_ref = attempt.get("evidence_ref")
        require(isinstance(evidence_ref, str) and evidence_ref,
                f"attempt {attempt.get('attempt_id')} has no retained evidence_ref")
        evidence_path = (REPO / evidence_ref).resolve()
        require(evidence_path.is_relative_to(REPO.resolve()) and evidence_path.is_file(),
                f"attempt {attempt.get('attempt_id')} has invalid evidence_ref: {evidence_ref}")
        evidence_sha256 = sha256_path(evidence_path)
        attempt["evidence_ref_sha256"] = evidence_sha256
        role = (
            "CURRENT_REPOSITORY_RECONCILIATION_RETAINED_RESULT"
            if evidence_ref == EVIDENCE_REF
            else "RETAINED_ATTEMPT_EVIDENCE"
        )
        existing = evidence_artifact_manifest.get(evidence_ref)
        require(existing is None or existing == {
            "path": evidence_ref, "sha256": evidence_sha256, "role": role,
        }, f"conflicting evidence artifact identity: {evidence_ref}")
        evidence_artifact_manifest[evidence_ref] = {
            "path": evidence_ref,
            "sha256": evidence_sha256,
            "role": role,
        }
    results["evidence_artifact_manifest"] = [
        evidence_artifact_manifest[path] for path in sorted(evidence_artifact_manifest)
    ]
    results["test_set_snapshot_sha256"] = snapshot
    results["counts"]["attempts"] = len(results["attempts"])
    results["counts"]["material_claim_results"] = len(results["material_claim_results"])
    results["counts"]["support_layer_results"] = len(results["support_layer_results"])

    volume_ids = {item[0] for item in VOLUME_COMMANDS}
    reconciled_command_ids = {spec["command_id"] for spec in RECONCILED_WORKFLOW_COMMANDS}
    generated_score_ids = volume_ids | reconciled_command_ids | RETIRED_RECONCILIATION_COMMAND_IDS
    scores["records"] = [row for row in scores["records"] if row["command_id"] not in generated_score_ids]
    scores["direct_evidence_bindings"] = [row for row in scores["direct_evidence_bindings"] if row["command_id"] not in generated_score_ids]
    command_context = {key[-1]: contexts[key] for key in entities if key[0] == "COMMAND"}
    for row in scores["records"]:
        key = next(key for key in entities if key[0] == "COMMAND" and key[-1] == row["command_id"])
        if row["execution_status"] != statuses[key]:
            row["execution_status"] = statuses[key]
            row["rationale"] = "Relevant retained context remains score 2, but no current claim-suitable direct execution/source result is bound. Missing evidence alone is UNVALIDATED; historical blocked records remain retained."
    for command_id, step_id, start, _end, _text, _treatment in VOLUME_COMMANDS:
        context = command_context[command_id]
        scores["records"].append({
            "command_id": command_id, "procedure_id": context["set"]["procedure_id"],
            "page_route": "/host/volume-offers", "source": f"host/volume-offers.mdx:{start}",
            "execution_status": "PASS", "evidence_ids": [VOLUME_EVIDENCE],
            "direct_evidence_ids": [VOLUME_EVIDENCE], "score": 2,
            "rationale": "Pinned canonical CLI registration/request construction and the current OpenAPI/link contract support the exact documented interface. Static evidence does not validate runtime marketplace, billing, persistence, mount, or cleanup behavior.",
        })
        scores["direct_evidence_bindings"].append({"command_id": command_id, "evidence_id": VOLUME_EVIDENCE, "role": "BOUNDED_STATIC_SUPPORT"})
    for spec in RECONCILED_WORKFLOW_COMMANDS:
        context = command_context[spec["command_id"]]
        scores["records"].append({
            "command_id": spec["command_id"],
            "procedure_id": context["set"]["procedure_id"],
            "page_route": context["page"]["route"],
            "source": f"{spec['file']}:{spec['line_start']}",
            "execution_status": "BLOCKED",
            "evidence_ids": [COMMAND_COVERAGE_EVIDENCE],
            "direct_evidence_ids": [COMMAND_COVERAGE_EVIDENCE],
            "score": 2,
            "rationale": (
                "Exact authored command occurrence, procedure placement, and conservative safety gate are retained. "
                "No privileged bootloader change, reboot, post-enable VM observation, or representative Host behavior ran, so semantic support is partial at score 2."
            ),
        })
        scores["direct_evidence_bindings"].append({
            "command_id": spec["command_id"],
            "evidence_id": COMMAND_COVERAGE_EVIDENCE,
            "role": "EXACT_OCCURRENCE_AND_SAFETY_GATE_ONLY",
        })
    scores["records"].sort(key=lambda item: item["command_id"])
    scores["direct_evidence_bindings"].sort(key=lambda item: (item["command_id"], item["evidence_id"]))
    score_counts = Counter(row["score"] for row in scores["records"])
    scores["counts"] = {"scored": len(scores["records"]), "score_1": score_counts[1], "score_2": score_counts[2],
                        "score_3": score_counts[3], "not_applicable": len(scores["not_applicable_records"])}
    scores["test_set_snapshot_sha256"] = snapshot
    for row in scores["not_applicable_records"]:
        row["approval_ref"] = f"CANONICAL_NON_EXECUTABLE_DISPLAY:{snapshot}"
    score_by_command = {row["command_id"]: row for row in scores["records"]}
    for row in scores.get("withdrawn_records", []):
        if row["command_id"] in score_by_command:
            row["current_execution_status"] = score_by_command[row["command_id"]]["execution_status"]
            row["current_score"] = score_by_command[row["command_id"]]["score"]

    runtime_md, owner_md = build_registers(claims, projection_records)
    return {
        SETS_PATH: sets_bytes,
        RESULTS_PATH: json_bytes(results),
        SCORES_PATH: json_bytes(scores),
        RUNTIME_REGISTER_PATH: runtime_md.encode(),
        OWNER_REGISTER_PATH: owner_md.encode(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="write reconciled canonical outputs")
    group.add_argument("--check", action="store_true", help="fail if canonical outputs differ")
    args = parser.parse_args()
    try:
        outputs = reconcile()
        if args.check:
            stale = [path.relative_to(REPO).as_posix() for path, expected in outputs.items()
                     if not path.is_file() or path.read_bytes() != expected]
            if stale:
                raise ReconciliationError("stale generated output: " + ", ".join(stale))
            print("PASS: reconciled Host V&V package is current (40 primary pages, 33 support layers, 1,004 targets).")
            return 0
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        print("WROTE: 40-page Host V&V baseline, claim contracts, status basis, scores, and blocker registers.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, ReconciliationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
