#!/usr/bin/env python3
import importlib.util, json, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('invoice',ROOT/'scripts/current_host_payout_invoice_correction.py');m=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(m)
IDS={'MCL-e2b956d14494e470','MCL-df7b287adb0df683','MCL-5936430d1b2d8de9','MCL-bbd64c772e9b4693','MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4'}

class PayoutInvoiceCorrectionTest(unittest.TestCase):
 def test_projection_and_seal(self):
  result=m.project(ROOT); claims={c['id']:c for p in result['pages'] for c in p['claims']}
  self.assertEqual(result['counts']['claim_statuses'],{'BLOCKED':23,'FAIL':26,'NOT_APPLICABLE':87,'PASS':319,'UNVALIDATED':1558})
  self.assertTrue(all(claims[i]['status']=='PASS' and claims[i]['history']['predecessor']['claim_id']==i for i in IDS))
  baseline={c['id']:c for p in json.loads((ROOT/m.BASELINE).read_text())['pages'] for c in p['claims']}
  self.assertEqual(sum(claims[i]==baseline[i] for i in baseline if i not in IDS),2007)
  self.assertEqual(m.load_payout_invoice_correction(ROOT,result)['guidance'],m.GUIDANCE)
 def test_tamper_and_replay_rejected(self):
  with self.assertRaisesRegex(ValueError,'source edits exceed six approved lines'):
   original=m.pin
   try:
    m.pin=lambda root,ref,wanted: b'changed' if ref==m.SOURCE else original(root,ref,wanted)
    m.project(ROOT)
   finally:m.pin=original
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'model.json';target.write_text(json.dumps(m.project(ROOT)))
   altered=json.loads(target.read_text());altered['counts']['claim_statuses']['PASS']-=1
   with self.assertRaisesRegex(ValueError,'whole model differs'):
    m.load_payout_invoice_correction(ROOT,altered)

if __name__=='__main__':unittest.main()
