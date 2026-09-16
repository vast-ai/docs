from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;AR=str(A.relative_to(R));sha=lambda b:hashlib.sha256(b).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
policy=json.loads((A/'cpu-policy-residual-proposals.json').read_text());assert sha((A/'cpu-policy-residual-proposals.json').read_bytes())=='da8494b40fb89b2053e9ef36583db6715d0f89a39587e13b3375e5f5e9fbd97b'
dup=json.loads((A/'duplicate-diagnostic-scope.json').read_text());claims=dup['claims'][:]
for p in policy['proposals']:
 c=p['before_claim'];claims.append({'id':c['id'],'page':c['spans'][0]['source_file'],'lane':'cpu-policy','literal_sha256':p['literal_sha256'],'claim_canonical_sha256':sha(canon(c).encode()),'claim':c})
paths={x['page'] for x in claims};hashes={p:sha((A/'sources-before'/p).read_bytes()) for p in paths}
record={'record_type':'FROZEN_SUPPLEMENTAL_SCOPE_REVISION_02','state':'ACCEPTED_BY_ROOT_FOR_INTEGRATION','scope_count':6,'claims':claims,'source_hashes':hashes,'groups':[{'source_family':'b-hardware-install','proposals_ref':str(A.relative_to(R)/'duplicate-diagnostic-proposals.json'),'proposals_sha256':dup['proposals_sha256']},{'source_family':'cpu-policy','proposals_ref':str(A.relative_to(R)/'cpu-policy-residual-proposals.json'),'proposals_sha256':sha((A/'cpu-policy-residual-proposals.json').read_bytes())}],'policy_sources':policy['source_registry'],'preserved_scope':'Original309 inventory plus original3 adjacent scope remain immutable; final scope adds exactly these6, totaling318. No further literal expansion.','acceptance_ref':AR+'/root-supplemental-acceptance-02.json'}
p=A/'supplemental-scope-02.json';p.write_text(json.dumps(record,indent=2)+'\n');supp=sha(p.read_bytes());oldpin=sha((R/'verification/current-host-evidence-reuse-review.json').read_bytes())
for ext in ['py','mjs']:
 p=R/f'scripts/current_host_evidence_reuse_review.{ext}';s=p.read_text();assert oldpin in s;s=s.replace(oldpin,'PENDING_REVISION_02_REGISTRY').replace('integration-scope.json','integration-scope-02.json').replace('312 frozen occurrences (309 review + 3 adjacent fixes)','318 frozen occurrences (309 review + 5 adjacent corrections + 4 policy residuals)').replace('===312','===318').replace('==312','==318')
 if ext=='py':
  s=s.replace("MARKER =",f"SUPPLEMENTAL_SHA256 = '{supp}'\nMARKER =",1)
  s=s.replace("frozen_claims=[*inventory['claims'],*expansion['claims']]","supplemental=json.loads(pin(ATTEMPT+'/supplemental-scope-02.json',SUPPLEMENTAL_SHA256))\n    frozen_claims=[*inventory['claims'],*expansion['claims'],*supplemental['claims']]")
  s=s.replace("inventory['source_hashes'].update(expansion['source_hashes'])","inventory['source_hashes'].update(expansion['source_hashes']);inventory['source_hashes'].update(supplemental['source_hashes'])")
  s=s.replace("len(expansion['claims'])==3", "len(expansion['claims'])==3 and len(supplemental['claims'])==6")
 else:
  s=s.replace("const ADJACENT_SHA256=",f"const SUPPLEMENTAL_SHA256='{supp}';\nconst ADJACENT_SHA256=",1)
  s=s.replace("frozenClaims=[...inventory.claims,...expansion.claims]", "supplemental=JSON.parse(pin(A+'/supplemental-scope-02.json',SUPPLEMENTAL_SHA256)),frozenClaims=[...inventory.claims,...expansion.claims,...supplemental.claims]")
  s=s.replace("Object.assign(inventory.source_hashes,expansion.source_hashes)", "Object.assign(inventory.source_hashes,expansion.source_hashes,supplemental.source_hashes)")
  s=s.replace("expansion.claims.length===3", "expansion.claims.length===3&&supplemental.claims.length===6")
  s=s.replace("[A+'/adjacent-scope.json',ADJACENT_SHA256],", "[A+'/adjacent-scope.json',ADJACENT_SHA256],[A+'/supplemental-scope-02.json',SUPPLEMENTAL_SHA256],")
  s=s.replace("resultRef:A+'/result.md'","resultRef:A+'/result-02.md'")
 p.write_text(s)
print('supplemental scope',supp,'policy IDs',[p['id'] for p in policy['proposals']])
