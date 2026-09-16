#!/usr/bin/env python3
"""Structural/adverse checks against the complete frozen production inventory.

Fixture dispositions are simulated to exercise fail-closed mechanics; they do
not adjudicate Host product claims or authorize any external operation.
"""
import copy
import functools
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
PAYOUT_BEFORE='verification/evidence/2026-09-14-payout-provider-correction-attempt-01/pre-correction-payment.mdx'
PAYOUT_BEFORE_SHA256='02022ade67dcc35c44c660a5d3cdac7547c889c3a30e239eff56b57b22525992'
spec=importlib.util.spec_from_file_location('authority_scan_test_target',REPO/'scripts/current_host_authority_scan.py')
scan=importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def frozen_before_model(root=REPO):
    """Historical tests use a fixed verified target, never today's moving model."""
    return scan.read_json(scan.pinned_bytes(root,scan.BASELINE,scan.BASELINE_SHA256),scan.BASELINE)


def frozen_payout_payment() -> bytes:
    """Return the correction predecessor only after its sealed pin is checked."""
    value=(REPO/PAYOUT_BEFORE).read_bytes()
    if scan.digest(value)!=PAYOUT_BEFORE_SHA256:
        raise ValueError('payout fixture predecessor hash drift')
    return value


def frozen_source_reader(original, root=REPO):
    snapshot=scan.read_json(scan.pinned_bytes(root,scan.SNAPSHOT,scan.SNAPSHOT_SHA256),scan.SNAPSHOT)
    by_path={r['path']:r for r in snapshot['records']}
    def read(*args):
        target,relative=(root,args[0]) if len(args)==1 else args
        if Path(target).resolve()==root.resolve() and relative=='host/payment.mdx':
            return frozen_payout_payment()
        if Path(target).resolve()==root.resolve() and relative in by_path:
            row=by_path[relative]
            return scan.pinned_bytes(root,row['snapshot'],row['sha256'])
        return original(*args)
    return read


