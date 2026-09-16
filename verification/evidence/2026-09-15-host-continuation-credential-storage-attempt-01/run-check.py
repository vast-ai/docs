from pathlib import Path
import tempfile,subprocess,os,json,hashlib,platform,datetime,stat
OUT=Path(__file__).resolve().parent
VENV=Path('/private/tmp/host-key-permissions-20260915-venv')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Only these explicitly synthetic values enter the disposable process/files.
NEW='synthetic-host-docs-key-20260915'
OLD='synthetic-prior-key'
GUARD='''import builtins,os,json,socket,stat
real_open=builtins.open
key=os.environ['TASK_TEST_KEY_FILE']
log=os.environ['TASK_TEST_AUDIT_FILE']
def record(d):
 with real_open(log,'a') as f:f.write(json.dumps(d)+'\\n')
def traced_open(file,mode='r',*a,**k):
 if isinstance(file,(str,bytes,os.PathLike)) and os.path.abspath(file)==key and any(x in mode for x in 'wax+'):
  fm=oct(stat.S_IMODE(os.stat(key).st_mode)) if os.path.exists(key) else None
  dm=oct(stat.S_IMODE(os.stat(os.path.dirname(key)).st_mode))
  record({'event':'before_key_write','file_mode':fm,'directory_mode':dm})
  assert fm=='0o600' and dm=='0o700', 'Key permissions not restricted before CLI write'
 return real_open(file,mode,*a,**k)
builtins.open=traced_open
def denied(*a,**k):
 record({'event':'network_attempt_blocked'})
 raise RuntimeError('network disabled for synthetic credentials check')
socket.socket.connect=denied
socket.socket.connect_ex=denied
socket.create_connection=denied
'''
(OUT/'primary/sitecustomize.py').write_text(GUARD)
rows=[]
with tempfile.TemporaryDirectory(prefix='host-key-synthetic-',dir='/private/tmp') as tmp:
 base=Path(tmp)
 for name in ['new-default','existing0644-custom-xdg','legacy0644-with-new-config','blank-input-existing','symlink-rejected']:
  root=base/name;userdir=root/'user';userdir.mkdir(parents=True)
  cfg=root/'xdg' if 'custom' in name else userdir/'.config'
  key=cfg/'vastai/vast_api_key';audit=root/'audit.jsonl'
  env={'PATH':str(VENV/'bin')+':/usr/bin:/bin','HOME':str(userdir),'LANG':'C.UTF-8','PYTHONPATH':str(OUT/'primary'),'TASK_TEST_KEY_FILE':str(key),'TASK_TEST_AUDIT_FILE':str(audit)}
  if 'custom' in name:env['XDG_CONFIG_HOME']=str(cfg)
  legacy=userdir/'.vast_api_key'
  if name in ['existing0644-custom-xdg','blank-input-existing']:
   key.parent.mkdir(parents=True);key.write_text(OLD);key.chmod(0o644)
  if name=='legacy0644-with-new-config':legacy.write_text(OLD);legacy.chmod(0o644)
  target=root/'synthetic-symlink-target'
  if name=='symlink-rejected':
   key.parent.mkdir(parents=True);target.write_text(OLD);key.symlink_to(target)
  before={'file_mode':oct(stat.S_IMODE(key.stat().st_mode)) if key.exists() else None,'legacy_present':legacy.exists()}
  proc=subprocess.run(['/bin/bash','--noprofile','--norc',str(OUT/'proposed-command.sh')],input=('' if name=='blank-input-existing' else NEW)+'\n',text=True,capture_output=True,env=env,umask=0o022,timeout=30)
  events=[json.loads(x) for x in audit.read_text().splitlines()] if audit.exists() else []
  assert not any(x['event']=='network_attempt_blocked' for x in events)
  assert NEW not in proc.stdout+proc.stderr and OLD not in proc.stdout+proc.stderr
  expected_ok=name not in ['blank-input-existing','symlink-rejected']
  if expected_ok:
   assert proc.returncode==0 and key.read_text()==NEW and stat.S_IMODE(key.stat().st_mode)==0o600 and stat.S_IMODE(key.parent.stat().st_mode)==0o700
   assert events==[{'event':'before_key_write','file_mode':'0o600','directory_mode':'0o700'}]
   assert not legacy.exists()
  else:
   assert proc.returncode!=0 and key.read_text()==OLD and not events
   if name=='symlink-rejected':assert key.is_symlink() and target.read_text()==OLD
  rows.append({'case':name,'before':before,'exit_code':proc.returncode,'events':events,'file_mode_after':oct(stat.S_IMODE(key.stat().st_mode)),'directory_mode_after':oct(stat.S_IMODE(key.parent.stat().st_mode)),'synthetic_content_matches_expected':True,'input_not_in_captured_output':True,'legacy_file_present_after':legacy.exists(),'result':'PASS'})
cleanup=not Path(tmp).exists();assert cleanup
r={'record_type':'SYNTHETIC_CREDENTIAL_STORAGE_WORKFLOW_CHECK','state':'PASS','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'architecture':platform.machine(),'python':subprocess.check_output([str(VENV/'bin/python'),'--version'],text=True).strip(),'bash':subprocess.check_output(['/bin/bash','--version'],text=True).splitlines()[0],'vastai_version':'1.5.6','shell_script_sha256':sha(OUT/'proposed-command.sh'),'harness_sha256':sha(Path(__file__)),'sitecustomize_sha256':sha(OUT/'primary/sitecustomize.py'),'installed_source_manifest_sha256':sha(OUT/'primary/installed-source-manifest.json'),'cases':rows,'cleanup_confirmed':cleanup,'limits':['Actual Bash stanza and installed CLI1.5.6 executed on macOSarm64 only; Linux/Windows not executed.','No real credentials, Host/API/account calls or rental; network guard observed zero attempts.','Python startup instrumentation observes and asserts owner-only file/directory modes before the actual CLI opens the file; it does not implement or change CLI credential storage.','Existing configuration is assumed to be owned by the operator. The stanza rejects a symlink/nonregular key-file target; it is not a defense against a malicious process with the same user privileges.','The key is entered without shell echo/history; the existing CLI positional argument is still used. This is a file-permission correction, not a claim that command arguments are secret from all local process inspection.','Prior0644 unguarded CLI failure remains valid and retained. No CLI source change or fixed release is claimed.']}
(OUT/'checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'state':r['state'],'cases':len(rows),'cleanup':cleanup,'checks_sha256':sha(OUT/'checks.json')}))
