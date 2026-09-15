#!/usr/bin/env python3
"""Sealed source-family successor; replay historical proof before a bounded patch."""
from __future__ import annotations
import copy, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path

REGISTRY = 'verification/current-host-source-family-review.json'
REGISTRY_SHA256 = '6502a30c0e3f27f2808239fdca61a0497d8efd7406a0c5af02fa76c58ffe544d'
ATTEMPT = 'verification/evidence/2026-09-15-host-unvalidated-source-families-attempt-01'
MARKER = 'HOST-SOURCE-FAMILY-REVIEW-01'
INVENTORY_SHA256 = '25652cd08b4f811ff09237def69ee2e6b699f241e4735919115ea7116554f841'
BASELINE_SHA256 = '663f62b97a54c809a6516205583acf1a63d1866706d0c40296aacef4552ebd7b'
OWNER_AMENDMENT_SHA256 = '01482cf7725940c5d84f06774c886ee10c358837b532557f99b8a43de40dd5a5'
OWNER = 'verification/current-host-owner-questions.json'

def sha(value): return hashlib.sha256(value).hexdigest()
def canon(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def objhash(value): return sha(canon(value).encode())
def req(value, message):
    if not value: raise ValueError('host source-family review: ' + message)
def prior_module():
    spec=importlib.util.spec_from_file_location('source_family_closure_predecessor',Path(__file__).with_name('current_host_closure_correction.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def index(model): return {c['id']:c for p in model['pages'] for c in p['claims']}
def without_nodes(node): return {k:v for k,v in node.items() if k!='nodes'}

def project(root: Path, frozen_source_overrides=None):
    root=root.resolve();pre=prior_module()
    frozen_source_overrides = frozen_source_overrides or {}
    def read(ref): return frozen_source_overrides[ref] if ref in frozen_source_overrides else pre.safe(root,ref).read_bytes()
    def pin(ref,wanted):
        raw=read(ref);req(sha(raw)==wanted,'digest drift '+ref);return raw
    registry=json.loads(pin(REGISTRY,REGISTRY_SHA256))
    req(set(registry)=={'schema_version','record_type','generated_at','scope','sources','artifacts','transitions','procedures','limits'},'registry keys')
    req(registry['schema_version']=='1.0' and registry['record_type']=='HOST_SOURCE_FAMILY_REVIEW','registry type')
    inventory=json.loads(pin(ATTEMPT+'/inventory.json',INVENTORY_SHA256))
    baseline_check=json.loads(pin(ATTEMPT+'/integration-baseline.json',BASELINE_SHA256))
    req(registry['scope']['path']==ATTEMPT+'/integration-scope.json','scope path')
    scope=json.loads(pin(registry['scope']['path'],registry['scope']['sha256']))
    ids={c['id'] for c in inventory['claims']}
    req(len(ids)==358 and len(inventory['claims'])==358 and set(scope['decisions'])==ids,'frozen decision inventory')
    before={};current={};maps={};after_hashes={}
    for source in registry['sources']:
        ref=source['path'];req(ref in inventory['source_hashes'] and ref not in before,'source scope')
        req(source['before_artifact']['path']==ATTEMPT+'/sources-before/'+ref,'before source path')
        before[ref]=pin(source['before_artifact']['path'],source['before_artifact']['sha256'])
        req(sha(before[ref])==inventory['source_hashes'][ref],'before source drift')
        current[ref]=pin(ref,source['after_sha256']);after_hashes[ref]=sha(current[ref])
        oldlines,newlines=before[ref].decode().splitlines(),current[ref].decode().splitlines()
        mapping=dict(source['line_map']);maps[ref]=mapping
        req(len(mapping)==len(source['line_map']) and len(set(mapping.values()))==len(mapping),'duplicate line map')
        req(list(mapping)==sorted(mapping) and list(mapping.values())==sorted(mapping.values()),'unordered line map')
        for a,b in mapping.items():req(0<a<=len(oldlines) and 0<b<=len(newlines) and oldlines[a-1]==newlines[b-1],'source relocation drift')
        oldchanged={n for e in source['edits'] for n in range(e['before_start'],e['before_end']+1)}
        newchanged={n for e in source['edits'] for n in range(e['after_start'],e['after_end']+1)}
        req(set(mapping).isdisjoint(oldchanged) and set(mapping)|oldchanged==set(range(1,len(oldlines)+1)),'before line partition')
        req(set(mapping.values()).isdisjoint(newchanged) and set(mapping.values())|newchanged==set(range(1,len(newlines)+1)),'after line partition')
    for ref,wanted in inventory['source_hashes'].items():
        if ref not in before:pin(ref,wanted)
    amendment=json.loads(pin(ATTEMPT+'/owner-context-amendment.json',OWNER_AMENDMENT_SHA256))
    owner_before=pin(amendment['before_artifact']['path'],amendment['before_artifact']['sha256'])
    baseline=pre.project(root,frozen_source_overrides={**frozen_source_overrides,**before,OWNER:owner_before})
    req(objhash(baseline)==baseline_check['baseline_model_canonical_sha256'],'complete predecessor differs from baseline')
    old=index(baseline)
    req({cid:objhash(c) for cid,c in old.items()}==baseline_check['claim_hashes'],'baseline claim inventory')
    req(objhash([p['procedures'] for p in baseline['pages']])==baseline_check['procedure_population_sha256'],'baseline procedures')
    req(all(old[c['id']]['status']=='UNVALIDATED' and sha(old[c['id']]['text'].encode())==c['literal_sha256'] for c in inventory['claims']),'frozen literal drift')
    owners=json.loads(read(OWNER));expected=json.loads(owner_before)
    req(len(expected['questions'])==8 and amendment['question_id']=='HQ-PAYOUT-THRESHOLD','owner amendment scope')
    q=next(q for q in expected['questions'] if q['id']==amendment['question_id']);req(q==amendment['before'],'owner context predecessor')
    q.clear();q.update(copy.deepcopy(amendment['after']));owners.pop('model_sha256');expected.pop('model_sha256')
    req(owners==expected,'unrelated owner question drift')
    artifacts={a['path']:pin(a['path'],a['sha256']) for a in registry['artifacts']}
    req(len(artifacts)==len(registry['artifacts']),'duplicate artifact')
    def relocate(span):
        mapping=maps.get(span['source_file'])
        if mapping is None:return copy.deepcopy(span)
        values=[mapping.get(i) for i in range(span['start'],span['end']+1)]
        if None in values or values!=list(range(values[0],values[-1]+1)):return None
        return {**span,'start':values[0],'end':values[-1]}
    def verify(span):
        lines=(current.get(span['source_file']) or read(span['source_file'])).decode().splitlines()
        req(0<span['start']<=span['end']<=len(lines),'span bounds')
        text='\n'.join(lines[span['start']-1:span['end']]);req(sha(text.encode())==span['text_sha256'],'span text drift');return text
    model=copy.deepcopy(baseline);claims=index(model);entries={t['claim_id']:t for t in registry['transitions']}
    req(len(registry['transitions'])==358 and set(entries)==ids,'transition scope')
    for cid,entry in entries.items():
        prior=old[cid];patch=entry['after'];decision=scope['decisions'][cid]
        req(entry['before_sha256']==objhash(prior),'claim predecessor '+cid)
        req(set(patch)<= {'text','spans','status','classification','required_evidence_types','owner_role','rationale','next_action','evidence_refs','source_refs','coverage_state'},'unsupported patch')
        req(objhash({k:patch[k] for k in ['text','status','classification','required_evidence_types','owner_role']})==decision['fields_sha256'],'accepted disposition drift '+cid)
        req(patch['status'] in {'PASS','FAIL','BLOCKED','UNVALIDATED','NOT_APPLICABLE'},'unknown status')
        req(all(e in patch['evidence_refs'] for e in prior['evidence_refs']) and all(s in patch['source_refs'] for s in prior['source_refs']),'discarded prior evidence')
        if patch['required_evidence_types']!=prior['required_evidence_types']:req(entry['method_rationale']==decision['method_rationale'] and bool(entry['method_rationale']),'unjustified method change')
        req(bool(entry['basis']) and bool(entry['limits']) and bool(patch['rationale']),'missing scoped review')
        for basis in entry['basis']:
            ref=basis['artifactRef'];req(ref in artifacts and pre.selection(artifacts[ref],basis['text_pointer'])==basis['excerpt'],'source selector/excerpt drift '+cid)
            req(basis['support_rationale'] and any(e['artifact_ref']==ref for e in patch['evidence_refs']),'unbound evidence')
            req(any(s['path']==(basis['sourceUrl'] or ref) and s['locator']==basis['text_pointer'] for s in patch['source_refs']),'unbound source')
        claims[cid].update(copy.deepcopy(patch))
        claims[cid]['history']={**prior.get('history',{}),'source_family_review':{'marker':MARKER,'before_claim_sha256':objhash(prior),'prior_status':prior['status'],'prior_text_sha256':sha(prior['text'].encode()),'prior_text':prior['text'] if patch['text']!=prior['text'] else None,'limits':entry['limits']}}
    procedure_entries={p['model_pointer']:p for p in registry['procedures']};seen_procedures=set()
    req(len(procedure_entries)==len(registry['procedures']),'duplicate procedure review')
    for page_index,page in enumerate(model['pages']):
        if page['source_file'] in after_hashes:page['source_sha256']=after_hashes[page['source_file']];page['coverage_state']='CHANGED'
        for dep in page['dependencies']:
            if dep['source_file'] in after_hashes:dep['source_sha256']=after_hashes[dep['source_file']];page['coverage_state']='CHANGED'
        for claim in page['claims']:
            cid=claim['id']
            if 'spans' not in entries.get(cid,{}).get('after',{}):claim['spans']=[relocate(s) for s in old[cid]['spans']]
            req(None not in claim['spans'],'unreviewed changed occurrence '+cid)
            literal='\n'.join(verify(s) for s in claim['spans'])
            if claim['text']!=old[cid]['text']:req(literal==claim['text'],'replacement literal drift '+cid)
            if cid not in ids:req({k:v for k,v in claim.items() if k!='spans'}=={k:v for k,v in old[cid].items() if k!='spans'},'unrelated claim drift '+cid)
        for procedure_index,procedure in enumerate(page['procedures']):
            for node_index,node in enumerate([procedure,*procedure['nodes']]):
                pointer=f'/pages/{page_index}/procedures/{procedure_index}'+(f'/nodes/{node_index-1}' if node_index else '')
                entry=procedure_entries.get(pointer)
                if entry:
                    req(entry['id']==node['id'] and objhash(without_nodes(node))==entry['before_sha256'],'procedure predecessor')
                    req(entry['after']==scope['procedures'][pointer]['after'] and entry['reason']==scope['procedures'][pointer]['reason'],'unaccepted procedure change')
                    req(set(entry['after'])<= {'spans','status','coverage_state','limits','history'},'procedure patch scope')
                    node.update(copy.deepcopy(entry['after']));seen_procedures.add(pointer)
                else:
                    spans=[relocate(s) for s in node.get('spans',[])];req(None not in spans,'unreviewed changed procedure '+node['id']);node['spans']=spans
                for span in node.get('spans',[]):verify(span)
    req(seen_procedures==set(procedure_entries)==set(scope['procedures']),'procedure scope drift')
    for item in model['source']['source_manifest']:
        if item['path'] in after_hashes:item['sha256']=after_hashes[item['path']]
    req(set(index(model))==set(old) and len(old)==2008,'active claim inventory drift')
    model['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in claims.values()).items()))
    model['counts']['page_coverage_states']=dict(sorted(Counter(p['coverage_state'] for p in model['pages']).items()))
    model['generated_at']=registry['generated_at'];model['corrections'].append({'id':MARKER,'scope':'358 frozen source-family occurrences','history':'Sealed closure predecessor replayed with exact before-source bytes; all prior findings and evidence retained.','current':'Accepted per-passage source reviews and corrections; explicit residual defects remain visible.','reason':registry['limits']})
    return model

def load_source_family_review(root,model):
    present=(root/REGISTRY).is_file();marked=any(x.get('id')==MARKER for x in model.get('corrections',[]))
    if not present:req(not marked,'source-family-marked model has no registry');return None
    req(model==project(root),'whole model differs from source-family projection');return {'registry':REGISTRY,'registry_sha256':REGISTRY_SHA256}
