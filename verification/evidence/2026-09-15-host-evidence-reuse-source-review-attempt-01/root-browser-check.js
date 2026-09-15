(async()=>{
 const r=await window.hostReviewReady;
 const checks=[];
 const check=(name,value)=>{checks.push({name,pass:!!value});if(!value)throw Error(name);};
 check('complete offline initialization',r&&document.getElementById('report-init').hidden);
 check('all 2008 passages and final statuses',r.claims.length===2008&&JSON.stringify(r.counts.claim_statuses)===JSON.stringify({BLOCKED:21,FAIL:3,NOT_APPLICABLE:91,PASS:1042,UNVALIDATED:851}));
 check('issues first and coverage initially hidden',!document.getElementById('overview').hidden&&document.getElementById('coverage').hidden);
 check('current and prior review counts retained',r.evidence_reuse_transition.reviewed_claims===318&&r.evidence_reuse_transition.wording_corrections===47&&r.source_family_transition.reviewed_claims===358&&r.source_family_transition.wording_corrections===69);
 const topics=new Map(r.issues.sourceFollowUpTopics.map(t=>[t.key,t]));
 check('nineteen residuals grouped into eleven topics',r.issues.sourceFollowUps.length===19&&topics.size===11);
 for(const [key,n] of [['HOST-AUTOSORT-DEFINITION',2],['HOST-ARM-SUPPORT-CONSISTENCY',3],['HOST-CPU-POLICY-CONSISTENCY',4]])check(key,topics.get(key)?.claimIds.length===n);
 const claims=new Map(r.claims.map(c=>[c.id,c]));
 for(const id of topics.get('HOST-CPU-POLICY-CONSISTENCY').claimIds)check('CPU owner and source-only route '+id,claims.get(id).owner_role==='Host Product/Engineering owner'&&!claims.get(id).required_evidence_types.includes('RUNTIME_OR_UI_OBSERVATION'));
 check('three FAIL passages in two correction groups',r.issues.counts.correctionPassages===3&&r.issues.counts.correctionTopics===2&&claims.get('MCL-9ad33b25fd88c5cb').status==='FAIL');
 const failButton=document.querySelector('[data-issue-claim="MCL-9ad33b25fd88c5cb"]');failButton.click();
 check('retained API-key permissions defect visible',document.getElementById('viewer').open&&document.getElementById('viewer').innerText.includes('0644'));document.getElementById('viewer').close();
 check('current registry display remains valid JSON',JSON.parse(r.files[r.evidence_reuse_transition.registry_ref].text).transitions.length===318);
 for(const item of r.issues.sourceFollowUps){
  const b=document.querySelector('[data-issue-claim="'+item.claimId+'"]');
  check('finding control '+item.claimId,!!b);
  for(let d=b.closest('details');d;d=d.parentElement?.closest('details'))d.open=true;
  b.click();const v=document.getElementById('viewer');
  check('finding dialog '+item.claimId,v.open&&v.innerText.includes(item.nextAction));
  const source=v.querySelector('button[data-basis][data-context="'+item.claimId+'"]');
  check('source control '+item.claimId,!!source);source.click();
  check('exact source dialog '+item.claimId,v.open&&v.innerText.includes('Source scope:')&&v.innerText.includes('What remains:'));
  check('literal in source dialog '+item.claimId,v.querySelector('pre')?.textContent===(claims.get(item.claimId).reader_copy?.statementText||claims.get(item.claimId).text));
  v.close();
 }
 for(const [transition,fragment] of [[r.evidence_reuse_transition,'47 complete wording corrections'],[r.source_family_transition,'69'],[r.closure_transition,'']]){
  const ref=transition.result_ref,b=document.querySelector('[data-artifact="'+ref+'"]');
  check('visible retained result control '+ref,!!b);b.click();
  const v=document.getElementById('viewer');check('retained result opens '+ref,v.open&&(!fragment||v.innerText.includes(fragment)));v.close();
 }
 for(const id of ['CUR-f992e392221fe492','CUR-1de91e8c48307d8b'])check('earlier CPU failure remains in history '+id,claims.get(id).status==='PASS'&&claims.get(id).history.evidence_reuse_review.prior_status==='FAIL'&&!!claims.get(id).history.source_family_review);
 check('corrected duplicate image CPU declaration',claims.get('MCL-80298fc395621cfb').text.includes('at least two physical CPU cores'));
 check('corrected duplicate image VRAM declaration',claims.get('MCL-0a57d1f50a0d246f').text.includes('PyTorch allocated plus reserved'));
 window.rootBrowserChecks={record_type:'ROOT_ACTUAL_OFFLINE_BROWSER_CHECK',checked_at_utc:new Date().toISOString(),checks,model_sha256:r.input.sha256,registry_sha256:r.evidence_reuse_transition.registry_sha256,counts:r.counts.claim_statuses,claim_count:r.claims.length,embedded_files:Object.keys(r.files).length,source_topics:topics.size,source_followup_passages:r.issues.sourceFollowUps.length,user_agent:navigator.userAgent,limits:'Offline browser initialization and document/control activation. No external links, Host commands, paid or account operations. Initial offscreen agent-browser clicks needed scrollintoview; bounded control sweep activates DOM controls directly.'};
 location.hash='claim-MCL-80298fc395621cfb';
 return {checks_passed:checks.length,deep_link_requested:location.hash};
})()
