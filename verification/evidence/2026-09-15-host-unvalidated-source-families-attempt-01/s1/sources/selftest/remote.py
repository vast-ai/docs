import os
import subprocess
import ssl
import http.server
import threading
import sys
import time
import json
import uuid
import re
import copy
from datetime import datetime, timezone
import psutil

# Define the port to listen on and the log file to serve
PORT = 5000
LOG_FILE = 'progress.log'
JSONL_FILE = 'progress.jsonl'
SUMMARY_FILE = 'summary.json'
CERT_FILE = 'server.crt'
KEY_FILE = 'server.key'
SCHEMA_VERSION = '1.0'

EVENT_CATALOG = {
    'image_started': {
        'title': 'Self-test image started',
        'purpose': 'Confirm the self-test runtime started and can report progress.',
        'remediation': ['If this is the last event, inspect container startup logs and Python import errors.'],
        'doc_id': 'self-test.runtime.image_started',
    },
    'system_requirements': {
        'title': 'System requirements',
        'purpose': 'Verify GPU visibility, available VRAM, host RAM, and CPU core capacity.',
        'remediation': ['Check CUDA visibility, host memory, CPU allocation, and competing GPU workloads.'],
        'doc_id': 'self-test.runtime.system_requirements',
    },
    'resnet': {
        'title': 'ResNet GPU execution',
        'purpose': 'Run a CUDA ResNet18 workload across visible GPUs.',
        'remediation': ['Check PyTorch CUDA compatibility, GPU memory pressure, and driver health.'],
        'doc_id': 'self-test.runtime.resnet',
    },
    'ecc': {
        'title': 'ECC memory allocation',
        'purpose': 'Allocate most GPU memory on each visible GPU to surface memory/ECC failures.',
        'remediation': ['Check GPU ECC/Xid errors, available VRAM, and device health.'],
        'doc_id': 'self-test.runtime.ecc',
    },
    'nccl': {
        'title': 'NCCL distributed communication',
        'purpose': 'Initialize NCCL workers across all visible GPUs and synchronize them.',
        'remediation': ['Check NCCL support, peer communication, CUDA driver/runtime compatibility, and process limits.'],
        'doc_id': 'self-test.runtime.nccl',
    },
    'stress_gpu_burn': {
        'title': 'CPU stress and GPU burn',
        'purpose': 'Run stress-ng and gpu-burn together to exercise sustained host and GPU load.',
        'remediation': ['Check thermals, power limits, gpu-burn output, stress-ng output, and system stability.'],
        'doc_id': 'self-test.runtime.stress_gpu_burn',
    },
    'final_summary': {
        'title': 'Final summary',
        'purpose': 'Report the overall self-test result.',
        'remediation': ['Review the failed stage event and raw output tails for the first actionable failure.'],
        'doc_id': 'self-test.runtime.final_summary',
    },
}

def _atomic_write(path, content):
    """Replace `path` with `content` via os.replace so /progress readers
    can never observe an empty or torn body during a truncate+write."""
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        f.write(content)
    os.replace(tmp, path)

def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def _tail(text, max_lines=30, max_chars=4000):
    if not text:
        return None
    lines = text.splitlines()
    tailed = '\n'.join(lines[-max_lines:])
    if len(tailed) > max_chars:
        return tailed[-max_chars:]
    return tailed

def _error_text(stdout, stderr):
    return (stdout or '') + ' ' + (stderr or '')

