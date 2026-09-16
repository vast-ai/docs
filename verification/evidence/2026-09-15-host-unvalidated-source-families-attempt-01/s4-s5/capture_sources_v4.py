"""Final focused selectors and exact Ubuntu source sections; older captures remain."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
O=pathlib.Path(__file__).parent
PAGES={'apt-policy-source-v4': ('https://git.launchpad.net/ubuntu/+source/apt/plain/apt-private/private-show.cc?h=applied/ubuntu/noble', ['Installed:', 'Candidate:', 'Version table:']), 'apt-install-source': ('https://git.launchpad.net/ubuntu/+source/apt/plain/apt-private/private-install.cc?h=applied/ubuntu/noble', ['only upgrades are requested', 'The following packages have been kept back', 'The following NEW packages']), 'gnu-grep': ('https://www.gnu.org/software/grep/manual/html_node/Command_002dline-Options.html', ['Command-line Options']), 'gnu-awk': ('https://www.gnu.org/software/gawk/manual/html_node/Fields.html', ['Fields', 'whitespace']), 'openssh-files': ('https://manpages.ubuntu.com/manpages/noble/man8/sshd.8.html', ['~/.ssh/authorized_keys', 'read/write/execute for the user'])}
def get(item):
 key,(url,needles)=item
 try:
  with urllib.request.urlopen(url,timeout=25)as r:b=r.read();final=r.url
  raw=b.decode();s=BeautifulSoup(raw,'html.parser')
  for t in s(['script','style','nav','header','footer']):t.decompose()
  iscode='launchpad.net' in final or 'raw.githubusercontent' in final
  text=raw if iscode else re.sub(r'\s+',' ',' '.join((s.find('main')or s).stripped_strings))
  es=[]
  for needle in needles:
   i=text.find(needle)
   if i<0:es.append({'selector':needle,'found':False});continue
   a=max(0,i-90);z=min(len(text),i+700)
   if iscode:a=text.rfind('\n',0,i)+1;z=text.find('\n',z);z=len(text)if z<0 else z
   es.append({'selector':needle,'found':True,'text':text[a:z],**({'lines':[text[:a].count('\n')+1,text[:z].count('\n')+1]}if iscode else {'normalized_text_start':a})})
  j={'record_type':'PRIMARY_SOURCE_EXCERPTS','source_url':final,'requested_url':url,'source_revision':url.split('h=')[-1]if'launchpad.net'in final else 'V_9_6_P1'if'raw.githubusercontent'in final else 'official manual retrieved '+datetime.date.today().isoformat(),'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_response_sha256':hashlib.sha256(b).hexdigest(),'excerpts':es,'limit':'Exact source or manual definitions only; no Host execution, no current package/boot state observation.'}
  (O/(key+'.json')).write_text(json.dumps(j,indent=2)+'\n');return {'id':key,'missing':[x['selector']for x in es if not x['found']]}
 except Exception as e:return {'id':key,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:r=list(pool.map(get,PAGES.items()))
(O/"capture-results-v4.json").write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r))
