#!/usr/bin/env python3
"""Regression checks for narrow current Host claim corrections.

These checks are repository-local: they bind every correction to the exact
historical source line, confirm the replacement is present, and prohibit a
status promotion. They deliberately execute no documented Host/API/network
command.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import unittest


REPO = Path(__file__).resolve().parents[1]
BASELINE_REVISION = "bfa926c9421521767fa7411718bd31ea38b38528"
CORRECTIONS_PATH = REPO / "verification/current-host-claim-corrections.json"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def baseline_bytes(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{BASELINE_REVISION}:{path}"],
        cwd=REPO,
        check=True,
        capture_output=True,
    ).stdout


class CurrentHostClaimCorrectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8"))

    def test_original_failures_are_identity_bound_to_baseline(self) -> None:
        self.assertEqual(self.payload["baseline"]["revision"], BASELINE_REVISION)
        for correction in self.payload["corrections"]:
            with self.subTest(correction=correction["id"]):
                baseline = baseline_bytes(correction["source_file"])
                self.assertEqual(
                    hashlib.sha256(baseline).hexdigest(),
                    correction["original_file_sha256"],
                )
                lines = baseline.decode("utf-8").splitlines()
                literal = "\n".join(
                    line
                    for span in correction["source_spans"]
                    for line in lines[span["start"] - 1:span["end"]]
                )
                self.assertEqual(literal, correction["original_text"])
                self.assertEqual(sha256_text(literal), correction["original_sha256"])
                self.assertTrue(correction["root_retest"]["initial_failure"])

    def test_replacements_and_retests_preserve_unvalidated_status(self) -> None:
        for correction in self.payload["corrections"]:
            with self.subTest(correction=correction["id"]):
                current = (REPO / correction["source_file"]).read_text(encoding="utf-8")
                self.assertIn(correction["replacement_text"], current)
                self.assertNotIn(correction["original_text"], current)
                self.assertEqual(correction["status"], "UNVALIDATED")
                self.assertTrue(correction["root_retest"]["retest"])
                self.assertTrue(correction["root_retest"]["evidence_limits"])
                for binding in correction["evidence_partial_bindings"]:
                    self.assertEqual(binding["revision"], BASELINE_REVISION)
                    self.assertTrue((REPO / binding["path"]).is_file())
                    self.assertNotIn("PASS", binding["scope"].upper())

    def test_market_binding_is_static_and_does_not_infer_a_rate(self) -> None:
        correction = next(
            item for item in self.payload["corrections"]
            if item["id"] == "CHC-MARKET-METRICS-FRESHNESS-01"
        )
        self.assertEqual(len(correction["evidence_partial_bindings"]), 3)
        self.assertIn("Do not infer", correction["root_retest"]["evidence_limits"])
        self.assertNotIn("5 requests per second per user", correction["replacement_text"])
        self.assertIn("do not document", correction["replacement_text"])
        market_page = (REPO / "host/market-metrics.mdx").read_text(encoding="utf-8")
        self.assertIn("## Freshness And Limits", market_page)
        for binding in correction["evidence_partial_bindings"]:
            self.assertIn(
                f"https://github.com/vast-ai/docs/blob/{BASELINE_REVISION}/{binding['path']}",
                correction["replacement_text"],
            )

    def test_second_pass_history_and_connectivity_gate_are_retained(self) -> None:
        history = self.payload["correction_history"]
        self.assertEqual(history[-1]["revision"], "1.1")
        self.assertIn("Freshness And Limits anchor", history[-1]["reason"])
        gate = next(
            item for item in self.payload["corrections"]
            if item["id"] == "CHC-MACHINE-OFFLINE-CONNECTIVITY-GATE-01"
        )
        self.assertIn("filtered or inconclusive", gate["replacement_text"])
        self.assertEqual(gate["status"], "UNVALIDATED")
        web_request = next(
            item for item in self.payload["corrections"]
            if item["id"] == "CHC-MACHINE-OFFLINE-WEB-REQUEST-SCOPE-01"
        )
        self.assertIn("observed HTTP egress address", web_request["replacement_text"])
        self.assertNotIn("HTTP/HTTPS traffic actually works", web_request["replacement_text"])


if __name__ == "__main__":
    unittest.main()
