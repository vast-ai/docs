#!/usr/bin/env python3
"""Sealed continuation successor; replay historical proof before a bounded patch."""
from __future__ import annotations
import copy, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path

REGISTRY = 'verification/current-host-final-owner-review.json'
REGISTRY_SHA256 = '8448d5f3c62abadb06a4ce354be88a38a847c4ece13afde188be7adfef39d1a0'
ATTEMPT = 'verification/evidence/2026-09-15-host-final-owner-reconciliation-attempt-01'
MARKER = 'HOST-FINAL-OWNER-REVIEW-01'
CORRECTION_NEXT_ACTION = 'The accepted wording correction is applied. Recheck this passage if its wording, authoritative source or relevant console changes; retain the recorded evidence limits.'
INVENTORY_SHA256 = '8934a40b9193b3df526ecc6e035a91bb017056377c5ee7adb998e6fb6748eb1f'
SOURCE_NEXT_ACTION = 'The accepted source review is applied. Recheck this passage if its wording, authoritative source or relevant product behavior changes; retain the recorded evidence limits.'
BASELINE_SHA256 = 'b122770ec1771a28699c5da6217d300c1d192f4bb75cbd6d3903b0f5e9fab71a'

def sha(value): return hashlib.sha256(value).hexdigest()
def canon(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def objhash(value): return sha(canon(value).encode())
def req(value, message):
    if not value: raise ValueError('host Final owner review: ' + message)
def prior_module():
    spec=importlib.util.spec_from_file_location('continuation_evidence_reuse_predecessor',Path(__file__).with_name('current_host_hardware_operator_review.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def index(model): return {c['id']:c for p in model['pages'] for c in p['claims']}
def without_nodes(node): return {k:v for k,v in node.items() if k!='nodes'}

def source_origin(raw, pointer, meta):
    """Nearest selected JSON block wins over aggregate record metadata."""
    url=meta.get('url',meta.get('source_url'));revision=meta.get('revision',meta.get('source_revision'));kind=meta.get('source_kind','STATIC_CONTEXT_REVIEW')
    if pointer.startswith('/lines/'):return url,revision,kind
    value=json.loads(raw)
    tokens=pointer[1:].split('/')
    for depth in range(len(tokens)+1):
        if depth and isinstance(value,dict):
            candidate=value.get('url',value.get('source_url'))
            if isinstance(candidate,str) and candidate:url=candidate
            candidate=value.get('revision',value.get('source_revision'))
            if isinstance(candidate,str) and candidate:revision=candidate
            candidate=value.get('source_kind')
            if isinstance(candidate,str) and candidate:kind=candidate
        if depth==len(tokens):break
        token=tokens[depth].replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return url,revision,kind

def project(root: Path, frozen_source_overrides=None):
    root=root.resolve();pre=prior_module();utils=pre.prior_module().prior_module().prior_module().prior_module().prior_module().prior_module().prior_module().prior_module().prior_module()
    frozen_source_overrides = frozen_source_overrides or {}
    def read(ref): return frozen_source_overrides[ref] if ref in frozen_source_overrides else utils.safe(root,ref).read_bytes()
    def pin(ref,wanted):
        raw=read(ref);req(sha(raw)==wanted,'digest drift '+ref);return raw
    registry=json.loads(pin(REGISTRY,REGISTRY_SHA256))
    req(set(registry)=={'schema_version','record_type','generated_at','scope','sources','artifacts','transitions','procedures','limits'},'registry keys')
    req(registry['schema_version']=='1.0' and registry['record_type']=='HOST_FINAL_OWNER_REVIEW','registry type')
    inventory=json.loads(pin(ATTEMPT+'/inventory.json',INVENTORY_SHA256))
    baseline_check=json.loads(pin(ATTEMPT+'/integration-baseline.json',BASELINE_SHA256))
    req(registry['scope']['path']==ATTEMPT+'/integration-scope.json','scope path')
    scope=json.loads(pin(registry['scope']['path'],registry['scope']['sha256']))
    acceptance=json.loads(pin(ATTEMPT+'/integration-acceptance.json',scope['acceptance_sha256']))
    req(acceptance['baseline_model_sha256']==inventory['baseline_model_sha256'] and acceptance['baseline_commit']==inventory['baseline_commit'],'accepted baseline drift')
    req(len(acceptance['lanes'])==2 and {x['lane'] for x in acceptance['lanes']}=={'final','storage_adjacent'},'accepted lane scope')
    req(acceptance['scope_counts']=={'reviewed_passages':11,'adjacent_pass_consistency_records':1,'transitions':12,'newly_resolved':11,'uncounted_context_edits':0},'accepted coverage accounting')
    req(acceptance['resolved_next_action_rule']=={'correction':CORRECTION_NEXT_ACTION,'supported_resolved':SOURCE_NEXT_ACTION,'residual':'Retain exact accepted next_action.'},'next-action normalization rule')
    approved_source=json.loads(pin(ATTEMPT+'/root-source-acceptance.json',acceptance['root_source_acceptance_sha256']))
    seal=json.loads(pin(ATTEMPT+'/final-seal.json',acceptance['final_seal_sha256']))
    req(approved_source['state']=='ACCEPTED_FOR_FINITE_INTEGRATION_IMPACT' and approved_source['baseline_commit']==inventory['baseline_commit'] and approved_source['baseline_model_sha256']==inventory['baseline_model_sha256'],'source approval baseline')
    req(approved_source['final_seal_sha256']==acceptance['final_seal_sha256'] and seal['files']==approved_source['accepted_files'],'accepted seal drift')
    accepted_decisions={};accepted_sources={}
    for lane in acceptance['lanes']:
        lane_root=ATTEMPT+'/'+lane['lane']+'/'
        stem='' if lane['lane']=='final' else 'storage-adjacent/'
        for name,field in [('decisions_file','decisions_sha256'),('sources_file','sources_sha256'),('inventory_file','inventory_sha256')]:
            req(lane[name].endswith('-05.json') and lane[field]==seal['files'][stem+lane[name]],'sealed lane digest');pin(lane_root+lane[name],lane[field])
        data=json.loads(read(lane_root+lane['decisions_file']));sources=json.loads(read(lane_root+lane['sources_file']))['sources']
        req(len(data['decisions'])==lane['count']==(11 if lane['lane']=='final' else 1),'lane count')
        for d in data['decisions']:
            req(d['id'] not in accepted_decisions,'duplicate accepted decision');accepted_decisions[d['id']]=d;accepted_sources[d['id']]=sources
    frozen_claims=inventory['claims'];ids={c['id'] for c in frozen_claims}
    req(len(ids)==12 and len(frozen_claims)==12 and set(scope['decisions'])==set(accepted_decisions)==ids,'frozen decision inventory')
    req(ids==set(approved_source['selected_ids']) and accepted_decisions['VOL-C28']['proposed_status']=='PASS','final scope')
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
    baseline=pre.project(root,frozen_source_overrides={**frozen_source_overrides,**before})
    req(objhash(baseline)==baseline_check['baseline_model_canonical_sha256'],'complete predecessor differs from baseline')
    old=index(baseline)
    req({cid:objhash(c) for cid,c in old.items()}==baseline_check['claim_hashes'],'baseline claim inventory')
    req(objhash([p['procedures'] for p in baseline['pages']])==baseline_check['procedure_population_sha256'],'baseline procedures')
    req(all(old[c['id']]['status']==c['claim']['status'] and sha(old[c['id']]['text'].encode())==c['literal_sha256'] for c in frozen_claims),'frozen literal drift')
    artifacts={a['path']:pin(a['path'],a['sha256']) for a in registry['artifacts']}
    req(len(artifacts)==len(registry['artifacts']),'duplicate artifact')
    approval=scope['impact_acceptance'];req(approval['path']==ATTEMPT+'/root-impact-acceptance.json','impact approval path')
    approved=json.loads(pin(approval['path'],approval['sha256']));req(approved['impact_sha256']==sha(artifacts[ATTEMPT+'/integration-impact.json']) and approved['baseline_model_sha256']==inventory['baseline_model_sha256'],'impact approval drift')
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
    req(len(registry['transitions'])==12 and set(entries)==ids,'transition scope')
    for cid,entry in entries.items():
        prior=old[cid];patch=entry['after'];decision=scope['decisions'][cid];accepted=accepted_decisions[cid]
        req(objhash(accepted)==decision['accepted_decision_sha256'],'accepted decision bytes '+cid)
        expected={'text':accepted.get('replacement_text',accepted.get('proposed_replacement',prior['text'])),'status':accepted['proposed_status'],'classification':accepted['proposed_classification'],'required_evidence_types':accepted['proposed_methods'],'owner_role':accepted.get('proposed_owner_role',prior['owner_role'])}
        req({k:patch[k] for k in expected}==expected,'accepted proposal fields '+cid)
        req(entry['decision']==accepted['decision'] and entry['method_rationale']==accepted['method_rationale'] and entry['limits']==accepted['limitation'],'accepted review scope '+cid)
        req(patch['rationale']==accepted['support_rationale'] and patch['next_action']==(CORRECTION_NEXT_ACTION if accepted['decision']=='correction' else (SOURCE_NEXT_ACTION if accepted['proposed_status'] in ('PASS','NOT_APPLICABLE') else accepted['next_action'])),'accepted review rationale '+cid)
        req(len(entry['basis'])==len(accepted['source_refs']),'accepted source count '+cid)
        for basis,binding in zip(entry['basis'],accepted['source_refs']):
            meta=accepted_sources[cid][binding['source']]
            req(basis['sourceKey']==binding['source'] and basis['artifactRef']==meta.get('artifact_ref',meta.get('path')) and basis['text_pointer']==binding['text_pointer'] and basis['excerpt']==binding['source_excerpt'],'accepted source binding '+cid)
            req(sha(artifacts[basis['artifactRef']])==meta['sha256'],'accepted source hash '+cid)
            req((basis['sourceUrl'],basis['sourceRevision'],basis['sourceKind'])==source_origin(artifacts[basis['artifactRef']],basis['text_pointer'],meta),'accepted source provenance '+cid)
        req(entry['before_sha256']==objhash(prior),'claim predecessor '+cid)
        req(entry.get('residual_topic')==decision.get('residual_topic'),'unaccepted residual topic')
        req(set(patch)<= {'text','spans','status','classification','required_evidence_types','owner_role','rationale','next_action','evidence_refs','source_refs','coverage_state'},'unsupported patch')
        req(objhash({k:patch[k] for k in ['text','status','classification','required_evidence_types','owner_role']})==decision['fields_sha256'],'accepted disposition drift '+cid)
        req(patch['status'] in {'PASS','FAIL','BLOCKED','UNVALIDATED','NOT_APPLICABLE'},'unknown status')
        req(all(e in patch['evidence_refs'] for e in prior['evidence_refs']) and all(s in patch['source_refs'] for s in prior['source_refs']),'discarded prior evidence')
        if patch['required_evidence_types']!=prior['required_evidence_types']:req(entry['method_rationale']==decision['method_rationale'] and bool(entry['method_rationale']),'unjustified method change')
        req(bool(entry['basis']) and bool(entry['limits']) and bool(patch['rationale']),'missing scoped review')
        for basis in entry['basis']:
            ref=basis['artifactRef'];req(ref in artifacts and utils.selection(artifacts[ref],basis['text_pointer'])==basis['excerpt'],'source selector/excerpt drift '+cid)
            req(basis['support_rationale'] and any(e['artifact_ref']==ref for e in patch['evidence_refs']),'unbound evidence')
            req(any(s['path']==(basis['sourceUrl'] or ref) and s['locator']==basis['text_pointer'] for s in patch['source_refs']),'unbound source')
        claims[cid].update(copy.deepcopy(patch))
        claims[cid]['history']={**prior.get('history',{}),'final_owner_review':{'marker':MARKER,'before_claim_sha256':objhash(prior),'prior_status':prior['status'],'prior_text_sha256':sha(prior['text'].encode()),'prior_text':prior['text'] if patch['text']!=prior['text'] else None,'limits':entry['limits']}}
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
    impact=json.loads(artifacts[ATTEMPT+'/integration-impact.json'])
    req(all(c['fences_unchanged'] for c in impact['affected_procedures']),'changed command fence')
    owner_meta=scope['owner_reconciliation'];req(owner_meta['path']==ATTEMPT+'/owner-reconciliation.json' and owner_meta['before_registry_ref']==ATTEMPT+'/before-owner-questions.json','owner binding paths')
    owner=json.loads(pin(owner_meta['path'],owner_meta['sha256']));owner_before=json.loads(pin(owner_meta['before_registry_ref'],owner_meta['before_registry_sha256']))
    req(owner_meta['sha256']==seal['files']['owner-card-proposals-05.json'] and owner_meta['before_registry_sha256']==seal['baseline_owner_registry_sha256'],'sealed owner proposal')
    req(len(owner['cards'])==len(owner_before['questions'])==8 and len(owner['additional_residual_topics'])==3,'owner scope')
    old_cards={q['id']:q for q in owner_before['questions']};source_index=accepted_sources[next(iter(accepted_decisions))]
    for card in owner['cards']:
        req(objhash(old_cards[card['id']])==card['original_card_sha256'] and card['current_wording_requires_answer'] is False,'original owner card drift')
        for binding in card['source_refs']:
            meta=source_index[binding['source']];raw=artifacts[meta['artifact_ref']]
            req(sha(raw)==meta['sha256'] and utils.selection(raw,binding['text_pointer'])==binding['source_excerpt'],'owner source binding')
    req(sum(q['suggested_presentation']=='current_publication_conflict' for q in owner['cards'])==3,'publication conflict count')
    for alias in scope['historical_source_aliases']:
        req(alias in impact['historical_source_aliases'] and alias['path'] in before and sha(before[alias['path']])==alias['sha256'] and read(alias['frozen_ref'])==before[alias['path']],'historical mutable-source alias')
    for record in scope['historical_artifacts']:req(sha(artifacts[record['path']])==record['sha256'],'retained rejected/superseded provenance')
    for item in model['source']['source_manifest']:
        if item['path'] in after_hashes:item['sha256']=after_hashes[item['path']]
    req(set(index(model))==set(old) and len(old)==2008,'active claim inventory drift')
    model['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in claims.values()).items()))
    model['counts']['page_coverage_states']=dict(sorted(Counter(p['coverage_state'] for p in model['pages']).items()))
    model['generated_at']=registry['generated_at'];model['corrections'].append({'id':MARKER,'scope':'11 remaining assertions corrected, plus one already-PASS storage caveat with zero resolution credit','history':'Sealed 106-, 175-, 148-, 117-, 121-, 120-, 88-, 318- and 358-occurrence reviews replayed with exact before-source bytes; all prior findings and evidence retained.','current':'Current passage wording is source-supported; original owner questions and current publication conflicts remain distinct from passage status.','reason':registry['limits']})
    return model

def load_final_owner_review(root,model):
    present=(root/REGISTRY).is_file();marked=any(x.get('id')==MARKER for x in model.get('corrections',[]))
    if not present:req(not marked,'Final owner-marked model has no registry');return None
    req(model==project(root),'whole model differs from Final owner projection');return {'registry':REGISTRY,'registry_sha256':REGISTRY_SHA256}
