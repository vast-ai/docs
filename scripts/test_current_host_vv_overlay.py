#!/usr/bin/env python3
"""Focused contract checks for the additive current Host review package."""

from __future__ import annotations

import importlib.util
import copy
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("build_current_host_vv_overlay.py")
SPEC = importlib.util.spec_from_file_location("current_overlay", SCRIPT)
assert SPEC and SPEC.loader
overlay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(overlay)


class CurrentHostReviewPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = overlay.build()

    def test_scope_and_support_layers_are_complete(self) -> None:
        counts = self.package["counts"]
        self.assertEqual(counts["primary_pages"], 44)
        self.assertEqual(counts["cli_support_layers"], 18)
        self.assertEqual(counts["sdk_support_layers"], 15)
        self.assertEqual(counts["total_host_routes"], 44)
        self.assertEqual(counts["total_reviewed_layers"], 77)
        # 44 primary + 33 three-file support layers + current rendered MDX dependencies.
        self.assertGreaterEqual(len(self.package["source"]["source_manifest"]), 44 + 33 * 3)
        self.assertEqual(sum(item["kind"] == "PRIMARY" for item in self.package["source"]["source_manifest"]), 44)
        self.assertEqual(sum(item["kind"] == "SUPPORT_WRAPPER" for item in self.package["source"]["source_manifest"]), 33)

    def test_current_carry_forward_requires_exact_source_identity(self) -> None:
        pages = {page["route"]: page for page in self.package["pages"]}
        self.assertEqual(pages["/host/hosting-overview"]["coverage_state"], "UNCHANGED_EXACT")
        self.assertEqual(pages["/host/guide-to-taxes"]["coverage_state"], "CHANGED")
        self.assertEqual(pages["/host/machine-metrics"]["coverage_state"], "NEW")
        for claim in pages["/host/guide-to-taxes"]["claims"]:
            self.assertNotEqual(claim["history"]["carry_decision"], "CARRIED_FORWARD_EXACT_SOURCE")
        carried = pages["/host/hosting-overview"]["claims"]
        self.assertTrue(any(item["history"]["carry_decision"] == "CARRIED_FORWARD_EXACT_SOURCE" for item in carried))

    def test_vol_c35_current_scope_is_composite_and_retested(self) -> None:
        volume = next(page for page in self.package["pages"] if page["route"] == "/host/volume-offers")
        claim = next(item for item in volume["claims"] if item["id"] == "VOL-C35")
        self.assertEqual(claim["status"], "UNVALIDATED")
        self.assertEqual(claim["required_evidence_types"], ["CANONICAL_IMPLEMENTATION_SOURCE"])
        self.assertEqual(claim["headings"], ["Command Map", "Related Pages"])
        self.assertEqual([(item["start"], item["end"]) for item in claim["spans"]], [(101, 109), (111, 118)])
        expected = "\n".join("\n".join((overlay.REPO / "host/volume-offers.mdx").read_text().splitlines()[start - 1:end])
                             for start, end in ((101, 109), (111, 118)))
        self.assertEqual(claim["text"], expected)
        self.assertEqual(claim["history"]["carry_decision"], "CURRENT_STATIC_RETEST")

    def test_changed_and_new_pages_have_current_ordered_checks(self) -> None:
        for route in ("/host/guide-to-taxes", "/host/machine-metrics"):
            page = next(item for item in self.package["pages"] if item["route"] == route)
            checks = [node for procedure in page["procedures"] for node in procedure["nodes"]
                      if node["kind"] == "CURRENT_HEADING_CHECK"]
            self.assertTrue(checks, route)
            self.assertTrue(all(node["status"] == "UNVALIDATED" for node in checks))

    def test_typography_and_tax_correction_are_explicit_without_runtime_claim(self) -> None:
        ids = {item["id"]: item for item in self.package["corrections"]}
        self.assertIn("lines 155 and 198", ids["SELFTEST-REFERENCE-FLAG-TYPOGRAPHY"]["current"])
        taxes = next(page for page in self.package["pages"] if page["route"] == "/host/guide-to-taxes")
        claim = next(item for item in taxes["claims"] if "does not currently collect or remit VAT" in item["text"])
        self.assertEqual(claim["status"], "FAIL")
        self.assertEqual(claim["required_evidence_types"], ["ACCOUNTABLE_OWNER_CONFIRMATION", "AUTHORITATIVE_DOCUMENTATION_CITATION"])

    def test_retained_static_evidence_has_bound_outputs(self) -> None:
        generated = overlay.outputs()
        self.assertEqual(generated[overlay.STATIC_EVIDENCE], overlay.STATIC_EVIDENCE.read_bytes())
        evidence = __import__("json").loads(generated[overlay.STATIC_EVIDENCE])
        self.assertEqual([item["id"] for item in evidence["checks"]], [
            "EV-CURRENT-LOCAL-NAVIGATION-01", "EV-CURRENT-SUPPORT-STRUCTURE-01", "EV-CURRENT-VOL-C35-NAVIGATION-01",
        ])
        self.assertTrue(all(item["result"] == "PASS" for item in evidence["checks"]))

    def test_live_endpoint_adjudications_are_exact_and_keep_product_proof_separate(self) -> None:
        expected = {
            "CUR-a5b27de02fca3c9a": "/api/v0/metrics/gpu/current/",
            "CUR-6c8062ab1c766957": "/api/v0/metrics/gpu/history/",
            "CUR-2de1188bec6c9f72": "/api/v0/metrics/gpu/locations/",
        }
        actual = {claim["id"]: claim for page in self.package["pages"] for claim in page["claims"] if claim["id"] in expected}
        self.assertEqual(set(actual), set(expected))
        for claim_id, endpoint in expected.items():
            claim = actual[claim_id]
            self.assertEqual(claim["status"], "PASS")
            self.assertEqual(claim["history"]["carry_decision"], "CURRENT_LIVE_ENDPOINT_ADJUDICATION")
            self.assertEqual(claim["required_evidence_types"], ["CANONICAL_IMPLEMENTATION_SOURCE", "RUNTIME_OR_UI_OBSERVATION"])
            self.assertEqual(claim["evidence_refs"][0]["artifact_ref"], "verification/evidence/2026-09-08-host-live-readonly-attempt-01/market-api-01.json")
            self.assertIn(endpoint, claim["text"])
            self.assertEqual({ref["source_kind"] for ref in claim["source_refs"]}, {"CANONICAL_API_CLIENT_SOURCE", "OPENAPI_SOURCE"})
        marketplace = next(claim for page in self.package["pages"] for claim in page["claims"] if claim["id"] == "MCL-e12ac9f6be2ce502")
        self.assertEqual(marketplace["status"], "PASS")
        self.assertEqual(marketplace["history"]["carry_decision"], "CURRENT_PRODUCT_PUBLICATION_ADJUDICATION")
        self.assertEqual(marketplace["required_evidence_types"], ["PRODUCT_PUBLICATION_SOURCE"])

    def test_live_adjudication_rejects_artifact_drift_extra_lane_and_docs_self_proof(self) -> None:
        original = overlay.json_load
        cases = [
            ("artifact", lambda data: data["artifact"].update({"sha256": "0" * 64})),
            ("span-digest", lambda data: data["adjudications"][0]["span"].update({"text_sha256": "0" * 64})),
            ("extra-lane", lambda data: data["adjudications"][0]["required_evidence_types"].append("ACCOUNTABLE_OWNER_CONFIRMATION")),
            ("self-proof", lambda data: data["adjudications"][0]["source_binding"].update({"openapi_path": "host/market-metrics.mdx"})),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                def load(path: Path):
                    value = original(path)
                    if path == overlay.LIVE_ADJUDICATION_INPUT:
                        value = copy.deepcopy(value)
                        mutate(value)
                    return value
                with patch.object(overlay, "json_load", side_effect=load):
                    with self.assertRaises(ValueError):
                        overlay.build()

    def test_local_href_resolution_handles_explicit_anchor_and_rejects_unknown_anchor(self) -> None:
        self.assertTrue(overlay.resolve_local_href("host/hardware-prep.mdx", "/host/storage-setup#fstab-example"))
        self.assertFalse(overlay.resolve_local_href("host/hardware-prep.mdx", "/host/storage-setup#not-a-real-anchor"))

    def test_literal_parser_excludes_non_rendered_or_non_text_blocks(self) -> None:
        blocks = overlay.literal_blocks("/host/self-test-reference", "host/self-test-reference.mdx")
        text = "\n".join(item["text"] for item in blocks)
        self.assertNotIn("<!--", text)
        self.assertNotIn("{/*", text)
        self.assertNotIn("This page is generated", text)
        self.assertNotIn("| --- |", text)
        self.assertNotIn("| Code | Area | Meaning |", text)
        notifications = overlay.literal_blocks("/host/notifications", "snippets/notifications/channels.mdx")
        self.assertFalse(any("HIDDEN:" in item["text"] for item in notifications))

    def test_historical_claim_refs_bind_narrow_attempt_artifacts_and_worklist_relativizes_them(self) -> None:
        overview = next(page for page in self.package["pages"] if page["route"] == "/host/hosting-overview")
        claim = next(item for page in self.package["pages"] for item in page["claims"]
                     if item["evidence_refs"] and item["history"]["carry_decision"] == "CARRIED_FORWARD_EXACT_SOURCE")
        self.assertTrue(all(item["artifact_ref"].startswith("verification/evidence/") for item in claim["evidence_refs"]))
        worklist, _runtime, _owners = overlay.worklist(self.package)
        self.assertNotIn("](verification/evidence/", worklist)
        self.assertIn("](evidence/", worklist)

    def test_generated_markdown_has_exactly_one_terminal_newline(self) -> None:
        for text in overlay.worklist(self.package):
            self.assertTrue(text.endswith("\n"))
            self.assertFalse(text.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
