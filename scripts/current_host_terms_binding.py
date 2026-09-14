#!/usr/bin/env python3
"""Pinned phase-47 Terms binding after the immutable authority/clarification chain.

This reader permits one reviewed Workload Policy source edit and only the six
hash-bound Terms claim transitions.  Registry and generated-model records are
context, never proof; the retained published Terms capture is the only new
terminal source.
"""
from __future__ import annotations
import copy, difflib, hashlib, importlib.util, json, re
from collections import Counter
from pathlib import Path
from typing import Any

REGISTRY='verification/current-host-terms-binding.json'
REGISTRY_SHA256='36961fcabe5fbd105a67c37ef8918e17e98c78351008f108224114abde77ac38'
ATTEMPT='verification/evidence/2026-09-10-host-terms-binding-attempt-01'
BASELINE=ATTEMPT+'/before-review.json'
BASELINE_SHA256='f4df32dc9fc85a0b31f578cc8481d0305cc7af9d530e110013769ce2ac6cce2b'
SOURCE='host/workload-policy.mdx'
MARKER='HOST-TERMS-BINDING-01'
IDS={'MCL-99ca28f707d5966a','MCL-2c3f7082e2c7fdf2','MCL-c4c4bfc59eb7b49f','MCL-399798a3c4946b5f','MCL-633317ca7ebecfef','MCL-fe3eccd1cd40b4bd'}
LANES={'CANONICAL_IMPLEMENTATION_SOURCE','RUNTIME_OR_UI_OBSERVATION','ACCOUNTABLE_OWNER_CONFIRMATION','AUTHORITATIVE_DOCUMENTATION_CITATION','REPOSITORY_STATIC_CHECK','PRODUCT_PUBLICATION_SOURCE'}
AFTER={'classification','status','required_evidence_types','owner_role','rationale','next_action','text','headings','spans','evidence_refs','source_refs'}

def fail(message: str) -> None: raise ValueError('terms binding: '+message)
def require(value: Any, message: str) -> None:
    if not value: fail(message)
def digest(value: bytes) -> str: return hashlib.sha256(value).hexdigest()
def canonical(value: Any) -> Any:
    if isinstance(value,dict): return {key:canonical(value[key]) for key in sorted(value)}
    if isinstance(value,list): return [canonical(item) for item in value]
    return value
def objhash(value: Any) -> str: return digest(json.dumps(canonical(value),separators=(',',':'),ensure_ascii=False).encode())
def keys(value: Any, required: set[str], optional: set[str]=frozenset(), name='record') -> None:
    require(isinstance(value,dict) and required <= value.keys() and value.keys() <= required|optional,name+' has missing/unknown fields')
def safe(root: Path, ref: str) -> Path:
    require(isinstance(ref,str) and ref and not ref.startswith('/') and '\\' not in ref and all(x not in {'','.','..'} for x in ref.split('/')),'unsafe path')
    path=root.resolve()
    for part in ref.split('/'):
        path/=part; require(not path.is_symlink(),'unsafe path')
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file(),'missing path '+ref); return path
def pinned(root: Path, ref: str, wanted: str) -> bytes:
    require(isinstance(wanted,str) and re.fullmatch('[0-9a-f]{64}',wanted),'invalid pin')
    value=safe(root,ref).read_bytes(); require(digest(value)==wanted,'digest drift '+ref); return value
def json_object(value: bytes, name: str) -> dict[str,Any]:
    try: result=json.loads(value)
    except Exception as error: raise ValueError('terms binding: invalid JSON '+name) from error
    require(isinstance(result,dict),name+' must be object'); return result
def map_lines(before: list[str], after: list[str]) -> dict[int,int]:
    require(len(before)==len(after),'Terms source edit must preserve line count')
    return {index+1:index+1 for index,(left,right) in enumerate(zip(before,after)) if left==right}
def relocate(span: dict[str,Any], mapping: dict[int,int], after: list[str]) -> dict[str,Any]|None:
    start,end=span['start'],span['end']; values=[mapping.get(line) for line in range(start,end+1)]
    if None in values or values!=list(range(values[0],values[-1]+1)): return None
    result={**span,'start':values[0],'end':values[-1]}; text='\n'.join(after[result['start']-1:result['end']])
    require(digest(text.encode())==result['text_sha256'],'relocated span text drift'); return result
def module(name: str):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py')); result=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(result); return result

def predecessor(root: Path, baseline: dict[str,Any], old_source: bytes) -> None:
    authority=module('current_host_authority_scan'); clarification=module('current_host_clarification')
    clarification.validate_model(baseline,root,lambda r,phase43: authority.validate_model(phase43,r,{SOURCE:old_source}))

