"""One authorized read-only CLI search; credentials stay in process memory."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = Path('/private/tmp/host-docs-d10-3o6tftdu/current-cli')
REVISION = '1c6f8b61d3929a7ae423f89a3a0a53e4e9be02bc'
PYTHON = Path('/Users/hanneszietsman/VastAi/vast-cli/.venv/bin/python')
PRIVATE = Path('/Users/hanneszietsman/VastAi/CON-1584/private-evidence/2026-09-14-host-unvalidated-evidence-attempt-02')
QUERY = 'gpu_name=RTX_4090 cpu_ram>257 cpu_ram<258'
sha = lambda data: hashlib.sha256(data).hexdigest()

assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SOURCE).decode().strip() == REVISION
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=SOURCE)
assert not (HERE / 'offer-search-current.json').exists(), 'Preserve the existing attempt'
PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=True)
os.chmod(PRIVATE, 0o700)
os.umask(0o077)
key_result = subprocess.run(
    ['/usr/bin/security', 'find-generic-password', '-s', 'Crypto Labs Vast.ai Client API Key',
     '-a', 'cryptolabs-client', '-w'], capture_output=True, timeout=30)
assert key_result.returncode == 0 and key_result.stdout.strip(), 'Client credential unavailable'
key = key_result.stdout.strip().decode()
env = os.environ.copy()
for name in list(env):
    if name.startswith('VAST_') or name in ('PYTHONPATH', 'PYTHONHOME'):
        env.pop(name)
env.update(VAST_API_KEY=key, VAST_URL='https://console.vast.ai', PYTHONDONTWRITEBYTECODE='1')
metadata_path = PRIVATE / 'runtime-identity.json'
wrapper = '''import hashlib, json, pathlib, sys
from vastai.cli.main import main
try:
    main()
finally:
    base = pathlib.Path.cwd().resolve()
    modules = {}
    for name, module in list(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if not path:
            continue
        p = pathlib.Path(path).resolve()
        if p.is_file() and p.is_relative_to(base):
            modules[name] = {'path': str(p.relative_to(base)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
    pathlib.Path(METADATA_PATH).write_text(json.dumps({'python': sys.version, 'executable': sys.executable, 'cwd': str(base), 'imported_source_modules': modules}, indent=2) + '\\n')
'''.replace('METADATA_PATH', repr(str(metadata_path)))
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = subprocess.run([str(PYTHON), '-c', wrapper, 'search', 'offers', QUERY],
                        cwd=SOURCE, env=env, capture_output=True, timeout=90)
finished = datetime.datetime.now(datetime.timezone.utc).isoformat()
# Even private captures exclude the credential and any diagnostic suffix.
outputs = {}
for name, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
    data = data.replace(key.encode(), b'[REDACTED_CREDENTIAL]')
    if name == 'stderr':
        data = data.replace(key[-4:].encode(), b'[REDACTED_SUFFIX]')
    path = PRIVATE / ('offer-search.' + name)
    path.write_bytes(data)
    os.chmod(path, 0o600)
    outputs[name] = {'bytes': len(data), 'sha256': sha(data), 'lines': len(data.splitlines())}
identity = json.loads(metadata_path.read_text())
for info in identity['imported_source_modules'].values():
    blob = subprocess.check_output(['git', 'show', REVISION + ':' + info['path']], cwd=SOURCE)
    assert sha(blob) == info['sha256'], info['path']
assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=SOURCE)
text = (PRIVATE / 'offer-search.stdout').read_text()
lines = [line for line in text.splitlines() if line.strip()]
header = lines[0] if lines and lines[0].lstrip().startswith('ID') else None
row_count = len(lines) - 1 if header else None
record = {
    'claim_id': 'MCL-c36fc6f15087d072', 'method': 'RUNTIME',
    'started_at_utc': started, 'finished_at_utc': finished,
    'documented_command': 'vastai search offers ' + repr(QUERY),
    'entrypoint': 'vastai.cli.main:main from pinned source, invoked via Python -c',
    'revision': REVISION, 'source_tracked_clean_before_after': True,
    'interpreter_sha256': sha(PYTHON.resolve().read_bytes()),
    'pyproject_sha256': sha((SOURCE / 'pyproject.toml').read_bytes()),
    'runtime_identity': identity,
    'exit_code': result.returncode, 'output': outputs,
    'table_header': header, 'table_data_rows': row_count,
    'result': 'PASS' if result.returncode == 0 and header and not result.stderr else 'REVIEW_REQUIRED',
    'private_capture': 'CON-1584/private-evidence/2026-09-14-host-unvalidated-evidence-attempt-02',
    'script_sha256': sha(Path(__file__).read_bytes()),
    'limits': [
        'One time-local marketplace search with the existing client account; no rental, listing, SSH or host mutation.',
        'Only the documented search syntax, command completion and table output are observed.',
        'No guarantee of a specific offer, future inventory, rental authority, or whole-CLI qualification.',
        'Credentials remained in memory and the child environment; no secret or account profile was retained.',
        'HTTP status is not separately instrumented; command exit and output are retained.'
    ]
}
(HERE / 'offer-search-current.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: record[k] for k in ('claim_id', 'result', 'exit_code', 'table_header', 'table_data_rows', 'output')}, indent=2))
