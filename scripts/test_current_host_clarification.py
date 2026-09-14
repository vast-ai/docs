#!/usr/bin/env python3
"""Adversarial local fixtures for the clarification transition reader."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('clarification_test_target',REPO/'scripts/current_host_clarification.py')
clarification=importlib.util.module_from_spec(spec); spec.loader.exec_module(clarification)
terms_spec=importlib.util.spec_from_file_location('terms_test_target',REPO/'scripts/current_host_terms_binding.py')
terms=importlib.util.module_from_spec(terms_spec); terms_spec.loader.exec_module(terms)


def model():
    claim={'id':'C1','text':'Advice.','headings':['H'],'spans':[],'status':'UNVALIDATED','required_evidence_types':['RUNTIME_OR_UI_OBSERVATION'],'owner_role':'Old owner','rationale':'Old rationale','next_action':'Old next action','evidence_refs':[],'source_refs':[],'history':{},'classification':'IMPLEMENTATION_OR_CONCEPT','coverage_state':'UNCHANGED_EXACT'}
    node={'id':'N1','title':'N','next_action':'Old node action','status':'UNVALIDATED','spans':[],'limits':[],'history':{},'coverage_state':'UNCHANGED_EXACT','parent_id':None}
    procedure={'id':'P1','title':'P','next_action':'Old procedure action','nodes':[node],'status':'UNVALIDATED','spans':[],'limits':[],'history':{},'coverage_state':'UNCHANGED_EXACT'}
    return {'schema_version':'1.0','record_type':'HOST_DOCS_CURRENT_REVIEW','generated_at':'old','source':{},'history':{},'pages':[{'route':'/host/x','title':'X','claims':[claim],'procedures':[procedure]}],'support_layers':[],'counts':{},'corrections':[]}


class ClarificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.before=model()
        self.baseline='before.json'; self.registry='registry.json'
        (self.root/self.baseline).write_text(json.dumps(self.before))
        c,p,n=clarification._index(self.before)
        self.value={'schema_version':'1.0','record_type':'HOST_REVIEW_CLARIFICATION_TRANSITION','generated_at':'2026-09-10T00:00:00Z','baseline':{'path':self.baseline,'sha256':clarification.digest((self.root/self.baseline).read_bytes())},'claims':[{'claim_id':'C1','before_sha256':clarification.canonical_hash(c['C1']),'review_method':'ADVICE_REVIEW','review_rationale':'Advice needs review, not runtime proof.','after':{'classification':'OPERATIONAL_ADVICE','required_evidence_types':['REPOSITORY_STATIC_CHECK'],'owner_role':'Documentation reviewer','rationale':'Exact instruction is advice.','next_action':'Review safety and factual inputs.'}}],'nodes':[{'node_id':'N1','before_sha256':clarification.canonical_hash(n['N1']),'next_action':'Review pending node check.'}],'procedures':[{'procedure_id':'P1','before_sha256':clarification.canonical_hash(p['P1']),'next_action':'Review pending procedure check.'}]}
    def tearDown(self):
        self.tmp.cleanup()
    def pin(self):
        (self.root/self.registry).write_text(json.dumps(self.value,separators=(',',':')))
        return clarification.digest((self.root/self.registry).read_bytes())
    def project(self):
        pin=self.pin()
        with patch.object(clarification,'REGISTRY',self.registry),patch.object(clarification,'REGISTRY_SHA256',pin),patch.object(clarification,'BASELINE',self.baseline),patch.object(clarification,'BASELINE_SHA256',self.value['baseline']['sha256']):
            return clarification.project(self.root,lambda root,before: self.assertEqual(before,self.before))
    def test_projection_preserves_status_and_proof_fields(self):
        out=self.project(); claim=out['pages'][0]['claims'][0]
        self.assertEqual(claim['status'],'UNVALIDATED'); self.assertEqual(claim['text'],'Advice.'); self.assertEqual(claim['evidence_refs'],[])
        self.assertEqual(claim['classification'],'OPERATIONAL_ADVICE'); self.assertEqual(out['pages'][0]['procedures'][0]['next_action'],'Review pending procedure check.')
        self.assertIn('registry SHA-256 ',out['corrections'][-1]['current'])
    def test_resealed_unauthorized_status_and_duplicate_ids_fail(self):
        self.value['claims'][0]['after']['status']='PASS'
        with self.assertRaisesRegex(ValueError,'unauthorized'): self.project()
        del self.value['claims'][0]['after']['status']; self.value['claims'].append(copy.deepcopy(self.value['claims'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'): self.project()
    def test_empty_replacement_evidence_lanes_fail(self):
        self.value['claims'][0]['after']['required_evidence_types']=[]
        with self.assertRaisesRegex(ValueError,'invalid evidence enum'): self.project()
    def test_pass_and_fail_citation_methods_are_not_weakened(self):
        claim=self.before['pages'][0]['claims'][0]
        claim['status']='PASS'; (self.root/self.baseline).write_text(json.dumps(self.before)); self.value['baseline']['sha256']=clarification.digest((self.root/self.baseline).read_bytes()); self.value['claims'][0]['before_sha256']=clarification.canonical_hash(claim)
        with self.assertRaisesRegex(ValueError,'PASS/N/A'): self.project()
        claim['status']='FAIL'; claim['required_evidence_types']=['AUTHORITATIVE_DOCUMENTATION_CITATION']; (self.root/self.baseline).write_text(json.dumps(self.before)); self.value['baseline']['sha256']=clarification.digest((self.root/self.baseline).read_bytes()); self.value['claims'][0]['before_sha256']=clarification.canonical_hash(claim)
        with self.assertRaisesRegex(ValueError,'citation lane'): self.project()
    def test_wrong_predecessor_hash_and_missing_pin_fail(self):
        self.value['claims'][0]['before_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'predecessor drift'): self.project()
        self.value['claims'][0]['before_sha256']=clarification.canonical_hash(clarification._index(self.before)[0]['C1'])
        pin=self.pin()
        with patch.object(clarification,'REGISTRY',self.registry),patch.object(clarification,'REGISTRY_SHA256',''),patch.object(clarification,'BASELINE',self.baseline),patch.object(clarification,'BASELINE_SHA256',self.value['baseline']['sha256']):
            with self.assertRaisesRegex(ValueError,'invalid pin'): clarification.project(self.root,lambda *_: None)
        self.assertTrue(pin)
    def test_phase43_runs_before_patch_and_projection_tamper_fails(self):
        calls=[]
        pin=self.pin()
        with patch.object(clarification,'REGISTRY',self.registry),patch.object(clarification,'REGISTRY_SHA256',pin),patch.object(clarification,'BASELINE',self.baseline),patch.object(clarification,'BASELINE_SHA256',self.value['baseline']['sha256']):
            out=clarification.project(self.root,lambda *_: calls.append('phase43'))
            self.assertEqual(calls,['phase43'])
            out['pages'][0]['claims'][0]['status']='PASS'
            with self.assertRaisesRegex(ValueError,'whole model differs'): clarification.validate_model(out,self.root,lambda *_: None)
    def test_predecessor_source_drift_and_symlink_path_fail_closed(self):
        pin=self.pin()
        with patch.object(clarification,'REGISTRY',self.registry),patch.object(clarification,'REGISTRY_SHA256',pin),patch.object(clarification,'BASELINE',self.baseline),patch.object(clarification,'BASELINE_SHA256',self.value['baseline']['sha256']):
            with self.assertRaisesRegex(ValueError,'source drift'):
                clarification.project(self.root,lambda *_: (_ for _ in ()).throw(ValueError('clarification transition: source drift')))
        (self.root/'outside').mkdir(); (self.root/'linked').symlink_to(self.root/'outside',target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'unsafe path'): clarification.safe(self.root,'linked/file.json')
    def test_current_taxonomy_uses_exact_projected_claim_or_requires_id_for_ambiguity(self):
        overlay_spec=importlib.util.spec_from_file_location('clarification_overlay_target',REPO/'scripts/build_current_host_vv_overlay.py')
        overlay=importlib.util.module_from_spec(overlay_spec); overlay_spec.loader.exec_module(overlay)
        (self.root/'registry.json').write_text('{}')
        claims=[{'id':'C1','text':'Same literal','spans':[{'source_file':'host/x.mdx'}],
                 'classification':'OPERATIONAL_ADVICE','required_evidence_types':['REPOSITORY_STATIC_CHECK']}]
        projected={'pages':[{'claims':claims}]}
        transition=types.SimpleNamespace(REGISTRY='registry.json',project=lambda root: projected)
        with patch.object(overlay,'REPO',self.root),patch.object(overlay,'clarification_module',return_value=transition):
            self.assertEqual(overlay.classify_literal_source_first('host/x.mdx','Same literal'),
                             ('OPERATIONAL_ADVICE',['REPOSITORY_STATIC_CHECK'],False))
            claims.append({'id':'C2','text':'Same literal','spans':[{'source_file':'host/x.mdx'}],
                           'classification':'IMPLEMENTATION_OR_CONCEPT','required_evidence_types':['CANONICAL_IMPLEMENTATION_SOURCE']})
            with self.assertRaisesRegex(ValueError,'select exact claim ID'):
                overlay.classify_literal_source_first('host/x.mdx','Same literal')
    def test_real_current_context_is_pinned_and_missing_registry_fails_closed(self):
        # This is the exact phase-46 predecessor, not today's Terms or
        # jurisdiction sources.  Phase-43 validates against its own retained
        # post-authority bytes: the phase-47 Workload source and phase-48 Tax
        # artifacts are later layers and cannot be read as its current inputs.
        current=json.loads((REPO/terms.BASELINE).read_text())
        phase43_sources={
            terms.SOURCE: (REPO/'verification/evidence/2026-09-10-host-terms-binding-attempt-01/workload-policy-before.mdx').read_bytes(),
            'host/datacenter-status.mdx': (REPO/'verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/before-datacenter-status.mdx').read_bytes(),
            'host/guide-to-taxes.mdx': (REPO/'verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01/before-guide-to-taxes.mdx').read_bytes(),
            'host/payment.mdx': __import__('scripts.test_current_host_authority_scan', fromlist=['frozen_payout_payment']).frozen_payout_payment(),
        }
        authority=terms.module('current_host_authority_scan')
        context=clarification.load_clarification(REPO,current,
            lambda root,phase43: authority.validate_model(phase43,root,phase43_sources))
        self.assertEqual(context['registry_sha256'],clarification.REGISTRY_SHA256)
        self.assertEqual(len(context['registry']['claims']),len({item['claim_id'] for item in context['registry']['claims']}))
        self.assertLessEqual(len(context['registry']['claims']),current['counts']['claims'])
        self.assertTrue(any(item.get('id')==clarification.MARKER for item in current['corrections']))
        with patch.object(clarification,'REGISTRY','verification/missing-clarification-registry.json'):
            with self.assertRaisesRegex(ValueError,'missing registry'):
                clarification.load_clarification(REPO,current)

if __name__=='__main__': unittest.main()
