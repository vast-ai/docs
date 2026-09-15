"""One-off retained review assembly; writes only this evidence directory."""
import json, hashlib, re, subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
INV=json.loads((OUT.parent/'inventory.json').read_text())
MODEL=json.loads((ROOT/'verification/current-host-docs-review.json').read_text())
ROWS={x['id']:x for x in INV['claims'] if x['family'] in ('S2','S3')}
DEC={}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def literal(i):
 c=MODEL
 for p in ROWS[i]['model_pointer'].split('/')[1:]: c=c[int(p)] if isinstance(c,list) else c[p]
 return c['text']
def ref(path, start, end=None, authority='CANONICAL_IMPLEMENTATION_SOURCE', url=None, revision=None):
 p=Path(path); p=p if p.is_absolute() else ROOT/p
 end=end or start
 r={'artifact_ref':str(p.relative_to(ROOT)), 'sha256':sha(p),'text_pointer':f'/lines/{start}-{end}','excerpt':'\n'.join(p.read_text().splitlines()[start-1:end]),'source_kind':authority}
 if url:r['source_url']=url
 if revision:r['source_revision']=revision
 return r
def owner(comment,start,end=None):
 return ref(OUT/f'owner-{comment}.md',start,end,'AUTHORITATIVE_DOCUMENTATION_CITATION',f'https://vastai.atlassian.net/browse/CON-1531?focusedCommentId={comment}',f'comment {comment}, Hanran Yang, 2026-06-{22 if comment==58017 else 23}')
def jref(path,pointer,authority='CANONICAL_IMPLEMENTATION_SOURCE'):
 p=Path(path);p=p if p.is_absolute() else ROOT/p
 val=json.loads(p.read_text())
 for bit in pointer.split('/')[1:]:
  bit=bit.replace('~1','/').replace('~0','~');val=val[int(bit)] if isinstance(val,list) else val[bit]
 assert isinstance(val,str)
 return {'artifact_ref':str(p.relative_to(ROOT)),'sha256':sha(p),'text_pointer':pointer,'excerpt':val,'source_kind':authority}
def public(key):
 r=jref(OUT/'public-sources.json',f'/sources/{key}/reviewed_definition','AUTHORITATIVE_DOCUMENTATION_CITATION')
 s=json.loads((OUT/'public-sources.json').read_text())['sources'][key]
 r.update(source_url=s['url'],source_revision=s['version'],primary_locator=s['locator'],primary_quote=s['quote'],excerpt_kind='retained reviewer paraphrase of primary source; exact quote separately identified')
 return r
def oldtool(n):
 return jref('verification/evidence/2026-09-14-host-unvalidated-evidence-attempt-02/source-diagnostics/primary-tool-sources.json',f'/sources/{n}/reviewed_definition','AUTHORITATIVE_DOCUMENTATION_CITATION')
def code(path,start,end,repo='cli'):
 base=Path('/private/tmp/host-docs-d10-3o6tftdu')/('current-cli' if repo=='cli' else 'self-test')
 revision=subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()
 b=subprocess.check_output(['git','-C',str(base),'show',f'{revision}:{path}'])
 assert b==(base/path).read_bytes()
 name=f"{repo}-{path.replace('/','_')}-{start}-{end}.txt";p=OUT/name
 p.write_text('\n'.join(b.decode().splitlines()[start-1:end])+'\n')
 r=ref(p,1,end-start+1,url=f'https://github.com/vast-ai/{"vast-cli" if repo=="cli" else "self-test"}/blob/{revision}/{path}#L{start}-L{end}',revision=revision)
 r.update(original_path=path,original_sha256=hashlib.sha256(b).hexdigest(),original_line_range=[start,end])
 return r
def add(i,refs,why,decision='supported',replacement=None,limit=None,methods=None,classification=None):
 x=ROWS[i]; text=literal(i); assert hashlib.sha256(text.encode()).hexdigest()==x['literal_sha256']
 d={'id':i,'family':x['family'],'page':x['page'],'current_literal':text,'current_literal_sha256':x['literal_sha256'],'decision':decision,'source_refs':refs,'support_rationale':why,'limits':limit or 'Source/static meaning only; no current Host, recovery, backend deployment, listing outcome, or human acceptance is inferred.','next_action':'Root independent review and exact-source integration; no new live run is required for this declared meaning.' if decision=='supported' else 'Root review and apply the complete replacement, then recheck exact source/context before adjudication.' if decision=='correction' else why}
 if replacement is not None:d['full_replacement']=replacement
 if methods is not None:
  d['proposed_required_methods']=methods;d['method_change_rationale']=why;d['proposed_classification']=classification or 'REVIEWED_TECHNICAL_DECLARATION'
 DEC[i]=d
def catalog(i,start,end=None,comment=58492):
 x=ROWS[i]; routing=literal(i).startswith('|') and '](' in literal(i)
 why='The primary engineering owner explicitly defines this exact message/category. '+('The full row is a diagnostic routing entry, not a promise that a listed check repairs a machine; its local target was inspected in the frozen page.' if routing else 'The literal is a paraphrase of the defined condition; it does not assert successful recovery or current backend state.')
 methods=['AUTHORITATIVE_DOCUMENTATION_CITATION','STATIC_CONTEXT_REVIEW'] if routing else ['AUTHORITATIVE_DOCUMENTATION_CITATION']
 add(i,[owner(comment,start,end)],why,methods=methods)
