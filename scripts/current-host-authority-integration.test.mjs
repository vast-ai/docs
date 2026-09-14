/** Active-scan integration. All mutations are isolated temporary fixtures.
 * VV_SCAN_FIXTURE_ROOT / VV_SCAN_FIXTURE_PRODUCER are test-only inputs used to
 * inspect an unsealed candidate; the production reader has no override path.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fsSync from 'node:fs';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import vm from 'node:vm';
import {spawn,execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
const CODE_ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const INPUT_ROOT=process.env.VV_SCAN_FIXTURE_ROOT||CODE_ROOT;
const REGISTRY='verification/current-host-authority-scan.json';
const JURISDICTION_REGISTRY='verification/current-host-jurisdiction.json';
const CLEANUP_REGISTRY='verification/current-host-review-cleanup.json';
const PAYOUT_TERMS_REGISTRY='verification/current-host-payout-terms-correction.json';
const PAYOUT_INVOICE_REGISTRY='verification/current-host-payout-invoice-correction.json';
const jurisdictionLabels=new Map([
 ['CUR-708c718cf735c8b2','Advice checked'],['CUR-555543e9b2ceddb4','Advice checked'],['CUR-2ead4eda972e84b0','Advice checked'],
 ['MCL-8fe2020c0e7efe26','Advice and rule checked'],
 ['MCL-1536a1bd58d80927','Published program source checked'],['MCL-c9882f043e407640','Published program source checked'],
 ['MCL-c8bf23127171e2b0','Published program source checked'],['MCL-3acecd71e6a7b312','Published program source checked'],
]);
const hash=value=>crypto.createHash('sha256').update(value).digest('hex');
const registryBytes=await fs.readFile(path.join(INPUT_ROOT,REGISTRY)).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
const listen=server=>new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',()=>resolve(server.address().port));});
async function sibling(name){let cursor=process.env.VV_TEST_SOURCE_ROOT?path.resolve(process.env.VV_TEST_SOURCE_ROOT,'docs'):CODE_ROOT;for(;;){try{return await fs.realpath(path.join(path.dirname(cursor),name));}catch{}const parent=path.dirname(cursor);if(parent===cursor)throw Error(`Missing pinned external fixture ${name}`);cursor=parent;}}
async function fixture(){
 const container=await fs.mkdtemp(path.join(os.tmpdir(),'host-authority-integration-')),root=path.join(container,'docs');await fs.mkdir(root);
 for(const name of ['vast-cli','self-test'])await fs.symlink(await sibling(name),path.join(container,name),'dir');
 for(const ref of ['.git','docs.json','host','snippets','cli','sdk','verification','host-docs-cli-command-check.json'])await fs.cp(path.join(INPUT_ROOT,ref),path.join(root,ref),{recursive:true});
 await fs.mkdir(path.join(root,'scripts/templates'),{recursive:true});
 for(const ref of ['review-server.mjs','scripts/current_host_authority_scan.mjs','scripts/current_host_clarification.mjs','scripts/current_host_terms_binding.mjs','scripts/current_host_jurisdiction.mjs','scripts/current_host_review_transition.mjs','scripts/current_host_payout_terms_correction.mjs','scripts/current_host_payout_invoice_correction.mjs','scripts/current_host_install_evidence_intake.mjs','scripts/export_host_review_html.mjs','scripts/templates/host-docs-review.html'])await fs.copyFile(path.join(CODE_ROOT,ref),path.join(root,ref));
 await fs.copyFile(path.join(CODE_ROOT,'scripts/host_review_reader_copy.mjs'),path.join(root,'scripts/host_review_reader_copy.mjs'));
 await fs.copyFile(path.join(CODE_ROOT,'scripts/host_review_work_queue.mjs'),path.join(root,'scripts/host_review_work_queue.mjs'));
 await fs.copyFile(path.join(CODE_ROOT,'scripts/current_host_review_cleanup.mjs'),path.join(root,'scripts/current_host_review_cleanup.mjs')).catch(error=>{if(error.code!=='ENOENT')throw error;});
 await fs.copyFile(path.join(CODE_ROOT,'scripts/current_host_payout_provider_correction.mjs'),path.join(root,'scripts/current_host_payout_provider_correction.mjs'));
 if(process.env.VV_SCAN_FIXTURE_PRODUCER){
  const digest=hash(registryBytes),script="import importlib.util,json,sys,pathlib;spec=importlib.util.spec_from_file_location('scan',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.REGISTRY_SHA256=sys.argv[3];print(json.dumps(m.project(pathlib.Path(sys.argv[2])),ensure_ascii=False))";
  const model=execFileSync('python3',['-c',script,process.env.VV_SCAN_FIXTURE_PRODUCER,INPUT_ROOT,digest],{maxBuffer:20000000});
  await fs.writeFile(path.join(root,'verification/current-host-docs-review.json'),model);
  const gate=path.join(root,'scripts/current_host_authority_scan.mjs');await fs.writeFile(gate,(await fs.readFile(gate,'utf8')).replace("AUTHORITY_SCAN_REGISTRY_SHA256 = 'UNSEALED'",`AUTHORITY_SCAN_REGISTRY_SHA256 = '${digest}'`));
  // Candidate presentation fixtures do not claim a final result. Production
  // runs read the real retained summary and separate registers without stubs.
  const attempt='verification/evidence/2026-09-09-host-authority-scan-attempt-01';
  for(const name of ['result.md','runtime-operator-register.md','source-owner-register.md'])try{await fs.access(path.join(root,attempt,name));}catch{await fs.writeFile(path.join(root,attempt,name),'# Isolated candidate presentation fixture\nNot a retained product result.\n',{flag:'wx'});}
 }
 return {root,container,model:JSON.parse(await fs.readFile(path.join(root,'verification/current-host-docs-review.json'),'utf8'))};
}
test('active scan retains all current pages and exact source selectors; tampering invalidates the reader',{skip:!registryBytes},async()=>{
 const f=await fixture();let child,target;let logs='';
 try{
  const jurisdictionRegistry=await fs.readFile(path.join(f.root,JURISDICTION_REGISTRY),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
  target=http.createServer((req,res)=>res.end('<!doctype html><main>Local review fixture</main>'));const targetPort=await listen(target);
  const probe=http.createServer(),port=await listen(probe);await new Promise(resolve=>probe.close(resolve));
  child=spawn(process.execPath,['review-server.mjs','--port',String(port),'--target',`http://127.0.0.1:${targetPort}`,'--dir',path.join(f.root,'feedback')],{cwd:f.root,env:{...process.env,VAST_REVIEW_DEBUG:'1'},stdio:['ignore','pipe','pipe']});child.stdout.on('data',data=>logs+=data);child.stderr.on('data',data=>logs+=data);
  const origin=`http://127.0.0.1:${port}`;
  const context=async route=>{for(let i=0;i<600;i++){try{const response=await fetch(`${origin}/__review__/api/context?path=${encodeURIComponent(route)}`);if(response.ok)return response.json();}catch{}await new Promise(resolve=>setTimeout(resolve,25));}throw Error(`Local reader did not start: ${logs}`);};
  let seen=0,controls=0,sameSource=0,readonlyClaims=0,readonlyControls=0;const reviews=[];
  for(const page of f.model.pages){const current=await context(page.route);assert.equal(current.currentReview.available,true,String(current.currentReview.unavailableReason)+logs);assert.equal(current.currentReview.page.claims.length,page.claims.length);seen+=page.claims.length;
   reviews.push(current.currentReview);
   for(const claim of current.currentReview.page.claims){
    if(claim.readonlyProof){readonlyClaims++;
     for(const check of claim.readonlyProof.checks){
      const href=`${origin}/__review__/current-artifact?ref=${encodeURIComponent(check.artifactRef)}&page=${encodeURIComponent(page.route)}&claim=${encodeURIComponent(claim.id)}&readonly=${encodeURIComponent(check.id)}`;
      const response=await fetch(href);assert.equal(response.status,200,href);const selected=await response.text();
      assert.match(selected,/Selected observation/);assert.ok(selected.includes(check.id));assert.ok(selected.includes(check.artifactSha256));assert.match(selected,/Scope limit/);assert.doesNotMatch(selected,/previous_claim|Original finding|Open runtime adjudication record/);
      assert.equal((await fetch(href.replace(`&readonly=${check.id}`,'&readonly=UNBOUND-CHECK'))).status,404);
      assert.equal((await fetch(href.replace(`&page=${encodeURIComponent(page.route)}`,'&page=%2Fhost%2Fhosting-overview'))).status,404);
      readonlyControls++;
     }
    }
    const transition=claim.authorityScan;if(!transition)continue;
    for(const [index,basis]of transition.basis.entries()){
     const href=`${origin}/__review__/current-artifact?ref=${encodeURIComponent(basis.artifactRef)}&page=${encodeURIComponent(page.route)}&claim=${encodeURIComponent(claim.id)}&basis=${index}`;
     const response=await fetch(href);assert.equal(response.status,200,href);const html=await response.text();const reviewOnly=basis.kind==='CONTEXT_REVIEW'||basis.kind==='DOCUMENTATION_CHECK';assert.ok(html.includes(reviewOnly?'Review scope:':'What this source proves:'));assert.ok(html.includes('What remains:'));assert.doesNotMatch(html,/Original finding|transition history|Open frozen/);assert.ok(basis.sourceLabel&&basis.sourceLocator);assert.ok(html.includes(basis.sourceLabel.replaceAll('&','&amp;')));if(basis.kind==='DOCUMENTATION_CHECK'){assert.equal(basis.sourceLabel,'Documentation check');assert.equal(basis.sourceUrl,null);assert.match(html,/<h1>Exact documentation check<\/h1>/);assert.doesNotMatch(html,/What this source proves:|Open canonical source/);}else if(basis.sourceUrl)assert.ok(html.includes(basis.sourceUrl.replaceAll('&','&amp;')));assert.doesNotMatch(html,/https:\/\/cloud\.vast\.ai\/host\/agreement#/);
     assert.equal((await fetch(href.replace(`&basis=${index}`,'&basis=99999'))).status,404);controls++;if(transition.basis.slice(0,index).some(prior=>prior.artifactRef===basis.artifactRef))sameSource++;
    }
   }
  }
  assert.equal(seen,2013);assert.ok(controls>0);assert.ok(sameSource>0,'multiple excerpts from the same artifact remain separately selectable');
  assert.equal(readonlyClaims,10);assert.ok(readonlyControls>=10);
  if(f.model.corrections.some(entry=>entry.id==='HOST-TERMS-BINDING-01')){
   const termsIds=new Set(['MCL-99ca28f707d5966a','MCL-2c3f7082e2c7fdf2','MCL-c4c4bfc59eb7b49f','MCL-399798a3c4946b5f','MCL-633317ca7ebecfef','MCL-fe3eccd1cd40b4bd']);
   assert.deepEqual(f.model.counts.claim_statuses,f.model.pages.flatMap(page=>page.claims).reduce((counts,claim)=>{counts[claim.status]=(counts[claim.status]||0)+1;return counts;},{}));
   const termsClaims=reviews.flatMap(review=>review.page.claims).filter(claim=>termsIds.has(claim.id));
   assert.equal(termsClaims.length,termsIds.size);
   for(const claim of termsClaims){assert.equal(claim.status,'PASS',claim.id);assert.deepEqual(claim.requiredEvidenceTypes,['AUTHORITATIVE_DOCUMENTATION_CITATION'],claim.id);assert.equal(claim.readerCopy.reviewKind,'published-terms-source',claim.id);assert.match(claim.readerCopy.finding,/does not prove runtime enforcement/i,claim.id);assert.equal(claim.readerCopy.pendingNote,undefined,claim.id);assert.ok(claim.authorityScan?.basis.some(basis=>basis.sourceUrl==='https://vast.ai/terms'),claim.id);}
  }
  if(jurisdictionRegistry){
   const selected=reviews.flatMap(review=>review.page.claims).filter(claim=>jurisdictionLabels.has(claim.id));
   assert.equal(selected.length,8);assert.deepEqual(jurisdictionRegistry.transitions.map(row=>row.claim_id).sort(),[...jurisdictionLabels.keys()].sort());
   for(const claim of selected){
    const decision=jurisdictionRegistry.transitions.find(row=>row.claim_id===claim.id),transition=claim.authorityScan;
    assert.equal(claim.status,'PASS',claim.id);assert.equal(claim.readerCopy.statusLabel,jurisdictionLabels.get(claim.id),claim.id);
    assert.deepEqual(claim.requiredEvidenceTypes,decision.after.required_evidence_types,claim.id);
    assert.equal(transition.registryRef,JURISDICTION_REGISTRY,claim.id);assert.equal(transition.basis.length,decision.basis.length,claim.id);
    assert.ok(transition.auditHistory.length,`previous source history retained: ${claim.id}`);
    for(const [index,basis]of transition.basis.entries()){
     const expected=decision.basis[index],artifact=jurisdictionRegistry.artifacts.find(item=>item.id===expected.artifact_id);
     assert.equal(basis.sourceLabel,artifact.source_label,claim.id);assert.equal(basis.sourceLocator,expected.source_locator,claim.id);
     assert.equal(basis.text_pointer,expected.text_pointer,claim.id);assert.equal(basis.excerpt,expected.excerpt,claim.id);
     assert.equal(basis.sourceUrl,artifact.origin.url||null,claim.id);
    }
   }
  }
  const overlay=await (await fetch(`${origin}/__review__/overlay.js`)).text();
  assert.doesNotThrow(()=>new vm.Script(overlay),'served overlay must remain executable');
  const sourceUi=overlay.slice(overlay.indexOf('function sourceTransitionHtml('),overlay.indexOf('function currentEvidenceRefs('));
  assert.doesNotMatch(sourceUi,/Original finding|Previous finding|Open frozen|Open bounded authority registry|scan\.reviewRationale/);
  assert.match(overlay,/class="vv-reader-finding"/);
  assert.match(overlay,/if \(hostPage && currentReview\.available\)/);
  const cardUi=overlay.slice(overlay.indexOf('  function currentClaimLocator('),overlay.indexOf('  function renderPageContext('));
  const escape=value=>String(value??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  for(const review of reviews){
   const rendered=vm.runInNewContext(cardUi+'\ncurrentReviewHtml(review);',{review,esc:escape,currentCitationDefect:()=>false,
    currentClaimSectionFilter:null,currentCitationDefectFilter:'ALL',sectionFromHash:()=>'',passageWording:p=>({text:p.text}),
    comparableWording:s=>s,claimWording:s=>s,readableStatus:s=>s,checkedContentLink:()=>({href:'#'}),
    H100_DIRECT_POSTINSTALL_ADJUDICATION:'verification/current-h100x4-direct-postinstall-adjudications.json',H100_DIRECT_POSTCHECK_ARTIFACT:'unused',H100_DIRECT_POSTCHECK_BY_CLAIM:new Map()});
   for(const claim of review.page.claims.filter(c=>c.readonlyProof||c.authorityScan?.basis.length)){
    const start=rendered.indexOf('data-current-claim="'+claim.id+'"'),card=rendered.slice(start,rendered.indexOf('</article>',start));
    assert.doesNotMatch(card,/No source pin is recorded|No retained artifact reference|No supporting proof is attached/,'misleading missing-proof message '+claim.id);
    if(claim.readonlyProof)assert.match(card,/Open selected observation/);
    if(claim.id==='CUR-c5c5c961094767f1')assert.ok(card.includes('href="https://cloud.vast.ai/host/agreement"'));
   }
  }
  const source=path.join(f.root,f.model.pages.at(-1).source_file),before=await fs.readFile(source);await fs.writeFile(source,Buffer.concat([before,Buffer.from('\nUnreviewed source addition.\n')]));assert.equal((await context(f.model.pages[0].route)).currentReview.available,false,'other-page source tamper must invalidate full model');await fs.writeFile(source,before);
  const oldRegistry=path.join(f.root,'verification/current-host-connection-adjudications.json'),oldBytes=await fs.readFile(oldRegistry);await fs.writeFile(oldRegistry,Buffer.from('{}'));assert.equal((await context(f.model.pages[0].route)).currentReview.available,false,'preserved proof registry tamper must invalidate current presentation');await fs.writeFile(oldRegistry,oldBytes);
  const {buildReport}=await import(pathToFileURL(path.join(f.root,'scripts/export_host_review_html.mjs')));const report=buildReport();assert.equal(report.payload.claims.length,2013);assert.equal(report.payload.readonly_command_proofs.length,10);
  const authorityModule=await import(pathToFileURL(path.join(f.root,'scripts/current_host_authority_scan.mjs'))),clarificationRegistry=JSON.parse(await fs.readFile(path.join(f.root,'verification/current-host-clarification.json'))),phase43Model=JSON.parse(await fs.readFile(path.join(f.root,clarificationRegistry.baseline.path)));
  const termsRegistry=await fs.readFile(path.join(f.root,'verification/current-host-terms-binding.json'),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
  const payoutTermsRegistry=await fs.readFile(path.join(f.root,PAYOUT_TERMS_REGISTRY),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
  const payoutInvoiceRegistry=await fs.readFile(path.join(f.root,PAYOUT_INVOICE_REGISTRY),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
  const beforeSourceRefs=new Map((jurisdictionRegistry?.sources||[]).map(source=>[source.path,source.before_artifact.path]));
  if(termsRegistry)beforeSourceRefs.set(termsRegistry.source.path,termsRegistry.source.before_artifact.path);
  if (payoutInvoiceRegistry||payoutTermsRegistry||report.payload.payout_provider_transition) {
   const frozen='verification/evidence/2026-09-14-payout-provider-correction-attempt-01/pre-correction-payment.mdx';
   assert.equal(hash(await fs.readFile(path.join(f.root,frozen))),'02022ade67dcc35c44c660a5d3cdac7547c889c3a30e239eff56b57b22525992');
   beforeSourceRefs.set('host/payment.mdx',frozen);
  }
  const phase43=authorityModule.validateAuthorityScanInput({read:ref=>fsSync.readFileSync(path.join(f.root,beforeSourceRefs.get(ref)||ref)),model:phase43Model,pins:{registry:authorityModule.AUTHORITY_SCAN_REGISTRY_SHA256,baseline:authorityModule.AUTHORITY_SCAN_BASELINE_SHA256,snapshot:authorityModule.AUTHORITY_SCAN_SNAPSHOT_SHA256}});
  const cleanupRegistry=await fs.readFile(path.join(f.root,CLEANUP_REGISTRY),'utf8').then(JSON.parse).catch(error=>{if(error.code==='ENOENT')return null;throw error;});
  const phase43Ids=new Set(phase43.presentation.keys()),clarificationIds=new Set(clarificationRegistry.claims.map(entry=>entry.claim_id)),termsIds=new Set((termsRegistry?.transitions||[]).map(entry=>entry.claim_id)),jurisdictionIds=new Set((jurisdictionRegistry?.transitions||[]).map(entry=>entry.claim_id)),cleanupIds=new Set((cleanupRegistry?.transitions||[]).map(entry=>entry.claim_id)),payoutTermsIds=new Set((payoutTermsRegistry?.transitions||[]).map(entry=>entry.claim_id)),payoutInvoiceIds=new Set((payoutInvoiceRegistry?.transitions||[]).map(entry=>entry.claim_id)),expectedIds=new Set([...phase43Ids,...clarificationIds,...termsIds,...jurisdictionIds,...cleanupIds,...payoutTermsIds,...payoutInvoiceIds]),transitions=report.payload.authority_scan.transitions;
  const retainedTransition=(entry,registryRef)=>{if(entry.registryRef===registryRef)return entry;for(const previous of entry.auditHistory||[]){const retained=retainedTransition(previous,registryRef);if(retained)return retained;}return null;};
  assert.equal(phase43Ids.size,JSON.parse(registryBytes).transitions.length,'all phase-43 transition IDs are present');assert.equal(clarificationIds.size,clarificationRegistry.claims.length,'all clarification IDs are present');if(cleanupRegistry)assert.equal(cleanupIds.size,cleanupRegistry.transitions.length,'all exact cleanup transition IDs are present');if(payoutTermsRegistry)assert.equal(payoutTermsIds.size,payoutTermsRegistry.transitions.length,'all exact payout Terms transition IDs are present');if(payoutInvoiceRegistry)assert.equal(payoutInvoiceIds.size,payoutInvoiceRegistry.transitions.length,'all exact payout invoice transition IDs are present');assert.deepEqual(new Set(Object.keys(transitions)),expectedIds,'presentation is the exact phase-43/clarification/Terms/jurisdiction/cleanup/payout Terms/payout invoice ID union');
  for(const [id,original] of phase43.presentation){
   if(!termsIds.has(id)){
    const retained=retainedTransition(transitions[id],REGISTRY);
    assert.ok(retained,`original source transition retained: ${id}`);assert.deepEqual(retained.basis,original.basis,`original source basis preserved: ${id}`);
   }
   for(const basis of original.basis)assert.ok(report.payload.files[basis.artifactRef]);
  }
  for(const id of clarificationIds)if(!phase43Ids.has(id)&&!termsIds.has(id)){
   const retained=transitions[id].registryRef==='verification/current-host-clarification.json'?transitions[id]:transitions[id].auditHistory.find(previous=>previous.registryRef==='verification/current-host-clarification.json');
   assert.ok(retained,`clarification source transition retained: ${id}`);assert.deepEqual(retained.basis,[],`clarification-only context has no source basis: ${id}`);assert.ok(retained.clarification,`clarification context retained: ${id}`);
  }
  if(termsRegistry){
   const termsBaseline=JSON.parse(await fs.readFile(path.join(f.root,termsRegistry.baseline.path))),before=new Map(termsBaseline.pages.flatMap(page=>page.claims).map(claim=>[claim.id,claim]));
   assert.equal(termsIds.size,6);assert.equal(report.payload.terms_transition.changed_claims,6);
   for(const id of termsIds){const transition=transitions[id];assert.equal(transition.registryRef,'verification/current-host-terms-binding.json',id);assert.equal(transition.baselineRef,termsRegistry.baseline.path,id);assert.deepEqual(transition.previous,before.get(id),id);assert.ok(transition.basis.some(basis=>basis.sourceUrl==='https://vast.ai/terms'),id);}
   if(!jurisdictionRegistry)assert.match(report.payload.current_result_ref,/host-terms-binding-attempt-01\/result\.md$/);
  }else if(!jurisdictionRegistry)assert.match(report.payload.current_result_ref,/host-authority-scan-attempt-01\/result\.md$/);
  if(payoutInvoiceRegistry){
   const baseline=JSON.parse(await fs.readFile(path.join(f.root,payoutInvoiceRegistry.baseline.path))),before=new Map(baseline.pages.flatMap(page=>page.claims).map(claim=>[claim.id,claim]));
   assert.equal(payoutInvoiceIds.size,6);assert.equal(report.payload.payout_invoice_transition.changed_claims,6);
   for(const id of payoutInvoiceIds){const transition=transitions[id];assert.equal(transition.registryRef,PAYOUT_INVOICE_REGISTRY,id);assert.equal(transition.baselineRef,payoutInvoiceRegistry.baseline.path,id);assert.deepEqual(transition.previous,before.get(id),id);assert.ok(transition.basis.some(basis=>basis.artifactRef===payoutInvoiceRegistry.guidance.path),id);}
  }
  if(jurisdictionRegistry){
   const before=new Map(JSON.parse(await fs.readFile(path.join(f.root,jurisdictionRegistry.baseline.path))).pages.flatMap(page=>page.claims).map(claim=>[claim.id,claim]));
   assert.equal(report.payload.jurisdiction_transition.changed_claims,8);assert.equal(jurisdictionIds.size,8);
   assert.equal(report.payload.current_result_ref,(report.payload.payout_invoice_transition||report.payload.payout_terms_transition||report.payload.payout_provider_transition||report.payload.cleanup_transition||report.payload.jurisdiction_transition).result_ref);
   assert.match(report.payload.current_result_ref,report.payload.payout_invoice_transition?/payout-invoice-correction-attempt-01\/result\.md$/:report.payload.payout_terms_transition?/payout-terms-correction-attempt-01\/result\.md$/:report.payload.payout_provider_transition?/payout-provider-correction-attempt-01\/result\.md$/:report.payload.cleanup_transition?/host-review-cleanup-attempt-01\/result\.md$/:/host-jurisdiction-authority-attempt-01\/result\.md$/);
   for(const id of jurisdictionIds){const transition=transitions[id];assert.equal(transition.registryRef,JURISDICTION_REGISTRY,id);assert.equal(transition.baselineRef,jurisdictionRegistry.baseline.path,id);assert.deepEqual(transition.previous,before.get(id),id);assert.ok(transition.auditHistory.length,id);}
  }
 }finally{if(child&&child.exitCode===null){child.kill('SIGTERM');await new Promise(resolve=>child.once('exit',resolve));}if(target)await new Promise(resolve=>target.close(resolve));await fs.rm(f.container,{recursive:true,force:true});}
});
