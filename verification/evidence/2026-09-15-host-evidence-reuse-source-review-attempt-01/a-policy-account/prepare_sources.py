import json,hashlib,pathlib,subprocess,datetime
R=pathlib.Path(__file__).resolve().parents[4]
A=pathlib.Path(__file__).resolve().parent
C=pathlib.Path('/private/tmp/host-docs-d10-3o6tftdu/current-cli')
def sha(b):return hashlib.sha256(b).hexdigest()
def write(f,d): (A/f).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
raw=json.loads((A/'agreement-browser-response.json').read_text())
clauses={}
for key,i,start,end in [
 ('hardware',0,None,None),('performance',1,None,None),
 ('maintenance',3,'Provider shall provide Preventative Maintenance and Remedial Maintenance when','All provider downtime'),
 ('uptime',3,'Uptime. Provider shall use commercially best efforts','Daily system logs'),
 ('privacy',3,'Downloading, Storing, or Printing.','Data Breach Liability.'),
 ('interference',2,'Provider will not','Provider will not'),
]:
 t=raw['sections'][i]['text']
 if start is None: selected=t
 elif key=='interference':continue
 else:
  s=t.index(start);e=t.index(end,s+len(start));selected=t[s:e]
 clauses[key]={'raw_pointer':f'/sections/{i}/text','text':selected}
# Exact sentence selection from full retained public sections, not paraphrased assertions.
for key,i,needle in [('current-account',2,'true, accurate'),('cooperate',2,'cooperate'),('unauthorized-access',2,'unauthorized'),('safeguards',4,'reasonable measures'),('interfere',2,'interfere'),('technology',4,'telecommunications')]:
 t=raw['sections'][i]['text'];s=t.lower().find(needle.lower());assert s>=0,(key,needle)
 lo=t.rfind('. ',0,s)+2;lo=0 if lo==1 else lo;e=t.find('. ',s)+1;e=len(t) if e==0 else e
 clauses[key]={'raw_pointer':f'/sections/{i}/text','text':t[lo:e]}
write('agreement-clauses.json',{'record_type':'EXACT_FRESH_PUBLIC_AGREEMENT_SUBSTRINGS','raw_ref':str((A/'agreement-browser-response.json').relative_to(R)),'raw_sha256':sha((A/'agreement-browser-response.json').read_bytes()),'url':raw['url'],'retrieved_at_utc':raw['recorded_at_utc'],'clauses':clauses,'limit':'Public rendered text establishes published clause wording. No acceptance, account operation, universal product compliance or private data inspection.'})
items=[]
for key,f,s,e in [
 ('listing-args','vastai/cli/commands/machines.py',230,258),('listing-api','vastai/api/machines.py',49,106),('sdk-self-test','vastai/sdk.py',1191,1197),('team-members','vastai/cli/commands/teams.py',151,188),('pricing-guidance','vastai/cli/commands/price_increase.py',127,145),
]:
 b=(C/f).read_bytes();revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=C,text=True).strip();assert b==subprocess.check_output(['git','show',f'{revision}:{f}'],cwd=C)
 items.append({'id':key,'repository':'vast-ai/vast-cli','revision':revision,'source_file':f,'source_sha256':sha(b),'url':f'https://github.com/vast-ai/vast-cli/blob/{revision}/{f}#L{s}-L{e}','line_start':s,'line_end':e,'text':'\n'.join(b.decode().splitlines()[s-1:e])})
write('cli-excerpts.json',{'record_type':'EXACT_PINNED_CLI_SOURCE_EXCERPTS','excerpts':items,'limit':'Source declarations and client payloads only. No new CLI/SDK, account, rental, pricing or daemon execution.'})
print(A);print(json.dumps(clauses,ensure_ascii=False,indent=2))