@functools.lru_cache(maxsize=1)
def historical_overlay():
    """Run dated producer tests on real materialized frozen sources/artifacts.

    No pin is relaxed. The fixture restores each of144 verified source files
    and the exact prior model, and omits the new registry to select old phases.
    Read-only git object lookups continue using the repository's existing Git
    directory. All fixture data remains local and is removed at process exit.
    """
    temporary=tempfile.TemporaryDirectory()
    root=Path(temporary.name)/'repo'
    shutil.copytree(REPO,root,ignore=shutil.ignore_patterns('.git','node_modules','.orchestra','graphify-out','__pycache__','.env','.env.*','current-host-authority-scan.json','current-host-clarification.json','current-host-payout-provider-correction.json'))
    git=REPO/'.git'
    if git.is_file():
        shutil.copyfile(git,root/'.git')
    else:
        (root/'.git').write_text('gitdir: '+str(git.resolve())+'\n')
    snapshot=scan.read_json(scan.pinned_bytes(REPO,scan.SNAPSHOT,scan.SNAPSHOT_SHA256),scan.SNAPSHOT)
    for item in snapshot['records']:
        (root/item['path']).write_bytes(scan.pinned_bytes(REPO,item['snapshot'],item['sha256']))
    (root/'verification/current-host-docs-review.json').write_bytes(scan.pinned_bytes(REPO,scan.BASELINE,scan.BASELINE_SHA256))
    spec=importlib.util.spec_from_file_location('frozen_historical_overlay',root/'scripts/build_current_host_vv_overlay.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._fixture_lifetime=temporary
    return module


class AuthorityScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=tempfile.TemporaryDirectory()
        cls.base=Path(cls.fixture.name)
        def copy_file(path):
            dest=cls.base/path
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(REPO/path,dest)
        copy_file(scan.BASELINE)
        copy_file(scan.SNAPSHOT)
        cls.before=json.loads((REPO/scan.BASELINE).read_text())
        cls.before_claims={c['id']:c for p in cls.before['pages'] for c in p['claims']}
        snapshots=json.loads((REPO/scan.SNAPSHOT).read_text())
        for source in snapshots['records']:
            copy_file(source['snapshot'])
            dest=cls.base/source['path']
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(REPO/source['snapshot'],dest)
        for p in ['scripts/build_current_host_vv_overlay.py','scripts/current_host_authority_scan.py','scripts/current_host_clarification.py','docs.json']:
            copy_file(p)
        paths=sorted({e['artifact_ref'] for p in cls.before['pages'] for c in p['claims'] for e in c['evidence_refs']} |
                     {e['artifact_ref'] for s in cls.before['support_layers'] for e in s['evidence_refs']})
        artifacts=[]
        for index,path in enumerate(paths):
            copy_file(path)
            artifacts.append({'id':f'OLD-{index}','path':path,'sha256':scan.digest((cls.base/path).read_bytes()),'kind':'CONTEXT'})
        required={cid for cid,c in cls.before_claims.items() if 'ACCOUNTABLE_OWNER_CONFIRMATION' in c['required_evidence_types']}
        required |= scan.ADDITIONAL_TAXONOMY_IDS | scan.VOLUME_DOWNGRADES | {'MCL-17c8031cb2c7e34a'}
        transitions=[]
        for cid in sorted(required):
            old=cls.before_claims[cid]
            after={'classification':'IMPLEMENTATION_OR_CONCEPT','status':'BLOCKED' if old['status']=='BLOCKED' else 'UNVALIDATED',
                   'required_evidence_types':['CANONICAL_IMPLEMENTATION_SOURCE'],'owner_role':'Engineering source reviewer',
                   'rationale':'SIMULATED fixture disposition; this is not product proof.',
                   'next_action':'Inspect existing canonical source for this exact occurrence.'}
            method='TAXONOMY_ONLY'
            if cid in scan.VOLUME_DOWNGRADES or cid=='MCL-17c8031cb2c7e34a':
                method='PROVENANCE_DOWNGRADE'
                after['evidence_refs']=[{**e,'role':'PARTIAL_'+e['role'],'limit':'Narrow static proof only; broader behavior remains unvalidated.'} for e in old['evidence_refs']]
            transitions.append({'claim_id':cid,'before_claim_sha256':scan.object_digest(old),
                                'method':method,'after':after,'basis':[],
                                'review_rationale':'SIMULATED test-only transition exercises structural validation.'})
        cls.registry={'schema_version':'1.0','record_type':'HOST_AUTHORITY_SCAN_TRANSITION',
                      'generated_at':'2026-09-09T00:00:00Z',
                      'baseline':{'path':scan.BASELINE,'sha256':scan.BASELINE_SHA256},
                      'source_snapshot':{'path':scan.SNAPSHOT,'sha256':scan.SNAPSHOT_SHA256},
                      'artifacts':artifacts,'source_transitions':[],'transitions':transitions}

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/'repo'
        shutil.copytree(self.base,self.root)
        self.registry_value=copy.deepcopy(self.registry)

    def tearDown(self):
        self.temp.cleanup()

    def write_registry(self,value=None):
        value=value or self.registry_value
        data=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
        (self.root/scan.REGISTRY).write_bytes(data)
        return scan.digest(data)

    def project(self):
        pin=self.write_registry()
        with patch.object(scan,'REGISTRY_SHA256',pin):
            return scan.project(self.root)

    def entry(self,cid='MCL-906c68dcab1918fd'):
        return next(e for e in self.registry_value['transitions'] if e['claim_id']==cid)

    def test_full_population_and_unaffected_payload_are_preserved(self):
        model=self.project()
        self.assertEqual(model['counts']['claims'],2013)
        self.assertEqual(len(model['pages']),44)
        self.assertEqual(len(model['support_layers']),33)
        changed={e['claim_id'] for e in self.registry_value['transitions']}
        claims={c['id']:c for p in model['pages'] for c in p['claims']}
        self.assertEqual(set(claims),set(self.before_claims))
        for cid in set(claims)-changed:
            self.assertEqual(claims[cid],self.before_claims[cid],cid)
        self.assertEqual(model['support_layers'],self.before['support_layers'])
        for cid in scan.VOLUME_DOWNGRADES:
            self.assertEqual(claims[cid]['status'],'UNVALIDATED')
            self.assertTrue(all('PARTIAL' in e['role'] for e in claims[cid]['evidence_refs']))

    def test_unsealed_or_tampered_registry_is_rejected(self):
        pin=self.write_registry()
        with patch.object(scan,'REGISTRY_SHA256',''):
            with self.assertRaisesRegex(ValueError,'invalid pin'):
                scan.project(self.root)
        self.registry_value['transitions'][0]['after']['status']='PASS'
        self.write_registry()
        with patch.object(scan,'REGISTRY_SHA256',pin):
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                scan.project(self.root)

    def test_tampered_model_status_is_rejected(self):
        model=self.project()
        model['pages'][0]['claims'][1]['status']='PASS'
        pin=self.write_registry()
        with patch.object(scan,'REGISTRY_SHA256',pin):
            with self.assertRaisesRegex(ValueError,'current model differs'):
                scan.validate_model(model,self.root)

    def test_taxonomy_cannot_promote_pass_even_when_registry_is_resealed(self):
        self.entry()['after']['status']='PASS'
        with self.assertRaisesRegex(ValueError,'cannot clear'):
            self.project()

    def test_missing_and_duplicate_dispositions_are_rejected(self):
        for operation,pattern in [('missing','all331'),('duplicate','duplicate/unknown')]:
            with self.subTest(operation=operation):
                self.registry_value=copy.deepcopy(self.registry)
                if operation=='missing':
                    self.registry_value['transitions']=[e for e in self.registry_value['transitions'] if e['claim_id']!='MCL-906c68dcab1918fd']
                else:
                    self.registry_value['transitions'].append(copy.deepcopy(self.entry()))
                with self.assertRaisesRegex(ValueError,pattern):
                    self.project()

    def test_previous_claim_identity_is_not_replaceable(self):
        self.entry()['before_claim_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'previous claim hash'):
            self.project()

    def test_missing_artifact_ref_does_not_fall_back_to_model(self):
        self.entry()['after']['evidence_refs']=[{'id':'BROKEN','role':'SOMETHING','limit':'No file'}]
        with self.assertRaisesRegex(ValueError,'missing artifact_ref'):
            self.project()

    def test_unregistered_source_change_is_rejected(self):
        path=self.root/'host/hosting-overview.mdx'
        path.write_text(path.read_text()+'\nUnregistered new claim.\n')
        with self.assertRaisesRegex(ValueError,'unregistered/tampered current source'):
            self.project()

    def test_registered_changed_source_cannot_silently_drop_affected_occurrence(self):
        path=self.root/'host/hosting-overview.mdx'
        before=scan.digest(path.read_bytes())
        path.write_text(path.read_text().replace('Vast is a GPU marketplace. Hosts provide machines; renters run workloads on them.','An unrelated new assertion.'))
        self.registry_value['source_transitions']=[{'path':'host/hosting-overview.mdx','before_sha256':before,'after_sha256':scan.digest(path.read_bytes())}]
        with self.assertRaisesRegex(ValueError,'unregistered source occurrence change'):
            self.project()

    def test_registered_hash_cannot_hide_new_uninventoried_prose(self):
        path=self.root/'host/hosting-overview.mdx'
        before=scan.digest(path.read_bytes())
        path.write_text(path.read_text()+'\nAn unreviewed guarantee appears here.\n')
        self.registry_value['source_transitions']=[{'path':'host/hosting-overview.mdx','before_sha256':before,'after_sha256':scan.digest(path.read_bytes())}]
        with self.assertRaisesRegex(ValueError,'outside the reconciled claim inventory'):
            self.project()

    def test_exact_line_relocation_preserves_unaffected_proof(self):
        path=self.root/'host/hosting-overview.mdx'
        before=scan.digest(path.read_bytes())
        path.write_text('\n'+path.read_text())
        self.registry_value['source_transitions']=[{'path':'host/hosting-overview.mdx','before_sha256':before,'after_sha256':scan.digest(path.read_bytes())}]
        model=self.project()
        claim=next(c for p in model['pages'] for c in p['claims'] if c['id']=='MCL-e12ac9f6be2ce502')
        old=self.before_claims[claim['id']]
        self.assertEqual(claim['status'],old['status'])
        self.assertEqual(claim['evidence_refs'],old['evidence_refs'])
        self.assertEqual(claim['spans'][0]['start'],old['spans'][0]['start']+1)
        self.assertEqual(claim['history']['carry_decision'],scan.RELOCATION)

    def test_current_snapshot_and_terminal_artifact_tampering_are_rejected(self):
        snapshot=json.loads((self.root/scan.SNAPSHOT).read_text())['records'][0]['snapshot']
        path=self.root/snapshot
        path.write_bytes(path.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            self.project()

    def test_escape_and_symlink_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'unsafe path'):
            scan.safe_path(self.root,'../escape')
        target=self.root/'verification/evidence-link'
        target.symlink_to(self.root/'verification/evidence',target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'):
            scan.safe_path(self.root,'verification/evidence-link/anything.json')

    def test_model_graph_registry_and_snapshot_are_not_proof_terminals(self):
        for path in ['verification/current-host-docs-review.json',scan.REGISTRY,scan.BASELINE,
                     scan.SNAPSHOT,'graphify-out/graph.json',scan.ATTEMPT+'/sources-before/host/payment.mdx']:
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'terminal proof'):
                scan.terminal_allowed({'path':path,'kind':'GOVERNING_SOURCE'})
        with self.assertRaisesRegex(ValueError,'context-only'):
            scan.terminal_allowed({'path':scan.ATTEMPT+'/report.json','kind':'CONTEXT'})

    def test_source_adjudication_needs_all_lanes_and_independent_proof(self):
        entry=self.entry()
        entry['method']='SOURCE_ADJUDICATION'
        entry['after']['status']='PASS'
        with self.assertRaisesRegex(ValueError,'unsatisfied evidence lanes'):
            self.project()

    def test_source_excerpt_and_pointer_must_select_actual_text(self):
        data=json.dumps({'sections':[{'text':'retained primary-source sentence'}]}).encode()
        self.assertEqual(scan.pointer_text(data,'/sections/0/text'),'retained primary-source sentence')
        for pointer in ['/sections/8/text','/sections/0/missing','/sections','/limits','/support_rationale']:
            with self.subTest(pointer=pointer),self.assertRaises(ValueError):
                scan.pointer_text(data,pointer)
        metadata=json.dumps({'limits':'retained primary-source sentence','support_rationale':'retained primary-source sentence'}).encode()
        for pointer in ['/limits','/support_rationale']:
            with self.subTest(metadata=pointer),self.assertRaisesRegex(ValueError,'not metadata'):
                scan.pointer_text(metadata,pointer)
        with self.assertRaisesRegex(ValueError,'source_text hash'):
            scan.pointer_text(b'{"source_text":"text without its capture hash"}','/source_text')

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            scan.read_json(b'{"status":"UNVALIDATED","status":"PASS"}','test')

    def test_bounded_navigation_positive_and_missing_destination_negative(self):
        cid='MCL-29c442c7d32660e6'
        entry=self.entry(cid)
        old=self.before_claims[cid]
        source=next(p for p in self.before['pages'] if any(c['id']==cid for c in p['claims']))
        proof={'claim_id':cid,'text_sha256':scan.digest(old['text'].encode()),'source_sha256':source['source_sha256'],'result':'PASS'}
        path=scan.ATTEMPT+'/fixture-navigation-retest.json'
        (self.root/path).write_text(json.dumps(proof))
        self.registry_value['artifacts'].append({'id':'NAV','path':path,'sha256':scan.digest((self.root/path).read_bytes()),'kind':'STATIC_RETEST'})
        entry['method']='NAVIGATION_RETEST'
        entry['after'].update({'status':'PASS','classification':'NAVIGATION_CONTRACT','required_evidence_types':['REPOSITORY_STATIC_CHECK'],
                               'evidence_refs':[{'id':'NAV','role':'CURRENT_STATIC_RETEST','limit':'Local route existence only.','artifact_ref':path}]})
        entry['basis']=[{'artifact_id':'NAV','lane':'REPOSITORY_STATIC_CHECK','support_rationale':'Exact route existence only; fixture proof.'}]
        self.assertEqual(next(c for p in self.project()['pages'] for c in p['claims'] if c['id']==cid)['status'],'PASS')
        # A report saying PASS cannot override a changed/missing destination.
        (self.root/'host/earning.mdx').unlink()
        with self.assertRaisesRegex(ValueError,'missing or escaping path'):
            self.project()

    def test_provenance_downgrade_cannot_drop_partial_evidence(self):
        self.entry('VOL-C06')['after']['evidence_refs']=[]
        with self.assertRaisesRegex(ValueError,'retain narrow proof as PARTIAL'):
            self.project()
        self.registry_value=copy.deepcopy(self.registry)
        self.entry('VOL-C06')['after']['evidence_refs'][0]['id']='UNRELATED-PROOF'
        with self.assertRaisesRegex(ValueError,'retained narrow proof identity'):
            self.project()

    def test_arbitrary_extra_claim_or_removed_model_claim_is_rejected(self):
        model=self.project()
        model['pages'][0]['claims'].pop()
        pin=self.write_registry()
        with patch.object(scan,'REGISTRY_SHA256',pin),self.assertRaisesRegex(ValueError,'current model differs'):
            scan.validate_model(model,self.root)


if __name__=='__main__':
    unittest.main(verbosity=2)
