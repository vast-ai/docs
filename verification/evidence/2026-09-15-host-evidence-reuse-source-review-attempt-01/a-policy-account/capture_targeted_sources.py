"""Bounded fresh primary publication excerpts; no accounts or requests beyond public GET."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
O=pathlib.Path(__file__).parent
PAGES={
'hosting-details':('https://docs.vast.ai/host/hosting-overview',['Clients have high expectations','A rental contract is created each time','the pricing for GPUs','Volume Offers','How the offer becomes','out of sync']),
'bittensor':('https://www.bittensor.com/docs',['compute, inference','training']),
'hosting-requirements':('https://docs.vast.ai/host/how-to-self-test',['same','VRAM','TCP','UDP']),
'hosting-prep':('https://docs.vast.ai/host/hosting-overview',['Clients require open ports']),
'keys-rotation':('https://docs.vast.ai/guides/reference/api-keys',['Rotate a key','Revoke a key','compromised']),
}
def get(item):
 key,(url,needles)=item
 try:
  with urllib.request.urlopen(url,timeout=25)as r:raw=r.read();final=r.url;http=r.status
  s=BeautifulSoup(raw,'html.parser')
  for t in s(['script','style','nav','header','footer']):t.decompose()
  text=re.sub(r'\s+',' ',' '.join((s.find('main')or s).stripped_strings));es=[]
  for needle in needles:
   i=text.lower().find(needle.lower())
   if i<0:es.append({'selector':needle,'found':False});continue
   a=max(0,i-70);z=min(len(text),i+650);es.append({'selector':needle,'found':True,'normalized_text_start':a,'text':text[a:z]})
  return key,{'source_url':final,'requested_url':url,'http_status':http,'title':s.title.get_text()if s.title else'','retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response_sha256':hashlib.sha256(raw).hexdigest(),'normalized_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'excerpts':es,'scope':'Fresh primary publication; no authenticated account state, enacted contract, runtime compliance or actual payment behavior verified.'}
 except Exception as e:return key,{'requested_url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:results=dict(pool.map(get,PAGES.items()))
(O/'published-targeted.json').write_text(json.dumps({'record_type':'FRESH_PRIMARY_PUBLICATION_EXCERPTS','sources':results},indent=2)+'\n')
print(json.dumps({k: {'error':v['error']}if'error'in v else{'missing':[x['selector']for x in v['excerpts']if not x['found']]}for k,v in results.items()}))
