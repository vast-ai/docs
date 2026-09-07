#!/usr/bin/env python3
"""Focused regressions for Host Docs command execution classification."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from typing import Any


SCRIPT_PATH = Path(__file__).resolve().with_name("inventory_host_docs.py")


def load_inventory_module() -> Any:
    spec = importlib.util.spec_from_file_location("host_docs_inventory", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import inventory generator from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INVENTORY = load_inventory_module()


class CommandClassificationTests(unittest.TestCase):
    def test_self_test_is_host_owned_not_paid(self) -> None:
        command = "vastai self-test machine <machine_id>"

        tier, method = INVENTORY.command_tier(command)
        access = INVENTORY.command_execution_access(command)

        self.assertEqual(tier, "host-owned-self-test")
        self.assertIn("Host-owner account", method)
        self.assertIn("idle Host", method)
        self.assertIn("cleanup/return-to-idle proof", method)
        self.assertEqual(access["group"], "host-machine-no-root")
        self.assertFalse(access["paid_resource"])
        self.assertTrue(access["host_machine"])
        self.assertFalse(access["root_required"])
        self.assertEqual(
            access["additional_gates"],
            [
                "account-authentication",
                "host-owner-account-authentication",
                "representative-idle-host",
                "cleanup-proof",
            ],
        )

    def test_client_resource_commands_remain_paid_live(self) -> None:
        for command in (
            "vastai create instance 12345 --image ubuntu:22.04",
            "vastai create bid --price 0.10",
            "vastai create volume 12345 --size 100",
            "vastai rent 12345",
        ):
            with self.subTest(command=command):
                tier, _ = INVENTORY.command_tier(command)
                access = INVENTORY.command_execution_access(command)

                self.assertEqual(tier, "paid-live")
                self.assertTrue(access["paid_resource"])
                self.assertEqual(access["group"], "paid-only")

    def test_host_offer_list_commands_are_mutations(self) -> None:
        for command in (
            "vastai list machine 12345 --price_gpu 0.10",
            "vastai list machines 12345 67890 --price_gpu 0.10",
            "vastai list volume 12345 --size 100 --price_disk 0.10",
            "vastai list volumes 12345 67890 --size 100 --price_disk 0.10",
        ):
            with self.subTest(command=command):
                tier, _ = INVENTORY.command_tier(command)
                access = INVENTORY.command_execution_access(command)

                self.assertEqual(tier, "destructive-or-mutating")
                self.assertIn("destructive-or-mutating", access["additional_gates"])

    def test_vm_status_helper_is_host_read_only_not_root_required(self) -> None:
        command = "python3 /var/lib/vastai_kaalia/enable_vms.py check"

        tier, method = INVENTORY.command_tier(command)
        access = INVENTORY.command_execution_access(command)

        self.assertEqual(tier, "environment-dependent")
        self.assertIn("without assuming root", method)
        self.assertEqual(access["group"], "host-machine-no-root")
        self.assertTrue(access["host_machine"])
        self.assertFalse(access["root_required"])
        self.assertEqual(access["additional_gates"], ["matching-environment"])

        privileged = INVENTORY.command_execution_access(
            "sudo python3 /var/lib/vastai_kaalia/enable_vms.py off"
        )
        self.assertEqual(privileged["group"], "host-root")
        self.assertTrue(privileged["root_required"])


if __name__ == "__main__":
    unittest.main()
