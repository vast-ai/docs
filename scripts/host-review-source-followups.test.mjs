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
  assert.throws(()=>project([transition(autoSort),transition(autoSort)]),/current reviewed residual/);
  assert.throws(()=>project([transition({...autoSort,text:'Different wording'})]),/current reviewed residual/);
  assert.throws(()=>project([transition({...autoSort,next_action:''})]),/current reviewed residual/);
  assert.throws(()=>project([transition({...autoSort,next_action:'Different next action'})]),/current reviewed residual/);
  assert.throws(()=>buildHostReviewIssues({pages:[{...pages[0],claims:[{...autoSort,status:'PASS'}]}],ownerQuestions:[],sourceFamilyTransitions:[transition(autoSort)]}),/current reviewed residual/);
  assert.throws(()=>project({}),/explicit source-family transitions/);
});
