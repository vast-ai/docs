"""Read official documentation; retain selected text and provenance, not full HTML."""
import concurrent.futures,datetime,hashlib,json,pathlib,re,urllib.request
from bs4 import BeautifulSoup
OUT=pathlib.Path(__file__).parent
PAGES={
 'sshd-jammy':('https://manpages.ubuntu.com/manpages/jammy/man8/sshd.8.html',['Extended test mode.','Test mode.','forks a new daemon','command-line options override','~/.ssh/authorized_keys']),
 'sshd-noble':('https://manpages.ubuntu.com/manpages/noble/man8/sshd.8.html',['Extended test mode.','Test mode.','forks a new daemon','command-line options override','~/.ssh/authorized_keys']),
 'sshd-config-jammy':('https://manpages.ubuntu.com/manpages/jammy/man5/sshd_config.5.html',['For each keyword','Include /etc/ssh/sshd_config.d/*.conf','PasswordAuthentication Specifies','KbdInteractiveAuthentication Specifies','StrictModes Specifies','If all of the criteria']),
 'sshd-config-noble':('https://manpages.ubuntu.com/manpages/noble/man5/sshd_config.5.html',['For each keyword','Include /etc/ssh/sshd_config.d/*.conf','PasswordAuthentication Specifies','KbdInteractiveAuthentication Specifies','StrictModes Specifies','If all of the criteria']),
 'ssh-config':('https://manpages.ubuntu.com/manpages/noble/man5/ssh_config.5.html',['PreferredAuthentications Specifies','IdentitiesOnly Specifies']),
 'ssh-copy-id':('https://manpages.ubuntu.com/manpages/noble/man1/ssh-copy-id.1.html',['ssh-copy-id is a script','authorized_keys','-i identity_file']),
 'apt-jammy':('https://manpages.ubuntu.com/manpages/jammy/man8/apt.8.html',['update (apt-get','upgrade (apt-get','install, reinstall, remove, purge','EXIT STATUS']),
 'apt-noble':('https://manpages.ubuntu.com/manpages/noble/man8/apt.8.html',['update (apt-get','upgrade (apt-get','install, reinstall, remove, purge','EXIT STATUS']),
 'apt-get':('https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html',['--only-upgrade','--with-new-pkgs','NeverAutoRemove','--simulate']),
 'apt-cache':('https://manpages.ubuntu.com/manpages/noble/man8/apt-cache.8.html',['policy [','--installed','information acquired']),
 'dpkg-query':('https://manpages.ubuntu.com/manpages/noble/man1/dpkg-query.1.html',['db:Status-Abbrev','-W, --show','-f, --showformat','Package']),
 'ubuntu-kernels':('https://ubuntu.com/kernel/lifecycle',['Ubuntu 22.04 LTS','Ubuntu 24.04 LTS','Ubuntu Server','GA','HWE']),
 'hwe-edge-package':('https://packages.ubuntu.com/jammy/linux-generic-hwe-22.04-edge',['Complete Generic Linux kernel','dep: linux-headers','dep: linux-image']),
 'hwe-package':('https://packages.ubuntu.com/jammy/linux-generic-hwe-22.04',['Complete Generic Linux kernel','dep: linux-headers','dep: linux-image']),
 'grub-config':('https://www.gnu.org/software/grub/manual/grub/html_node/Simple-configuration.html',['GRUB_DEFAULT','GRUB_SAVEDEFAULT','GRUB_DISABLE_SUBMENU','GRUB_TIMEOUT_STYLE']),
 'update-grub':('https://manpages.ubuntu.com/manpages/noble/man8/update-grub.8.html',['stub for running','grub-mkconfig']),
 'gnu-coreutils':('https://www.gnu.org/software/coreutils/manual/html_node/Version-sort-overview.html',['Version sort','sort -V']),
 'nvidia-smi':('https://docs.nvidia.com/deploy/nvidia-smi/index.html',['NVIDIA System Management Interface','GPU attributes','-L, --list-gpus']),
}
def capture(item):
 key,(url,needles)=item
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Host-docs-source-review/1.0'}),timeout=25) as r:body=r.read();final=r.url
  soup=BeautifulSoup(body,'html.parser')
  for tag in soup(['script','style','nav','header','footer']):tag.decompose()
  text=' '.join((soup.find('main') or soup).stripped_strings);text=re.sub(r'\s+',' ',text)
  excerpts=[]
  for needle in needles:
   start=text.lower().find(needle.lower())
   if start<0:excerpts.append({'selector':needle,'found':False});continue
   a=max(0,start-80);b=min(len(text),start+650)
   excerpts.append({'selector':needle,'found':True,'normalized_text_start':a,'normalized_text_end':b,'text':text[a:b]})
  out={'record_type':'PRIMARY_DOCUMENTATION_EXCERPTS','requested_url':url,'source_url':final,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_response_sha256':hashlib.sha256(body).hexdigest(),'normalized_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'title':soup.title.get_text(' ',strip=True) if soup.title else key,'excerpts':excerpts,'limit':'Compact source excerpts, not executed Host results. Character selectors refer to whitespace-normalized main-page text. Version-specific Ubuntu manuals identify their distribution in the URL.'}
  (OUT/(key+'.json')).write_text(json.dumps(out,indent=2)+'\n')
  return {'key':key,'result':'captured','missing':[e['selector'] for e in excerpts if not e['found']]}
 except Exception as e:return {'key':key,'result':'error','error':str(e)}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(capture,PAGES.items()))
 (OUT/'capture-results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