class ProgressState:
    def __init__(self):
        self.lock = threading.RLock()
        self.run_id = str(uuid.uuid4())
        self.sequence = 0
        self.events = []
        self.legacy_content = 'RUNNING\n'
        now = _now_iso()
        self.summary = {
            'schema_version': SCHEMA_VERSION,
            'run_id': self.run_id,
            'status': 'running',
            'current_stage': None,
            'started_at': now,
            'updated_at': now,
            'completed_at': None,
            'exit_code': None,
            'stages': {},
            'event_count': 0,
        }
        self._sync_files_locked()

    def _sync_files_locked(self):
        _atomic_write(LOG_FILE, self.legacy_content)
        jsonl = ''.join(json.dumps(event, sort_keys=True) + '\n' for event in self.events)
        _atomic_write(JSONL_FILE, jsonl)
        _atomic_write(SUMMARY_FILE, json.dumps(self.summary, indent=2, sort_keys=True) + '\n')

    def set_legacy(self, content):
        if not content.endswith('\n'):
            content += '\n'
        with self.lock:
            self.legacy_content = content
            self.summary['updated_at'] = _now_iso()
            self._sync_files_locked()
        print(content.rstrip('\n'), flush=True)

    def append_legacy(self, message):
        with self.lock:
            base = self.legacy_content
            if base == 'RUNNING\n':
                base = ''
            if base and not base.endswith('\n'):
                base += '\n'
            self.legacy_content = base + message + '\n'
            self.summary['updated_at'] = _now_iso()
            self._sync_files_locked()
        print(message, flush=True)

    def emit(
        self,
        stage,
        status,
        message,
        event_type='stage_update',
        actual=None,
        threshold=None,
        raw_error=None,
        stdout=None,
        stderr=None,
        exit_code=None,
    ):
        catalog = EVENT_CATALOG[stage]
        event_actual = copy.deepcopy(actual)
        event_threshold = copy.deepcopy(threshold)
        with self.lock:
            self.sequence += 1
            timestamp = _now_iso()
            event = {
                'schema_version': SCHEMA_VERSION,
                'run_id': self.run_id,
                'sequence': self.sequence,
                'timestamp': timestamp,
                'event_type': event_type,
                'stage': stage,
                'status': status,
                'title': catalog['title'],
                'purpose': catalog['purpose'],
                'message': message,
                'actual': event_actual,
                'threshold': event_threshold,
                'raw_error': raw_error,
                'stdout_tail': _tail(stdout),
                'stderr_tail': _tail(stderr),
                'remediation': catalog['remediation'],
                'doc_id': catalog['doc_id'],
            }
            self.events.append(event)
            self.summary['current_stage'] = stage
            self.summary['updated_at'] = timestamp
            self.summary['event_count'] = len(self.events)
            self.summary['stages'][stage] = {
                'status': status,
                'message': message,
                'updated_at': timestamp,
                'sequence': self.sequence,
                'actual': event_actual,
                'threshold': event_threshold,
                'doc_id': catalog['doc_id'],
            }
            if stage == 'final_summary':
                self.summary['status'] = status
                self.summary['completed_at'] = timestamp
                self.summary['exit_code'] = exit_code
            elif status in ('failed', 'error'):
                self.summary['status'] = 'failed'
            elif self.summary['status'] == 'running':
                self.summary['status'] = 'running'
            self._sync_files_locked()
        return event

    def render_legacy(self):
        with self.lock:
            return self.legacy_content

    def render_jsonl(self):
        with self.lock:
            return ''.join(json.dumps(event, sort_keys=True) + '\n' for event in self.events)

    def render_summary(self):
        with self.lock:
            return json.dumps(self.summary, indent=2, sort_keys=True) + '\n'

# Initialize progress files immediately so a CLI client (and anyone running
# `docker exec ... cat /verification/progress.log` for triage) always has
# something to read, even if torch import, openssl cert generation, or the
# HTTPS server itself fails to start below.
progress_state = ProgressState()
progress_state.emit(
    'image_started',
    'running',
    'Self-test image runtime started.',
    event_type='image_started',
)

# Import torch only after progress.log exists; record an import-time
# failure (driver mismatch, libcuda missing, NCCL preload bust, etc.)
# before dying so the failure mode is discoverable.
try:
    import torch
except Exception as _torch_import_error:
    error_message = f'ERROR: torch import failed: {_torch_import_error}'
    progress_state.set_legacy(error_message)
    progress_state.emit(
        'final_summary',
        'failed',
        'Torch import failed before tests could run.',
        event_type='final_summary',
        raw_error=str(_torch_import_error),
        exit_code=1,
    )
    raise

from systemreqtest import required_system_ram_bytes

