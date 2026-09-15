"""Bounded fresh primary publication excerpts; no accounts or requests beyond public GET."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
O=pathlib.Path(__file__).parent
PAGES={
'hosting':('https://docs.vast.ai/host/hosting-overview',['Account Setup and Hosting Agreement','Ubuntu','dedicated','contract','fee']),
'earning':('https://docs.vast.ai/host/earning',['Total Rental Earnings','Template Performance','How can I have earnings']),
'tax':('https://docs.vast.ai/host/guide-to-taxes',['does not automatically withhold taxes']),
'pricing':('https://docs.vast.ai/guides/instances/pricing',['Storage','Bandwidth','stopped','per second']),
'volumes':('https://docs.vast.ai/guides/instances/storage/volumes',['Pricing','storage','billing']),
'calculator':('https://vast.ai/hosting/calculator',['Host Earnings','25%','host','revenue']),
'notifications':('https://docs.vast.ai/host/notifications',['The notification system is shared','Open Account Settings','Click Save','Notification types are identified','Maintenance window confirmed','Mandatory email notifications','Email and webhook preferences']),
'notification-reference':('https://docs.vast.ai/guides/reference/notifications',['context prefix','host:machine_offline','GET /notification-types/','mandatory','preferences']),
'2fa':('https://docs.vast.ai/guides/reference/two-factor-authentication',['two-factor','authenticator','recovery']),
'keys':('https://docs.vast.ai/guides/reference/keys',['API Key','Reset','Delete','revoke']),
'api-keys':('https://docs.vast.ai/guides/reference/api-keys',['permissions','API key','secret']),
'teams':('https://docs.vast.ai/guides/teams/teams-overview',['account','Context Switcher','owner']),
'teams-roles':('https://docs.vast.ai/guides/teams/teams-roles',['machine_read','machine_write','2FA','owner']),
'teams-quickstart':('https://docs.vast.ai/guides/teams/teams-quickstart',['The Members section','Inviting Team Members','Roles tab']),
'permissions':('https://docs.vast.ai/api-reference/permissions',['machine_read','machine_write','team_write','billing_read']),
'account-settings':('https://docs.vast.ai/guides/reference/account',['Invoice','Escalation','Settings']),
'compliance':('https://vast.ai/compliance',['ISO 27001','not strictly required','Client Data Isolation']),
'security-2024':('https://vast.ai/article/security-and-compliance-at-vast-ai',['ISO 27001','Third-Party Certifications']),
'terms':('https://vast.ai/terms',['cryptocurrency','prohibited','tax']),
'referral':('https://docs.vast.ai/guides/reference/referral-program',['template','credit','earn']),
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
(O/'published-current.json').write_text(json.dumps({'record_type':'FRESH_PRIMARY_PUBLICATION_EXCERPTS','sources':results},indent=2)+'\n')
print(json.dumps({k: {'error':v['error']}if'error'in v else{'missing':[x['selector']for x in v['excerpts']if not x['found']]}for k,v in results.items()}))
