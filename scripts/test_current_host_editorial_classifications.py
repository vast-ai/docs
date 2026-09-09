#!/usr/bin/env python3
"""Source-identity checks for the narrow Host editorial classification input."""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "verification/current-host-editorial-classifications.json"
BASELINE = "bfa926c9421521767fa7411718bd31ea38b38528"
PREAMBLES = {
    "MCL-6875ca55bab20f5f",
    "MCL-3a33d3c659eb4cc0",
    "MCL-57c97a3c5eea2909",
    "MCL-1ce282a975cbca46",
}
NAVIGATION = {
    "MCL-e958038c111225e5",
    "MCL-af45ae12e370a52f",
    "MCL-b3e44d6bcf2f6be4",
    "MCL-f753042dac326835",
    "MCL-cd7827ce19c102f1",
    "MCL-5bb54f4781b68e90",
}


def span_text(text: str, start: int, end: int) -> str:
    return "\n".join(text.splitlines()[start - 1:end])


class EditorialClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_schema_and_narrow_id_allowlist(self) -> None:
        self.assertEqual(self.data["schema_version"], "1.0")
        self.assertEqual(self.data["artifact_type"], "CURRENT_HOST_EDITORIAL_CLASSIFICATION_INPUT")
        self.assertEqual(self.data["baseline_revision"], BASELINE)
        rows = self.data["classifications"]
        self.assertEqual({row["id"] for row in rows}, PREAMBLES | NAVIGATION)
        self.assertEqual(len(rows), 10)

    def test_every_literal_matches_the_baseline_and_live_source(self) -> None:
        for row in self.data["classifications"]:
            baseline = subprocess.check_output(
                ["git", "show", f"{BASELINE}:{row['source_file']}"], cwd=ROOT, text=True
            )
            expected = span_text(baseline, row["start"], row["end"])
            live = span_text((ROOT / row["source_file"]).read_text(encoding="utf-8"), row["start"], row["end"])
            self.assertEqual(row["literal"], expected, row["id"])
            self.assertEqual(live, expected, row["id"])
            self.assertEqual(
                row["literal_sha256"], hashlib.sha256(expected.encode("utf-8")).hexdigest(), row["id"]
            )

    def test_only_preambles_are_not_applicable_and_links_remain_unvalidated(self) -> None:
        for row in self.data["classifications"]:
            if row["id"] in PREAMBLES:
                self.assertEqual(row["class"], "EDITORIAL_NAVIGATION_PREAMBLE")
                self.assertEqual(row["status"], "NOT_APPLICABLE")
                self.assertEqual(row["required_evidence_types"], [])
                self.assertEqual(row["proof_check_method"], "NONE_EDITORIAL_NONPRODUCT")
            else:
                self.assertEqual(row["class"], "NAVIGATION_CONTRACT")
                self.assertEqual(row["status"], "UNVALIDATED")
                self.assertEqual(row["required_evidence_types"], ["REPOSITORY_STATIC_CHECK"])
                self.assertEqual(row["proof_check_method"], "REPOSITORY_LOCAL_ROUTE_AND_FRAGMENT_RESOLUTION")
                self.assertIn("](/", row["literal"])


if __name__ == "__main__":
    unittest.main()
