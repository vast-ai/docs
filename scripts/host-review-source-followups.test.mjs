import test from 'node:test';
import assert from 'node:assert/strict';
import {buildHostReviewIssues} from './host_review_work_queue.mjs';

const autoSort = {id:'MCL-b106578dbaccc269',status:'UNVALIDATED',headings:['Auto Sort'],
  text:'The default marketplace search order.',next_action:'Obtain the console ranking source or an owner definition.'};
const bandwidth = {id:'MCL-1221941af8a7a4fe',status:'UNVALIDATED',headings:['Quick Lookup'],
  text:'| `bad bandwidthtest2` | GPU transfer or PCIe bandwidth health |',next_action:'Obtain the diagnostic emitter or an owner definition.'};
const pages = [{route:'/host/glossary',title:'Host Glossary',claims:[autoSort,{...autoSort,id:'untouched-uv'}]},
  {route:'/host/machine-errors',title:'Machine Error Reference',claims:[bandwidth]}];
const transition = claim => ({claim_id:claim.id,decision:'residual',after:{...claim}});
const project = sourceFamilyTransitions => buildHostReviewIssues({pages,ownerQuestions:[],sourceFamilyTransitions});

test('only explicitly reviewed source residuals become named follow-ups without changing statuses or existing counts', () => {
  const transitions=[transition(autoSort),transition(bandwidth),{claim_id:'untouched-uv',decision:'supported',after:{status:'PASS'}}];
  const before=JSON.stringify({pages,transitions}), result=project(transitions), baseline=project([]);
  assert.deepEqual(result.sourceFollowUps.map(item=>item.claimId),[autoSort.id,bandwidth.id]);
  assert.deepEqual(result.sourceFollowUps.map(item=>item.title),['Auto Sort','bad bandwidthtest2']);
  assert.equal(result.sourceFollowUps[1].route,'/host/machine-errors');
  assert.equal(result.sourceFollowUps[1].nextAction,bandwidth.next_action);
  assert.deepEqual(result.counts,baseline.counts);
  assert.deepEqual(result.corrections,baseline.corrections);
  assert.deepEqual(result.questions,baseline.questions);
  assert.deepEqual(result.workflows,baseline.workflows);
  assert.deepEqual(baseline.sourceFollowUps,[]);
  assert.equal(JSON.stringify({pages,transitions}),before);
});

test('source residual projection rejects unknown or duplicate IDs and stale status, wording or next action', () => {
  assert.throws(()=>project([transition({...autoSort,id:'missing'})]),/current reviewed residual/);
  assert.throws(()=>project([transition(autoSort),transition(autoSort)]),/distinct transition IDs/);
  assert.throws(()=>project([transition({...autoSort,text:'Different wording'})]),/current reviewed residual/);
  assert.throws(()=>project([transition({...autoSort,next_action:''})]),/current reviewed residual/);
  assert.throws(()=>project([transition({...autoSort,next_action:'Different next action'})]),/current reviewed residual/);
  assert.throws(()=>buildHostReviewIssues({pages:[{...pages[0],claims:[{...autoSort,status:'PASS'}]}],ownerQuestions:[],sourceFamilyTransitions:[transition(autoSort)]}),/current reviewed residual/);
  assert.throws(()=>project({}),/explicit review transitions/);
});

test('source follow-ups use the latest review, group explicit topics and retain every exact residual', async () => {
  const {buildHostReviewIssues}=await import('./host_review_work_queue.mjs');
  const make=(id,text,status='UNVALIDATED')=>({id,text,status,next_action:`Find the source for ${id}`,headings:['Definitions']});
  const cpu=make('cpu','CPU rule','PASS'),auto=make('MCL-b106578dbaccc269','Earlier AutoSort wording'),newAuto=make('new-auto','Later AutoSort wording'),fallback=make('old-gap','An earlier unresolved source question'),unreviewed=make('unreviewed','No reviewed issue');
  const pages=[{route:'/host/one',title:'One',claims:[cpu,auto,fallback,unreviewed]},{route:'/host/two',title:'Two',claims:[newAuto]}];
  const transition=(claim,topic)=>({claim_id:claim.id,decision:'residual',after:{text:claim.text,status:'UNVALIDATED',next_action:claim.next_action},...(topic?{residual_topic:topic}:{})});
  const previous=[transition({...cpu,status:'UNVALIDATED'}),transition(auto),transition(fallback)];
  const latest=[{claim_id:cpu.id,decision:'supported',after:{text:cpu.text,status:'PASS'}},transition(newAuto,{key:'HOST-AUTOSORT-DEFINITION',title:'Confirm AutoSort ranking and randomness'})];
  const before=JSON.stringify({pages,previous,latest});
  const result=buildHostReviewIssues({pages,ownerQuestions:[],sourceFamilyTransitions:previous,evidenceReuseTransitions:latest});
  assert.deepEqual(result.sourceFollowUps.map(item=>item.claimId),[auto.id,fallback.id,newAuto.id]);
  assert.equal(result.sourceFollowUpTopics.length,2);
  const topic=result.sourceFollowUpTopics.find(item=>item.key==='HOST-AUTOSORT-DEFINITION');
  assert.deepEqual(topic.claimIds,[auto.id,newAuto.id]);
  assert.deepEqual(topic.routes,['/host/one','/host/two']);
  assert.deepEqual(topic.passages.map(item=>[item.literal,item.nextAction]),[[auto.text,auto.next_action],[newAuto.text,newAuto.next_action]]);
  assert.deepEqual(result.sourceFollowUpTopics.find(item=>item.key===`passage:${fallback.id}`).claimIds,[fallback.id]);
  assert.equal(JSON.stringify({pages,previous,latest}),before);
  assert.throws(()=>buildHostReviewIssues({pages,ownerQuestions:[],sourceFamilyTransitions:[previous[1],previous[1]]}),/distinct transition IDs/);
  assert.throws(()=>buildHostReviewIssues({pages,ownerQuestions:[],evidenceReuseTransitions:[{...transition(newAuto),after:{...transition(newAuto).after,text:'stale text'}}]}),/does not match/);
  assert.throws(()=>buildHostReviewIssues({pages,ownerQuestions:[],sourceFamilyTransitions:[previous[1]],evidenceReuseTransitions:[transition(newAuto,{key:'HOST-AUTOSORT-DEFINITION',title:'A conflicting title'})]}),/titles disagree/);
});
