/** Test-only historical source view; production never imports this helper. */
import crypto from 'node:crypto';
import {projectClosureCorrection} from './current_host_closure_correction.mjs';

export function beforeSourceFamily(read) {
  const path='verification/current-host-source-family-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const attempt='verification/evidence/2026-09-15-host-unvalidated-source-families-attempt-01';
  const amendment=JSON.parse(read(`${attempt}/owner-context-amendment.json`));
  frozen.set('verification/current-host-owner-questions.json',read(amendment.before_artifact.path));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectClosureCorrection({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read(`${attempt}/inventory.json`));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical closure test serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeClosure(read) {
  read=beforeSourceFamily(read);
  let registry;
  try { registry=JSON.parse(read('verification/current-host-closure-correction.json')); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  return ref=>frozen.get(ref)||read(ref);
}
