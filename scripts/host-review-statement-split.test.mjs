import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {hostReviewReaderCopy} from './host_review_reader_copy.mjs';

const model = JSON.parse(fs.readFileSync('verification/current-host-docs-review.json','utf8'));
const claims = model.pages.flatMap(p => p.claims);
const ids = ['MCL-470bf8ec992a342e','MCL-6e0046c21ac71be4','MCL-8d3286528a924e12','MCL-a4b087a3103c5bdb'];
test('four composite rental cards show only their child statement without adjudication', () => {
  const before = JSON.stringify(model);
  for (const id of ids) {
    const claim = claims.find(c => c.id === id), copy = hostReviewReaderCopy(claim);
    assert.equal(copy.statementText, claim.text.split('\n')[1]);
    assert.equal(copy.statementSpanIndex, 1);
    assert.equal(copy.relatedClaimId, 'MCL-3d66c8305aa70982');
    assert.match(copy.sourceContextLabel, /Partial support|Related pricing guidance/);
    assert.ok(copy.finding.length < 240 && copy.nextStep.length < 240);
    const camel = {...claim, requiredEvidenceTypes:claim.required_evidence_types, sourceRefs:claim.source_refs};
    delete camel.required_evidence_types; delete camel.source_refs;
    assert.deepEqual(hostReviewReaderCopy(camel),copy);
    for (const changed of [{id:id+'-changed'}, {text:claim.text+' changed'}, {status:'PASS'}, {classification:'OTHER'}, {source_refs:[]}, {spans:[]}, {rationale:claim.rationale+' changed'}, {next_action:claim.next_action+' changed'}]) {
      assert.equal(hostReviewReaderCopy({...claim,...changed}).statementText,undefined);
    }
  }
  assert.equal(claims.find(c => c.id === 'MCL-3d66c8305aa70982').status,'PASS');
  assert.equal(JSON.stringify(model),before);
  assert.equal(claims.filter(c => hostReviewReaderCopy(c).statementText).length,4);
});
