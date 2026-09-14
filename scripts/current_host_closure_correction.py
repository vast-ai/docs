#!/usr/bin/env python3
"""One sealed, bounded closure successor. Source evidence is not runtime proof."""
from __future__ import annotations
import copy, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path

REGISTRY = 'verification/current-host-closure-correction.json'
REGISTRY_SHA256 = 'b42dc3ed5dde29a2c7dc9031acb1803837b50298686e0ccaad4e6a77bd420945'
ATTEMPT = 'verification/evidence/2026-09-14-host-closure-correction-attempt-01'
MARKER = 'HOST-CLOSURE-CORRECTION-01'
BASELINE = ATTEMPT + '/pre-correction-model.json'
BASELINE_SHA256 = '56650fad892d1f1d387dd4328bdb474f7c2c923907419a2b74868c4a68b7daf5'
CORRECTED = {'CUR-a991f28f683ba829','CUR-93f089288e67669d','MCL-b61d15c0282ef567','MCL-c59caa4cd52bcc1f','MCL-af1c482a08b09316','MCL-393941d0e9be9d31','MCL-57133525f112013a','MCL-dcb653ae3a927dae','MCL-47b85b40f58091a2','MCL-ae7f4423cef61511'}
RENTAL = {'MCL-470bf8ec992a342e','MCL-b7440bdb3eb40fa1','MCL-9cfc73236e4c395a','MCL-250a0c0aa31550a1','MCL-5286ec9ff0cc3272','MCL-6e0046c21ac71be4','MCL-939467a533f82627','MCL-e36ac539565db44a','MCL-c9441dfe43eb92f1'}
ADJACENT = {'MCL-5ab653314f9e68e8','MCL-23085b459da844bc'}
CORRECTED |= RENTAL
ATTEMPT_02 = 'verification/evidence/2026-09-14-host-closure-correction-attempt-02'
RETIRED = {'MCL-08d534d1cc02eb2c','MCL-4be2159765519977','MCL-b87645b43a9136dd','MCL-d5001953fbd7df0b','MCL-e03564808f65b40b'}
RUNTIME = {'MCL-d2f649ad765ea7bb','MCL-b15c6cfc26e189c2','MCL-115b4938222083ac','MCL-9edeb94eaa736bca','MCL-e6fb82f7e167fdc8','MCL-3aca6b1f291d4d0c','VOL-C31','VOL-C33'}
UPSTREAM = {'CUR-f9aad9428d594b40','MCL-217525688a0854b4','CUR-65ffc3ba1623ad1c','CUR-bf6233f2e53eca43','MCL-9dc3b0e54070a926','MCL-ab00ca89f31d5db1'}
NAVIGATION = {'MCL-0ae9c2fd5ac2ef9a','MCL-9459e18a155808c9'}
IDS = CORRECTED | RUNTIME | UPSTREAM | NAVIGATION | ADJACENT
UNCHANGED_REVIEW = {'MCL-b165e7ceb4cea896','MCL-66dcd03d8d3ac701','MCL-9a580f94561b2775','MCL-3b82e89867c343f8','CUR-86637c5b58be0905','CUR-a0c1b91834ef5f98','CUR-e2bb91ee982dd5b1','CUR-acbd513b75fc99a9','CUR-46851196d475b688','CUR-8b49b48a8f4b55e6','CUR-31030b5f3ede8df7','CUR-47f7eac245b806c6','CUR-fa63eb10bec89134','MCL-b4de2df6a8e20829','MCL-6bcbb0e678b9eb65','MCL-e9e8363bc9d2fc20','MCL-f48f7f89c7355a3f','MCL-14556d751bb3fc5b','MCL-582bf3922775c488','MCL-9006e38f7277157f','MCL-151132b1bb16b498','MCL-33c81159a9587c53','MCL-23baa90e841cbe43','MCL-e5ac633b4cd16181'}
UNCHANGED_HELD = {'CUR-d4f1da8861e06594','CUR-6a6640ac777aa39c'}
UNCHANGED_ATTEMPT = 'verification/evidence/2026-09-14-host-unvalidated-source-attempt-01'
UNCHANGED_INVENTORY = UNCHANGED_ATTEMPT + '/inventory.json'
UNCHANGED_INVENTORY_SHA256 = 'fd7d453317ec6aebea68701e49e55fb93337134beb3095d42923d6c3855ec783'
EVIDENCE_ATTEMPT = 'verification/evidence/2026-09-14-host-unvalidated-evidence-attempt-02'
EVIDENCE_INVENTORY_SHA256 = '588d6d4f9776764c32e2ab3d93fa00956dc5a209006a4a88cbe1e302a20d301a'
EVIDENCE_SCOPE_SHA256 = 'd0cea0452b048b78b76c1b01d70fbe8a9cdecd3898d020df307df1e369b26fc6'
EVIDENCE_REVIEW = {'MCL-9e63dfa32acf8aad', 'CUR-64fa2d17e93746a5', 'CUR-0bad472a0b9106e0', 'MCL-37eacf61109c9393', 'MCL-5f07229056d10052', 'MCL-720d258a01fceff8', 'MCL-c36fc6f15087d072', 'MCL-67c1400801647f68', 'CUR-6a6640ac777aa39c', 'MCL-0d219848df6db3d4', 'MCL-0eaf940e59130dcc', 'MCL-2713359efabc2462', 'MCL-f0a3f4f3f551bac6', 'MCL-9a0af54ea0f29f6a', 'MCL-02551a51955f4134', 'MCL-3001d315efd6d799', 'MCL-5b8305045e67acdd', 'MCL-bcd6a81f46a051c6', 'MCL-eb966558ff3e0a48', 'CUR-2faec90d5784d0e6', 'MCL-f42cc0abe33f4df9', 'MCL-1153ad469e9e9fc6', 'CUR-d4f1da8861e06594'}
EVIDENCE_CORRECTED = {'CUR-d4f1da8861e06594', 'MCL-9a0af54ea0f29f6a', 'CUR-6a6640ac777aa39c'}
EVIDENCE_STALE = {'CUR-self-test-reference-ORDERED-SECTIONS','CUR-self-test-reference-H04','FLT-E02-B01-S02'}
IDS |= UNCHANGED_REVIEW | EVIDENCE_REVIEW
STALE = 'Closure source changed; retained procedure evidence does not transfer to changed steps.'
def sha(value): return hashlib.sha256(value).hexdigest()
def canon(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def objhash(value): return sha(canon(value).encode())
def req(value, message):
    if not value: raise ValueError('host closure correction: ' + message)
def safe(root, ref):
    req(isinstance(ref,str) and ref and not ref.startswith('/') and '\\' not in ref and all(p not in {'','.','..'} for p in ref.split('/')), 'unsafe path')
    path=root.resolve()
    for part in ref.split('/'):
        path/=part; req(not path.is_symlink(),'unsafe symlink')
    req(path.is_file() and path.resolve().is_relative_to(root.resolve()),'missing path '+ref)
    return path

def pin(root, ref, wanted):
    value=safe(root,ref).read_bytes();req(sha(value)==wanted,'digest drift '+ref);return value

def selection(raw, pointer):
    req(isinstance(pointer,str) and pointer.startswith('/'),'invalid source selector')
    if pointer.startswith('/lines/'):
        first,last=map(int,pointer[7:].split('-'));lines=raw.decode().splitlines()
        req(0<first<=last<=len(lines),'invalid source line range')
        return '\n'.join(lines[first-1:last])
    value=json.loads(raw)
    for part in pointer[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value if isinstance(value,str) else canon(value)

def index(model): return {c['id']:c for p in model['pages'] for c in p['claims']}

def project(root: Path):
    root=root.resolve();registry=json.loads(pin(root,REGISTRY,REGISTRY_SHA256))
    req(set(registry)=={'schema_version','record_type','generated_at','baseline','sources','artifacts','transitions','retirements','original_findings','limits'},'registry keys')
    req(registry['schema_version']=='1.0' and registry['record_type']=='HOST_CLOSURE_CORRECTION','registry type')
    req(registry['baseline']=={'path':BASELINE,'sha256':BASELINE_SHA256},'baseline substitution')
    baseline=json.loads(pin(root,BASELINE,BASELINE_SHA256));old=index(baseline)
    evidence_inventory=json.loads(pin(root,EVIDENCE_ATTEMPT+'/inventory.json',EVIDENCE_INVENTORY_SHA256))
    evidence_scope=json.loads(pin(root,EVIDENCE_ATTEMPT+'/integration-scope.json',EVIDENCE_SCOPE_SHA256))
    req(set(evidence_scope['accepted_ids'])==EVIDENCE_REVIEW and set(evidence_scope['corrected_ids'])==EVIDENCE_CORRECTED and set(evidence_scope['decisions'])==EVIDENCE_REVIEW,'evidence review inventory')
    req(set(evidence_scope['candidate_ids'])==set(evidence_inventory['scope_claim_ids']) and len(evidence_inventory['claims'])==23,'frozen evidence inventory')
    evidence_prior={item['claim']['id']:item['claim'] for item in evidence_inventory['claims']}
    req(all(old[cid]==claim for cid,claim in evidence_prior.items()),'evidence review predecessor')
    evidence_before={}
    for source in evidence_scope['before_sources']:
        ref=source['path'];req(ref in {'host/fleet-operations.mdx','host/self-test-reference.mdx'} and ref not in evidence_before,'evidence source scope')
        req(source['before_artifact']['path']==EVIDENCE_ATTEMPT+'/sources-before/'+ref,'evidence source snapshot path')
        evidence_before[ref]=pin(root,source['before_artifact']['path'],source['before_artifact']['sha256'])
        pin(root,ref,source['after_sha256'])
    req(set(evidence_before)=={'host/fleet-operations.mdx','host/self-test-reference.mdx'},'evidence source inventory')
    for ref,wanted in evidence_inventory['all_baseline_page_hashes'].items():
        req(sha(evidence_before[ref])==wanted,'evidence frozen source drift') if ref in evidence_before else pin(root,ref,wanted)
    inventory=json.loads(pin(root,UNCHANGED_INVENTORY,UNCHANGED_INVENTORY_SHA256))
    req(set(inventory['accepted_ids'])==UNCHANGED_REVIEW and set(inventory['held_ids'])==UNCHANGED_HELD and len(inventory['candidates'])==26,'unchanged review inventory')
    req(all(item['original_claim']==old[item['claim_id']] and objhash(item['original_claim'])==item['original_claim_sha256'] for item in inventory['candidates']),'unchanged review predecessor')
    for ref,wanted in inventory['customer_mdx_sha256'].items():
        req(sha(evidence_before[ref])==wanted,'unchanged review frozen source drift') if ref in evidence_before else pin(root,ref,wanted)
    req(len(old)==2013 and len(registry['transitions'])==len(IDS) and {x['claim_id'] for x in registry['transitions']}==IDS,'transition inventory')
    req(len(registry['retirements'])==5 and {x['claim_id'] for x in registry['retirements']}==RETIRED,'retirement inventory')
    findings={x['claim_id']:x for x in registry['original_findings']}
    req(len(registry['original_findings'])==26 and set(findings)=={cid for cid,c in old.items() if c['status']=='FAIL'},'original finding inventory')
    req({cid for cid,f in findings.items() if f['disposition']=='CORRECT_NOW'}==CORRECTED|RETIRED,'correction decision scope')
    before={};current={};maps={};after_hashes={}
    for source in registry['sources']:
        ref=source['path'];req(ref.startswith('host/') and ref not in before,'source scope')
        req(source['before_artifact']['path']==(EVIDENCE_ATTEMPT if ref=='host/fleet-operations.mdx' else ATTEMPT_02 if ref in {'host/glossary.mdx','host/maintenance-windows.mdx','host/hosting-agreement.mdx'} else ATTEMPT)+'/sources-before/'+ref,'source snapshot path')
        before[ref]=pin(root,source['before_artifact']['path'],source['before_artifact']['sha256']);current[ref]=pin(root,ref,source['after_sha256']);after_hashes[ref]=sha(current[ref])
        oldlines,newlines=before[ref].decode().splitlines(),current[ref].decode().splitlines()
        maps[ref]=dict(source['line_map']);req(len(maps[ref])==len(source['line_map']) and len(set(maps[ref].values()))==len(maps[ref]),'duplicate line map')
        req(list(maps[ref])==sorted(maps[ref]) and list(maps[ref].values())==sorted(maps[ref].values()),'unordered line map')
        for a,b in maps[ref].items():req(0<a<=len(oldlines) and 0<b<=len(newlines) and oldlines[a-1]==newlines[b-1],'source relocation drift')
        oldchanged={n for e in source['edits'] for n in range(e['before_start'],e['before_end']+1)};newchanged={n for e in source['edits'] for n in range(e['after_start'],e['after_end']+1)}
        req(set(maps[ref]).isdisjoint(oldchanged) and set(maps[ref])|oldchanged==set(range(1,len(oldlines)+1)),'before line partition')
        req(set(maps[ref].values()).isdisjoint(newchanged) and set(maps[ref].values())|newchanged==set(range(1,len(newlines)+1)),'after line partition')
    spec=importlib.util.spec_from_file_location('closure_invoice_predecessor',Path(__file__).with_name('current_host_payout_invoice_correction.py'));pre=importlib.util.module_from_spec(spec);spec.loader.exec_module(pre)
    req(pre.project(root,frozen_source_overrides=before)==baseline,'complete sealed predecessor differs from frozen baseline')
    artifacts={a['path']:pin(root,a['path'],a['sha256']) for a in registry['artifacts']};req(len(artifacts)==len(registry['artifacts']),'duplicate artifact')
    def relocate(span):
        ref=span['source_file']
        if ref not in maps:return copy.deepcopy(span)
        values=[maps[ref].get(i) for i in range(span['start'],span['end']+1)]
        if None in values or values!=list(range(values[0],values[-1]+1)):return None
        return {**span,'start':values[0],'end':values[-1]}
    def verify_span(span):
        ref=span['source_file'];raw=current.get(ref) or safe(root,ref).read_bytes();lines=raw.decode().splitlines()
        req(0<span['start']<=span['end']<=len(lines),'claim span bounds')
        text='\n'.join(lines[span['start']-1:span['end']]);req(sha(text.encode())==span['text_sha256'],'claim span hash drift');return text
    out=copy.deepcopy(baseline);claims=index(out)
    for entry in registry['transitions']:
        cid=entry['claim_id'];prior=old[cid];req(objhash(prior)==entry['before_sha256'],'claim predecessor '+cid)
        patch=entry['after'];req(set(patch)<= {'text','spans','status','classification','required_evidence_types','owner_role','rationale','next_action','evidence_refs','source_refs','coverage_state'},'unsupported claim patch')
        if cid in UNCHANGED_REVIEW:
            req(prior['status']=='UNVALIDATED' and patch['status']=='PASS' and 'spans' not in patch and all(patch[k]==prior[k] for k in ['text','classification','required_evidence_types','owner_role']),'unchanged review scope')
        if cid in EVIDENCE_REVIEW:
            decision=evidence_scope['decisions'][cid]
            req(prior==evidence_prior[cid] and prior['status']=='UNVALIDATED' and patch['status']==decision['expected_status'] and patch['text']==decision['expected_text'],'evidence review disposition')
            req(all(patch[k]==prior[k] for k in ['classification','required_evidence_types','owner_role']),'evidence review method drift')
            req(all(e in patch['evidence_refs'] for e in prior['evidence_refs']) and all(e in patch['source_refs'] for e in prior['source_refs']),'evidence review discarded history')
            req((cid in EVIDENCE_CORRECTED)==('spans' in patch) and (cid in EVIDENCE_CORRECTED)==(patch['text']!=prior['text']),'evidence review literal scope')
        if cid in RUNTIME:req(patch['text']==prior['text'] and patch['status']==('UNVALIDATED' if cid.startswith('VOL-') else prior['status']),'runtime promotion forbidden')
        for basis in entry['basis']:
            req(basis['artifactRef'] in artifacts and selection(artifacts[basis['artifactRef']],basis['text_pointer'])==basis['excerpt'],'source selector/excerpt drift '+cid)
            req(basis['support_rationale'] and any(e['artifact_ref']==basis['artifactRef'] for e in patch['evidence_refs']),'unbound scoped evidence')
            if cid in UNCHANGED_REVIEW|EVIDENCE_REVIEW:req(any(ref['path']==(basis['sourceUrl'] or basis['artifactRef']) and ref['locator']==basis['text_pointer'] for ref in patch['source_refs']),'unchanged review canonical binding')
            if cid in EVIDENCE_REVIEW and basis['artifactRef']==EVIDENCE_ATTEMPT+'/source-static/selectors.json':
                selected=selection(artifacts[basis['artifactRef']],basis['text_pointer'].rsplit('/',1)[0])
                req(json.loads(selected)['canonical_url']==basis['sourceUrl'],'selected source canonical URL drift')
            if basis['text_pointer'].startswith('/observations/'):
                observation=json.loads(artifacts[basis['artifactRef']])['observations'][int(basis['text_pointer'].split('/')[2])]
                if isinstance(observation,dict) and observation.get('url'):
                    req(basis['sourceUrl']==observation['url'] and any(ref['path']==observation['url'] and ref['locator']==basis['text_pointer'] for ref in patch['source_refs']),'selected observation canonical URL drift '+cid)
        claims[cid].update(copy.deepcopy(patch));claims[cid]['history']={**prior.get('history',{}),'carry_decision':'CURRENT_HOST_CLOSURE_CORRECTION','reason':prior.get('history',{}).get('reason','')+' '+entry['limits'],'predecessor':{'claim_id':cid,'status':prior['status'],'text':prior['text'],'text_sha256':sha(prior['text'].encode())}}
    for retired in registry['retirements']:
        cid=retired['claim_id'];req(retired['before_sha256']==objhash(old[cid]) and retired['replaced_by']=='MCL-0ae9c2fd5ac2ef9a','retirement predecessor')
    claims['MCL-0ae9c2fd5ac2ef9a']['history']['superseded_claims']=[{'claim':copy.deepcopy(old[x['claim_id']]),'reason':x['reason']} for x in registry['retirements']]
    entries={x['claim_id']:x for x in registry['transitions']}
    for page in out['pages']:
        page['claims']=[c for c in page['claims'] if c['id'] not in RETIRED]
        if page['source_file'] in after_hashes:page['source_sha256']=after_hashes[page['source_file']];page['coverage_state']='CHANGED'
        for dep in page['dependencies']:
            if dep['source_file'] in after_hashes:dep['source_sha256']=after_hashes[dep['source_file']];page['coverage_state']='CHANGED'
        for claim in page['claims']:
            cid=claim['id']
            if 'spans' not in entries.get(cid,{}).get('after',{}):
                claim['spans']=[relocate(s) for s in old[cid]['spans']];req(None not in claim['spans'],'unreviewed changed occurrence '+cid)
            literal='\n'.join(verify_span(s) for s in claim['spans'])
            if claim['text']!=old[cid]['text']:req(literal==claim['text'],'changed literal mismatch '+cid)
            if cid not in IDS:req({k:v for k,v in claim.items() if k!='spans'}=={k:v for k,v in old[cid].items() if k!='spans'},'unrelated claim drift '+cid)
        for procedure in page['procedures']:
            for node in [procedure,*procedure['nodes']]:
                relocated=[relocate(s) for s in node.get('spans',[])]
                if None in relocated:
                    node['spans']=[];node['status']='STALE';node['coverage_state']='CHANGED';node['limits']=[*node.get('limits',[]),STALE];node['history']={**node.get('history',{}),'carry_decision':'CURRENT_HOST_CLOSURE_SOURCE_CHANGED'}
                else:node['spans']=relocated
    for item in out['source']['source_manifest']:
        if item['path'] in after_hashes:item['sha256']=after_hashes[item['path']]
    remaining=index(out);req(set(remaining)==set(old)-RETIRED and len(remaining)==2008,'active inventory drift')
    for cid,f in findings.items():
        if f['disposition']!='CORRECT_NOW':req(remaining[cid]==old[cid],'unresolved stronger assertion changed '+cid)
    req(set(remaining)==set(inventory['all_current_claim_hashes']) and all(objhash(c)==inventory['all_current_claim_hashes'][cid] for cid,c in remaining.items() if cid not in UNCHANGED_REVIEW|EVIDENCE_REVIEW),'unrelated current claim changed')
    req(set(remaining)==set(evidence_inventory['all_baseline_claim_hashes']) and all(objhash(c)==evidence_inventory['all_baseline_claim_hashes'][cid] for cid,c in remaining.items() if cid not in EVIDENCE_REVIEW),'unrelated evidence-batch claim changed')
    original_nodes={item['id']:item['before'] for item in evidence_scope['affected_procedures']}
    req(set(original_nodes)==EVIDENCE_STALE,'affected procedure inventory')
    historical_procedures=copy.deepcopy([p['procedures'] for p in out['pages']]);seen=set()
    for procedures in historical_procedures:
        for procedure in procedures:
            for node in [procedure,*procedure['nodes']]:
                if node['id'] in original_nodes:
                    prior=original_nodes[node['id']];expected={**prior,'spans':[],'status':'STALE','coverage_state':'CHANGED','limits':[*prior.get('limits',[]),STALE],'history':{**prior.get('history',{}),'carry_decision':'CURRENT_HOST_CLOSURE_SOURCE_CHANGED'}}
                    req({k:v for k,v in node.items() if k!='nodes'}==expected,'affected procedure drift')
                    children=node.get('nodes');node.clear();node.update(copy.deepcopy(prior))
                    if children is not None:node['nodes']=children
                    seen.add(node['id'])
    req(seen==EVIDENCE_STALE and objhash(historical_procedures)==inventory['procedures_sha256']==evidence_inventory['procedure_population_sha256'],'evidence review procedure drift')
    expected_manifest=copy.deepcopy(inventory['source_manifest'])
    for item in expected_manifest:
        if item['path'] in evidence_before:item['sha256']=after_hashes[item['path']]
    req(out['source']['source_manifest']==expected_manifest,'evidence review source manifest drift')
    owners=json.loads(safe(root,'verification/current-host-owner-questions.json').read_bytes());owners.pop('model_sha256')
    req(objhash(owners)==inventory['owner_questions_without_model_hash_sha256'],'unchanged review owner question drift')
    out['counts']['claims']=len(remaining);out['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in remaining.values()).items()));out['counts']['page_coverage_states']=dict(sorted(Counter(p['coverage_state'] for p in out['pages']).items()))
    out['generated_at']=registry['generated_at'];out['corrections'].append({'id':MARKER,'scope':'24 original findings handled: 19 narrowed corrections and 5 retired checklist clauses; 2 adjacent rental edits; 8 bounded evidence/status reconciliations; upstream PR948 and CON1531 routing; 24 unchanged source/declaration occurrences from a frozen 26-candidate inventory; bounded evidence attempt02 source corrections and retained observations','history':'Complete sealed predecessor replayed against exact frozen source bytes. Five historical FAIL objects remain in the application instruction history and frozen baseline.','current':'Two tax FAIL assertions remain open. Nine original rental FAIL assertions are retained in history after withdrawal from active prose; backend and maintenance owner questions remain open. Partial runtime observations do not promote compound workflows.','reason':registry['limits']})
    return out

def load_closure_correction(root,model):
    present=(root/REGISTRY).is_file();marked=any(x.get('id')==MARKER for x in model.get('corrections',[]))
    if not present:req(not marked,'closure-marked model has no registry');return None
    req(model==project(root),'whole model differs from closure projection');return {'registry':REGISTRY,'registry_sha256':REGISTRY_SHA256}