def generate_self_signed_cert():
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("Generating self-signed certificate and private key...")
        try:
            subprocess.run([
                'openssl', 'req', '-new', '-newkey', 'rsa:2048', '-days', '365', '-nodes', '-x509',
                '-subj', '/CN=localhost',
                '-keyout', KEY_FILE, '-out', CERT_FILE
            ], check=True)
            print("Certificate and key generated successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            progress_state.set_legacy(f'ERROR: cert generation failed: {e}')
            progress_state.emit(
                'final_summary',
                'failed',
                'Certificate generation failed before tests could run.',
                event_type='final_summary',
                raw_error=str(e),
                exit_code=1,
            )
            print(f"Failed to generate certificate and key: {e}")
            sys.exit(1)

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Serve progress endpoints over GET. Inherits from BaseHTTPRequestHandler
    rather than SimpleHTTPRequestHandler so there's no inherited do_HEAD
    or file-serving methods that would leak working-directory contents
    (server.key, test scripts, mtimes) to unauthenticated clients."""

    def do_GET(self):
        if self.path == '/progress':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(progress_state.render_legacy().encode('utf-8'))
        elif self.path == '/progress.jsonl':
            self.send_response(200)
            self.send_header('Content-type', 'application/x-ndjson')
            self.end_headers()
            self.wfile.write(progress_state.render_jsonl().encode('utf-8'))
        elif self.path == '/summary.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(progress_state.render_summary().encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

generate_self_signed_cert()

def start_https_server():
    httpd = http.server.HTTPServer(('0.0.0.0', PORT), CustomHTTPRequestHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(f"Serving HTTPS on port {PORT}...")
    httpd.serve_forever()

# Daemon so sys.exit() at the end of the script can actually take the
# container down with a non-zero code on failure. The grace sleep before
# exit gives the CLI a final /progress poll before the daemon dies.
server_thread = threading.Thread(target=start_https_server, daemon=True)
server_thread.start()
progress_state.emit(
    'image_started',
    'passed',
    'HTTPS progress server started.',
    event_type='stage_completed',
)

def log_message(message):
    progress_state.append_legacy(message)

def write_message(message):
    progress_state.set_legacy(message)

def _run_command(command):
    return subprocess.run(command, capture_output=True, text=True)

def _collect_system_requirements_metrics():
    try:
        gpu_count = torch.cuda.device_count()
        gpus = []
        total_vram = 0
        for index in range(gpu_count):
            properties = torch.cuda.get_device_properties(index)
            total_memory = properties.total_memory
            used_memory = torch.cuda.memory_allocated(index) + torch.cuda.memory_reserved(index)
            total_vram += total_memory
            gpus.append({
                'index': index,
                'name': properties.name,
                'total_vram_bytes': total_memory,
                'used_vram_bytes': used_memory,
                'used_vram_fraction': used_memory / total_memory if total_memory else None,
            })
        physical_cpu_cores = psutil.cpu_count(logical=False)
        total_ram = psutil.virtual_memory().total
        return {
            'gpu_count': gpu_count,
            'gpus': gpus,
            'total_gpu_vram_bytes': total_vram,
            'total_ram_bytes': total_ram,
            'physical_cpu_cores': physical_cpu_cores,
        }, {
            'max_used_vram_fraction_per_gpu': 0.02,
            'min_total_ram_bytes': required_system_ram_bytes(total_vram),
            'min_physical_cpu_cores': 2 * gpu_count,
        }
    except Exception as e:
        return {'collection_error': str(e)}, None

def _gpu_count_actual():
    try:
        return {'gpu_count': torch.cuda.device_count()}
    except Exception as e:
        return {'collection_error': str(e)}

def _parse_resnet_actual(stdout):
    actual = _gpu_count_actual()
    match = re.search(r'Successfully executed with batch size (\d+)', stdout or '')
    if match:
        actual['successful_batch_size'] = int(match.group(1))
    return actual

def _emit_command_result(stage, result, success_message, failure_message, actual=None, threshold=None):
    print(result.stdout, flush=True)
    print(result.stderr, flush=True)
    if result.returncode == 0:
        progress_state.emit(
            stage,
            'passed',
            success_message,
            event_type='stage_completed',
            actual=actual,
            threshold=threshold,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        return True
    progress_state.emit(
        stage,
        'failed',
        failure_message,
        event_type='stage_completed',
        actual=actual,
        threshold=threshold,
        raw_error=_error_text(result.stdout, result.stderr).strip(),
        stdout=result.stdout,
        stderr=result.stderr,
    )
    return False

def _final_summary(success, message):
    progress_state.emit(
        'final_summary',
        'passed' if success else 'failed',
        message,
        event_type='final_summary',
        exit_code=0 if success else 1,
    )

def run_tests():
    """Return True on full success, False on any test failure."""
    progress_state.set_legacy("Starting tests...")

    # First Test
    log_message("Running system requirements test...")
    system_actual, system_threshold = _collect_system_requirements_metrics()
    progress_state.emit(
        'system_requirements',
        'running',
        'Running system requirements test.',
        actual=system_actual,
        threshold=system_threshold,
    )
    result = _run_command(['python3', 'systemreqtest.py'])
    if _emit_command_result(
        'system_requirements',
        result,
        'System requirements test passed.',
        'System requirements test failed.',
        actual=system_actual,
        threshold=system_threshold,
    ):
        log_message("TESTED : System requirements test passed.")
    else:
        write_message("ERROR 1: System requirements test failed. " + _error_text(result.stdout, result.stderr))
        _final_summary(False, 'Self-test failed during system requirements.')
        return False

    # Second Test
    log_message("Running ResNet18 test on all GPUs...")
    progress_state.emit(
        'resnet',
        'running',
        'Running ResNet18 test on all GPUs.',
        actual=_gpu_count_actual(),
        threshold={'requires_any_successful_batch_size': True},
    )
    result = _run_command(['python3', 'testAllGpusResNet50.py'])
    resnet_actual = _parse_resnet_actual(result.stdout)
    if _emit_command_result(
        'resnet',
        result,
        'ResNet18 test passed.',
        'ResNet18 test failed.',
        actual=resnet_actual,
        threshold={'requires_any_successful_batch_size': True},
    ):
        log_message("TESTED : ResNet18 passed")
    else:
        write_message("ERROR 2: Test All GPU ResNet18 failed. " + _error_text(result.stdout, result.stderr))
        _final_summary(False, 'Self-test failed during ResNet GPU execution.')
        return False

    # Third Test
    log_message("Running ECC test on all GPUs...")
    ecc_actual = _gpu_count_actual()
    progress_state.emit(
        'ecc',
        'running',
        'Running ECC test on all GPUs.',
        actual=ecc_actual,
        threshold={'target_allocation_fraction_per_gpu': 0.95},
    )
    result = _run_command(['python3', 'eccfunction.py'])
    if _emit_command_result(
        'ecc',
        result,
        'ECC test passed.',
        'ECC test failed.',
        actual=ecc_actual,
        threshold={'target_allocation_fraction_per_gpu': 0.95},
    ):
        log_message("TESTED : ECC test passed.")
    else:
        write_message("ERROR 3: ECC test failed. " + _error_text(result.stdout, result.stderr))
        _final_summary(False, 'Self-test failed during ECC memory allocation.')
        return False

    # Fourth Test: NCCL distributed test (dynamic GPU detection)
    try:
        gpu_count = torch.cuda.device_count()
    except Exception as e:
        write_message("ERROR 4: Unable to detect GPU count using PyTorch. " + str(e))
        progress_state.emit(
            'nccl',
            'failed',
            'Unable to detect GPU count using PyTorch.',
            event_type='stage_completed',
            actual={'collection_error': str(e)},
            threshold={'min_gpu_count': 1},
            raw_error=str(e),
        )
        _final_summary(False, 'Self-test failed before NCCL could run.')
        return False

    if gpu_count == 0:
        write_message("ERROR 4: No GPUs detected. Cannot run NCCL test.")
        progress_state.emit(
            'nccl',
            'failed',
            'No GPUs detected. Cannot run NCCL test.',
            event_type='stage_completed',
            actual={'gpu_count': gpu_count},
            threshold={'min_gpu_count': 1},
            raw_error='No GPUs detected.',
        )
        _final_summary(False, 'Self-test failed before NCCL could run.')
        return False

    log_message(f"Running NCCL distributed test with {gpu_count} GPUs...")
    nccl_actual = {'gpu_count': gpu_count, 'backend': 'NCCL', 'num_machines': 1, 'machine_rank': 0}
    progress_state.emit(
        'nccl',
        'running',
        f'Running NCCL distributed test with {gpu_count} GPUs.',
        actual=nccl_actual,
        threshold={'min_gpu_count': 1, 'requires_all_ranks_to_initialize': True},
    )
    result = _run_command([
        'python3',
        'test_NCCL.py',
        '--backend', 'NCCL',
        '--num-gpus', str(gpu_count),   # pass the dynamically detected GPU count
        '--num-machines', '1',
        '--machine-rank', '0'
        # The --dist-url defaults to tcp://127.0.0.1:1234 in test_NCCL.py
    ])
    if _emit_command_result(
        'nccl',
        result,
        'NCCL distributed test passed.',
        'NCCL distributed test failed.',
        actual=nccl_actual,
        threshold={'min_gpu_count': 1, 'requires_all_ranks_to_initialize': True},
    ):
        log_message("TESTED : NCCL distributed test passed.")
    else:
        write_message("ERROR 4: NCCL distributed test failed. " + _error_text(result.stdout, result.stderr))
        _final_summary(False, 'Self-test failed during NCCL distributed communication.')
        return False

    # Fifth Test - Run stress-ng and gpu-burn simultaneously
    log_message("Running stress-ng and gpu-burn tests simultaneously for 60 seconds...")
    # Use all CPU cores except one; clamp to at least 1 (psutil.cpu_count
    # can return None on some unusual cgroup/container setups, and
    # `stress-ng --cpu 0` errors out before doing anything useful).
    cpu_cores = max(1, (psutil.cpu_count(logical=True) or 1) - 1)
    stress_ng_command = ['stress-ng', '--cpu', str(cpu_cores), '--timeout', '60s']
    gpu_burn_command = ['./gpu_burn', '60']
    stress_actual = {'cpu_cores': cpu_cores, 'duration_seconds': 60}
    stress_threshold = {
        'stress_ng_returncode': 0,
        'gpu_burn_returncode': 0,
        'duration_seconds': 60,
    }
    progress_state.emit(
        'stress_gpu_burn',
        'running',
        'Running stress-ng and gpu-burn tests simultaneously for 60 seconds.',
        actual=stress_actual,
        threshold=stress_threshold,
    )

    try:
        # text=True + errors='replace' so non-UTF-8 bytes in tool output
        # (terminal control sequences, truncated progress lines, etc.)
        # don't trip UnicodeDecodeError and get mis-reported as ERROR 7.
        stress_ng_process = subprocess.Popen(
            stress_ng_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors='replace',
        )
        gpu_burn_process = subprocess.Popen(
            gpu_burn_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors='replace',
        )

        stress_ng_stdout, stress_ng_stderr = stress_ng_process.communicate()
        gpu_burn_stdout, gpu_burn_stderr = gpu_burn_process.communicate()
        stress_actual.update({
            'stress_ng_returncode': stress_ng_process.returncode,
            'gpu_burn_returncode': gpu_burn_process.returncode,
        })
        combined_stdout = (
            'stress-ng stdout:\n' + (stress_ng_stdout or '') +
            '\ngpu-burn stdout:\n' + (gpu_burn_stdout or '')
        )
        combined_stderr = (
            'stress-ng stderr:\n' + (stress_ng_stderr or '') +
            '\ngpu-burn stderr:\n' + (gpu_burn_stderr or '')
        )

        if stress_ng_process.returncode == 0 and gpu_burn_process.returncode == 0:
            progress_state.emit(
                'stress_gpu_burn',
                'passed',
                'stress-ng and gpu-burn tests passed.',
                event_type='stage_completed',
                actual=stress_actual,
                threshold=stress_threshold,
                stdout=combined_stdout,
                stderr=combined_stderr,
            )
            write_message("DONE")
            _final_summary(True, 'Self-test completed successfully.')
            return True
        else:
            if stress_ng_process.returncode != 0:
                write_message("ERROR 5: stress-ng test failed. " + _error_text(stress_ng_stdout, stress_ng_stderr))
            if gpu_burn_process.returncode != 0:
                write_message("ERROR 6: gpu-burn test failed. " + _error_text(gpu_burn_stdout, gpu_burn_stderr))
            progress_state.emit(
                'stress_gpu_burn',
                'failed',
                'stress-ng or gpu-burn test failed.',
                event_type='stage_completed',
                actual=stress_actual,
                threshold=stress_threshold,
                raw_error=_error_text(combined_stdout, combined_stderr).strip(),
                stdout=combined_stdout,
                stderr=combined_stderr,
            )
            _final_summary(False, 'Self-test failed during stress-ng and gpu-burn.')
            return False
    except Exception as e:
        write_message(f"ERROR 7: An exception occurred while running the tests: {str(e)}")
        progress_state.emit(
            'stress_gpu_burn',
            'failed',
            'An exception occurred while running stress-ng and gpu-burn.',
            event_type='stage_completed',
            actual=stress_actual,
            threshold=stress_threshold,
            raw_error=str(e),
        )
        _final_summary(False, 'Self-test failed during stress-ng and gpu-burn.')
        return False

# Run the tests, then keep the HTTPS server up for a short grace window
# so the CLI's poll loop can read the final progress.log state. Then
# exit with a code that reflects the test result so orchestrators
# waiting on the container (k8s health checks, docker-compose, etc.)
# get a real signal instead of "container is up forever".
EXIT_GRACE_SECONDS = 30
_success = run_tests()
time.sleep(EXIT_GRACE_SECONDS)
sys.exit(0 if _success else 1)
