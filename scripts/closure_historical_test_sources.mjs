/** Test-only historical source view; production never imports this helper. */
export function beforeClosure(read) {
  let registry;
  try { registry=JSON.parse(read('verification/current-host-closure-correction.json')); }
  catch (error) { if(error.code==='ENOENT') return read; throw error; }
  const frozen=new Map(registry.sources.map(source=>[source.path,read(source.before_artifact.path)]));
  return ref=>frozen.get(ref)||read(ref);
}
