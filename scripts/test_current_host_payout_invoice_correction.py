#!/usr/bin/env python3
import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('invoice',ROOT/'scripts/current_host_payout_invoice_correction.py');m=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(m)
IDS={'MCL-e2b956d14494e470','MCL-df7b287adb0df683','MCL-5936430d1b2d8de9','MCL-bbd64c772e9b4693','MCL-3d796f5ae7f2020e','MCL-3afd93ae0b6cf8a4'}

def closure_before_sources():
    """Replay this historical phase with the sealed pre-closure Host pages."""
    registry = json.loads((ROOT / 'verification/current-host-closure-correction.json').read_text())
    return {source['path']: (ROOT / source['before_artifact']['path']).read_bytes()
            for source in registry['sources']}

def load_frozen(model):
    original = m.project
    with patch.object(m, 'project', side_effect=lambda root: original(root, closure_before_sources())):
        return m.load_payout_invoice_correction(ROOT, model)

class PayoutInvoiceCorrectionTest(unittest.TestCase):
 def test_projection_and_seal(self):
  result=m.project(ROOT, closure_before_sources()); self.assertEqual(result,json.loads((ROOT/'verification/evidence/2026-09-14-host-closure-correction-attempt-01/pre-correction-model.json').read_text())); claims={c['id']:c for p in result['pages'] for c in p['claims']}
  self.assertEqual(result['counts']['claim_statuses'],{'BLOCKED':23,'FAIL':26,'NOT_APPLICABLE':87,'PASS':319,'UNVALIDATED':1558})
  self.assertTrue(all(claims[i]['status']=='PASS' and claims[i]['history']['predecessor']['claim_id']==i for i in IDS))
  baseline={c['id']:c for p in json.loads((ROOT/m.BASELINE).read_text())['pages'] for c in p['claims']}
  self.assertEqual(sum(claims[i]==baseline[i] for i in baseline if i not in IDS),2007)
  self.assertEqual(load_frozen(result)['guidance'],m.GUIDANCE)
 def test_tamper_and_replay_rejected(self):
  with self.assertRaisesRegex(ValueError,'source edits exceed six approved lines'):
   original=m.pin
   try:
    m.pin=lambda root,ref,wanted,frozen_source_overrides=None: b'changed' if ref==m.SOURCE else original(root,ref,wanted,frozen_source_overrides)
    m.project(ROOT, closure_before_sources())
   finally:m.pin=original
  with tempfile.TemporaryDirectory() as tmp:
   target=Path(tmp)/'model.json';target.write_text(json.dumps(m.project(ROOT, closure_before_sources())))
   altered=json.loads(target.read_text());altered['counts']['claim_statuses']['PASS']-=1
   with self.assertRaisesRegex(ValueError,'whole model differs'):
    load_frozen(altered)

if __name__=='__main__':unittest.main()