catalog('MCL-5ef562461a015aad',16,17)
catalog('MCL-22fbca1b73497073',15)
catalog('MCL-3f8842d8ae8384a4',22)
catalog('MCL-b28fced4b1a6184b',19)
catalog('MCL-694d449174e7d0f4',18,comment=58017)
catalog('MCL-d63686b534cbf505',24)
catalog('MCL-ca213e23f60ba778',23)
catalog('MCL-f0787eb7f15682e3',21)
catalog('MCL-7ccb5cafc341757b',25)
catalog('MCL-84bd956810d5bdb4',26)
catalog('MCL-d20593d74e807618',30,43)
catalog('MCL-3958c0b2b3b026e1',47,66)
catalog('MCL-54edb13fe8c0e5d0',19)
catalog('MCL-a8d6bba43add3bdb',32,comment=58017)
catalog('MCL-756a4e6e0e2c7633',24)
catalog('MCL-165460e8dbaacce7',41)
catalog('MCL-a559e069a733c192',53)
catalog('MCL-da4576c44bad0b29',56)
catalog('MCL-961b88428e7ab8b0',58)
catalog('MCL-4f12ad8bf75543d3',60)
catalog('MCL-fcfa473622135a42',62)
catalog('MCL-cfbc1ebcaea8a51c',63)
catalog('MCL-a5c03528d88f45f6',64)
catalog('MCL-08717c2cb481b0ca',65)
catalog('MCL-decd53fd86502f29',66)
catalog('MCL-8f9043e6471f67c1',25)
def save():
 context=[]
 for i,d in DEC.items():
  row=ROWS[i]; page=ROOT/row['page']; text=page.read_text(); links=[]
  for dest in re.findall(r'\]\(([^)]+)\)',d.get('full_replacement',d['current_literal'])):
   if dest.startswith('http'):continue
   route,_,fragment=dest.partition('#')
   target=(ROOT/(route.lstrip('/')+'.mdx')) if route else page
   exists=target.exists();targettext=target.read_text() if exists else ''
   headings=re.findall(r'^#{1,6}\s+(.+)$',targettext,re.M)
   slugs={re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
   explicit=set(re.findall(r'id=["\']([^"\']+)["\']',targettext))
   found=not fragment or fragment in slugs or fragment in explicit
   links.append({'target':dest,'file':str(target.relative_to(ROOT)),'exists':exists,'fragment_present':found,'target_sha256':sha(target) if exists else None})
   assert exists and found,(i,dest)
  c=MODEL
  for bit in row['model_pointer'].split('/')[1:]:c=c[int(bit)] if isinstance(c,list) else c[bit]
  spans=c['spans'];lo=max(1,min(s['start'] for s in spans)-2);hi=min(len(text.splitlines()),max(s['end'] for s in spans)+2)
  context.append({'id':i,'current_literal':d['current_literal'],'current_literal_sha256':row['literal_sha256'],'page':row['page'],'page_sha256':sha(page),'headings':row['headings'],'context_line_range':[lo,hi],'context_excerpt':'\n'.join(text.splitlines()[lo-1:hi]),'review':d['support_rationale'],'replacement':d.get('full_replacement'),'local_route_checks':links,'limit':d['limits']})
 cp=OUT/'context-review.json';cp.write_text(json.dumps({'record_type':'exact_literal_context_review','baseline_commit':INV['baseline_commit'],'baseline_model_sha256':INV['baseline_model_sha256'],'method':'Human/agent source and full-context inspection plus deterministic local route/fragment and literal-hash checks; no hardware commands or application tests.','claims':context},indent=2)+'\n')
 for n,c in enumerate(context):
  d=DEC[c['id']]
  d['source_refs'].append(jref(cp,f'/claims/{n}/review','STATIC_CONTEXT_REVIEW'))
  d['current_classification']=ROWS[c['id']]['classification']
  d['current_required_methods']=ROWS[c['id']]['required_methods']
  if 'proposed_required_methods' not in d and 'REPOSITORY_STATIC_CHECK' in d['current_required_methods']:
   d['proposed_required_methods']=['STATIC_CONTEXT_REVIEW' if m=='REPOSITORY_STATIC_CHECK' else m for m in d['current_required_methods']]
   d['proposed_classification']=d['current_classification']
   d['method_change_rationale']='The full occurrence is qualified task advice, so the factual inputs are checked against the cited primary source and the recommendation is reviewed in context; no separate executable repository test would establish more. '+d['support_rationale']
 out={'record_type':'source_family_claim_decisions','baseline_commit':INV['baseline_commit'],'baseline_model_sha256':INV['baseline_model_sha256'],'review_scope':'S2 and S3 only; every proposal awaits independent integration review; supported is not a model status write.','expected_count':len(ROWS),'completed_count':len(DEC),'counts':{k:sum(d['decision']==k for d in DEC.values()) for k in ('supported','correction','residual')},'decisions':[DEC[i] for i in ROWS if i in DEC], 'not_yet_reviewed':[i for i in ROWS if i not in DEC]}
 (OUT/'decisions.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'completed_count':len(DEC),'counts':out['counts']}))
if __name__=='__main__':
 extra=OUT/'additional_decisions.py'
 if extra.exists():exec(compile(extra.read_text(),str(extra),'exec'))
 save()
