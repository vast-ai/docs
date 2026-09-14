import copy
import importlib.util
import json
import unittest
from unittest import mock
from pathlib import Path
from scripts.test_current_host_authority_scan import frozen_payout_payment

REPO=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('current_host_terms_binding_test_target', REPO/'scripts/current_host_terms_binding.py')
TERMS=importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(TERMS)

class CurrentHostTermsBindingTests(unittest.TestCase):
    def jurisdiction(self):
        path=REPO/'verification/current-host-jurisdiction.json'
        return json.loads(path.read_text()) if path.is_file() else None

    def model(self):
        latest=self.jurisdiction()
        path=latest['baseline']['path'] if latest else 'verification/current-host-docs-review.json'
        return json.loads((REPO/path).read_text())

    def validate(self, model):
        # Exercise the unchanged Terms reader against its actual historical
        # model/page bytes. Newer source edits are not Terms fixture inputs.
        latest=self.jurisdiction(); overrides={}
        for source in latest['sources'] if latest else []:
            overrides[REPO/source['path']]=(REPO/source['before_artifact']['path']).read_bytes()
        overrides[REPO/'host/payment.mdx']=frozen_payout_payment()
        original=Path.read_bytes
        with mock.patch.object(Path,'read_bytes',lambda path:overrides[path] if path in overrides else original(path)):
            TERMS.validate_model(model, REPO)

    def test_sealed_projection_accepts_all_six_terms_claims(self):
        model=self.model()
        self.validate(model)
        registry=json.loads((REPO/TERMS.REGISTRY).read_text())
        self.assertEqual({entry['claim_id'] for entry in registry['transitions']}, TERMS.IDS)
        self.assertEqual(len(registry['transitions']), 6)

    def test_rejects_tampered_current_span_or_terms_source_reference(self):
        for field, value in [('text_sha256','0'*64), ('source_file','host/hosting-overview.mdx')]:
            altered=copy.deepcopy(self.model())
            claim=next(item for page in altered['pages'] for item in page['claims'] if item['id']=='MCL-633317ca7ebecfef')
            claim['spans'][0][field]=value
            with self.assertRaises(ValueError): self.validate(altered)
        altered=copy.deepcopy(self.model())
        claim=next(item for page in altered['pages'] for item in page['claims'] if item['id']=='MCL-fe3eccd1cd40b4bd')
        claim['source_refs']=[ref for ref in claim['source_refs'] if ref['path']!='https://vast.ai/terms']
        with self.assertRaises(ValueError): self.validate(altered)

if __name__=='__main__': unittest.main()