def source_text(artifact: dict[str,Any], pointer: str) -> str:
    value: Any=json_object(artifact['_bytes'],artifact['path'])
    require(isinstance(pointer,str) and re.fullmatch(r'/sections/[01]/(?:text|items/[0-8]/text)',pointer),'invalid Terms source pointer')
    parent: Any=None
    for part in pointer[1:].split('/'):
        parent=value
        value=value[int(part)] if isinstance(value,list) and part.isdecimal() else value.get(part) if isinstance(value,dict) else None
    require(isinstance(value,str) and value.strip(),'Terms pointer missing text')
    # Whole-capture hashing pins the introductory clause; selected section/item
    # objects add their own text hash where the retained capture exposes one.
    require(not isinstance(parent,dict) or 'text_sha256' not in parent or parent['text_sha256']==digest(value.encode()),'Terms pointer hash mismatch')
    return value

def project(root: Path) -> dict[str,Any]:
    root=root.resolve(); registry=json_object(pinned(root,REGISTRY,REGISTRY_SHA256),REGISTRY)
    keys(registry,{'schema_version','record_type','generated_at','baseline','source','artifacts','transitions'},name='registry')
    require(registry['schema_version']=='1.0' and registry['record_type']=='HOST_TERMS_BINDING_TRANSITION','wrong registry type')
    require(registry['baseline']=={'path':BASELINE,'sha256':BASELINE_SHA256},'baseline substitution')
    keys(registry['source'],{'path','before_sha256','after_sha256','before_artifact'},name='source transition'); source=registry['source']
    require(source['path']==SOURCE,'only Workload Policy may change'); keys(source['before_artifact'],{'path','sha256'},name='before source')
    old=pinned(root,source['before_artifact']['path'],source['before_artifact']['sha256']); require(digest(old)==source['before_sha256'],'before source mismatch')
    current=pinned(root,SOURCE,source['after_sha256'])
    baseline=json_object(pinned(root,BASELINE,BASELINE_SHA256),BASELINE); predecessor(root,baseline,old)
    artifacts={}
    for item in registry['artifacts']:
        keys(item,{'id','path','sha256','kind','origin'},name='artifact'); require(item['id'] not in artifacts and item['kind']=='GOVERNING_SOURCE','invalid/duplicate Terms artifact')
        require(not item['path'].startswith(('verification/current-','graphify-out/','.orchestra/')),'derived artifact is not Terms proof')
        artifacts[item['id']]={**item,'_bytes':pinned(root,item['path'],item['sha256'])}
    require(artifacts, 'Terms source artifact required')
    for artifact in artifacts.values():
        capture=json_object(artifact['_bytes'],artifact['path'])
        require(capture.get('url')=='https://vast.ai/terms' and capture.get('version')=='Version Date: November 10, 2025', 'Terms capture URL/version drift')
        require(capture.get('response_status')==200, 'Terms capture is not a successful published response')
    before_claims={claim['id']:claim for page in baseline['pages'] for claim in page['claims']}; entries={}
    for item in registry['transitions']:
        keys(item,{'claim_id','before_sha256','after','basis','review_rationale'},name='claim transition'); cid=item['claim_id']
        require(cid in IDS and cid not in entries and item['before_sha256']==objhash(before_claims[cid]),'unknown/duplicate/predecessor-drift claim')
        require(isinstance(item['review_rationale'],str) and item['review_rationale'].strip() and isinstance(item['after'],dict) and item['after'] and set(item['after'])<=AFTER,'invalid claim transition')
        entries[cid]=item
    require(set(entries)==IDS,'six Terms transitions required')
    result=copy.deepcopy(baseline); before_lines=old.decode().splitlines(); after_lines=current.decode().splitlines(); mapping=map_lines(before_lines,after_lines)
    page=next((p for p in result['pages'] if p['source_file']==SOURCE),None); require(page is not None,'Workload Policy page missing')
    page['source_sha256']=digest(current); page['coverage_state']='CHANGED'
    for manifest in result['source']['source_manifest']:
        if manifest['path']==SOURCE: manifest['sha256']=digest(current)
    covered=set()
    for claim in page['claims']:
        prior=before_claims[claim['id']]; rel=[relocate(span,mapping,after_lines) for span in prior['spans']]
        if claim['id'] in entries:
            entry=entries[claim['id']]; claim.update(copy.deepcopy(entry['after'])); require(claim['status'] in {'PASS','FAIL','UNVALIDATED'} and set(claim['required_evidence_types'])<=LANES,'invalid Terms status/lanes')
            require('spans' in entry['after'] and claim['text']=='\n'.join('\n'.join(after_lines[s['start']-1:s['end']]) for s in claim['spans']),'Terms literal/spans mismatch')
            for span in claim['spans']:
                require(isinstance(span,dict) and span.get('source_file')==SOURCE and isinstance(span.get('start'),int) and isinstance(span.get('end'),int) and 0<span['start']<=span['end']<=len(after_lines),'invalid Terms claim span')
                require(digest('\n'.join(after_lines[span['start']-1:span['end']]).encode())==span.get('text_sha256'),'Terms claim span hash drift')
            require(isinstance(entry['basis'],list) and entry['basis'],'Terms citation basis required')
            for basis in entry['basis']:
                keys(basis,{'artifact_id','lane','text_pointer','excerpt','support_rationale'},name='Terms basis'); artifact=artifacts.get(basis['artifact_id']); require(artifact and basis['lane']=='AUTHORITATIVE_DOCUMENTATION_CITATION','invalid Terms basis lane')
                require(isinstance(basis['excerpt'],str) and basis['excerpt'].strip() in source_text(artifact,basis['text_pointer']),'Terms excerpt absent from retained source')
                require(artifact['origin']=={'url':'https://vast.ai/terms'},'Terms origin must be canonical published URL')
            require(all(ref in claim.get('evidence_refs',[]) for ref in prior.get('evidence_refs',[])), 'Terms transition dropped prior evidence')
            require(all(ref in claim.get('source_refs',[]) for ref in prior.get('source_refs',[])), 'Terms transition dropped prior sources')
            terms_paths={artifact['path'] for artifact in artifacts.values()}
            require(any(ref.get('artifact_ref') in terms_paths for ref in claim.get('evidence_refs',[])), 'Terms transition lacks retained Terms evidence ref')
            require(any(ref.get('path')=='https://vast.ai/terms' and ref.get('source_kind')=='AUTHORITATIVE_DOCUMENTATION_CITATION' for ref in claim.get('source_refs',[])), 'Terms transition lacks canonical Terms source ref')
            if claim['status']=='PASS': require(claim['required_evidence_types']==['AUTHORITATIVE_DOCUMENTATION_CITATION'],'Terms PASS must be narrow cited-rule only')
            claim['history']={**prior['history'],'carry_decision':'CURRENT_HOST_TERMS_BINDING','reason':str(prior['history'].get('reason',''))+' Exact published Terms binding; no runtime, monitoring, escalation, or acceptance inference.'}; claim['coverage_state']='CHANGED'
        else:
            require(None not in rel,'unpatched Workload Policy occurrence crosses edited source '+claim['id'])
            if rel != prior['spans']:
                claim['spans']=rel; claim['coverage_state']='CHANGED'; claim['history']={**prior['history'],'carry_decision':'CURRENT_HOST_TERMS_BINDING_RELOCATION'}
        for span in claim['spans']: covered.update(range(span['start'],span['end']+1))
    for procedure in page['procedures']:
        for node in [procedure,*procedure['nodes']]:
            rel=[relocate(span,mapping,after_lines) for span in node.get('spans',[])]
            if None in rel:
                node['spans']=[]; node['status']='STALE'; node['coverage_state']='CHANGED'; node['limits']=[*node.get('limits',[]),'Previous procedure span crosses the Terms-bound Workload Policy edit; no procedure evidence transfers.']; node['history']={**node.get('history',{}),'carry_decision':'CURRENT_HOST_TERMS_BINDING_SOURCE_CHANGED'}
            elif rel != node.get('spans',[]): node['spans']=rel; node['coverage_state']='CHANGED'; node['history']={**node.get('history',{}),'carry_decision':'CURRENT_HOST_TERMS_BINDING_RELOCATION'}
    for kind,_a,_b,start,end in difflib.SequenceMatcher(a=before_lines,b=after_lines,autojunk=False).get_opcodes():
        if kind in {'insert','replace'}:
            for number in range(start+1,end+1):
                line=after_lines[number-1].strip(); structural=not line or line=='---' or line.startswith('#') or line.startswith('| ---') or line.startswith('| Category |')
                require(structural or number in covered,'new nonblank Workload Policy source line lacks a claim occurrence')
    claims=[claim for p in result['pages'] for claim in p['claims']]; result['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in claims).items())); result['generated_at']=registry['generated_at']
    result['corrections'].append({'id':MARKER,'scope':'Six Workload Policy Terms bindings after frozen clarification','history':'Phase-43 authority and phase-46 clarification predecessors remain hash-pinned and are validated against the exact frozen Workload Policy bytes.','current':f'{len(entries)} exact Terms claim bindings; one source SHA-256 transition {source["before_sha256"]} → {source["after_sha256"]}.','reason':'Published-rule citations are bounded policy source proof only; no runtime, monitoring, escalation, acceptance, or whole-page inference is authorized.'})
    return result

def validate_model(model: dict[str,Any],root:Path)->None: require(model==project(root),'whole model differs from Terms projection')
def load_terms_binding(root:Path,model:dict[str,Any])->dict[str,Any]|None:
    candidate=root.resolve()/REGISTRY
    present=candidate.is_file() and not candidate.is_symlink()
    marked=any(item.get('id')==MARKER for item in model.get('corrections',[]))
    if not present:
        require(not marked,'Terms-marked model has no registry')
        return None
    validate_model(model,root); return {'registry':json_object(pinned(root,REGISTRY,REGISTRY_SHA256),REGISTRY),'registry_sha256':REGISTRY_SHA256,'baseline':BASELINE,'baseline_sha256':BASELINE_SHA256}
