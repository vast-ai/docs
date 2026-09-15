#!/usr/bin/env python3
"""Apply only the root-accepted frozen 120; replay sealed prior evidence unchanged."""
from pathlib import Path
import argparse, copy, datetime, difflib, hashlib, importlib.util, json, re

ROOT=Path(__file__).resolve().parents[1]
ATTEMPT='verification/evidence/2026-09-15-host-continuation-diagnostics-ssh-attempt-01'
BASELINE='5e23962030e42fb599f89b56f232ba926cc0c6d11467ebfaa7c321d7d5ecec4e'
COMMIT='36d2945482f18cb2995be466dbdce1ecc592a62e'
CORRECTION_NEXT_ACTION='The accepted wording correction is applied. Recheck this passage if its wording, authoritative source or relevant console changes; retain the recorded evidence limits.'
LANES={'diagnostics':('continuation-diagnostics-20260915',116,'verification/evidence/2026-09-15-host-continuation-diagnostics-attempt-01/'),'adjacent-ssh':('continuation-adjacent-20260915',3,'verification/evidence/2026-09-15-host-continuation-adjacent-attempt-01/')}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canon=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
oh=lambda value:sha(canon(value).encode())
encoded=lambda value:(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
def require(condition,message):
    if not condition:raise ValueError('continuation integration: '+message)
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def safe(ref):
    require(isinstance(ref,str) and ref and not Path(ref).is_absolute() and '\\' not in ref and all(p not in ('','.','..') for p in ref.split('/')),'unsafe artifact path')
    path=(ROOT/ref).resolve();require(path.is_relative_to(ROOT.resolve()),'artifact escaped checkout');return path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proposals',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--addendum',type=Path,required=True)
    parser.add_argument('--impact-acceptance',type=Path)
    parser.add_argument('--source-amendment',type=Path,required=True)
    args=parser.parse_args();proposal=args.proposals.resolve()
    # Verify actual root approvals before any output or document mutation.
    require(COMMIT!='PENDING_SIGNED_88_COMMIT','signed predecessor commit is not pinned')
    acceptance={'baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'lanes':[]}
    for lane,(directory,count,prefix) in LANES.items():
        approvalraw=(proposal/directory/'root-acceptance.json').read_bytes();approval=json.loads(approvalraw)
        require(approval['state'] in ('ACCEPTED_FOR_INTEGRATION_REVIEW','ROOT_ACCEPTED_CORRECTIONS'),'unaccepted lane '+lane)
        acceptance['lanes'].append({'lane':lane,'acceptance_sha256':sha(approvalraw),'inventory_file':'inventory.json','inventory_sha256':approval['inventory_sha256'],'decisions_file':approval.get('decisions_file','decisions.json'),'decisions_sha256':approval['decisions_sha256'],'sources_file':approval.get('sources_file','sources.json'),'sources_sha256':approval['sources_sha256']})
    addendum_raw=args.addendum.read_bytes();addendum=json.loads(addendum_raw)
    require(addendum['baseline_commit']==COMMIT and addendum['baseline_model_sha256']==BASELINE and addendum['successor_claim_count']==120,'addendum baseline')
    require(sha(addendum_raw)=='b32d79ffbd415b9b5d58546587adde78cbee6c310707c671729df6023667d7c8','unaccepted addendum bytes')
    acceptance['addendum_sha256']=sha(addendum_raw)
    wiki_raw=args.source_amendment.read_bytes();wiki=json.loads(wiki_raw)
    wiki_approval_path=args.source_amendment.with_name('root-acceptance-03.json');wiki_approval_raw=wiki_approval_path.read_bytes();wiki_approval=json.loads(wiki_approval_raw)
    require(wiki_approval['record_type']=='ROOT_ACCEPTED_WIKI_AMENDMENT' and wiki_approval['proposal_sha256']==sha(wiki_raw)=='b6d7e8525ddc575114b6945ec61fb154cc8db21267f3fcd566df1f388604aec7','wiki amendment acceptance')
    wiki_prefix=LANES['diagnostics'][2]+'wiki-addendum-01/'
    acceptance['source_amendment']={'proposal':{'path':wiki_prefix+'proposal-03.json','sha256':sha(wiki_raw)},'approval':{'path':wiki_prefix+'root-acceptance-03.json','sha256':sha(wiki_approval_raw)}}
    acceptance_raw=encoded(acceptance)
    modelraw=safe('verification/current-host-docs-review.json').read_bytes()
    require(sha(modelraw)==BASELINE,'baseline model bytes changed')
    model=json.loads(modelraw);pre=module('current_host_continuation_review')
    require(pre.project(ROOT)==model,'whole sealed predecessor differs from frozen current model')
    claims={c['id']:c for p in model['pages'] for c in p['claims']}
    require(len(claims)==2008,'whole claim population changed')
    selection=module('current_host_closure_correction').selection
    staged={ATTEMPT+'/integration-acceptance.json':acceptance_raw};artifacts={};frozen=[];decisions={};families={};indexes={}
    def retain(ref,raw):
        safe(ref);require(ref not in staged or staged[ref]==raw,'conflicting staged artifact '+ref);staged[ref]=raw;return raw
    def bind(ref,wanted=None):
        raw=staged[ref] if ref in staged else safe(ref).read_bytes()
        require(wanted is None or sha(raw)==wanted,'source digest '+ref)
        require(b'\x00' not in raw,'binary evidence must not be embedded '+ref)
        artifacts[ref]=sha(raw);return raw
    for accepted in acceptance['lanes']:
        lane=accepted['lane'];directory,count,prefix=LANES[lane];folder=proposal/directory
        retain(ATTEMPT+'/'+lane+'/root-acceptance.json',(folder/'root-acceptance.json').read_bytes());bind(ATTEMPT+'/'+lane+'/root-acceptance.json')
        for name,field in [('inventory_file','inventory_sha256'),('decisions_file','decisions_sha256'),('sources_file','sources_sha256')]:
            filename=accepted[name];raw=(folder/filename).read_bytes();require(sha(raw)==accepted[field],'unaccepted '+lane+'/'+filename)
            retain(ATTEMPT+'/'+lane+'/'+filename,raw);bind(ATTEMPT+'/'+lane+'/'+filename)
        original=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['inventory_file']])
        require(len(original['claims'])==count,'lane count '+lane)
        data=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['decisions_file']])
        require(not data.get('context_corrections'),'unaccepted context expansion')
        records=data['decisions'];require({d['id'] for d in records}=={x['id'] for x in original['claims']} and len(records)==count,'decision inventory '+lane)
        indexes[lane]=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['sources_file']])['sources']
        for item in original['claims']:
            c=claims[item['id']]
            require(item['literal_sha256']==sha(c['text'].encode()),'relocated literal changed '+item['id'])
            if 'claim' in item:
                prior=item['claim'];require({k:v for k,v in prior.items() if k!='spans'}=={k:v for k,v in c.items() if k!='spans'},'previous full claim drift '+item['id'])
            else:require(item['text']==c['text'],'flat inventory literal drift '+item['id'])
            frozen.append({'id':item['id'],'literal_sha256':item['literal_sha256'],'claim':copy.deepcopy(c),'original_inventory_ref':ATTEMPT+'/'+lane+'/'+accepted['inventory_file'],'original_pointer':item.get('pointer',item.get('model_pointer'))})
        for d in records:
            require(d['id'] not in decisions,'overlapping lane '+d['id']);decisions[d['id']]=d;families[d['id']]=lane
        for meta in indexes[lane].values():
            ref=meta.get('artifact_ref',meta.get('path'));require(isinstance(ref,str),'missing source artifact')
            # Reuse already-retained bytes first, including the earlier 88's
            # official SSH manuals whose original index still has staged paths.
            if safe(ref).exists():require(sha(safe(ref).read_bytes())==meta['sha256'],'existing source hash '+ref);continue
            staged_file=meta.get('staged_path',meta.get('staged_file'));require(staged_file,'missing accepted source '+ref)
            source=Path(staged_file).resolve();require(source.is_relative_to(folder.resolve()),'new source outside its accepted lane')
            require(ref.startswith(prefix),'new artifact outside accepted original prefix')
            raw=source.read_bytes();require(sha(raw)==meta['sha256'],'staged source hash '+ref);retain(ref,raw)
    effective_sources={cid:copy.deepcopy(indexes[families[cid]]) for cid in decisions}
    retain(ATTEMPT+'/root-user-context-addendum.json',addendum_raw);bind(ATTEMPT+'/root-user-context-addendum.json')
    require(addendum['baseline_commit']==COMMIT and addendum['baseline_model_sha256']==BASELINE and addendum['successor_claim_count']==120,'addendum baseline/scope')
    require(set(addendum['overrides'])=={'MCL-6b3a48733434c5e5','MCL-1221941af8a7a4fe'} and [x['id'] for x in addendum['added_claims']]==['MCL-1221941af8a7a4fe'],'addendum occurrence scope')
    for cid,override in addendum['overrides'].items():
        original=copy.deepcopy(decisions.get(cid,{}));after=override['after'];source=override['source_ref']
        require(after['status']=='UNVALIDATED' and set(after)=={'status','required_evidence_types','owner_role','rationale','next_action','classification'},'addendum must not promote or replace literal')
        d={**original,'id':cid,'literal_sha256':override['current_literal_sha256'],'decision':'residual','proposed_status':after['status'],'proposed_methods':after['required_evidence_types'],'proposed_classification':after['classification'],'proposed_owner_role':after['owner_role'],'support_rationale':after['rationale'],'next_action':after['next_action'],'method_rationale':override['history_note'],'limitation':override['history_note'],'residual_topic':override['residual_topic'],'source_refs':original.get('source_refs',[])+[{'source':'user-operational-context','text_pointer':source['text_pointer'],'source_excerpt':source['source_excerpt']}]}
        decisions[cid]=d;effective_sources[cid]={**effective_sources.get(cid,{}),'user-operational-context':source}
    for item in addendum['added_claims']:
        require(item['claim']==claims[item['id']] and item['literal_sha256']==sha(claims[item['id']]['text'].encode()),'added frozen claim drift')
        frozen.append({**item,'original_inventory_ref':ATTEMPT+'/root-user-context-addendum.json'})
    for cid,override in addendum['overrides'].items():
        meta=override['source_ref'];ref=meta['artifact_ref'];source=Path(meta['staged_path']).resolve()
        require(source.is_relative_to((proposal/LANES['diagnostics'][0]).resolve()) and ref.startswith(LANES['diagnostics'][2]),'user context outside accepted scope')
        raw=source.read_bytes();require(sha(raw)==meta['sha256'],'user context digest');retain(ref,raw)
    require(wiki['original_user_addendum_sha256']==sha(addendum_raw) and wiki['baseline_commit']==COMMIT and wiki['baseline_model_sha256']==BASELINE,'wiki source lineage')
    require({d['id'] for d in wiki['decisions']}==set(addendum['overrides']) and len(wiki['decisions'])==2,'wiki occurrence scope')
    retain(acceptance['source_amendment']['proposal']['path'],wiki_raw);bind(acceptance['source_amendment']['proposal']['path'])
    retain(acceptance['source_amendment']['approval']['path'],wiki_approval_raw);bind(acceptance['source_amendment']['approval']['path'])
    retain(wiki['original_user_addendum_ref'],addendum_raw);bind(wiki['original_user_addendum_ref'])
    for ref,digest in [(wiki['incident_follow_up_ref'],wiki['incident_follow_up_sha256']),(wiki['prior_detailed_proposal_ref'],wiki['prior_detailed_proposal_sha256']),(wiki['prior_effective_proposal_ref'],wiki['prior_effective_proposal_sha256'])]:
        require(ref.startswith(wiki_prefix),'wiki retained reference outside scope')
        raw=(args.source_amendment.parent/Path(ref).name).read_bytes();require(sha(raw)==digest,'wiki retained digest '+ref);retain(ref,raw);bind(ref)
    for key,meta in wiki['sources'].items():
        ref=meta['artifact_ref'];source=Path(meta['staged_file']).resolve()
        require(source.is_relative_to((proposal/LANES['diagnostics'][0]).resolve()) and ref.startswith(LANES['diagnostics'][2]),'wiki source outside scope')
        raw=source.read_bytes();require(sha(raw)==meta['sha256'],'wiki source digest');retain(ref,raw);bind(ref)
        if meta.get('capture_ref'):
            ref=meta['capture_ref'];require(ref.startswith(wiki_prefix),'wiki capture outside scope')
            raw=(args.source_amendment.parent/Path(ref).name).read_bytes();require(sha(raw)==meta['capture_sha256'],'wiki capture digest');retain(ref,raw);bind(ref)
    for d in wiki['decisions']:
        require(d['before_claim']==claims[d['id']] and d['before_claim_sha256']==oh(claims[d['id']]),'wiki frozen before claim')
        decisions[d['id']]=d;effective_sources[d['id']]=wiki['sources']
    require(len(decisions)==len(frozen)==120,'frozen 120 inventory')
    bind(ATTEMPT+'/integration-acceptance.json')
    source_hashes={s['source_file']:sha(safe(s['source_file']).read_bytes()) for item in frozen for s in item['claim']['spans']}
    inventory={'record_type':'FROZEN_DIAGNOSTICS_SSH_INVENTORY','baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'claims':frozen,'source_hashes':source_hashes}
    changes={};replacement_spans={}
    for cid,d in decisions.items():
        c=claims[cid];require(d['literal_sha256']==sha(c['text'].encode()),'decision literal '+cid)
        require(d['decision'] in ('supported','correction','residual'),'decision kind '+cid)
        if d['decision']!='correction':
            require(not d.get('replacement_text'),'replacement on non-correction '+cid);continue
        replacement=d.get('replacement_text',d.get('proposed_replacement'))
        require(isinstance(replacement,str) and replacement!=c['text'] and len(c['spans'])==1,'exact correction '+cid)
        span=c['spans'][0];changes.setdefault(span['source_file'],[]).append({'id':cid,'start':span['start'],'end':span['end'],'before':c['text'],'after':replacement})
    sources=[];texts={};oldtexts={};maps={}
    for ref,edits in sorted(changes.items()):
        raw=safe(ref).read_bytes();old=raw.decode().splitlines();new=[];cursor=0
        for e in sorted(edits,key=lambda e:e['start']):
            require(cursor<e['start'] and '\n'.join(old[e['start']-1:e['end']])==e['before'],'overlap or nonliteral correction '+e['id'])
            new+=old[cursor:e['start']-1];first=len(new)+1;new+=e['after'].splitlines();last=len(new);cursor=e['end']
            replacement_spans[e['id']]=[{'source_file':ref,'start':first,'end':last,'text_sha256':sha(e['after'].encode())}]
        new+=old[cursor:];texts[ref]='\n'.join(new)+'\n';oldtexts[ref]=raw
        line_map=[];diffs=[]
        for op,a,z,b,y in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
            if op=='equal':line_map.extend([[a+i+1,b+i+1] for i in range(z-a)])
            else:diffs.append({'before_start':a+1,'before_end':z,'after_start':b+1,'after_end':y})
        maps[ref]=dict(line_map);before=ATTEMPT+'/sources-before/'+ref
        sources.append({'path':ref,'before_artifact':{'path':before,'sha256':sha(raw)},'after_sha256':sha(texts[ref].encode()),'line_map':line_map,'edits':diffs});retain(before,raw)
    def relocate(span):
        if span['source_file'] not in maps:return copy.deepcopy(span)
        values=[maps[span['source_file']].get(i) for i in range(span['start'],span['end']+1)]
        if None in values or values!=list(range(values[0],values[-1]+1)):return None
        return {**span,'start':values[0],'end':values[-1]}
    overlaps=[{'id':cid,'spans':c['spans']} for cid,c in claims.items() if cid not in decisions and any(relocate(s) is None for s in c['spans'])]
    require(not overlaps,'out-of-scope literal overlap: '+canon(overlaps))
    scope={'acceptance_sha256':sha(acceptance_raw),'decisions':{},'procedures':{}};transitions=[]
    for cid,d in decisions.items():
        c=claims[cid];basis=[];ev=copy.deepcopy(c['evidence_refs']);refs=copy.deepcopy(c['source_refs'])
        for b in d['source_refs']:
            meta=effective_sources[cid][b['source']];ref=meta.get('artifact_ref',meta.get('path'));raw=bind(ref,meta['sha256'])
            excerpt=selection(raw,b['text_pointer']);require(excerpt==b['source_excerpt'],'exact source selector '+cid+' '+b['text_pointer'])
            url=meta.get('url',meta.get('source_url'));kind=meta.get('source_kind','STATIC_CONTEXT_REVIEW');revision=meta.get('revision',meta.get('source_revision'))
            basis.append({'sourceKey':b['source'],'artifactRef':ref,'text_pointer':b['text_pointer'],'excerpt':excerpt,'sourceUrl':url,'sourceRevision':revision,'sourceKind':kind,'support_rationale':d['support_rationale']})
            if not any(e['artifact_ref']==ref for e in ev):ev.append({'id':'DIAGNOSTICS-SSH-'+cid+'-'+str(len(basis)),'role':kind,'limit':d['limitation'],'artifact_ref':ref})
            sr={'repository':meta.get('repository','retained-primary-source'),'revision':revision or 'sha256:'+meta['sha256'],'path':url or ref,'locator':b['text_pointer'],'source_kind':kind}
            if sr not in refs:refs.append(sr)
        after={'text':d.get('replacement_text',d.get('proposed_replacement',c['text'])),'status':d['proposed_status'],'classification':d['proposed_classification'],'required_evidence_types':d['proposed_methods'],'owner_role':d.get('proposed_owner_role',c['owner_role']),'rationale':d['support_rationale'],'next_action':CORRECTION_NEXT_ACTION if d['decision']=='correction' else d['next_action'],'evidence_refs':ev,'source_refs':refs,'coverage_state':'CHANGED'}
        if cid in replacement_spans:after['spans']=replacement_spans[cid]
        scope['decisions'][cid]={'accepted_decision_sha256':oh(d),'residual_topic':d.get('residual_topic'),'fields_sha256':oh({k:after[k] for k in ['text','status','classification','required_evidence_types','owner_role']}),'method_rationale':d['method_rationale']}
        transitions.append({'claim_id':cid,'before_sha256':oh(c),'after':after,'decision':d['decision'],'residual_topic':d.get('residual_topic'),'method':'SCOPED_DIAGNOSTICS_SSH_REVIEW','method_rationale':d['method_rationale'],'limits':d['limitation'],'basis':basis})
    def inclusive_span(span):
        same=relocate(span)
        if same:return same
        source=next(x for x in sources if x['path']==span['source_file']);mapping=maps[span['source_file']]
        def boundary(n,start):
            if n in mapping:return mapping[n]
            e=next(e for e in source['edits'] if e['before_start']<=n<=e['before_end']);return e['after_start'] if start else e['after_end']
        first,last=boundary(span['start'],True),boundary(span['end'],False);require(first<=last,'empty procedure span')
        return {**span,'start':first,'end':last,'text_sha256':sha('\n'.join(texts[span['source_file']].splitlines()[first-1:last]).encode())}
    def commands(span,new):
        content=(texts.get(span['source_file']) if new else None) or (oldtexts.get(span['source_file']) or safe(span['source_file']).read_bytes()).decode()
        return [m.group(1) for m in re.finditer(r'^```[^\n]*\n([\s\S]*?)^```',content,re.M) if content[:m.start()].count('\n')+1<=span['end'] and content[:m.end()].count('\n')+1>=span['start']]
    procedures=[];comparisons=[]
    for pi,page in enumerate(model['pages']):
        for qi,q in enumerate(page['procedures']):
            for ni,n in enumerate([q,*q['nodes']]):
                if not any(relocate(s) is None for s in n.get('spans',[])):continue
                pointer=f'/pages/{pi}/procedures/{qi}'+(f'/nodes/{ni-1}' if ni else '');spans=[inclusive_span(s) for s in n['spans']]
                beforecmd=[b for s in n['spans'] for b in commands(s,False)];aftercmd=[b for s in spans for b in commands(s,True)]
                # A changed passing command needs an explicit impact decision; never silently carry its runtime PASS.
                require(n['status']!='PASS' or beforecmd==aftercmd,'changed PASS procedure command requires explicit root review '+n['id'])
                reason='Rebind corrected source spans; preserve the existing procedure status and evidence. This passage review does not establish procedure execution.'
                after={'spans':spans,'history':{**n.get('history',{}),'diagnostics_ssh_review':{'prior_spans':copy.deepcopy(n['spans']),'before_source_root':ATTEMPT+'/sources-before/','reason':reason}},'coverage_state':'CHANGED'}
                procedures.append({'id':n['id'],'model_pointer':pointer,'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'after':after,'reason':reason});scope['procedures'][pointer]={'after':after,'reason':reason}
                comparisons.append({'id':n['id'],'model_pointer':pointer,'status':n['status'],'fences_unchanged':beforecmd==aftercmd,'before_fences_sha256':[sha(x.encode()) for x in beforecmd],'after_fences_sha256':[sha(x.encode()) for x in aftercmd]})
    impact={'literal_corrections':len(replacement_spans),'corrections':[{'source_file':ref,**edit,'after_spans':replacement_spans[edit['id']]} for ref,edits in sorted(changes.items()) for edit in edits],'changed_sources':list(texts),'out_of_scope_overlaps':overlaps,'affected_procedures':comparisons,'procedure_statuses_and_evidence_preserved':True,'baseline_commit':COMMIT,'baseline_model_sha256':BASELINE}
    impact_raw=encoded(impact)
    retain(ATTEMPT+'/integration-impact.json',impact_raw);bind(ATTEMPT+'/integration-impact.json')
    if args.apply:
        require(args.impact_acceptance is not None,'root impact acceptance is required')
        impact_approval_raw=args.impact_acceptance.read_bytes();impact_approval=json.loads(impact_approval_raw)
        require(impact_approval['impact_sha256']==sha(impact_raw) and impact_approval['baseline_model_sha256']==BASELINE,'root impact acceptance differs')
        retain(ATTEMPT+'/root-impact-acceptance.json',impact_approval_raw)
        bind(ATTEMPT+'/root-impact-acceptance.json')
        scope['impact_acceptance']={'path':ATTEMPT+'/root-impact-acceptance.json','sha256':sha(impact_approval_raw)}
    baseline={'baseline_model_canonical_sha256':oh(model),'claim_hashes':{cid:oh(c) for cid,c in claims.items()},'procedure_population_sha256':oh([p['procedures'] for p in model['pages']])}
    retain(ATTEMPT+'/inventory.json',encoded(inventory));retain(ATTEMPT+'/integration-baseline.json',encoded(baseline));retain(ATTEMPT+'/integration-scope.json',encoded(scope))
    registry={'schema_version':'1.0','record_type':'HOST_DIAGNOSTICS_SSH_REVIEW','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':{'path':ATTEMPT+'/integration-scope.json','sha256':sha(staged[ATTEMPT+'/integration-scope.json'])},'sources':sources,'artifacts':[{'path':ref,'sha256':digest} for ref,digest in sorted(artifacts.items())],'transitions':transitions,'procedures':procedures,'limits':'120 frozen occurrences: diagnostic definitions, recovery guidance and SSH instruction source review. No induced hardware failure, executed recovery, backend-policy validation or new rental. Earlier 88, 318 and 358 reviews, failures and evidence remain retained; incident-time evidence and the removed two-hour SSH warning promise remain explicit follow-ups.'}
    registryraw=encoded(registry)
    print(json.dumps({'accepted_claims':len(transitions),'corrections':len(replacement_spans),'changed_sources':list(texts),'affected_procedures':len(procedures),'apply':args.apply}))
    if not args.apply:
        target=safe(ATTEMPT+'/impact-proposal.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(impact_raw)
        print(json.dumps({'impact_proposal':str(target),'sha256':sha(impact_raw)}));return
    require(not safe('verification/current-host-diagnostics-ssh-review.json').exists(),'successor already exists; never overwrite a sealed attempt')
    for ref,raw in staged.items():
        target=safe(ref);require(not target.exists() or target.read_bytes()==raw,'existing attempt artifact differs '+ref);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    for ref,text in texts.items():safe(ref).write_text(text)
    safe('verification/current-host-diagnostics-ssh-review.json').write_bytes(registryraw)
    pins={'PENDING_ACCEPTED_REGISTRY':sha(registryraw),'PENDING_ACCEPTED_INVENTORY':sha(staged[ATTEMPT+'/inventory.json']),'PENDING_ACCEPTED_BASELINE':sha(staged[ATTEMPT+'/integration-baseline.json'])}
    for suffix in ('py','mjs'):
        target=safe('scripts/current_host_diagnostics_ssh_review.'+suffix);text=target.read_text()
        for token,digest in pins.items():require(token in text,'projector already sealed');text=text.replace(token,digest)
        target.write_text(text)
    print(json.dumps({'registry_sha256':sha(registryraw),'next':'Run paired projectors and inspect exact model/owner rebinding before generating the reviewer.'}))

if __name__=='__main__':main()
