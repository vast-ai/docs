#!/usr/bin/env python3
"""Apply only the root-accepted frozen 88; replay sealed prior evidence unchanged."""
from pathlib import Path
import argparse, copy, datetime, difflib, hashlib, importlib.util, json, re

ROOT=Path(__file__).resolve().parents[1]
ATTEMPT='verification/evidence/2026-09-15-host-continuation-88-attempt-01'
BASELINE='e376445856232f6a41f1b68ac3e01ee173590390cae8768c4392361bc04cc235'
COMMIT='e4117c2948dd52e2f714fab95fb2419948a46d0f'
CORRECTION_NEXT_ACTION='The accepted wording correction is applied. Recheck this passage if its wording, authoritative source or relevant console changes; retain the recorded evidence limits.'
LANES={'a-cli-reuse':32,'b-system-examples':28,'c-teams-source':19,'d-console':9}
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
    args=parser.parse_args();proposal=args.proposals.resolve()
    # This is the first read, before output, copying evidence or any docs mutation.
    acceptance_raw=(proposal/'root-lane-acceptance.json').read_bytes()
    acceptance=json.loads(acceptance_raw)
    require(acceptance['baseline_commit']==COMMIT and acceptance['baseline_model_sha256']==BASELINE,'accepted baseline identity')
    require(len(acceptance['lanes'])==4 and {x['lane'] for x in acceptance['lanes']}==set(LANES),'accepted lane inventory')
    require(not acceptance.get('assets'),'this batch does not authorize public screenshot or asset changes')
    modelraw=safe('verification/current-host-docs-review.json').read_bytes()
    require(sha(modelraw)==BASELINE,'baseline model bytes changed')
    model=json.loads(modelraw);pre=module('current_host_evidence_reuse_review')
    require(pre.project(ROOT)==model,'whole sealed predecessor differs from frozen current model')
    claims={c['id']:c for p in model['pages'] for c in p['claims']}
    require(len(claims)==2008,'whole claim population changed')
    selection=module('current_host_closure_correction').selection
    staged={ATTEMPT+'/root-lane-acceptance.json':acceptance_raw};artifacts={};frozen=[];decisions={};families={};indexes={}
    def retain(ref,raw):
        safe(ref);require(ref not in staged or staged[ref]==raw,'conflicting staged artifact '+ref);staged[ref]=raw;return raw
    def bind(ref,wanted=None):
        raw=staged[ref] if ref in staged else safe(ref).read_bytes()
        require(wanted is None or sha(raw)==wanted,'source digest '+ref)
        require(b'\x00' not in raw,'binary evidence must not be embedded '+ref)
        artifacts[ref]=sha(raw);return raw
    for accepted in acceptance['lanes']:
        lane=accepted['lane']
        for filename,field in [('inventory.json','inventory_sha256'),('decisions.json','decisions_sha256'),('sources.json','sources_sha256')]:
            raw=(proposal/lane/filename).read_bytes();require(sha(raw)==accepted[field],'unaccepted '+lane+'/'+filename)
            retain(ATTEMPT+'/'+lane+'/'+filename,raw);bind(ATTEMPT+'/'+lane+'/'+filename)
        inventory=json.loads(staged[ATTEMPT+'/'+lane+'/inventory.json'])
        require(inventory['baseline_model_sha256']==BASELINE and inventory['baseline_commit']==COMMIT,'lane baseline identity')
        require(len(inventory['claims'])==LANES[lane],'lane count '+lane)
        data=json.loads(staged[ATTEMPT+'/'+lane+'/decisions.json'])
        require(not data.get('context_corrections'),'unaccepted context expansion')
        records=data['decisions'];require({d['id'] for d in records}=={x['id'] for x in inventory['claims']} and len(records)==LANES[lane],'decision inventory '+lane)
        indexes[lane]=json.loads(staged[ATTEMPT+'/'+lane+'/sources.json'])['sources']
        for item in inventory['claims']:
            require(item['claim']==claims[item['id']] and item['literal_sha256']==sha(claims[item['id']]['text'].encode()),'frozen full claim '+item['id']);frozen.append(item)
        for d in records:
            require(d['id'] not in decisions,'overlapping lane '+d['id']);decisions[d['id']]=d;families[d['id']]=lane
        for meta in indexes[lane].values():
            ref=meta.get('artifact_ref',meta.get('path'));require(isinstance(ref,str),'missing source artifact')
            staged_file=meta.get('staged_path',meta.get('staged_file'))
            if staged_file:
                source=Path(staged_file).resolve();require(source.is_relative_to((proposal/lane).resolve()),'staged source outside its lane')
                require(ref.startswith(ATTEMPT+'/'+lane+'/'),'new artifact outside accepted lane')
                raw=source.read_bytes();require(sha(raw)==meta['sha256'],'staged source hash '+ref);retain(ref,raw)
            else:require(sha(safe(ref).read_bytes())==meta['sha256'],'existing source hash '+ref)
    require(len(decisions)==len(frozen)==88,'frozen 88 inventory')
    bind(ATTEMPT+'/root-lane-acceptance.json')
    source_hashes={s['source_file']:sha(safe(s['source_file']).read_bytes()) for item in frozen for s in item['claim']['spans']}
    inventory={'record_type':'FROZEN_CONTINUATION_INVENTORY','baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'claims':frozen,'source_hashes':source_hashes}
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
            meta=indexes[families[cid]][b['source']];ref=meta.get('artifact_ref',meta.get('path'));raw=bind(ref,meta['sha256'])
            excerpt=selection(raw,b['text_pointer']);require(excerpt==b['source_excerpt'],'exact source selector '+cid+' '+b['text_pointer'])
            url=meta.get('url',meta.get('source_url'));kind=meta.get('source_kind','STATIC_CONTEXT_REVIEW');revision=meta.get('revision',meta.get('source_revision'))
            basis.append({'sourceKey':b['source'],'artifactRef':ref,'text_pointer':b['text_pointer'],'excerpt':excerpt,'sourceUrl':url,'sourceRevision':revision,'sourceKind':kind,'support_rationale':d['support_rationale']})
            if not any(e['artifact_ref']==ref for e in ev):ev.append({'id':'CONTINUATION-'+cid+'-'+str(len(basis)),'role':kind,'limit':d['limitation'],'artifact_ref':ref})
            sr={'repository':meta.get('repository','retained-primary-source'),'revision':revision or 'sha256:'+meta['sha256'],'path':url or ref,'locator':b['text_pointer'],'source_kind':kind}
            if sr not in refs:refs.append(sr)
        after={'text':d.get('replacement_text',d.get('proposed_replacement',c['text'])),'status':d['proposed_status'],'classification':d['proposed_classification'],'required_evidence_types':d['proposed_methods'],'owner_role':d.get('proposed_owner_role',c['owner_role']),'rationale':d['support_rationale'],'next_action':CORRECTION_NEXT_ACTION if d['decision']=='correction' else d['next_action'],'evidence_refs':ev,'source_refs':refs,'coverage_state':'CHANGED'}
        if cid in replacement_spans:after['spans']=replacement_spans[cid]
        scope['decisions'][cid]={'accepted_decision_sha256':oh(d),'residual_topic':d.get('residual_topic'),'fields_sha256':oh({k:after[k] for k in ['text','status','classification','required_evidence_types','owner_role']}),'method_rationale':d['method_rationale']}
        transitions.append({'claim_id':cid,'before_sha256':oh(c),'after':after,'decision':d['decision'],'residual_topic':d.get('residual_topic'),'method':'SCOPED_CONTINUATION_REVIEW','method_rationale':d['method_rationale'],'limits':d['limitation'],'basis':basis})
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
                after={'spans':spans,'history':{**n.get('history',{}),'continuation_review':{'prior_spans':copy.deepcopy(n['spans']),'before_source_root':ATTEMPT+'/sources-before/','reason':reason}},'coverage_state':'CHANGED'}
                procedures.append({'id':n['id'],'model_pointer':pointer,'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'after':after,'reason':reason});scope['procedures'][pointer]={'after':after,'reason':reason}
                comparisons.append({'id':n['id'],'model_pointer':pointer,'status':n['status'],'fences_unchanged':beforecmd==aftercmd,'before_fences_sha256':[sha(x.encode()) for x in beforecmd],'after_fences_sha256':[sha(x.encode()) for x in aftercmd]})
    retain(ATTEMPT+'/integration-impact.json',encoded({'literal_corrections':len(replacement_spans),'changed_sources':list(texts),'out_of_scope_overlaps':overlaps,'affected_procedures':comparisons,'procedure_statuses_and_evidence_preserved':True}));bind(ATTEMPT+'/integration-impact.json')
    baseline={'baseline_model_canonical_sha256':oh(model),'claim_hashes':{cid:oh(c) for cid,c in claims.items()},'procedure_population_sha256':oh([p['procedures'] for p in model['pages']])}
    retain(ATTEMPT+'/inventory.json',encoded(inventory));retain(ATTEMPT+'/integration-baseline.json',encoded(baseline));retain(ATTEMPT+'/integration-scope.json',encoded(scope))
    registry={'schema_version':'1.0','record_type':'HOST_CONTINUATION_REVIEW','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':{'path':ATTEMPT+'/integration-scope.json','sha256':sha(staged[ATTEMPT+'/integration-scope.json'])},'sources':sources,'artifacts':[{'path':ref,'sha256':digest} for ref,digest in sorted(artifacts.items())],'transitions':transitions,'procedures':procedures,'limits':'88 frozen occurrences: exact source review, reused bounded CLI evidence, included-image descriptions and read-only console observations. No invitation, settings mutation, transaction, new paid rental or disruptive hardware action. Earlier 318 and 358 reviews, failures, residuals and all prior evidence remain retained; current-source semantics do not imply successful execution.'}
    registryraw=encoded(registry)
    print(json.dumps({'accepted_claims':len(transitions),'corrections':len(replacement_spans),'changed_sources':list(texts),'affected_procedures':len(procedures),'apply':args.apply}))
    if not args.apply:return
    require(not safe('verification/current-host-continuation-review.json').exists(),'successor already exists; never overwrite a sealed attempt')
    for ref,raw in staged.items():
        target=safe(ref);require(not target.exists() or target.read_bytes()==raw,'existing attempt artifact differs '+ref);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    for ref,text in texts.items():safe(ref).write_text(text)
    safe('verification/current-host-continuation-review.json').write_bytes(registryraw)
    pins={'PENDING_ACCEPTED_REGISTRY':sha(registryraw),'PENDING_ACCEPTED_INVENTORY':sha(staged[ATTEMPT+'/inventory.json']),'PENDING_ACCEPTED_BASELINE':sha(staged[ATTEMPT+'/integration-baseline.json'])}
    for suffix in ('py','mjs'):
        target=safe('scripts/current_host_continuation_review.'+suffix);text=target.read_text()
        for token,digest in pins.items():require(token in text,'projector already sealed');text=text.replace(token,digest)
        target.write_text(text)
    print(json.dumps({'registry_sha256':sha(registryraw),'next':'Run paired projectors and inspect exact model/owner rebinding before generating the reviewer.'}))

if __name__=='__main__':main()
