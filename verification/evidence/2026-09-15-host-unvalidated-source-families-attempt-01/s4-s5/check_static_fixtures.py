"""Disposable parser/operator fixtures. Never runs apt, ssh, sudo, reboot or Host actions."""
import datetime,hashlib,json,pathlib,platform,subprocess,tempfile
from build_decisions import O,ROOT,rows,current
from build_s4 import build
D={x['id']:x for x in build()};results=[]
def check(name,actual,expected,scope,**extra):
 r={'name':name,'actual':actual,'expected':expected,'passed':actual==expected,'scope':scope,**extra};r['finding']=f'{name}: observed {actual!r}; expected {expected!r}; '+scope;results.append(r)
def run(s,cwd=None):
 p=subprocess.run(['/bin/bash','--noprofile','--norc'],input=s,text=True,cwd=cwd,capture_output=True);return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def shellbody(text):return text[len('```bash\n'):-len('\n```')]
syntax=[]
for id,x in rows.items():
 if x['family']!='S4':continue
 c=current(x)
 for which,t in [('current',c['text']),('replacement',D[id].get('replacement',''))]:
  if not t.startswith('```bash\n'):continue
  p=subprocess.run(['/bin/bash','-n'],input=shellbody(t),text=True,capture_output=True)
  syntax.append({'id':id,'version':which,'literal_sha256':hashlib.sha256(t.encode()).hexdigest(),'returncode':p.returncode,'stderr':p.stderr})
check('all selected Bash fences and corrected fences parse',sum(x['returncode']!=0 for x in syntax),0,'Bash syntax only on macOS; no command in these fences is executed.')
with tempfile.TemporaryDirectory(prefix='disposable-static-',dir=O)as td:
 td=pathlib.Path(td);g=td/'grub';g.write_text('GRUB_DEFAULT=saved\n')
 pre='sudo() { "$@"; }; cp() { return 23; }; sed() { echo EDIT_RAN; }; grep() { return 0; };\n'
 outcomes={}
 for version,t in [('original',D['CUR-b100a6b8811cf951']['current_literal']),('corrected',D['CUR-b100a6b8811cf951']['replacement'])]:
  outcomes[version]=run(pre+shellbody(t).replace('/etc/default/grub',str(g)),td)
 check('failed GRUB backup permits original edit',outcomes['original']['stdout'],'EDIT_RAN\n','Shadow cp fails; shadow sed records invocation; all paths are disposable.',execution=outcomes['original'])
 check('failed GRUB backup prevents corrected edit',outcomes['corrected']['stdout'],'','Same failure input with parenthesized AND guard.',execution=outcomes['corrected'])
 check('corrected GRUB backup failure remains nonzero',outcomes['corrected']['returncode'],23,'The correction propagates the failed copy status.')
 empty=td/'empty';empty.mkdir()
 original='for f in '+str(empty)+'/*.conf; do printf "%s\\n" "$f"; done'
 corrected='for f in '+str(empty)+'/*.conf; do [ -f "$f" ] || continue; printf "%s\\n" "$f"; done'
 check('unmatched original backup glob is literal',run(original,td)['stdout'],str(empty)+'/*.conf\n','Only printf substitutes for the copy action; no files or remote systems copied.')
 check('corrected backup skips unmatched glob',run(corrected,td)['stdout'],'','The regular-file guard skips a nonexistent match.')
 ssh=td/'sshd_config';ssh.write_text('#PasswordAuthentication yes\n');drop=td/'sshd_config.d';drop.mkdir()
 (td/'sudo').write_text('#!/bin/sh\nexec "$@"\n');(td/'sudo').chmod(0o700)
 (td/'sed').write_text('#!/bin/sh\nprintf "<%s>\\n" "$@"\n');(td/'sed').chmod(0o700)
 body=shellbody(D['CUR-994864e626e37c79']['replacement']).replace('/etc/ssh/sshd_config',str(ssh))
 got=run('PATH='+str(td)+':/usr/bin:/bin\n'+body,td)
 check('corrected SSH edit preserves GNU sed expression argument',got['stdout'],'<-i>\n<-E>\n<s/^[[:space:]]*#?[[:space:]]*(PasswordAuthentication)[[:space:]]+.*/\\1 no/I>\n<'+str(ssh)+'>\n','A shadow sed prints argv. This verifies shell quoting and file selection, not GNU sed execution or authentication.',execution=got)
 missingbody=body.replace(str(ssh),str(td/'absent'))
 missing=run('PATH='+str(td)+':/usr/bin:/bin\n'+missingbody,td)
 check('corrected SSH edit rejects missing main config',missing['returncode'],1,'No edit runs when the named main file is absent.',execution=missing)
 awk=run("printf 'ii  linux-generic\\nrc  linux-generic-old\\nhi  linux-generic-held\\nii  linux-generic-hwe-22.04\\n' | awk '$1 == \"ii\" { print $2 }'",td)
 check('dpkg example status filter selects only ii records',awk['stdout'],'linux-generic\nlinux-generic-hwe-22.04\n','Synthetic dpkg status rows processed by local awk; not a query of installed Ubuntu packages.')
 scope=run("KERNEL_METAPACKAGES=linux-generic; /bin/bash --noprofile --norc -c 'printf \"%s\" \"${KERNEL_METAPACKAGES-unset}\"'",td)
 check('unexported package variable absent from fresh child shell',scope['stdout'],'unset','Local shell scope fixture; no SSH connection was opened.')
version=subprocess.run(['/bin/bash','--version'],text=True,capture_output=True).stdout.splitlines()[0]
j={'record_type':'DISPOSABLE_STATIC_FIXTURE_CHECKS','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'shell':version,'runner_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'command_policy':'Only bash -n, local shadow functions/executables, printf and awk; no privileged, network, package-manager, ssh, boot or GPU operation. Temporary data removed.','syntax':syntax,'checks':results,'result':'PASS'if all(x['passed']for x in results)else'FAIL','limits':'These are syntax/control-flow fixtures on macOS, not Ubuntu command execution, Host maintenance, GNU sed execution or authentication validation.'}
(O/'static-fixtures.json').write_text(json.dumps(j,indent=2)+'\n');print({'result':j['result'],'checks':len(results),'syntax_fences':len(syntax)})
assert j['result']=='PASS'
