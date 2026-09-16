#!/usr/bin/env python3
"""Regression coverage for Host material-claim authority classification."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import types
import unittest


REPO = Path(__file__).resolve().parents[1]
CLASSIFIER_PATH = REPO / "scripts/reconcile_host_vv_repository.py"
CURRENT_REVIEW_PATH = REPO / "verification/current-host-docs-review.json"
BASELINE_COMMIT = "4fa6fbb53f1b547f36652bff32a8133bab387f33"
CONTROL_KEYS = {
    "minimum_gpu_size",
    "interruptible_minimum_bid",
    "reserved_discount_settings",
    "offer_end_date",
}


def control_key(text: str) -> str | None:
    normalized = text.casefold().strip()
    patterns = {
        "minimum_gpu_size": r"minimum gpu (?:size|count)\s*\(`min_(?:gpu|chunk)`\)\.?",
        "interruptible_minimum_bid": r"interruptible minimum bid\.?",
        "reserved_discount_settings": (
            r"(?:reserved discount settings|"
            r"maximum prepaid discount\s*\(`discount_rate`\))\.?"
        ),
        "offer_end_date": r"offer end date\.?",
    }
    return next(
        (key for key, pattern in patterns.items() if re.fullmatch(pattern, normalized)),
        None,
    )


def load_current_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("current_reconcile", CLASSIFIER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_baseline_module() -> types.ModuleType:
    """Load the immutable pre-correction classifier, not moving ``HEAD``."""
    source = subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:scripts/reconcile_host_vv_repository.py"],
        cwd=REPO,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    module = types.ModuleType("baseline_reconcile")
    module.__file__ = str(CLASSIFIER_PATH)
    exec(compile(source, str(CLASSIFIER_PATH), "exec"), module.__dict__)
    return module


def current_review_model() -> dict:
    return json.loads(CURRENT_REVIEW_PATH.read_text())


def classify_current_host_claims(module: types.ModuleType) -> dict[str, tuple[str, tuple[str, ...], bool, str]]:
    """Return every parser-owned claim from the current 44-page review model."""
    classifications: dict[str, tuple[str, tuple[str, ...], bool, str]] = {}
    for page in current_review_model()["pages"]:
        # Volume Offers has its own reviewed parser and is intentionally outside
        # classify_claim's material-block inventory.
        if page["route"] == "/host/volume-offers":
            continue
        sources = [page["source_file"]] + [
            dependency["source_file"] for dependency in page["dependencies"]
        ]
        for source_file in sources:
            for claim in module.material_blocks(page["route"], REPO / source_file):
                classifications[claim["claim_id"]] = (
                    claim["claim"]["kind"],
                    tuple(claim["evidence_requirement"]["types"]),
                    claim["evidence_requirement"]["citation_required"],
                    claim["claim"]["text"],
                )
    return classifications


def preserved_baseline_overview_claims(module: types.ModuleType) -> list[dict]:
    """Parse the preserved source so the original ``min_gpu`` spelling is explicit."""
    source = subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:host/hosting-overview.mdx"],
        cwd=REPO,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    with tempfile.TemporaryDirectory() as directory:
        temporary_repo = Path(directory)
        source_path = temporary_repo / "host/hosting-overview.mdx"
        source_path.parent.mkdir()
        source_path.write_text(source)
        original_repo = module.REPO
        module.REPO = temporary_repo
        try:
            return module.material_blocks("/host/hosting-overview", source_path)
        finally:
            module.REPO = original_repo


class HostAuthorityClassificationTests(unittest.TestCase):
    def test_pinned_baseline_delta_is_only_the_four_technical_offer_controls(self) -> None:
        """The heading cannot turn bare technical controls into policy claims."""
        review = current_review_model()
        parser_pages = [
            page for page in review["pages"]
            if page["route"] != "/host/volume-offers"
        ]
        self.assertEqual(len(review["pages"]), 44)
        self.assertEqual(len(parser_pages), 43)
        self.assertEqual(
            sum(1 + len(page["dependencies"]) for page in parser_pages), 44,
        )
        before = classify_current_host_claims(load_baseline_module())
        after = classify_current_host_claims(load_current_module())
        deltas = {
            claim_id: (before[claim_id], after[claim_id])
            for claim_id in before.keys() & after.keys()
            if before[claim_id][:3] != after[claim_id][:3]
        }
        controls = {
            control_key(classification[3]): claim_id
            for claim_id, classification in after.items()
            if control_key(classification[3]) is not None and claim_id in deltas
        }
        self.assertEqual(set(controls), CONTROL_KEYS)
        self.assertEqual(set(deltas), set(controls.values()))
        for key, claim_id in controls.items():
            with self.subTest(control=key):
                original, revised = deltas[claim_id]
                self.assertEqual(original[0], "POLICY_OR_COMMERCIAL")
                self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", original[1])
                self.assertFalse(original[2])
                self.assertEqual(revised[:3], (
                    "IMPLEMENTATION_OR_CONCEPT",
                    ("CANONICAL_IMPLEMENTATION_SOURCE",),
                    False,
                ))

    def test_preserved_baseline_and_current_page_accept_both_identifier_spellings(self) -> None:
        baseline_claims = preserved_baseline_overview_claims(load_baseline_module())
        baseline_controls = {
            control_key(claim["claim"]["text"]): claim["claim"]["text"]
            for claim in baseline_claims
            if control_key(claim["claim"]["text"]) is not None
        }
        self.assertEqual(set(baseline_controls), CONTROL_KEYS)
        self.assertEqual(baseline_controls["minimum_gpu_size"], "Minimum GPU size (`min_gpu`).")
        self.assertEqual(baseline_controls["reserved_discount_settings"], "Reserved discount settings.")
        self.assertEqual(
            control_key("Maximum prepaid discount (`discount_rate`)."),
            "reserved_discount_settings",
        )

        current_controls = {
            control_key(claim["claim"]["text"]): claim
            for claim in load_current_module().material_blocks(
                "/host/hosting-overview", REPO / "host/hosting-overview.mdx"
            )
            if control_key(claim["claim"]["text"]) is not None
        }
        self.assertEqual(set(current_controls), CONTROL_KEYS)
        self.assertRegex(
            current_controls["minimum_gpu_size"]["claim"]["text"],
            r"^Minimum GPU (?:size|count) \(`min_(?:gpu|chunk)`\)\.$",
        )

    def test_actual_hosting_overview_controls_require_canonical_source_only(self) -> None:
        claims = load_current_module().material_blocks(
            "/host/hosting-overview", REPO / "host/hosting-overview.mdx"
        )
        controls = {
            control_key(claim["claim"]["text"]): claim
            for claim in claims
            if control_key(claim["claim"]["text"]) is not None
        }
        self.assertEqual(set(controls), CONTROL_KEYS)
        for key, claim in controls.items():
            with self.subTest(control=key):
                self.assertEqual(claim["claim"]["kind"], "IMPLEMENTATION_OR_CONCEPT")
                self.assertEqual(
                    tuple(claim["evidence_requirement"]["types"]),
                    ("CANONICAL_IMPLEMENTATION_SOURCE",),
                )
                self.assertFalse(claim["evidence_requirement"]["citation_required"])

    def test_obligation_enforcement_and_pricing_language_remains_policy(self) -> None:
        module = load_current_module()
        cases = (
            ("General Notes", "Must not change rental terms.", "- Must not change rental terms."),
            ("Offers And Rental Contracts", "Hosts are responsible for keeping the offer end date current.", "- Offer end date."),
            ("Offers And Rental Contracts", "GPU, storage, and bandwidth prices.", "- GPU, storage, and bandwidth prices."),
            ("Offers And Rental Contracts", "Only permitted GPU values may be listed.", "- Only permitted GPU values may be listed."),
            ("Offers And Rental Contracts", "The contract locks in the listed price.", "The contract locks in the listed price."),
            ("Offers And Rental Contracts", "The offer price is guaranteed for the rental.", "The offer price is guaranteed for the rental."),
        )
        for heading, text, raw in cases:
            with self.subTest(text=text):
                kind, lanes, _citation_required = module.classify_claim(
                    "host/hosting-overview.mdx", heading, text, raw
                )
                self.assertEqual(kind, "POLICY_OR_COMMERCIAL")
                self.assertIn("ACCOUNTABLE_OWNER_CONFIRMATION", lanes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
