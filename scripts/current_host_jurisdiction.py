#!/usr/bin/env python3
"""Sealed eight-claim source/advice correction after the unchanged Terms chain.

The registry fixes review identity, not product truth. Independent retained
captures support cited clauses; a separate contextual inspection records advice
review. No operational, whole-page, or human-acceptance result is inferred.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

REGISTRY='verification/current-host-jurisdiction.json'
REGISTRY_SHA256='a5ef30f14e19f9f572a98b3d314381c357424505da1894fcba0bb06721c077ba'
ATTEMPT='verification/evidence/2026-09-11-host-jurisdiction-authority-attempt-01'
BASELINE=ATTEMPT+'/before-review.json'
BASELINE_SHA256='e66ff7fe9253634c7ffcb2571816728a39549cf0236dc7052a8c1aab8d081b8a'
MARKER='HOST-JURISDICTION-01'
DECISION='CURRENT_HOST_JURISDICTION'
SOURCES={'host/guide-to-taxes.mdx':{25,26,27},'host/datacenter-status.mdx':{19,20,25,26}}
TAX={'CUR-708c718cf735c8b2','CUR-555543e9b2ceddb4','CUR-2ead4eda972e84b0'}
WORKLOAD='MCL-8fe2020c0e7efe26'
PROGRAM={'MCL-1536a1bd58d80927','MCL-c9882f043e407640','MCL-c8bf23127171e2b0','MCL-3acecd71e6a7b312'}
IDS=TAX|PROGRAM|{WORKLOAD}
STATIC='REPOSITORY_STATIC_CHECK'
CITE='AUTHORITATIVE_DOCUMENTATION_CITATION'
AFTER={'classification','status','required_evidence_types','owner_role','rationale','next_action','text','headings','spans','evidence_refs','source_refs'}
HISTORY_REASON=' Exact contextual advice and independent source review; no operational result or human acceptance is inferred.'
NODE_LIMIT='Previous procedure span crosses the jurisdiction source edit; no procedure evidence transfers.'

def require(ok: Any,message: str)->None:
    if not ok: raise ValueError('jurisdiction: '+message)
def digest(value: bytes)->str: return hashlib.sha256(value).hexdigest()
def objhash(value: Any)->str: return digest(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def module(name: str):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    result=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(result); return result
def safe(root: Path,ref: str)->Path:
    require(isinstance(ref,str) and ref and not ref.startswith('/') and '\\' not in ref and all(p not in {'','.','..'} for p in ref.split('/')),'unsafe path')
    path=root.resolve()
    for part in ref.split('/'):
        path/=part; require(not path.is_symlink(),'unsafe symlink')
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()),'missing path '+ref); return path
def pinned(root: Path,ref: str,wanted: str)->bytes:
    value=safe(root,ref).read_bytes(); require(digest(value)==wanted,'digest drift '+ref); return value
def decode(value: bytes)->dict[str,Any]:
    result=json.loads(value); require(isinstance(result,dict),'JSON object required'); return result
def keys(value: Any,expected: set[str])->None: require(isinstance(value,dict) and set(value)==expected,'missing/unknown fields')
def pointer(capture: dict[str,Any],ref: str)->str:
    require(ref in {'/text','/source_text','/excerpts/0/text','/sections/6/text'} or ref in {f'/reviews/{i}/finding' for i in range(8)},'invalid source pointer')
    value: Any=capture; parent=None
    for part in ref[1:].split('/'):
        parent=value; value=value[int(part)] if isinstance(value,list) else value.get(part) if isinstance(value,dict) else None
    require(isinstance(value,str) and value.strip(),'missing selected source text')
    if isinstance(parent,dict) and ref.endswith('/text') and 'text_sha256' in parent:
        require(parent['text_sha256']==digest(value.encode()),'selected source text hash drift')
    return value

def predecessor(root: Path,baseline: dict[str,Any],old: dict[str,bytes])->None:
    terms=module('current_host_terms_binding')
    # Terms has no overlay parameter. This private module instance retains its
    # complete projector while passing the two frozen page bytes through its
    # existing clarification/authority predecessor gate.
    def validate_prior(r: Path,model: dict[str,Any],old_workload: bytes)->None:
        authority=module('current_host_authority_scan'); clarification=module('current_host_clarification')
        clarification.validate_model(model,r,lambda rr,phase43: authority.validate_model(phase43,rr,{**old,terms.SOURCE:old_workload}))
    terms.predecessor=validate_prior
    terms.validate_model(baseline,root)

def correction(sources: list[dict[str,Any]])->dict[str,str]:
    return {'id':MARKER,'scope':'Eight exact Tax Guide, Workload Policy and Datacenter source/advice corrections',
        'history':'The complete Terms predecessor is hash-pinned and validated with the exact frozen Tax Guide and Datacenter bytes. Original wording, failures and all previous evidence remain available.',
        'current':'8 bounded claim transitions; 2 exact source transitions: '+ '; '.join(s['path']+' '+s['before_sha256']+' → '+s['after_sha256'] for s in sources)+'.',
        'reason':'Contextual advice, existing Agreement rule and published program scope only; no tax determination, runtime outcome, certification, procedure completion or human acceptance is inferred.'}

def project(root: Path)->dict[str,Any]:
    root=root.resolve(); registry=decode(pinned(root,REGISTRY,REGISTRY_SHA256))
    keys(registry,{'schema_version','record_type','generated_at','baseline','sources','artifacts','retained_raw_sources','transitions'})
    require(registry['schema_version']=='1.0' and registry['record_type']=='HOST_JURISDICTION_TRANSITION','wrong registry type')
    require(registry['baseline']=={'path':BASELINE,'sha256':BASELINE_SHA256},'baseline substitution')
    old={}; current={}; edited={}
    for source in registry['sources']:
        keys(source,{'path','before_sha256','after_sha256','before_artifact','changed_lines'}); ref=source['path']
        require(ref in SOURCES and ref not in old and set(source['changed_lines'])==SOURCES[ref],'out-of-scope source')
        keys(source['before_artifact'],{'path','sha256'})
        old[ref]=pinned(root,source['before_artifact']['path'],source['before_artifact']['sha256'])
        require(digest(old[ref])==source['before_sha256'],'before source mismatch')
        current[ref]=pinned(root,ref,source['after_sha256'])
        left=old[ref].decode().splitlines(); right=current[ref].decode().splitlines()
        require(len(left)==len(right),'source line count changed')
        edited[ref]={i+1 for i,(a,b) in enumerate(zip(left,right)) if a!=b}
        require(edited[ref]==SOURCES[ref],'source edits exceed exact approved lines')
    require(set(old)==set(SOURCES),'two source transitions required')
    baseline=decode(pinned(root,BASELINE,BASELINE_SHA256)); predecessor(root,baseline,old)
    artifacts={}
    for artifact in registry['artifacts']:
        keys(artifact,{'id','path','sha256','kind','origin','source_label'}); aid=artifact['id']
        require(aid not in artifacts and artifact['path'].startswith('verification/evidence/'),'invalid artifact')
        capture=decode(pinned(root,artifact['path'],artifact['sha256'])); artifacts[aid]=(artifact,capture)
        if artifact['kind']=='CONTEXT_REVIEW':
            require(aid=='context-review' and capture['record_type']=='CONTEXTUAL_SOURCE_AND_ADVICE_REVIEW','invalid contextual review')
        else:
            require(capture.get('url')==artifact['origin'].get('url'),'capture origin drift')
            if 'body' in capture:
                require(capture.get('response_status')==200 and digest(capture['body'].encode())==capture.get('body_sha256') and digest(capture['text'].encode())==capture.get('text_sha256'),'public capture response/hash drift')
            elif 'source_text' in capture:
                require(digest(capture['source_text'].encode())==capture.get('source_text_sha256'),'provider/publication text hash drift')
                if capture.get('raw_artifact_ref'): pinned(root,capture['raw_artifact_ref'],capture['raw_artifact_sha256'])
            else:
                require(aid=='agreement' and capture['url']=='https://cloud.vast.ai/host/agreement','unsupported capture')
    for item in registry['retained_raw_sources']: pinned(root,item['path'],item['sha256'])
    before={c['id']:c for p in baseline['pages'] for c in p['claims']}; result=copy.deepcopy(baseline)
    after={c['id']:c for p in result['pages'] for c in p['claims']}; seen=set()
    review=artifacts['context-review'][1]; require(len(review['reviews'])==8,'eight contextual reviews required')
    for entry in registry['transitions']:
        keys(entry,{'claim_id','before_sha256','after','basis','review_rationale','limits'}); cid=entry['claim_id']
        require(cid in IDS and cid not in seen and entry['before_sha256']==objhash(before[cid]),'claim identity/predecessor drift'); seen.add(cid)
        prior=before[cid]; claim=after[cid]; keys(entry['after'],AFTER); claim.update(copy.deepcopy(entry['after']))
        expected_lanes=[STATIC] if cid in TAX else [STATIC,CITE] if cid==WORKLOAD else [CITE]
        classification='REVIEWED_ADVICE' if cid in TAX else 'REVIEWED_ADVICE_WITH_GOVERNING_RULE' if cid==WORKLOAD else 'PUBLISHED_SOURCE_CLAUSE'
        require(claim['status']=='PASS' and claim['classification']==classification and claim['required_evidence_types']==expected_lanes,'invalid bounded classification/status/lanes')
        require(claim['headings']==prior['headings'] and len(claim['spans'])==1,'heading/span scope drift')
        span=claim['spans'][0]; require({k:v for k,v in span.items() if k!='text_sha256'}=={k:v for k,v in prior['spans'][0].items() if k!='text_sha256'},'span location drift')
        ref=span['source_file']; content=current.get(ref) or safe(root,ref).read_bytes(); lines=content.decode().splitlines()
        literal='\n'.join(lines[span['start']-1:span['end']]); require(claim['text']==literal and span['text_sha256']==digest(literal.encode()),'claim literal/span drift')
        if cid==WORKLOAD: require(claim['text']==prior['text'] and claim['spans']==prior['spans'],'Workload wording/citation must remain unchanged')
        rv=next((r for r in review['reviews'] if r['claim_id']==cid),None)
        require(rv and rv['before_claim_sha256']==entry['before_sha256'] and rv['text']==literal and rv['text_sha256']==digest(literal.encode()) and rv['source_sha256']==digest(content) and rv['context'] in content.decode() and rv['headings']==claim['headings'],'contextual review identity drift')
        require(entry['basis'] and entry['review_rationale']==rv['finding'] and entry['limits']==rv['limits'],'missing contextual rationale/limits')
        basis_lanes=set()
        for basis in entry['basis']:
            keys(basis,{'artifact_id','lane','text_pointer','excerpt','source_locator','support_rationale'})
            artifact,capture=artifacts[basis['artifact_id']]; basis_lanes.add(basis['lane'])
            require(basis['excerpt'] and basis['excerpt'] in pointer(capture,basis['text_pointer']) and basis['support_rationale'],'source excerpt absent')
            require(basis['lane']==(STATIC if artifact['kind']=='CONTEXT_REVIEW' else CITE),'invalid source basis lane')
            require(any(r['artifact_ref']==artifact['path'] for r in claim['evidence_refs']),'missing basis evidence reference')
            if basis['lane']==CITE:
                require(any(r=={'repository':'official-publication','revision':'sha256:'+artifact['sha256'],'path':artifact['origin']['url'],'locator':basis['text_pointer'],'source_kind':CITE} for r in claim['source_refs']),'missing exact independent source reference')
        require(set(expected_lanes)<=basis_lanes,'required review/source basis missing')
        require(all(ref in claim['evidence_refs'] for ref in prior['evidence_refs']) and all(ref in claim['source_refs'] for ref in prior['source_refs']),'prior evidence/source dropped')
        claim['history']={**prior['history'],'carry_decision':DECISION,'reason':prior['history'].get('reason','')+HISTORY_REASON}; claim['coverage_state']='CHANGED'
    require(seen==IDS,'eight exact transitions required')
    for page in result['pages']:
        ref=page['source_file']
        if ref not in current: continue
        page['source_sha256']=digest(current[ref]); page['coverage_state']='CHANGED'
        for claim in page['claims']:
            if claim['id'] not in seen:
                require(not any(edited[ref]&set(range(s['start'],s['end']+1)) for s in claim['spans']),'unrelated claim crosses source edit')
        for procedure in page['procedures']:
            for node in [procedure,*procedure['nodes']]:
                if any(edited[ref]&set(range(s['start'],s['end']+1)) for s in node.get('spans',[])):
                    node['spans']=[]; node['status']='STALE'; node['coverage_state']='CHANGED'; node['limits']=[*node.get('limits',[]),NODE_LIMIT]; node['history']={**node.get('history',{}),'carry_decision':DECISION+'_SOURCE_CHANGED'}
    for source in result['source']['source_manifest']:
        if source['path'] in current: source['sha256']=digest(current[source['path']])
    require(sum(before[cid]==after[cid] for cid in before)==2005,'unrelated claim drift')
    result['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in after.values()).items()))
    result['generated_at']=registry['generated_at']; result['corrections'].append(correction(registry['sources'])); return result

def validate_model(model: dict[str,Any],root: Path)->None: require(model==project(root),'whole model differs from jurisdiction projection')
def load_jurisdiction(root: Path,model: dict[str,Any])->dict[str,Any]|None:
    present=(root/REGISTRY).is_file(); marked=any(c.get('id')==MARKER for c in model.get('corrections',[]))
    if not present:
        require(not marked,'jurisdiction-marked model has no registry'); return None
    validate_model(model,root); return {'registry':decode(pinned(root,REGISTRY,REGISTRY_SHA256)),'registry_sha256':REGISTRY_SHA256}
