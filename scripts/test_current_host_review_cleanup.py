#!/usr/bin/env python3
"""Focused fail-closed gates for the optional cleanup projection."""
from __future__ import annotations

import importlib.util
import json
import copy
import unittest
from pathlib import Path
from contextlib import contextmanager
from unittest import mock
from scripts.test_current_host_authority_scan import frozen_payout_payment

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('cleanup_test_target', ROOT / 'scripts/current_host_review_cleanup.py')
TARGET = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(TARGET)

@contextmanager
def frozen_cleanup_predecessor():
    """Run cleanup's old chain against the hash-pinned payout predecessor."""
    original=TARGET.predecessor
    def predecessor(root, baseline):
        jurisdiction_spec=importlib.util.spec_from_file_location('cleanup_jurisdiction_fixture', ROOT/'scripts/current_host_jurisdiction.py')
        jurisdiction=importlib.util.module_from_spec(jurisdiction_spec); assert jurisdiction_spec.loader; jurisdiction_spec.loader.exec_module(jurisdiction)
        prior=jurisdiction.predecessor
        jurisdiction.predecessor=lambda repo, model, old: prior(repo, model, {**old, 'host/payment.mdx': frozen_payout_payment()})
        return jurisdiction.validate_model(baseline, root)
    with mock.patch.object(TARGET, 'predecessor', predecessor):
        yield

def cleanup_project():
    with frozen_cleanup_predecessor():
        return TARGET.project(ROOT)

def cleanup_load(model):
    with frozen_cleanup_predecessor():
        return TARGET.load_cleanup(ROOT, model)


class CleanupGateTest(unittest.TestCase):
    def current(self) -> dict:
        payout=json.loads((ROOT/'verification/current-host-payout-provider-correction.json').read_text())
        baseline=ROOT/payout['baseline']['path']
        self.assertEqual(TARGET.digest(baseline.read_bytes()), payout['baseline']['sha256'])
        return json.loads(baseline.read_text())

    def test_sealed_cleanup_projects_the_current_model(self) -> None:
        projected = cleanup_project()
        self.assertEqual(projected, self.current())
        self.assertEqual(cleanup_load(projected)['registry_sha256'], TARGET.REGISTRY_SHA256)
        self.assertEqual(projected['counts']['claim_statuses'], {
            'BLOCKED': 23, 'FAIL': 35, 'NOT_APPLICABLE': 87, 'PASS': 308, 'UNVALIDATED': 1560,
        })
        registry = json.loads((ROOT / TARGET.REGISTRY).read_text())
        self.assertEqual(len(registry['transitions']), 151)

    def test_unprojected_predecessor_model_fails_closed(self) -> None:
        model = json.loads((ROOT / TARGET.BASELINE).read_text())
        with self.assertRaisesRegex(ValueError, 'whole model differs'):
            cleanup_load(model)

    def test_cleanup_baseline_is_the_exact_current_jurisdiction_model(self) -> None:
        baseline = json.loads((ROOT / TARGET.BASELINE).read_text())
        self.assertEqual(TARGET.digest((ROOT / TARGET.BASELINE).read_bytes()), TARGET.BASELINE_SHA256)
        jurisdiction_spec = importlib.util.spec_from_file_location('jurisdiction_test_target', ROOT / 'scripts/current_host_jurisdiction.py')
        jurisdiction = importlib.util.module_from_spec(jurisdiction_spec)
        assert jurisdiction_spec.loader
        jurisdiction_spec.loader.exec_module(jurisdiction)
        prior=jurisdiction.predecessor
        jurisdiction.predecessor=lambda root, model, old: prior(root, model, {**old, 'host/payment.mdx': frozen_payout_payment()})
        self.assertEqual(baseline, jurisdiction.project(ROOT))

    def test_unselected_claim_tamper_fails_whole_projection_gate(self) -> None:
        model = copy.deepcopy(self.current())
        selected = {entry['claim_id'] for entry in json.loads((ROOT / TARGET.REGISTRY).read_text())['transitions']}
        claim = next(item for page in model['pages'] for item in page['claims'] if item['id'] not in selected)
        claim['rationale'] += ' tampered'
        with self.assertRaisesRegex(ValueError, 'whole model differs'):
            cleanup_load(model)

    def test_selected_fake_pass_fails_whole_projection_gate(self) -> None:
        model = copy.deepcopy(self.current())
        claim = next(item for page in model['pages'] for item in page['claims'] if item['status'] == 'UNVALIDATED')
        claim['status'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'whole model differs'):
            cleanup_load(model)


if __name__ == '__main__':
    unittest.main()
