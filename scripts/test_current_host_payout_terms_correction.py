import importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('terms',ROOT/'scripts/current_host_payout_terms_correction.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PIN=m.pin
TERMS_SOURCE='verification/evidence/2026-09-14-payout-invoice-correction-attempt-01/pre-correction-payment.mdx'
def frozen_pin(root,ref,want):
 if ref==m.SOURCE:return (ROOT/TERMS_SOURCE).read_bytes()
 return PIN(root,ref,want)
IDS={m.TERMS_ID,m.FAQ_ID}
def claims(model):return {item['id']:item for page in model['pages'] for item in page['claims']}
class Terms(unittest.TestCase):
 def test_actual_before_fails_then_two_target_projection(self):
  before=json.loads((ROOT/m.BASELINE).read_text());self.assertEqual(claims(before)[m.TERMS_ID]['status'],'FAIL');self.assertEqual(claims(before)[m.FAQ_ID]['status'],'PASS')
  with patch.object(m,'pin',side_effect=frozen_pin):current=m.project(ROOT)
  items=claims(current);self.assertEqual(items[m.TERMS_ID]['status'],'PASS');self.assertEqual(items[m.FAQ_ID]['classification'],'PUBLICATION_DESCRIPTION');self.assertIn('ACH, wire and SWIFT, are unavailable',items[m.FAQ_ID]['text']);self.assertEqual(current['counts']['claim_statuses'],{'BLOCKED':23,'FAIL':30,'NOT_APPLICABLE':87,'PASS':313,'UNVALIDATED':1560});self.assertEqual(sum(before_item==items[key] for key,before_item in claims(before).items()),2011);self.assertEqual([ref['locator'] for ref in items[m.TERMS_ID]['source_refs']],['/sections/0/text','/sections/2/text','/sections/1/text']);self.assertEqual(items[m.FAQ_ID]['source_refs'][0]['locator'],'/text')
 def test_project_rejects_missing_tampered_evidence_and_old_wording(self):
  original=frozen_pin
  def missing(root,ref,want):
   if ref==m.FAQ:raise ValueError('payout Terms correction: missing path '+ref)
   return original(root,ref,want)
  with patch.object(m,'pin',side_effect=missing):
   with self.assertRaisesRegex(ValueError,'missing path'):m.project(ROOT)
  def tampered(root,ref,want):return b'{}' if ref==m.FAQ else original(root,ref,want)
  with patch.object(m,'pin',side_effect=tampered):
   with self.assertRaisesRegex(ValueError,'FAQ capture keys'):m.project(ROOT)
  def old_source(root,ref,want):return original(root,m.BEFORE,m.BEFORE_SHA256) if ref==m.SOURCE else original(root,ref,want)
  with patch.object(m,'pin',side_effect=old_source):
   with self.assertRaisesRegex(ValueError,'source wording'):m.project(ROOT)
 def test_tampered_model_and_unsafe_path_fail(self):
  with patch.object(m,'pin',side_effect=frozen_pin):current=m.project(ROOT)
  claims(current)[m.FAQ_ID]['status']='FAIL'
  with patch.object(m,'pin',side_effect=frozen_pin):
   with self.assertRaisesRegex(ValueError,'whole model differs'):m.validate_model(current,ROOT)
  with self.assertRaisesRegex(ValueError,'unsafe path'):m.safe(ROOT,'../host/payment.mdx')
if __name__=='__main__':unittest.main()
