#!/usr/bin/env python3
"""Focused fail-closed tests for restricted live V&V authorization records."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from validate_live_vv_authorization import AuthorizationError, CLASS_TO_DECISION, load_and_validate


OPERATION_KEYS = [
    "ssh_read_only",
    "sudo_read_only",
    "temporary_tcp_listener",
    "temporary_udp_listener",
    "external_port_probe",
    "service_inspection",
    "service_mutation",
    "package_installation",
    "reboot",
    "storage_change",
    "network_change",
    "workload_impact",
    "host_self_test",
    "paid_rental",
]
DECISION_KEYS = [
    "host_read_only",
    "host_privileged_read_only",
    "wan",
    "host_mutating",
    "host_self_test",
    "paid",
]


def blocked_record() -> dict:
    credential = {
        "role_confirmed": False,
        "fresh_or_rotation_planned": False,
        "secure_non_chat_injection_ready": False,
        "secret_value_recorded_here": False,
    }
    return {
        "schema_version": "host-docs-live-vv-authorization/1.1",
        "authorization_id": "AUTH-TEST-BLOCKED",
        "approver": {
            "full_name": "Test Safety Approver",
            "exact_role": "Test-only safety approver",
            "approval_recorded_at": "2026-08-30T12:00:00Z",
            "approval_reference": None,
        },
        "window": {
            "start": "2026-08-30T12:00:00Z",
            "end": "2026-08-30T13:00:00Z",
            "timezone": "UTC",
        },
        "target": {
            "target_alias": "HOST_VV_TARGET",
            "active_or_shared": True,
            "disposable_or_isolated": False,
            "absence_of_affected_workloads_confirmed": False,
            "backup_or_recovery_plan_confirmed": False,
            "restricted_target_details_present": False,
        },
        "operations": {
            "allowed": {key: False for key in OPERATION_KEYS},
            "forbidden": ["all live operations"],
        },
        "wan": {
            "external_client_available": False,
            "confirmed_unused_port_present": False,
            "approved_protocols": [],
            "temporary_listener_cleanup_approved": False,
        },
        "host_self_test": {
            "max_runtime_minutes": 0,
            "polling_interval_seconds": 15,
            "automatic_stop_condition": "Not applicable",
            "cleanup_escalation_trigger": "Not applicable",
            "machine_read_permission_confirmed": False,
            "one_attempt_at_a_time": False,
        },
        "paid": {
            "max_spend_usd": 0,
            "max_runtime_minutes": 0,
            "polling_interval_seconds": 15,
            "automatic_stop_condition": "Not applicable",
            "cleanup_escalation_trigger": "Not applicable",
            "client_or_renter_role_confirmed": False,
            "provider_hard_spend_cap_available": False,
            "bounded_monitored_execution_approved_without_provider_hard_cap": False,
            "one_attempt_at_a_time": False,
        },
        "credentials": {"host": copy.deepcopy(credential), "client": copy.deepcopy(credential)},
        "cleanup": {
            "authority_granted": False,
            "escalation_contact": "Not applicable",
            "cleanup_only_on_uncertainty": False,
        },
        "decision": {key: "NOT_APPROVED" for key in DECISION_KEYS},
    }


class AuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="host-docs-live-auth-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "authorization.json"

    def write(self, value: dict, mode: int = 0o600) -> Path:
        self.path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        os.chmod(self.path, mode)
        return self.path

    def assert_rejected(self, value: dict, contains: str) -> None:
        path = self.write(value)
        with self.assertRaisesRegex(AuthorizationError, contains):
            load_and_validate(path)

    def test_blocked_record_is_valid_non_authorization(self) -> None:
        value, raw = load_and_validate(self.write(blocked_record()))
        self.assertEqual(value["decision"]["host_self_test"], "NOT_APPROVED")
        self.assertEqual(value["decision"]["paid"], "NOT_APPROVED")
        self.assertTrue(raw.endswith(b"\n"))

    def test_host_self_test_is_a_separate_validator_class(self) -> None:
        self.assertEqual(CLASS_TO_DECISION["host-self-test"], "host_self_test")
        self.assertEqual(CLASS_TO_DECISION["paid"], "paid")

    def test_host_read_only_requires_secure_role_correct_credential(self) -> None:
        value = blocked_record()
        value["decision"]["host_read_only"] = "APPROVED"
        value["target"]["restricted_target_details_present"] = True
        value["operations"]["allowed"]["ssh_read_only"] = True
        self.assert_rejected(value, "schema validation failed")
        value["credentials"]["host"].update(role_confirmed=True, secure_non_chat_injection_ready=True)
        loaded, _ = load_and_validate(self.write(value))
        self.assertEqual(loaded["decision"]["host_read_only"], "APPROVED")

    def test_host_self_test_needs_host_auth_workload_runtime_and_cleanup_not_paid_auth(self) -> None:
        value = blocked_record()
        value["decision"]["host_self_test"] = "APPROVED"
        value["target"]["restricted_target_details_present"] = True
        value["operations"]["allowed"].update(host_self_test=True, workload_impact=True)
        value["host_self_test"].update(
            max_runtime_minutes=30,
            automatic_stop_condition="Stop after terminal result or 30 minutes",
            cleanup_escalation_trigger="Escalate if the diagnostic workload remains",
            machine_read_permission_confirmed=True,
            one_attempt_at_a_time=True,
        )
        value["credentials"]["host"].update(role_confirmed=True, secure_non_chat_injection_ready=True)
        value["cleanup"]["authority_granted"] = True

        loaded, _ = load_and_validate(self.write(value))
        self.assertEqual(loaded["paid"]["max_spend_usd"], 0)
        self.assertFalse(loaded["paid"]["client_or_renter_role_confirmed"])
        self.assertFalse(loaded["credentials"]["client"]["role_confirmed"])

        required_paths = [
            ("host_self_test.max_runtime_minutes", lambda item: item["host_self_test"].update(max_runtime_minutes=0)),
            (
                "host_self_test.machine_read_permission_confirmed",
                lambda item: item["host_self_test"].update(machine_read_permission_confirmed=False),
            ),
            ("credentials.host.role_confirmed", lambda item: item["credentials"]["host"].update(role_confirmed=False)),
            (
                "credentials.host.secure_non_chat_injection_ready",
                lambda item: item["credentials"]["host"].update(secure_non_chat_injection_ready=False),
            ),
            (
                "operations.allowed.workload_impact",
                lambda item: item["operations"]["allowed"].update(workload_impact=False),
            ),
            (
                "operations.allowed.host_self_test",
                lambda item: item["operations"]["allowed"].update(host_self_test=False),
            ),
            ("cleanup.authority_granted", lambda item: item["cleanup"].update(authority_granted=False)),
        ]
        for label, mutate in required_paths:
            with self.subTest(missing_requirement=label):
                invalid = copy.deepcopy(value)
                mutate(invalid)
                self.assert_rejected(invalid, "schema validation failed")

    def test_paid_requires_rental_positive_caps_client_credential_and_cleanup(self) -> None:
        value = blocked_record()
        value["decision"]["paid"] = "APPROVED"
        value["paid"].update(
            max_spend_usd=5,
            max_runtime_minutes=30,
            client_or_renter_role_confirmed=True,
            bounded_monitored_execution_approved_without_provider_hard_cap=True,
            one_attempt_at_a_time=True,
        )
        value["credentials"]["client"].update(role_confirmed=True, secure_non_chat_injection_ready=True)
        value["cleanup"].update(authority_granted=True, cleanup_only_on_uncertainty=True)
        value["operations"]["allowed"]["host_self_test"] = True
        self.assert_rejected(value, "schema validation failed")
        value["operations"]["allowed"]["paid_rental"] = True
        load_and_validate(self.write(value))
        value["paid"]["max_spend_usd"] = 0
        self.assert_rejected(value, "schema validation failed")

    def test_version_1_0_record_is_rejected(self) -> None:
        value = blocked_record()
        value["schema_version"] = "host-docs-live-vv-authorization/1.0"
        self.assert_rejected(value, "schema validation failed")

    def test_stale_paid_self_test_operation_is_rejected(self) -> None:
        value = blocked_record()
        value["operations"]["allowed"]["paid_self_test"] = value["operations"]["allowed"].pop("host_self_test")
        self.assert_rejected(value, "schema validation failed")

    def test_wan_requires_listener_probe_port_and_cleanup(self) -> None:
        value = blocked_record()
        value["decision"]["wan"] = "APPROVED"
        value["target"]["restricted_target_details_present"] = True
        value["operations"]["allowed"]["external_port_probe"] = True
        value["wan"].update(
            external_client_available=True,
            confirmed_unused_port_present=True,
            approved_protocols=["TCP"],
            temporary_listener_cleanup_approved=True,
        )
        value["cleanup"]["authority_granted"] = True
        self.assert_rejected(value, "schema validation failed")
        value["operations"]["allowed"]["temporary_tcp_listener"] = True
        load_and_validate(self.write(value))

    def test_credential_shaped_value_is_rejected(self) -> None:
        value = blocked_record()
        value["approver"]["approval_reference"] = "token=do-not-record-this"
        self.assert_rejected(value, "credential-shaped value")

    def test_group_or_world_readable_record_is_rejected(self) -> None:
        path = self.write(blocked_record(), mode=0o644)
        with self.assertRaisesRegex(AuthorizationError, "deny group/other access"):
            load_and_validate(path)

    def test_symlink_is_rejected(self) -> None:
        target = self.write(blocked_record())
        link = Path(self.temp.name) / "authorization-link.json"
        link.symlink_to(target)
        with self.assertRaisesRegex(AuthorizationError, "symbolic link"):
            load_and_validate(link)


if __name__ == "__main__":
    unittest.main()
