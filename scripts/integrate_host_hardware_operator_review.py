#!/usr/bin/env python3
"""Prepare/apply the accepted106 plus one SSH consistency record and uncounted heading; preserve prior evidence."""
from pathlib import Path
import argparse, copy, datetime, difflib, hashlib, importlib.util, json, re

ROOT=Path(__file__).resolve().parents[1]
ATTEMPT='verification/evidence/2026-09-15-host-continuation-hardware-operator-attempt-01'
BASELINE='794b1e3a7ba316d6c10de2f5f43b8838b5f6896be90b68f39050d4803ed258c0'
COMMIT='853d6610e91b2749f2dd8ea8fa7c19de072b9918'
CORRECTION_NEXT_ACTION='The accepted wording correction is applied. Recheck this passage if its wording, authoritative source or relevant console changes; retain the recorded evidence limits.'
SOURCE_NEXT_ACTION='The accepted source review is applied. Recheck this passage if its wording, authoritative source or relevant product behavior changes; retain the recorded evidence limits.'
LANES={
    'hardware':('continuation-hardware-policy-20260915',23,'verification/evidence/2026-09-15-host-continuation-hardware-policy-attempt-01/'),
    'publication':('continuation-publication-advice44-20260915',44,'verification/evidence/2026-09-15-host-continuation-publication-advice44-attempt-01/'),
    'operator':('continuation-operator-ui33-20260915',33,'verification/evidence/2026-09-15-host-continuation-operator-ui33-attempt-01/'),
    'credential':('continuation-credential-storage-20260915-rev02',1,'verification/evidence/2026-09-15-host-continuation-credential-storage-attempt-02/'),
    'blocked':('continuation-blocked-instructions5-20260915',5,'verification/evidence/2026-09-15-host-continuation-blocked-instructions5-attempt-01/'),
    'ssh_adjacent':('continuation-operator-ui33-20260915/adjacent-ssh-auth',1,'verification/evidence/2026-09-15-host-continuation-operator-ui33-attempt-01/adjacent-ssh-auth/'),
}
REJECTED_CREDENTIAL=('continuation-credential-storage-20260915',0,'verification/evidence/2026-09-15-host-continuation-credential-storage-attempt-01/')


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
    parser.add_argument('--impact-acceptance',type=Path)
    args=parser.parse_args();proposal=args.proposals.resolve()
    # Verify actual root approvals before any output or document mutation.
    require(COMMIT!='PENDING_SIGNED_88_COMMIT','signed predecessor commit is not pinned')
    acceptance={'baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'lanes':[]}
    for lane,(directory,count,prefix) in LANES.items():
        approvalraw=(proposal/directory/'root-acceptance.json').read_bytes();approval=json.loads(approvalraw)
        require(approval['state']=='ACCEPTED_FOR_INTEGRATION_IMPACT_PROPOSAL','unaccepted lane '+lane)
        require(approval['current_commit']==COMMIT and approval['current_model_sha256']==BASELINE,'approval baseline '+lane)
        require(approval['selected_count']==count,'approval scope '+lane)
        reviewfile=approval['independent_review_file'];reviewraw=(proposal/directory/reviewfile).read_bytes()
        require(sha(reviewraw)==approval['independent_review_sha256'],'unaccepted independent review')
        retained=approval.get('retained_provenance',[])
        for record in retained:
            target=(proposal/directory/record['file']).resolve()
            require(target.is_relative_to((proposal/directory).resolve()),'retained history escaped lane')
            require(sha(target.read_bytes())==record['sha256'],'historical amendment provenance')
        acceptance['lanes'].append({'lane':lane,'independent_review_file':'independent-review.json','approved_review_file':reviewfile,'retained_provenance':retained,'acceptance_sha256':sha(approvalraw),'inventory_file':'inventory.json','inventory_sha256':approval['inventory_sha256'],'independent_review_sha256':sha(reviewraw),'decisions_file':approval['decisions_file'],'decisions_sha256':approval['decisions_sha256'],'sources_file':approval['sources_file'],'sources_sha256':approval['sources_sha256']})
    acceptance['scope_counts']={'reviewed_passages':106,'adjacent_pass_consistency_records':1,'transitions':107,'newly_resolved':105,'uncounted_context_edits':1}
    acceptance['resolved_next_action_rule']={'correction':CORRECTION_NEXT_ACTION,'supported_resolved':SOURCE_NEXT_ACTION,'residual':'Retain exact accepted next_action.'}
    acceptance_raw=encoded(acceptance)
    modelraw=safe('verification/current-host-docs-review.json').read_bytes()
    require(sha(modelraw)==BASELINE,'baseline model bytes changed')
    model=json.loads(modelraw);pre=module('current_host_verification_storage_review')
    require(pre.project(ROOT)==model,'whole sealed predecessor differs from frozen current model')
    claims={c['id']:c for p in model['pages'] for c in p['claims']}
    require(len(claims)==2008,'whole claim population changed')
    selection=module('current_host_closure_correction').selection
    staged={ATTEMPT+'/integration-acceptance.json':acceptance_raw};artifacts={};frozen=[];decisions={};families={};indexes={};index_documents={}
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
        retain(ATTEMPT+'/'+lane+'/'+accepted['independent_review_file'],(folder/accepted['approved_review_file']).read_bytes());bind(ATTEMPT+'/'+lane+'/'+accepted['independent_review_file'],accepted['independent_review_sha256'])
        for record in accepted['retained_provenance']:
            retain(ATTEMPT+'/'+lane+'/'+record['file'],(folder/record['file']).read_bytes());bind(ATTEMPT+'/'+lane+'/'+record['file'],record['sha256'])
        for name,field in [('inventory_file','inventory_sha256'),('decisions_file','decisions_sha256'),('sources_file','sources_sha256')]:
            filename=accepted[name];raw=(folder/filename).read_bytes();require(sha(raw)==accepted[field],'unaccepted '+lane+'/'+filename)
            retain(ATTEMPT+'/'+lane+'/'+filename,raw);bind(ATTEMPT+'/'+lane+'/'+filename)
        original=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['inventory_file']])
        if 'claim' in original:
            prior=original['claim'];original_items=[{'id':prior['id'],'claim':prior,'literal_sha256':sha(prior['text'].encode())}]
        else:original_items=original['claims']
        require(len(original_items)==count,'lane count '+lane)
        data=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['decisions_file']])
        require(not data.get('context_corrections'),'unaccepted context expansion')
        records=data['decisions'];require({d['id'] for d in records}=={x['id'] for x in original_items} and len(records)==count,'decision inventory '+lane)
        index_documents[lane]=json.loads(staged[ATTEMPT+'/'+lane+'/'+accepted['sources_file']]);indexes[lane]=index_documents[lane]['sources']
        for item in original_items:
            literal_hash=item.get('literal_sha256') or sha(item['claim']['text'].encode())
            c=claims[item['id']]
            require(literal_hash==sha(c['text'].encode()),'relocated literal changed '+item['id'])
            if 'claim' in item:
                prior=item['claim'];require({k:v for k,v in prior.items() if k!='spans'}=={k:v for k,v in c.items() if k!='spans'},'previous full claim drift '+item['id'])
            else:require(item['text']==c['text'],'flat inventory literal drift '+item['id'])
            frozen.append({'id':item['id'],'literal_sha256':literal_hash,'claim':copy.deepcopy(c),'original_inventory_ref':ATTEMPT+'/'+lane+'/'+accepted['inventory_file'],'original_pointer':item.get('pointer',item.get('model_pointer'))})
        for d in records:
            require(d['id'] not in decisions,'overlapping lane '+d['id']);decisions[d['id']]=d;families[d['id']]=lane
    # Preserve superseded proposals under the exact accepted lane; their hashes
    # are retained separately and never substitute for the accepted decisions.
    historical=[]
    for lane,(directory,_,prefix) in LANES.items():
        folder=proposal/directory
        for filename in ('decisions.json','sources.json','independent-review.json'):
            source=folder/filename
            if not source.is_file():continue
            ref=prefix+'superseded/'+filename
            if filename in (next(x for x in acceptance['lanes'] if x['lane']==lane)['decisions_file'],next(x for x in acceptance['lanes'] if x['lane']==lane)['sources_file']):continue
            raw=source.read_bytes();retain(ref,raw);bind(ref);historical.append({'path':ref,'sha256':sha(raw)})
    # The rejected synthetic credential attempt is a bounded, explicitly accepted
    # historical packet; exclude interpreter caches and keep its complete parents.
    oldfolder=proposal/REJECTED_CREDENTIAL[0];oldprefix=REJECTED_CREDENTIAL[2]
    credential_approval=json.loads((proposal/LANES['credential'][0]/'root-acceptance.json').read_bytes())
    require((proposal/LANES['credential'][0]/credential_approval['retain_rejected_attempt_directory']).resolve()==oldfolder.resolve(),'rejected credential identity')
    for filename in ('inventory.json','decisions.json','sources.json','checks.json','proposed-command.sh','run-check.py','independent-review/review-01.json','independent-review/review-01.md'):
        raw=(oldfolder/filename).read_bytes();retain(oldprefix+filename,raw);bind(oldprefix+filename);historical.append({'path':oldprefix+filename,'sha256':sha(raw)})
    amendment=json.loads((proposal/LANES['credential'][0]/'amendment-02.json').read_bytes())
    require(sha(staged[oldprefix+'decisions.json'])==amendment['prior_decisions_sha256'] and sha(staged[oldprefix+'independent-review/review-01.json'])==amendment['prior_independent_review_sha256'],'rejected credential amendment pins')
    index_documents['credential_rejected']=json.loads(staged[oldprefix+'sources.json'])
    indexes['credential_rejected']=index_documents['credential_rejected']['sources']
    # Only explicit source indexes, declared raw parents and the four accepted
    # original artifact namespaces can add files. Reuse existing bytes first.
    indexed_parents={}
    for document in index_documents.values():
        for meta in document.get('parents',[]):
            ref=meta['artifact_ref'];require(ref not in indexed_parents or indexed_parents[ref]['sha256']==meta['sha256'],'conflicting parent index')
            indexed_parents[ref]=meta
    def retain_source(meta):
        ref=meta.get('artifact_ref',meta.get('path'));require(isinstance(ref,str),'missing source artifact')
        if ref in staged:return bind(ref,meta['sha256'])
        if safe(ref).is_file():return bind(ref,meta['sha256'])
        staged_file=meta.get('staged_path',meta.get('staged_file'))
        candidates=sorted([*LANES.values(),REJECTED_CREDENTIAL],key=lambda x:len(x[2]),reverse=True)
        selected=next((entry for entry in candidates if ref.startswith(entry[2])),None)
        require(selected is not None,'new source outside accepted namespaces '+ref)
        directory,_,prefix=selected;folder=(proposal/directory).resolve()
        source=Path(staged_file).resolve() if staged_file else (folder/ref[len(prefix):]).resolve()
        require(source.is_relative_to(folder),'new source outside corresponding accepted lane '+ref)
        raw=source.read_bytes();require(sha(raw)==meta['sha256'],'staged source hash '+ref);retain(ref,raw);return bind(ref,meta['sha256'])
    for source_index in indexes.values():
        for meta in source_index.values():retain_source(meta)
    for meta in indexed_parents.values():retain_source(meta)
    # Follow declared raw artifact identities only; no file or source-tree crawl.
    inspected=set()
    while True:
        todo=[ref for ref in artifacts if ref.endswith('.json') and ref not in inspected]
        if not todo:break
        for ref in todo:
            inspected.add(ref);raw=staged.get(ref) or safe(ref).read_bytes();data=json.loads(raw)
            def declared(value):
                if isinstance(value,dict):
                    for pathkey,hashkey in [('parent_artifact_ref','parent_sha256'),('raw_artifact_ref','raw_sha256')]:
                        if isinstance(value.get(pathkey),str) and isinstance(value.get(hashkey),str):yield value[pathkey],value[hashkey]
                    for child in value.values():yield from declared(child)
                elif isinstance(value,list):
                    for child in value:yield from declared(child)
            for dep,digest in declared(data):
                meta=indexed_parents.get(dep,{'artifact_ref':dep,'sha256':digest})
                require(meta['sha256']==digest,'declared parent differs from index '+dep);retain_source(meta)
    effective_sources={cid:copy.deepcopy(indexes[families[cid]]) for cid in decisions}
    require(len(decisions)==len(frozen)==107,'frozen106 plus one adjacent inventory')
    bind(ATTEMPT+'/integration-acceptance.json')
    source_hashes={s['source_file']:sha(safe(s['source_file']).read_bytes()) for item in frozen for s in item['claim']['spans']}
    inventory={'record_type':'FROZEN_HARDWARE_OPERATOR_INVENTORY','baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'claims':frozen,'source_hashes':source_hashes}
    changes={};replacement_spans={}
    for cid,d in decisions.items():
        c=claims[cid];require(d['literal_sha256']==sha(c['text'].encode()),'decision literal '+cid)
        require(d['decision'] in ('supported','correction','residual'),'decision kind '+cid)
        if d['decision']!='correction':
            require(not d.get('replacement_text'),'replacement on non-correction '+cid);continue
        replacement=d.get('replacement_text',d.get('proposed_replacement'))
        require(isinstance(replacement,str) and replacement!=c['text'] and len(c['spans'])==1,'exact correction '+cid)
        span=c['spans'][0];changes.setdefault(span['source_file'],[]).append({'id':cid,'start':span['start'],'end':span['end'],'before':c['text'],'after':replacement})
    require(claims['CUR-97f860901c54e022']['status']==decisions['CUR-97f860901c54e022']['proposed_status']=='PASS' and 'CUR-0384df43f8e6b914' in decisions,'SSH dependency/zero credit')
    # An explicitly accepted unclaimed heading is a physical source edit, not a
    # passage disposition. Bind current labels separately for exact root review.
    heading_approval=json.loads((proposal/LANES['hardware'][0]/'root-acceptance.json').read_bytes())['accepted_uncounted_context']
    context_raw=(proposal/LANES['hardware'][0]/heading_approval['file']).read_bytes()
    require(sha(context_raw)==heading_approval['sha256'],'accepted heading artifact')
    context=json.loads(context_raw)['separate_uncounted_context_edits_for_root_acceptance']
    require(len(context)==1,'uncounted heading scope')
    heading=context[0];ref=heading['source_file'];old_heading=heading['before'].removeprefix('## ');new_heading=heading['replacement_text'].removeprefix('## ')
    require(sha(heading['before'].encode())==heading['before_sha256'],'heading literal hash')
    lines=safe(ref).read_text().splitlines();matches=[n+1 for n,line in enumerate(lines) if line==heading['before']]
    require(len(matches)==1,'heading occurrence');heading_line=matches[0]
    require(not any(span['source_file']==ref and span['start']<=heading_line<=span['end'] for claim in claims.values() for span in claim['spans']),'heading is a claimed literal')
    changes.setdefault(ref,[]).append({'id':'UNCOUNTED-HARDWARE-HEADING','start':heading_line,'end':heading_line,'before':heading['before'],'after':heading['replacement_text'],'uncounted_context':True})
    heading_changes=[]
    for pi,page in enumerate(model['pages']):
        if page['source_file']!=ref:continue
        for ci,c in enumerate(page['claims']):
            if old_heading in c['headings']:
                heading_changes.append({'kind':'claim','id':c['id'],'model_pointer':f'/pages/{pi}/claims/{ci}','before_sha256':oh(c),'before_headings':c['headings'],'after_headings':[new_heading if h==old_heading else h for h in c['headings']],'selected':c['id'] in decisions,'status':c['status'],'resolved_credit':0})
        for qi,q in enumerate(page['procedures']):
            for ni,n in enumerate([q,*q['nodes']]):
                if old_heading in n.get('headings',[]):
                    heading_changes.append({'kind':'procedure','id':n['id'],'model_pointer':f'/pages/{pi}/procedures/{qi}'+(f'/nodes/{ni-1}' if ni else ''),'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'before_headings':n['headings'],'after_headings':[new_heading if h==old_heading else h for h in n['headings']],'status':n['status'],'resolved_credit':0})
    for item in heading_changes:
        item['history_key']='hardware_operator_heading_rebind'
        item['history_value']={'prior_headings':item['before_headings'],'baseline_model_sha256':BASELINE,'source_file':ref,'prior_heading_sha256':heading['before_sha256'],'reason':'Rebind the current navigation heading to the explicitly accepted Hardware Planning label; preserve literal, status, evidence and existing history.'}
    require(sum(x['kind']=='claim' for x in heading_changes)==8 and sum(x['kind']=='procedure' for x in heading_changes)==3,'exact heading metadata scope')
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
    scope={'acceptance_sha256':sha(acceptance_raw),'decisions':{},'procedures':{},'heading_changes':heading_changes,'historical_artifacts':historical};transitions=[]
    for cid,d in decisions.items():
        c=claims[cid];basis=[];ev=copy.deepcopy(c['evidence_refs']);refs=copy.deepcopy(c['source_refs'])
        for b in d['source_refs']:
            meta=effective_sources[cid][b['source']];ref=meta.get('artifact_ref',meta.get('path'));raw=bind(ref,meta['sha256'])
            excerpt=selection(raw,b['text_pointer']);require(excerpt==b['source_excerpt'],'exact source selector '+cid+' '+b['text_pointer'])
            url,revision,kind=module('current_host_verification_storage_review').source_origin(raw,b['text_pointer'],meta)
            basis.append({'sourceKey':b['source'],'artifactRef':ref,'text_pointer':b['text_pointer'],'excerpt':excerpt,'sourceUrl':url,'sourceRevision':revision,'sourceKind':kind,'support_rationale':d['support_rationale']})
            if not any(e['artifact_ref']==ref for e in ev):ev.append({'id':'HARDWARE-OPERATOR-'+cid+'-'+str(len(basis)),'role':kind,'limit':d['limitation'],'artifact_ref':ref})
            sr={'repository':meta.get('repository','retained-primary-source'),'revision':revision or 'sha256:'+meta['sha256'],'path':url or ref,'locator':b['text_pointer'],'source_kind':kind}
            if sr not in refs:refs.append(sr)
        after={'text':d.get('replacement_text',d.get('proposed_replacement',c['text'])),'status':d['proposed_status'],'classification':d['proposed_classification'],'required_evidence_types':d['proposed_methods'],'owner_role':d.get('proposed_owner_role',c['owner_role']),'rationale':d['support_rationale'],'next_action':CORRECTION_NEXT_ACTION if d['decision']=='correction' else (SOURCE_NEXT_ACTION if d['proposed_status'] in ('PASS','NOT_APPLICABLE') else d['next_action']),'evidence_refs':ev,'source_refs':refs,'coverage_state':'CHANGED'}
        if cid in replacement_spans:after['spans']=replacement_spans[cid]
        scope['decisions'][cid]={'accepted_decision_sha256':oh(d),'residual_topic':d.get('residual_topic'),'fields_sha256':oh({k:after[k] for k in ['text','status','classification','required_evidence_types','owner_role']}),'method_rationale':d['method_rationale']}
        transitions.append({'claim_id':cid,'before_sha256':oh(c),'after':after,'decision':d['decision'],'residual_topic':d.get('residual_topic'),'method':'SCOPED_HARDWARE_OPERATOR_REVIEW','method_rationale':d['method_rationale'],'limits':d['limitation'],'basis':basis})
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
                after={'spans':spans,'history':{**n.get('history',{}),'hardware_operator_review':{'prior_spans':copy.deepcopy(n['spans']),'before_source_root':ATTEMPT+'/sources-before/','reason':reason}},'coverage_state':'CHANGED'}
                procedures.append({'id':n['id'],'model_pointer':pointer,'before_sha256':oh({k:v for k,v in n.items() if k!='nodes'}),'after':after,'reason':reason});scope['procedures'][pointer]={'after':after,'reason':reason}
                comparisons.append({'id':n['id'],'model_pointer':pointer,'status':n['status'],'fences_unchanged':beforecmd==aftercmd,'before_fences_sha256':[sha(x.encode()) for x in beforecmd],'after_fences_sha256':[sha(x.encode()) for x in aftercmd],'before_fences':beforecmd,'after_fences':aftercmd,'before_spans':n['spans'],'after_spans':spans,'before_record_sha256':oh({k:v for k,v in n.items() if k!='nodes'})})
    corrections=[{'source_file':ref,**edit,'after_spans':replacement_spans[edit['id']]} for ref,edits in sorted(changes.items()) for edit in edits]
    impact={'reviewed_passages':106,'newly_resolved':105,'adjacent_pass_consistency_records':1,'physical_source_edits':sum(map(len,changes.values())),'literal_corrections':len(replacement_spans)-1,'uncounted_context_edits':1,'heading_metadata_changes':heading_changes,'historical_artifacts':historical,'accepted_lane_pins':acceptance['lanes'],'corrections':corrections,'changed_sources':list(texts),'out_of_scope_overlaps':overlaps,'affected_procedures':comparisons,'procedure_statuses_and_evidence_preserved':True,'baseline_commit':COMMIT,'baseline_model_sha256':BASELINE,'accepted_claim_count':len(decisions),'next_action_normalization':{'rule':acceptance['resolved_next_action_rule'],'deltas':[{'id':t['claim_id'],'accepted_next_action':decisions[t['claim_id']]['next_action'],'applied_next_action':t['after']['next_action']} for t in transitions if t['after']['next_action']!=decisions[t['claim_id']]['next_action']]}}
    from collections import Counter
    counts=Counter(c['status'] for c in claims.values());status_deltas=Counter()
    for cid,d in decisions.items():
        status_deltas[claims[cid]['status']+'->'+d['proposed_status']]+=1
        counts[claims[cid]['status']]-=1;counts[d['proposed_status']]+=1
    require(dict(counts)=={'PASS':1902,'FAIL':2,'BLOCKED':0,'NOT_APPLICABLE':95,'UNVALIDATED':9},'expected whole-population outcomes')
    impact['proposed_model_counts']=dict(counts);impact['claim_status_deltas']=dict(status_deltas)
    impact['preservation']={'claims':2008,'selected_transitions':107,'unselected_literal_status_and_evidence_records':1901,'unselected_heading_only_records':[x['id'] for x in heading_changes if x['kind']=='claim' and not x['selected']],'procedure_count':sum(len(p['procedures']) for p in model['pages']),'node_count':sum(len(q['nodes']) for p in model['pages'] for q in p['procedures']),'all_procedure_outcomes_unchanged':True,'all_earlier_registries_and_history_preserved':True,'source_reference_count':sum(len(d['source_refs']) for d in decisions.values()),'retained_source_artifact_hashes':[{'path':ref,'sha256':digest} for ref,digest in sorted(artifacts.items())]}
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
    registry={'schema_version':'1.0','record_type':'HOST_HARDWARE_OPERATOR_REVIEW','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':{'path':ATTEMPT+'/integration-scope.json','sha256':sha(staged[ATTEMPT+'/integration-scope.json'])},'sources':sources,'artifacts':[{'path':ref,'sha256':digest} for ref,digest in sorted(artifacts.items())],'transitions':transitions,'procedures':procedures,'limits':'106 frozen occurrences: 23 hardware,44 publication/advice,33 operator/UI,one credential and five previously BLOCKED instructions; plus one already-PASS adjacent SSH correction and one uncounted hardware heading. 105 newly resolved:99 previous UNVALIDATED,5 BLOCKED and1 FAIL. One AMD policy assertion remains UNVALIDATED. All actual prior credential failures, boot/GPU/Jupyter/self-test procedure outcomes, owner questions and every earlier sealed review remain retained. Source/instruction PASS does not establish new Host operations or universal backend behavior.'}
    registryraw=encoded(registry)
    print(json.dumps({'accepted_claims':len(transitions),'reviewed_passages':106,'newly_resolved':105,'corrections':len(replacement_spans)-1,'changed_sources':list(texts),'affected_procedures':len(procedures),'apply':args.apply}))
    if not args.apply:
        target=safe(ATTEMPT+'/impact-proposal.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(impact_raw)
        print(json.dumps({'impact_proposal':str(target),'sha256':sha(impact_raw)}));return
    require(not safe('verification/current-host-hardware-operator-review.json').exists(),'successor already exists; never overwrite a sealed attempt')
    for ref,raw in staged.items():
        target=safe(ref);require(not target.exists() or target.read_bytes()==raw,'existing attempt artifact differs '+ref);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    for ref,text in texts.items():safe(ref).write_text(text)
    safe('verification/current-host-hardware-operator-review.json').write_bytes(registryraw)
    pins={'PENDING_ACCEPTED_REGISTRY':sha(registryraw),'PENDING_ACCEPTED_INVENTORY':sha(staged[ATTEMPT+'/inventory.json']),'PENDING_ACCEPTED_BASELINE':sha(staged[ATTEMPT+'/integration-baseline.json'])}
    for suffix in ('py','mjs'):
        target=safe('scripts/current_host_hardware_operator_review.'+suffix);text=target.read_text()
        for token,digest in pins.items():require(token in text,'projector already sealed');text=text.replace(token,digest)
        target.write_text(text)
    print(json.dumps({'registry_sha256':sha(registryraw),'next':'Run paired projectors and inspect exact model/owner rebinding before generating the reviewer.'}))

if __name__=='__main__':main()
