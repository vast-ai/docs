import assert from 'node:assert/strict';
import fs from 'node:fs';
import {PAYOUT_INVOICE_PATH,projectPayoutInvoiceCorrection,loadPayoutInvoiceCorrection} from './current_host_payout_invoice_correction.mjs';
const read=ref=>fs.readFileSync(ref),exists=ref=>fs.existsSync(ref),ids=['MCL-e2b956d14494e470','MCL-df7b287adb0df683','MCL-5936430d1b2d8de9','MCL-bbd64c772e9b4693','MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4'];
const projected=projectPayoutInvoiceCorrection({read,exists}),claims=new Map(projected.model.pages.flatMap(p=>p.claims.map(c=>[c.id,c])));
assert.deepEqual(projected.model.counts.claim_statuses,{PASS:319,UNVALIDATED:1558,NOT_APPLICABLE:87,FAIL:26,BLOCKED:23});
for(const id of ids){assert.equal(claims.get(id).status,'PASS');assert.equal(claims.get(id).history.predecessor.claim_id,id);}
for(const id of ['MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4']){
 const basis=projected.presentation.get(id).basis;
 assert.equal(basis.length,2);assert.equal(basis[0].sourceUrl,'https://docs.vast.ai/host/payment#payment-timeline');assert.equal(basis[1].sourceUrl,'https://cloud.vast.ai/host/agreement');assert.equal(basis[1].text_pointer,'/sections/4/text');assert.doesNotMatch(basis[1].support_rationale,/2 to 4|noon|Pacific/i);
}
assert.equal(loadPayoutInvoiceCorrection({read,model:projected.model,exists}).payoutInvoice.registrySha256,projected.payoutInvoice.registrySha256);
assert.throws(()=>projectPayoutInvoiceCorrection({read:ref=>ref==='host/payment.mdx'?Buffer.from('tamper'):read(ref),exists}),/digest drift host\/payment.mdx/);
const replay=structuredClone(projected.model);replay.counts.claim_statuses.PASS--;assert.throws(()=>loadPayoutInvoiceCorrection({read,model:replay,exists}),/whole model differs/);
const absent=ref=>ref===PAYOUT_INVOICE_PATH?false:exists(ref);const before=JSON.parse(read('verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/pre-correction-model.json'));assert.equal(loadPayoutInvoiceCorrection({read,model:before,exists:absent}),null);
