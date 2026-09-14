#!/usr/bin/env python3
"""Sealed published-guidance correction above the payout-Terms projection."""
from __future__ import annotations
import copy, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path
from typing import Any

REGISTRY='verification/current-host-payout-invoice-correction.json'; REGISTRY_SHA256='e956e3c121459722e024217eb371848d06c4e1252ef43f6ea8d895568bd7a7d6'
ATTEMPT='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01'; BASELINE=ATTEMPT+'/pre-correction-model.json'; BASELINE_SHA256='9873666e659403459d9d0c7a10f8cd3d4372709d86e26c396d0ef604cd13d257'; BEFORE=ATTEMPT+'/pre-correction-payment.mdx'; BEFORE_SHA256='6171ba7c1575be13bdbed837c9ea941c2a3314971c726dcd27f6fb2fd3932442'; GUIDANCE=ATTEMPT+'/published-invoice-guidance-01.json'; GUIDANCE_SHA256='9e4a9ff965510e9c08f6c45c929ab5a180d882e7dfe6c14bd65b7b30cef5814c'; SOURCE='host/payment.mdx'; MARKER='HOST-PAYOUT-INVOICE-CORRECTION-01'
CHANGED={53,54,55,58,84,106}
IDS={'MCL-e2b956d14494e470':(53,'minimum-payout-threshold'),'MCL-df7b287adb0df683':(54,'invoice-generation'),'MCL-3d796f5ae7f2020e':(55,'payment-timeline'),'MCL-5936430d1b2d8de9':(58,'minimum-payout-threshold'),'MCL-3afd93ae0b6cf8a4':(84,'payment-timeline'),'MCL-bbd64c772e9b4693':(106,'invoice-generation')}
LIMIT='Published guidance checked. This checks what Vast publishes. It does not test invoice generation or payment processing.'

def sha(v:bytes)->str:return hashlib.sha256(v).hexdigest()
def canon(v:Any)->Any:return {k:canon(v[k]) for k in sorted(v)} if isinstance(v,dict) else [canon(x) for x in v] if isinstance(v,list) else v
def objhash(v:Any)->str:return sha(json.dumps(canon(v),separators=(',',':'),ensure_ascii=False).encode())
def fail(m):raise ValueError('payout invoice correction: '+m)
def req(v,m):
 if not v:fail(m)
