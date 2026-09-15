/** Test-only historical source view; production never imports this helper. */
import crypto from 'node:crypto';
import {projectTeamsConsoleReview} from './current_host_teams_console_review.mjs';
import {projectDiagnosticsSshReview} from './current_host_diagnostics_ssh_review.mjs';
import {projectContinuationReview} from './current_host_continuation_review.mjs';
import {projectEvidenceReuseReview} from './current_host_evidence_reuse_review.mjs';
import {projectSourceFamilyReview} from './current_host_source_family_review.mjs';
import {projectClosureCorrection} from './current_host_closure_correction.mjs';

export function beforeSetupMetrics(read) {
  const path='verification/current-host-setup-metrics-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectTeamsConsoleReview({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read('verification/evidence/2026-09-15-host-continuation-setup-metrics-attempt-01/inventory.json'));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical Teams/console serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  const owner=JSON.parse(read('verification/current-host-owner-questions.json'));owner.model_sha256=inventory.baseline_model_sha256;frozen.set('verification/current-host-owner-questions.json',Buffer.from(JSON.stringify(owner,null,2)+'\n'));
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeTeamsConsole(read) {
  read=beforeSetupMetrics(read);
  const path='verification/current-host-teams-console-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectDiagnosticsSshReview({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read('verification/evidence/2026-09-15-host-continuation-teams-console-attempt-01/inventory.json'));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical diagnostics/SSH serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  const owner=JSON.parse(read('verification/current-host-owner-questions.json'));owner.model_sha256=inventory.baseline_model_sha256;frozen.set('verification/current-host-owner-questions.json',Buffer.from(JSON.stringify(owner,null,2)+'\n'));
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeDiagnosticsSsh(read) {
  read=beforeTeamsConsole(read);
  const path='verification/current-host-diagnostics-ssh-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectContinuationReview({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read('verification/evidence/2026-09-15-host-continuation-diagnostics-ssh-attempt-01/inventory.json'));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical continuation serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  const owner=JSON.parse(read('verification/current-host-owner-questions.json'));owner.model_sha256=inventory.baseline_model_sha256;frozen.set('verification/current-host-owner-questions.json',Buffer.from(JSON.stringify(owner,null,2)+'\n'));
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeContinuation(read) {
  read=beforeDiagnosticsSsh(read);
  const path='verification/current-host-continuation-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectEvidenceReuseReview({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read('verification/evidence/2026-09-15-host-continuation-88-attempt-01/inventory.json'));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical evidence-reuse serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  const owner=JSON.parse(read('verification/current-host-owner-questions.json'));owner.model_sha256=inventory.baseline_model_sha256;frozen.set('verification/current-host-owner-questions.json',Buffer.from(JSON.stringify(owner,null,2)+'\n'));
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeEvidenceReuse(read) {
  read=beforeContinuation(read);
  const path='verification/current-host-evidence-reuse-review.json';
  let registry;
  try { registry=JSON.parse(read(path)); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  const historicalRead=ref=>frozen.get(ref)||read(ref);
  const modelBytes=Buffer.from(JSON.stringify(projectSourceFamilyReview({read:historicalRead}).model,null,2)+'\n');
  const inventory=JSON.parse(read('verification/evidence/2026-09-15-host-evidence-reuse-source-review-attempt-01/inventory.json'));
  if(crypto.createHash('sha256').update(modelBytes).digest('hex')!==inventory.baseline_model_sha256)
    throw Error('Historical source-family serialization differs from frozen model bytes');
  frozen.set('verification/current-host-docs-review.json',modelBytes);
  const owner=JSON.parse(read('verification/current-host-owner-questions.json'));owner.model_sha256=inventory.baseline_model_sha256;frozen.set('verification/current-host-owner-questions.json',Buffer.from(JSON.stringify(owner,null,2)+'\n'));
  return ref=>{if(ref===path){const error=Error('Historical view excludes successor');error.code='ENOENT';throw error;}return historicalRead(ref);};
}

export function beforeSourceFamily(read) {
  read=beforeEvidenceReuse(read);
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
