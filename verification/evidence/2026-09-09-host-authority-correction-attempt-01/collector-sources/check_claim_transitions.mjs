import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='verification/evidence/2026-09-09-host-authority-correction-attempt-01';
const name=process.argv[2];assert.match(name||'',/^[a-z0-9-]+$/);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const frozen=fs.readFileSync(root+'/pre-authority-current-host-docs-review.json');
assert.equal(sha(frozen),'8b24aad067b2d98d41cd1824a31a831fa88f9a9cfaa8cb39379c6c37839bdaf9');
const before=JSON.parse(frozen),after=JSON.parse(fs.readFileSync('verification/current-host-docs-review.json'));
const editedRoutes=new Set(['/host/hosting-overview','/host/workload-policy','/host/hosting-agreement','/host/community']);
const procedures=[];
for(const page of before.pages){const current=after.pages.find(p=>p.route===page.route);for(const old of page.procedures){const now=current.procedures.find(p=>p.id===old.id);assert.ok(now,'Lost historical procedure '+old.id);if(!editedRoutes.has(page.route))assert.deepEqual(now,old);else{assert.equal(now.status,'STALE');assert.deepEqual(now.nodes.map(n=>[n.id,n.kind,n.parent_id,n.required]),old.nodes.map(n=>[n.id,n.kind,n.parent_id,n.required]));for(let i=0;i<now.nodes.length;i++){assert.equal(now.nodes[i].status,'STALE');assert.equal(now.nodes[i].history.baseline_status,old.nodes[i].status);}}procedures.push({id:old.id,route:page.route,prior_status:old.status,current_status:now.status,nodes:old.nodes.length});}}
const oldProcedureIds=new Set(procedures.map(p=>p.id));
const addedProcedures=after.pages.flatMap(p=>p.procedures.filter(q=>!oldProcedureIds.has(q.id)).map(q=>({route:p.route,...q})));
assert.equal(addedProcedures.length,4);
for(const p of addedProcedures){assert.ok(editedRoutes.has(p.route));assert.equal(p.title,'Current ordered section review');assert.equal(p.status,'UNVALIDATED');assert.ok(p.nodes.every(n=>n.kind==='CURRENT_HEADING_CHECK'&&n.status==='UNVALIDATED'));}
assert.deepEqual(after.support_layers,before.support_layers,'Central-reference support layers changed');
const technical=['MCL-508003945b6ef934','MCL-c85a4e96752730ab','MCL-437e58c77dcafecc','MCL-943ba22ec56a356a'];
const agreement=['MCL-805ef8a72833f2b8','MCL-3cfe1a3c265f0223','MCL-1a4146b033bd9b88','MCL-f855ff5e92cfbec1','MCL-181b0127498ba639'];
const partial=['MCL-ed68c47bda19e986','MCL-8fe2020c0e7efe26','MCL-399798a3c4946b5f'];
const changed=new Set([...technical,...agreement,...partial]);
const newById=new Map(after.pages.flatMap(p=>p.claims.map(c=>[c.id,{route:p.route,...c}])));
const oldById=new Map(before.pages.flatMap(p=>p.claims.map(c=>[c.id,{route:p.route,...c}])));
assert.equal(newById.size,after.pages.reduce((n,p)=>n+p.claims.length,0),'Duplicate occurrence ID');
const preserved=[],updates=[];
for(const [id,old]of oldById){const current=newById.get(id);assert.ok(current,'Lost predecessor occurrence '+id);if(changed.has(id)){updates.push({id,route:current.route,headings:current.headings,prior_status:old.status,current_status:current.status,prior_text:old.text,current_text:current.text,rationale:current.rationale,limitations:current.evidence_refs.map(r=>r.limit),next_action:current.next_action});continue;}for(const key of ['route','text','headings','status','required_evidence_types','owner_role','rationale','next_action','evidence_refs','source_refs','classification'])assert.deepEqual(current[key],old[key],id+' changed '+key+' outside explicit correction');preserved.push(id);}
for(const id of technical){const c=newById.get(id);assert.equal(c.status,'PASS');assert.equal(c.classification,'IMPLEMENTATION_OR_CONCEPT');assert.deepEqual(c.required_evidence_types,['CANONICAL_IMPLEMENTATION_SOURCE']);assert.match(c.evidence_refs[0].limit,/not.*enforcement/i);}
for(const id of agreement){const c=newById.get(id);assert.equal(c.status,'PASS');assert.equal(c.classification,'POLICY_OR_COMMERCIAL');assert.deepEqual(c.required_evidence_types,['AUTHORITATIVE_DOCUMENTATION_CITATION']);assert.equal(c.source_refs[0].path,'https://cloud.vast.ai/host/agreement');}
for(const id of partial){const c=newById.get(id);assert.equal(c.status,'FAIL');assert.match(c.rationale,/partial|subset|covers only/i);assert.deepEqual(c.required_evidence_types,oldById.get(id).required_evidence_types);assert.equal(c.owner_role,oldById.get(id).owner_role);assert.match(c.next_action,/source|owner/i);}
const additions=[...newById].filter(([id])=>!oldById.has(id)).map(([id,c])=>({id,route:c.route,headings:c.headings,status:c.status,text:c.text,rationale:c.rationale,next_action:c.next_action}));
assert.ok(additions.every(c=>!c.text.includes('className="persona-chips"')),'Presentation markup is not a material product claim');
assert.equal(additions.filter(c=>c.status==='PASS').length,1);assert.equal(newById.get('AUTH-DATA-SECURITY-01')?.status,'PASS');
assert.ok(newById.get('MCL-508003945b6ef934').text.includes('Minimum GPU count (`min_chunk`)'));
assert.ok(newById.get('MCL-437e58c77dcafecc').text.includes('Maximum prepaid discount (`discount_rate`)'));
assert.ok(!fs.readFileSync('host/hosting-agreement.mdx','utf8').includes('except where a documented platform or support process requires it'));
const candidates=JSON.parse(fs.readFileSync(root+'/candidate-inventory-01.json')).records.map(r=>({id:r.prior_claim.id,route:r.route,inspection_basis:r.inspection_basis,adjudicated:changed.has(r.prior_claim.id),status:newById.get(r.prior_claim.id).status,next_action:newById.get(r.prior_claim.id).next_action}));
fs.writeFileSync(root+'/'+name+'.json',JSON.stringify({recorded_at:new Date().toISOString(),status:'PASS',original_model_sha256:sha(frozen),current_model_sha256:sha(fs.readFileSync('verification/current-host-docs-review.json')),preserved_unchanged_claims:preserved.length,updated:updates,additions,candidates,procedures,added_source_review_records:addedProcedures.map(p=>({id:p.id,route:p.route,status:p.status,nodes:p.nodes.length,limits:p.limits})),limits:'Independent occurrence/history/status and scope accounting. Original procedures remain in the frozen predecessor; eight current carriers become STALE after source edits. Four added section-review records retain source coverage, not new Host workflows or runtime proof. The linked CLI, dated readback and agreement capture—not this manifest or documentation—supply substantive source evidence.'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'PASS',preserved_unchanged_claims:preserved.length,updated:updates.length,additions:additions.length,candidates:candidates.length}));
