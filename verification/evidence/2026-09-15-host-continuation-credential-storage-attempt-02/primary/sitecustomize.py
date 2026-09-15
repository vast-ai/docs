import builtins,os,json,socket,stat
real_open=builtins.open
key=os.environ['TASK_TEST_KEY_FILE']
log=os.environ['TASK_TEST_AUDIT_FILE']
def record(d):
 with real_open(log,'a') as f:f.write(json.dumps(d)+'\n')
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
