"""Finite Tax Guide retirement after exact replay of the signed review history."""
import copy, hashlib, importlib.util, json, re
from collections import Counter
from pathlib import Path
REGISTRY='verification/current-host-tax-guide-retirement.json'
REGISTRY_SHA256='616212169f6e8d9a1a3a0e35296e96da6e0ce04ea9c63b770dfceea2f663ce8f'
ATTEMPT='verification/evidence/2026-09-15-host-tax-guide-retirement-attempt-01'
MARKER='HOST-TAX-GUIDE-RETIREMENT-01'
sha=lambda x:hashlib.sha256(x).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
oh=lambda x:sha(canon(x).encode())
def req(x,msg):
    if not x:raise ValueError('Tax Guide retirement: '+msg)
def project(root, frozen_source_overrides=None):
    root=Path(root);overrides=frozen_source_overrides or {}
    def read(ref):return overrides[ref] if ref in overrides else (root/ref).read_bytes()
    def pin(ref,wanted):
        raw=read(ref);req(sha(raw)==wanted,'digest drift '+ref);return raw
    r=json.loads(pin(REGISTRY,REGISTRY_SHA256));req(r['record_type']=='HOST_TAX_GUIDE_RETIREMENT','registry type')
    before={};current={}
    for s in r['sources']:
        before[s['path']]=pin(s['before_artifact']['path'],s['before_artifact']['sha256'])
        if s['removed']:req(s['path']=='host/guide-to-taxes.mdx' and not (root/s['path']).exists(),'removed source is still current');continue
        text=before[s['path']].decode()
        for e in s['edits']:req(text.count(e['before'])==1,'edit occurrence');text=text.replace(e['before'],e['after'],1)
        current[s['path']]=pin(s['path'],s['after_sha256']);req(current[s['path']]==text.encode(),'unaccepted source change')
    before['verification/current-host-owner-questions.json']=pin(r['before_owners']['path'],r['before_owners']['sha256'])
    spec=importlib.util.spec_from_file_location('tax_retirement_pre',Path(__file__).with_name('current_host_final_owner_review.py'));pre=importlib.util.module_from_spec(spec);spec.loader.exec_module(pre)
    baseline=pre.project(root,frozen_source_overrides={**overrides,**before});req(oh(baseline)==r['baseline_canonical_sha256'],'whole predecessor drift')
    archive=json.loads(pin(r['archive']['path'],r['archive']['sha256']));owners=json.loads(pin(r['before_owners']['path'],r['before_owners']['sha256']));instruction=json.loads(pin(r['instruction']['path'],r['instruction']['sha256']))
    req(instruction['comment']['id']=='34984' and 'just remove this tax section entirely.' in instruction['comment']['body'],'removal instruction')
    old={c['id']:c for p in baseline['pages'] for c in p['claims']};retired=set(r['retired_claim_ids']);page=next(p for p in baseline['pages'] if p['route']==r['retired_route'])
    req(archive['page']==page and archive['faq_claim']==old['MCL-7b86589912c968bb'],'retired record drift')
    req(retired=={c['id'] for c in page['claims']}|{'MCL-7b86589912c968bb'} and len(retired)==16,'retired scope')
    req(archive['owner_question']==next(q for q in owners['questions'] if q['id']=='HQ-VAST-TAX-HANDLING') and r['retired_owner_ids']==['HQ-VAST-TAX-HANDLING'],'retired owner scope')
    m=copy.deepcopy(baseline);m['pages']=[p for p in m['pages'] if p['route']!=r['retired_route']]
    patches={c['id']:c for c in r['claims']};seen=set();seenprocs=set()
    def verify(s):
        lines=(current.get(s['source_file']) or read(s['source_file'])).decode().splitlines();req(0<s['start']<=s['end']<=len(lines),'span bounds');text='\n'.join(lines[s['start']-1:s['end']]);req(sha(text.encode())==s['text_sha256'],'span literal drift');return text
    for p in m['pages']:
        p['claims']=[c for c in p['claims'] if c['id'] not in retired]
        if p['source_file'] in current:p['source_sha256']=sha(current[p['source_file']]);p['coverage_state']='CHANGED'
        for i,c in enumerate(p['claims']):
            if c['id'] in patches:
                patch=patches[c['id']];req(oh(c)==patch['before_sha256'],'claim before drift');new=copy.deepcopy(patch['after']);changed=patch['text_changed']
                allowed={'spans','text','history'} if changed else {'spans'}
                req({k:v for k,v in c.items() if k not in allowed}=={k:v for k,v in new.items() if k not in allowed},'unaccepted claim fields')
                if changed:req(c['id'] in {'MCL-e9c7af0148732c9b','MCL-335de916e219e04a'} and all(new['history'].get(k)==v for k,v in c.get('history',{}).items()),'referral history')
                p['claims'][i]=new;c=new;seen.add(c['id'])
            for s in c['spans']:verify(s)
        for pi,proc in enumerate(p['procedures']):
            for ni,node in enumerate([proc,*proc['nodes']]):
                entry=next((e for e in r['procedures'] if e['route']==p['route'] and e['procedure_index']==pi and e['node_index']==(None if ni==0 else ni-1)),None)
                if entry:
                    req(oh({k:v for k,v in node.items() if k!='nodes'})==entry['before_sha256'] and node['id']==entry['id'],'procedure before drift')
                    oldtext='\n'.join('\n'.join((before.get(s['source_file']) or read(s['source_file'])).decode().splitlines()[s['start']-1:s['end']]) for s in node['spans']);newtext='\n'.join(verify(s) for s in entry['spans'])
                    fences=lambda t:re.findall(r'^```[^\n]*\n.*?^```',t,re.M|re.S)
                    req(entry['fences_unchanged'] and fences(oldtext)==fences(newtext),'command fence changed');node['spans']=copy.deepcopy(entry['spans']);seenprocs.add((p['route'],pi,ni))
                for s in node['spans']:verify(s)
    req(seen==set(patches) and len(seenprocs)==len(r['procedures']),'patch scope')
    m['source']['source_manifest']=[s for s in m['source']['source_manifest'] if s['path']!='host/guide-to-taxes.mdx']
    for s in m['source']['source_manifest']:
        if s['path'] in current:s['sha256']=sha(current[s['path']])
    m['source']['primary_route_count']=43
    counts=m['counts'];counts.update(primary_pages=43,total_host_routes=43,total_reviewed_layers=76,claims=1992,procedures=114,procedure_nodes=1071)
    counts['claim_statuses']=dict(sorted(Counter(c['status'] for p in m['pages'] for c in p['claims']).items()));counts['page_coverage_states']=dict(sorted(Counter(p['coverage_state'] for p in m['pages']).items()))
    req(counts['claim_statuses']=={'NOT_APPLICABLE':94,'PASS':1898},'retirement accounting')
    m['generated_at']=r['generated_at'];m['corrections'].append({'id':MARKER,'scope':'Tax Guide page and its FAQ referral retired; two payout referrals narrowed.','history':'All 16 retired passages, two procedures, 14 nodes and the tax owner question remain in the immutable retirement archive and predecessor evidence.','current':'43 pages and 1,992 current passages. Tax guidance and its current owner follow-up are removed; zero new validation credit.','reason':r['limits']})
    return m
