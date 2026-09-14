import copy
import importlib.util
import json
import unittest
from unittest import mock
from pathlib import Path
from contextlib import contextmanager
from scripts.test_current_host_authority_scan import frozen_payout_payment, PAYOUT_BEFORE

ROOT=Path(__file__).resolve().parents[1]
IDS={'CUR-708c718cf735c8b2','CUR-555543e9b2ceddb4','CUR-2ead4eda972e84b0','MCL-8fe2020c0e7efe26','MCL-1536a1bd58d80927','MCL-c9882f043e407640','MCL-c8bf23127171e2b0','MCL-3acecd71e6a7b312'}
ATTEMPT='verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01'
CLEANUP_PREDECESSOR='verification/evidence/2026-09-11-host-review-cleanup-attempt-01/before-current-host-docs-review.json'
SPEC=importlib.util.spec_from_file_location('jurisdiction_test_target',ROOT/'scripts/current_host_jurisdiction.py')
JUR=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(JUR)

def load(ref): return json.loads((ROOT/ref).read_text())
def claims(model): return {c['id']:c for p in model['pages'] for c in p['claims']}
def jurisdiction_model(): return load(CLEANUP_PREDECESSOR if (ROOT/CLEANUP_PREDECESSOR).is_file() else 'verification/current-host-docs-review.json')

@contextmanager
def frozen_payout_predecessor():
    """Keep this pre-payout phase on its pinned payment source only."""
    original=JUR.predecessor
    def predecessor(root, baseline, old):
        return original(root, baseline, {**old, 'host/payment.mdx': frozen_payout_payment()})
    with mock.patch.object(JUR, 'predecessor', predecessor):
        yield

def project_jurisdiction():
    with frozen_payout_predecessor():
        return JUR.project(ROOT)

def validate_jurisdiction(model):
    with frozen_payout_predecessor():
        return JUR.validate_model(model, ROOT)

class JurisdictionReviewTests(unittest.TestCase):
    def test_python_projector_reproduces_sealed_jurisdiction_predecessor(self):
        validate_jurisdiction(jurisdiction_model())

    def test_eight_bounded_passes_and_all_other_records_preserved(self):
        model=jurisdiction_model()
        before=claims(load(ATTEMPT+'/before-review.json')); after=claims(model)
        self.assertEqual(model['counts']['claim_statuses'],{'PASS':241,'FAIL':35,'BLOCKED':23,'NOT_APPLICABLE':13,'UNVALIDATED':1701})
        self.assertEqual({cid for cid in before if before[cid]!=after[cid]},IDS)
        for cid in IDS:
            self.assertEqual(after[cid]['status'],'PASS',cid)
            self.assertNotIn('RUNTIME_OR_UI_OBSERVATION',after[cid]['required_evidence_types'])
            self.assertTrue(all(ref in after[cid]['evidence_refs'] for ref in before[cid]['evidence_refs']))
            self.assertTrue(all(ref in after[cid]['source_refs'] for ref in before[cid]['source_refs']))

    def test_exact_source_edits_and_open_procedures(self):
        registry=load(JUR.REGISTRY); model=jurisdiction_model()
        for source in registry['sources']:
            old=(ROOT/source['before_artifact']['path']).read_text().splitlines()
            current=(ROOT/source['path']).read_text().splitlines()
            self.assertEqual(len(old),len(current))
            self.assertEqual({i+1 for i,(a,b) in enumerate(zip(old,current)) if a!=b},JUR.SOURCES[source['path']])
            page=next(p for p in model['pages'] if p['source_file']==source['path'])
            self.assertTrue(all(p['status']!='PASS' for p in page['procedures']))
        original=claims(load(ATTEMPT+'/before-review.json'))[JUR.WORKLOAD]
        current=claims(model)[JUR.WORKLOAD]
        self.assertEqual(original['text'],current['text']); self.assertEqual(original['spans'],current['spans'])

    def test_changed_registry_source_capture_raw_and_baseline_all_fail_closed(self):
        registry=load(JUR.REGISTRY)
        refs=[JUR.REGISTRY,JUR.BASELINE,*JUR.SOURCES,*[s['before_artifact']['path'] for s in registry['sources']],
              *[a['path'] for a in registry['artifacts']],*[a['path'] for a in registry['retained_raw_sources']],
              PAYOUT_BEFORE,'verification/current-host-terms-binding.json']
        original=Path.read_bytes
        for target in refs:
            with self.subTest(target=target):
                def changed(path):
                    value=original(path)
                    return value+b' ' if path==ROOT/target else value
                with mock.patch.object(Path,'read_bytes',changed):
                    with self.assertRaises(ValueError): project_jurisdiction()

    def test_every_changed_and_unrelated_model_field_is_protected(self):
        for cid in [*IDS,'CUR-99fb8d131e321e03']:
            for field,value in [('status','UNVALIDATED'),('text','rewritten'),('rationale','unchecked'),('required_evidence_types',[]),('evidence_refs',[]),('source_refs',[])]:
                model=jurisdiction_model(); claim=claims(model)[cid]
                if claim[field]==value: continue
                claim[field]=value
                with self.subTest(cid=cid,field=field):
                    with self.assertRaisesRegex(ValueError,'whole model differs'): validate_jurisdiction(model)

    def test_missing_registry_cannot_validate_a_marked_model(self):
        model=jurisdiction_model(); original=Path.is_file
        with frozen_payout_predecessor(), mock.patch.object(Path,'is_file',lambda path:False if path==ROOT/JUR.REGISTRY else original(path)):
            with self.assertRaisesRegex(ValueError,'has no registry'): JUR.load_jurisdiction(ROOT,model)
            self.assertIsNone(JUR.load_jurisdiction(ROOT,load(JUR.BASELINE)))

if __name__=='__main__': unittest.main()