def mod(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py')); result=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(result); return result
def safe(root:Path,ref:str)->Path:
 req(isinstance(ref,str) and ref and not ref.startswith('/') and '\\' not in ref and all(p not in {'','.','..'} for p in ref.split('/')),'unsafe path')
 path=root.resolve()
 for p in ref.split('/'):
  path/=p;req(not path.is_symlink(),'unsafe symlink')
 req(path.is_file() and path.resolve().is_relative_to(root.resolve()),'missing path '+ref);return path
def pin(root,ref,wanted):
 value=safe(root,ref).read_bytes();req(sha(value)==wanted,'digest drift '+ref);return value
def span(line,lines):return {'source_file':SOURCE,'start':line,'end':line,'text_sha256':sha(lines[line-1].encode())}

def predecessor(root,baseline,before):
 terms=mod('current_host_payout_terms_correction'); original=terms.pin
 def oldpin(inner,ref,wanted):
  if ref==SOURCE:req(sha(before)==wanted,'predecessor source drift');return before
  return original(inner,ref,wanted)
 terms.pin=oldpin
 req(terms.project(root)==baseline,'sealed payout Terms predecessor differs from invoice baseline')

def project(root:Path)->dict[str,Any]:
 root=root.resolve(); registry=json.loads(pin(root,REGISTRY,REGISTRY_SHA256))
 req(set(registry)=={'schema_version','record_type','generated_at','baseline','source','guidance','transitions'},'registry keys')
 req(registry['schema_version']=='1.0' and registry['record_type']=='HOST_PAYOUT_INVOICE_CORRECTION','registry type')
 req(registry['baseline']=={'path':BASELINE,'sha256':BASELINE_SHA256},'baseline')
 req(registry['guidance']=={'path':GUIDANCE,'sha256':GUIDANCE_SHA256},'guidance')
 req(registry['source']['path']==SOURCE and registry['source']['before_artifact']=={'path':BEFORE,'sha256':BEFORE_SHA256} and registry['source']['before_sha256']==BEFORE_SHA256 and registry['source']['changed_lines']==sorted(CHANGED),'source scope')
 before=pin(root,BEFORE,BEFORE_SHA256);after=pin(root,SOURCE,registry['source']['after_sha256']);oldlines=before.decode().splitlines(); lines=after.decode().splitlines()
 req(len(oldlines)==len(lines) and {i+1 for i,(a,b) in enumerate(zip(oldlines,lines)) if a!=b}==CHANGED,'source edits exceed six approved lines')
 guidance=json.loads(pin(root,GUIDANCE,GUIDANCE_SHA256)); sections={s['heading_id']:s for s in guidance.get('sections',[])}
 req(guidance.get('url')=='https://docs.vast.ai/host/payment' and guidance.get('limitations')=='This records current published Vast guidance from the same docs repository. It is not independent backend scheduling, account enforcement, actual payment, or owner approval evidence. The deployed Git revision is not identified by the page.','guidance provenance')
 req(set(sections)=={'minimum-payout-threshold','invoice-generation','payment-timeline','when-will-i-get-paid','my-account-is-not-generating-invoices'} and all(s['text_sha256']==sha(s['text'].encode()) for s in sections.values()),'guidance sections')
 req('$20 USD before an invoice can be generated.' in sections['minimum-payout-threshold']['text'] and 'roll forward until the minimum threshold' in sections['minimum-payout-threshold']['text'] and 'weekly on Fridays' in sections['invoice-generation']['text'] and 'valid payout method connected' in sections['invoice-generation']['text'] and 'up to two weeks to receive your first payout' in sections['payment-timeline']['text'] and 'depending on the provider and your region' in sections['payment-timeline']['text'],'guidance wording')
 baseline=json.loads(pin(root,BASELINE,BASELINE_SHA256)); predecessor(root,baseline,before); old={c['id']:c for p in baseline['pages'] for c in p['claims']};req(len(old)==2013 and set(IDS)<=set(old),'claim inventory')
 req({x.get('claim_id'):x.get('before_sha256') for x in registry['transitions']}=={k:objhash(old[k]) for k in IDS},'claim predecessor')
 result=copy.deepcopy(baseline);claims={c['id']:c for p in result['pages'] for c in p['claims']}
 def evidence(anchor):return {'id':'EV-PAYOUT-INVOICE-GUIDANCE-01-'+anchor,'role':'PUBLISHED_PAYOUT_INVOICE_GUIDANCE','limit':LIMIT,'artifact_ref':GUIDANCE}
 def source(anchor):return {'repository':'official-publication','revision':'sha256:'+GUIDANCE_SHA256,'path':'https://docs.vast.ai/host/payment#'+anchor,'locator':'/sections/'+str(list(sections).index(anchor))+'/text','source_kind':'AUTHORITATIVE_DOCUMENTATION_CITATION'}
 for cid,(line,anchor) in IDS.items():
  prior,claim=old[cid],claims[cid]; agreement=list(prior.get('source_refs',[])); agreement_evidence=list(prior.get('evidence_refs',[]))
  claim.update({'text':lines[line-1],'spans':[span(line,lines)],'status':'PASS','classification':'PUBLISHED_FINANCIAL_GUIDANCE_DESCRIPTION','required_evidence_types':['AUTHORITATIVE_DOCUMENTATION_CITATION'],'owner_role':'Documentation authoritative-source reviewer','rationale':'Exact attributed published payout guidance supports this wording only. '+LIMIT,'next_action':'Recheck this exact published guidance section if its wording or anchor changes.','evidence_refs':[evidence(anchor),*agreement_evidence],'source_refs':[source(anchor),*agreement],'coverage_state':'CHANGED','history':{**prior['history'],'carry_decision':'CURRENT_HOST_PAYOUT_INVOICE_CORRECTION','reason':prior['history'].get('reason','')+' Exact published-guidance correction; no backend scheduling, account enforcement, actual payment, or owner approval is inferred.','predecessor':{'claim_id':cid,'status':prior['status'],'text':prior['text'],'text_sha256':sha(prior['text'].encode())}}})
 page=next(p for p in result['pages'] if p['source_file']==SOURCE);page['source_sha256']=sha(after);page['coverage_state']='CHANGED'
 req(all(c['id'] in IDS or not any(s['start']<=line<=s['end'] for s in c['spans'] for line in CHANGED) for c in page['claims']),'unrelated claim drift')
 for procedure in page['procedures']:
  for node in [procedure,*procedure['nodes']]:
   if any(s['start']<=line<=s['end'] for s in node.get('spans',[]) for line in CHANGED):
    node['spans']=[];node['status']='STALE';node['coverage_state']='CHANGED';node['limits']=[*node.get('limits',[]),'Payout/invoice source span changed; no procedure evidence transfers.'];node['history']={**node.get('history',{}),'carry_decision':'CURRENT_HOST_PAYOUT_INVOICE_CORRECTION_SOURCE_CHANGED'}
 for item in result['source']['source_manifest']:
  if item['path']==SOURCE:item['sha256']=sha(after)
 req(sum(old[k]==claims[k] for k in old)==2007,'unrelated claim drift')
 result['counts']['claim_statuses']=dict(sorted(Counter(c['status'] for c in claims.values()).items()));result['generated_at']=registry['generated_at'];result['corrections'].append({'id':MARKER,'scope':'Six exact Host Payouts invoice/payout guidance occurrences','history':'Payout Terms predecessor and pre-correction payment source are hash-pinned.','current':'Four former FAIL and two formerly UNVALIDATED occurrences are attributed to captured published guidance; agreement evidence remains separately bounded.','reason':'Published guidance only; no backend scheduling, invoice generation, payment processing, account enforcement, Finance approval, or owner acknowledgement is inferred.'});return result
def validate_model(model,root):req(model==project(root),'whole model differs from payout/invoice projection')
def load_payout_invoice_correction(root,model):
 present=(root/REGISTRY).is_file();marked=any(x.get('id')==MARKER for x in model.get('corrections',[]))
 if not present:req(not marked,'invoice-marked model has no registry');return None
 projected=project(root);req(model==projected,'whole model differs from payout/invoice projection');return {'registry':REGISTRY,'registry_sha256':REGISTRY_SHA256,'baseline':BASELINE,'guidance':GUIDANCE}
