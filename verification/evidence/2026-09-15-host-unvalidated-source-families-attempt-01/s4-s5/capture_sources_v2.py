"""Second capture: exact command-definition phrases; prior attempts preserved."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
O=pathlib.Path(__file__).parent
pages={
 'sshd-jammy-v2':('https://manpages.ubuntu.com/manpages/jammy/man8/sshd.8.html',['-T Extended test mode.','-t Test mode.','-C connection_spec','command-line options override']),
 'sshd-noble-v2':('https://manpages.ubuntu.com/manpages/noble/man8/sshd.8.html',['-T Extended test mode.','-t Test mode.','-C connection_spec','command-line options override']),
 'apt-jammy-v2':('https://manpages.ubuntu.com/manpages/jammy/man8/apt.8.html',['update is used to download','upgrade is used to install','Performs the requested action','apt returns zero','autoremove is used']),
 'apt-noble-v2':('https://manpages.ubuntu.com/manpages/noble/man8/apt.8.html',['update is used to download','upgrade is used to install','Performs the requested action','apt returns zero','autoremove is used']),
 'dpkg-query-v2':('https://manpages.ubuntu.com/manpages/noble/man1/dpkg-query.1.html',['-W , --show [','-f , --showformat=','db:Status-Abbrev','Package The binary package name']),
 'apt-cache-v2':('https://manpages.ubuntu.com/manpages/noble/man8/apt-cache.8.html',['policy [ pkg ...] policy','apt-cache performs a variety','installed version','Candidate']),
 'bash':('https://www.gnu.org/software/bash/manual/html_node/Lists.html',['Commands separated by a','AND and OR lists','command1 && command2','command1 || command2']),
 'bash-variables':('https://www.gnu.org/software/bash/manual/html_node/Shell-Parameters.html',['A parameter can be assigned','A variable is a parameter']),
 'cp':('https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html',['--no-clobber','do not overwrite','exit status']),
 'sed':('https://www.gnu.org/software/sed/manual/html_node/The-_0022s_0022-Command.html',['REGEXP','I i','replacement can contain','The g flag']),
 'uname':('https://www.gnu.org/software/coreutils/manual/html_node/uname-invocation.html',['--kernel-release','kernel release']),
 'grub-config-v2':('https://www.gnu.org/software/grub/manual/grub/html_node/Simple-configuration.html',['The default menu entry.','This is only useful','Normally, grub-mkconfig','If ESC or F4']),
 'grub-source':('https://git.launchpad.net/ubuntu/+source/grub2/plain/util/grub-mkconfig.in?h=applied/ubuntu/noble',['/etc/default/grub','for x in','grub.d']),
}
def get(item):
 key,(url,needles)=item
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Host-docs-source-review/1.0'}),timeout=25) as r:b=r.read();final=r.url
  soup=BeautifulSoup(b,'html.parser')
  for tag in soup(['script','style','nav','header','footer']):tag.decompose()
  text=re.sub(r'\s+',' ',' '.join((soup.find('main')or soup).stripped_strings))
  es=[]
  for needle in needles:
   i=text.find(needle)
   es.append({'selector':needle,'found':i>=0,**({'normalized_text_start':max(0,i-25),'text':text[max(0,i-25):i+550]} if i>=0 else {})})
  j={'record_type':'PRIMARY_DOCUMENTATION_EXCERPTS','attempt':2,'requested_url':url,'source_url':final,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_response_sha256':hashlib.sha256(b).hexdigest(),'normalized_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'title':soup.title.get_text(' ',strip=True)if soup.title else key,'excerpts':es,'limit':'Source declarations only; no Host execution. The previous imprecise/missing selectors are retained and not used as successful proof.'}
  (O/(key+'.json')).write_text(json.dumps(j,indent=2)+'\n');return {'id':key,'missing':[x['selector'] for x in es if not x['found']]}
 except Exception as e:return {'id':key,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:results=list(pool.map(get,pages.items()))
(O/'capture-results-v2.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
