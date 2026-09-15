#!/usr/bin/env python3
"""Generate the host self-test reference page from self-test source code.

The generator intentionally reads the current Vast CLI diagnostics and
self-test image metadata instead of duplicating threshold and remediation copy
by hand in docs. Pass explicit ``--vast-cli`` and ``--self-test`` paths when
generating from source branches that are not checked out next to this docs repo.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DOCS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = DOCS_ROOT.parent


def existing_default(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


DEFAULT_VAST_CLI = existing_default(
    WORKSPACE_ROOT / "vast-cli",
    WORKSPACE_ROOT / "vast-cli-con1510-p1",
)
DEFAULT_SELF_TEST = WORKSPACE_ROOT / "self-test"
DEFAULT_OUTPUT = DOCS_ROOT / "host" / "self-test-reference.mdx"
CLI_OPTION_TOKEN = re.compile(r"(?<![\w-])--[A-Za-z0-9][A-Za-z0-9_-]*(?![\w-])")
BACKTICK_RUN = re.compile(r"`+")


def run_git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def repo_ref(repo: Path) -> dict[str, str]:
    remote = (
        run_git(repo, "remote", "get-url", "upstream")
        or run_git(repo, "remote", "get-url", "origin")
        or repo.name
    )
    remote_name = remote.rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    if "vast-ai/vast-cli" in remote or remote_name in {"vast-cli", "vast-python"}:
        label = "vast-ai/vast-cli"
    elif "vast-ai/self-test" in remote or remote_name == "self-test":
        label = "vast-ai/self-test"
    else:
        label = repo.name
    branch = run_git(repo, "branch", "--show-current") or ""
    if not branch:
        containing_refs = run_git(repo, "branch", "-r", "--contains", "HEAD", "--format=%(refname:short)") or ""
        refs = [ref.strip() for ref in containing_refs.splitlines() if ref.strip()]
        preferred_refs = ("upstream/master", "origin/master", "upstream/main", "origin/main")
        branch = next((ref for ref in preferred_refs if ref in refs), refs[0] if refs else "unknown")
    branch = re.sub(r"^(?:origin|upstream)/", "", branch)
    commit = run_git(repo, "rev-parse", "--short", "HEAD") or "unknown"
    status = run_git(repo, "status", "--porcelain") or ""
    return {
        "label": label,
        "branch": branch,
        "commit": commit,
        "dirty": "yes" if status else "no",
    }


def literal_assignment(path: Path, name: str) -> Any:
    module = ast.parse(path.read_text(), filename=str(path))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise ValueError(f"{name} not found in {path}")


def first_regex(text: str, pattern: str, default: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else default


def parse_cli_image_config(vast_cli: Path) -> dict[str, Any]:
    machines_py = vast_cli / "vastai" / "cli" / "commands" / "machines.py"
    text = machines_py.read_text()
    repo = first_regex(text, r'docker_repo\s*=\s*"([^"]+)"', "vastai/test")
    prefix = first_regex(text, r'image_tag_prefix\s*=\s*"([^"]+)"', "self-test-v2-cuda")
    versions = []
    for left, right in re.findall(r'"(\d+\.\d+)"\s*:\s*image_for\("(\d+\.\d+)"\)', text):
        if left == right:
            versions.append(left)
    return {
        "repo": repo,
        "prefix": prefix,
        "versions": versions or ["11.8", "12.8", "13.0", "13.3"],
    }


def parse_self_test_image_catalog(self_test: Path) -> dict[str, dict[str, str]]:
    readme = self_test / "README.md"
    catalog: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r"^\| `vastai/test:self-test-cuda-(\d+\.\d+)` \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$"
    )
    for line in readme.read_text().splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        version, torch_version, targets, platforms = match.groups()
        catalog[version] = {
            "torch": torch_version.strip(),
            "targets": targets.strip(),
            "platforms": platforms.strip(),
        }
    return catalog


def cell(value: Any) -> str:
    text = "" if value is None else str(value)
    text = normalize_text(text)
    text = format_cli_option_tokens(text)
    text = html.escape(text, quote=False)
    text = text.replace("\n", "<br />")
    text = text.replace("|", "\\|")
    return text


def normalize_text(text: str) -> str:
    text = text.replace("1 listed GPU(s)", "the listed GPU count")
    text = text.replace("Machine ID", "machine")
    text = text.replace("machine ID", "machine")
    text = text.replace("machine_id", "machine")
    text = text.replace(
        "vastai search offers 'machine=example rentable=any rented=any'",
        "review the machine's listing and offer state in the Console",
    )
    text = text.replace(
        "vastai search offers 'machine=<machine> rentable=any rented=any'",
        "review the machine's listing and offer state in the Console",
    )
    return text.strip()


def format_cli_option_tokens(text: str) -> str:
    """Wrap bare CLI flags while preserving existing Markdown code spans.

    Generated diagnostic strings are generally prose, but source messages can
    already use inline code or fenced examples. Only prose segments are
    rewritten so existing backtick delimiters and code-fence contents are left
    untouched.
    """
    rendered: list[str] = []
    cursor = 0

    while match := BACKTICK_RUN.search(text, cursor):
        rendered.append(CLI_OPTION_TOKEN.sub(lambda token: code(token.group(0)), text[cursor : match.start()]))
        delimiter = match.group(0)
        closing = re.compile(rf"(?<!`)`{{{len(delimiter)}}}(?!`)").search(text, match.end())
        if closing is None:
            rendered.append(text[match.start() :])
            return "".join(rendered)
        rendered.append(text[match.start() : closing.end()])
        cursor = closing.end()

    rendered.append(CLI_OPTION_TOKEN.sub(lambda token: code(token.group(0)), text[cursor:]))
    return "".join(rendered)


def bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def code(value: str) -> str:
    return f"`{value}`"


def preflight_threshold(check: dict[str, Any], system_ram_cap_mib: int) -> str:
    check_id = check["id"]
    if check_id == "cuda.version":
        return "CUDA version >= 11.8"
    if check_id == "reliability":
        return "Reliability > 0.90"
    if check_id == "network.direct_ports":
        return "Direct ports >= 3 * listed GPUs"
    if check_id == "pcie.bandwidth":
        return "PCIe bandwidth > 2.85 GB/s"
    if check_id == "network.download":
        return "Download >= min(500, max(100, 500 * total_vram_gib / 192)) Mb/s"
    if check_id == "network.upload":
        return "Upload >= min(500, max(100, 500 * total_vram_gib / 192)) Mb/s"
    if check_id == "gpu.ram":
        return "Per-GPU VRAM > 7 GiB"
    if check_id == "system.ram":
        return f"System RAM >= min(0.95 * total GPU VRAM, {system_ram_cap_mib:,} MiB)"
    if check_id == "cpu.cores":
        return "`offer.cpu_cores` >= 2 × `num_gpus`"
    if check_id == "network.direct_ports.recommended_max":
        return "direct ports <= 64 * listed GPUs"
    return f"{check.get('operator', '')} {check.get('required', '')} {check.get('unit', '')}".strip()


def preflight_purpose(check: dict[str, Any]) -> str:
    if check["id"] == "gpu.ram":
        return "The verification workload requires more than 7 GiB of VRAM per GPU."
    if check["id"] == "network.direct_ports.recommended_max":
        return "The CLI flags counts above 64 ports per listed GPU as an advisory about oversized mappings."
    if check["id"] == "cpu.cores":
        return (
            "The CLI checks the reported offer core count against twice the listed GPU count. "
            "This check does not establish how `offer.cpu_cores` was measured."
        )
    return check["purpose"]


def preflight_remediation(check: dict[str, Any]) -> str:
    if check["id"] == "network.direct_ports.recommended_max":
        return "This is advisory only, not a self-test gate. Keep enough direct ports for self-test and normal workloads, and review very large unused ranges."
    if check["id"] == "cuda.version":
        return "Update the NVIDIA driver/CUDA stack, then confirm the machine is listed and healthy in the Console."
    if check["id"] == "cpu.cores":
        return "Check the reported core count and GPU count; add CPU capacity or reduce the listed GPU count if this preflight gate is unmet."
    return check["remediation"]


def runtime_thresholds(system_ram_cap_mib: int) -> dict[str, str]:
    return {
        "image_started": "The runtime container starts and writes the first progress event.",
        "system_requirements": (
            "For each visible GPU, PyTorch allocated plus reserved memory must be at most 2% of its reported VRAM; system RAM is at least "
            f"95% of total GPU VRAM capped at {system_ram_cap_mib:,} MiB; "
            "there are at least 2 physical CPU cores per visible GPU, counted with `psutil.cpu_count(logical=False)`. "
            "Hyperthreads/logical CPUs do not count as physical cores."
        ),
        "resnet": "A CUDA ResNet18 workload completes on the visible GPU set at any tested batch size.",
        "ecc": "The test targets approximately 95% of total memory on each visible GPU and passes only if the allocations succeed.",
        "nccl": "At least 1 GPU is visible and all NCCL ranks initialize and synchronize on one machine.",
        "stress_gpu_burn": "stress-ng and gpu-burn run together for 60 seconds and both exit with code 0.",
        "final_summary": "The runtime reports the overall pass/fail result and exit code.",
    }


NO_OFFER_ROOT_STATE_COPY = {
    "currently_rented": "Visible offers exist and one or more are already rented.",
    "deverified_or_below_threshold": "Visible offers exist but host reliability, verification state, vericode, or error metadata points to a host quality gate.",
    "api_permission_failed": "The API key or account could not read the machine or offer state required by self-test.",
    "zero_active_offers": "The machine lookup is visible, but no on-demand offers were returned to this API account. This is a likely state, not proof that no offers exist.",
    "offline_or_not_listed": "The machine is not visible to the account or appears offline/not listed.",
    "unknown_no_rentable_offer": "Visible offers exist, but the payload does not expose a specific non-rentable reason.",
}


PREFLIGHT_FAILURE_CODES = [
    (
        "no_offer",
        "No on-demand offer found for the machine.",
        "Confirm the host is online, listed, and has a visible on-demand offer in the Console.",
    ),
    (
        "no_rentable_offer",
        "Offers were visible, but none were currently rentable.",
        "Wait for rentals/state refreshes or inspect host offer state.",
    ),
    (
        "api_permission_failed",
        "The API key could not inspect the required machine/offer state.",
        "Use an API key/account with host machine and offer visibility.",
    ),
    (
        "preflight_requirements_failed",
        "One or more minimum requirement checks failed before renting.",
        "Resolve the failed checks or rerun with --ignore-requirements for runtime diagnostics only.",
    ),
]


def failure_area(code_value: str) -> str:
    if code_value.startswith("instance_") or code_value in {
        "missing_public_ip",
        "progress_port_not_mapped",
        "progress_endpoint_unreachable",
        "progress_endpoint_lost",
        "progress_empty_timeout",
        "runtime_test_timeout",
        "interrupted",
        "cleanup_failed",
    }:
        return "Launch, network, or cleanup"
    if code_value in {"docker_pull_failed", "daemon_startup_failed"}:
        return "Image or container startup"
    if code_value in {
        "nvml_failed",
        "resnet_failed",
        "ecc_failed",
        "nccl_failed",
        "stress_gpu_burn_failed",
        "legacy_progress_error",
    }:
        return "Runtime test"
    return "Runtime"


def load_cli_metadata(vast_cli: Path) -> dict[str, Any]:
    sys.path.insert(0, str(vast_cli))
    try:
        from vastai.cli.self_test.machine_diagnostics import (  # type: ignore
            NO_OFFER_ROOT_STATES,
            SYSTEM_RAM_REQUIREMENT_CAP_MIB,
            preflight_requirement_checks,
        )
        from vastai.cli.self_test.runtime_diagnostics import failure_catalog  # type: ignore
        from vastai.cli.self_test.support_bundle import (  # type: ignore
            DEFAULT_BUNDLE_DIR,
            MAX_LOG_BYTES,
            MAX_TEXT_BYTES,
        )
        from vastai.cli.util import required_inet_mbps  # type: ignore
    finally:
        try:
            sys.path.remove(str(vast_cli))
        except ValueError:
            pass

    sample_offer = {
        "id": 1,
        "machine_id": "example",
        "gpu_name": "RTX_4090",
        "num_gpus": 1,
        "dph_total": 0.1,
        "dlperf": 100,
        "cuda_max_good": 13.3,
        "compute_cap": 890,
        "reliability": 0.99,
        "direct_port_count": 100,
        "pcie_bw": 16.0,
        "inet_down": 500,
        "inet_up": 500,
        "gpu_ram": 24 * 1024,
        "gpu_total_ram": 24 * 1024,
        "cpu_ram": 64 * 1024,
        "cpu_cores": 8,
        "rentable": True,
        "rented": False,
        "verification": "verified",
    }

    return {
        "preflight_checks": preflight_requirement_checks(sample_offer),
        "failure_catalog": failure_catalog(),
        "no_offer_root_states": list(NO_OFFER_ROOT_STATES),
        "system_ram_cap_mib": SYSTEM_RAM_REQUIREMENT_CAP_MIB,
        "support_bundle": {
            "default_bundle_dir": DEFAULT_BUNDLE_DIR,
            "max_text_bytes": MAX_TEXT_BYTES,
            "max_log_bytes": MAX_LOG_BYTES,
        },
        "bandwidth_examples": [
            ("8 GiB total VRAM", required_inet_mbps(8 * 1024)),
            ("48 GiB total VRAM", required_inet_mbps(48 * 1024)),
            ("80 GiB total VRAM", required_inet_mbps(80 * 1024)),
            ("96 GiB total VRAM", required_inet_mbps(96 * 1024)),
            ("160 GiB total VRAM", required_inet_mbps(160 * 1024)),
            ("192 GiB total VRAM or more", required_inet_mbps(192 * 1024)),
        ],
    }


def render_preflight_table(checks: list[dict[str, Any]], system_ram_cap_mib: int) -> str:
    lines = [
        "| Check | Gate | Purpose | Host guidance |",
        "| --- | --- | --- | --- |",
    ]
    for check in checks:
        status = "Advisory" if check.get("status") == "info" else "Required"
        gate = f"{status}: {preflight_threshold(check, system_ram_cap_mib)}"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{code(check['id'])}<br />{cell(check['title'])}",
                    cell(gate),
                    cell(preflight_purpose(check)),
                    cell(preflight_remediation(check)),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_bandwidth_examples(examples: list[tuple[str, float]]) -> str:
    lines = ["| Total machine VRAM | Required upload and download |", "| --- | --- |"]
    for label, mbps in examples:
        value = f"{mbps:.2f}".rstrip("0").rstrip(".")
        suffix = " Mb/s (rounded)" if float(value) != mbps else " Mb/s"
        lines.append(f"| {cell(label)} | {cell(value + suffix)} |")
    return "\n".join(lines)


def render_runtime_stage_table(event_catalog: dict[str, dict[str, Any]], thresholds: dict[str, str]) -> str:
    lines = [
        "| Stage | Pass condition / threshold | Purpose | Failure guidance |",
        "| --- | --- | --- | --- |",
    ]
    for stage, entry in event_catalog.items():
        remediation = " ".join(entry.get("remediation") or [])
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{code(stage)}<br />{cell(entry['title'])}",
                    cell(thresholds.get(stage, "")),
                    cell(entry["purpose"]),
                    cell(remediation),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_image_table(image_config: dict[str, Any], image_catalog: dict[str, dict[str, str]]) -> str:
    lines = [
        "| CLI image | Torch | Targets | Platforms |",
        "| --- | --- | --- | --- |",
    ]
    for version in image_config["versions"]:
        details = image_catalog.get(version, {})
        image = f"{image_config['repo']}:{image_config['prefix']}-{version}"
        target = details.get("targets", "").split(";", 1)[0]
        if version == "11.8":
            target += "; legacy GPU target"
        if version == "13.3":
            target += "; PyTorch index `cu132`"
        lines.append(
            "| "
            + " | ".join(
                [
                    code(image) + " (CLI-selected tag)",
                    cell("Build pin: " + details.get("torch", "")),
                    cell("Build target: " + target),
                    cell("Build platforms: " + details.get("platforms", "")),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_preflight_failure_table(root_states: list[str]) -> str:
    displayed_codes = {row[0] for row in PREFLIGHT_FAILURE_CODES}
    lines = [
        "| Code or root state | Meaning | Guidance |",
        "| --- | --- | --- |",
    ]
    for code_value, summary, guidance in PREFLIGHT_FAILURE_CODES:
        lines.append(f"| {code(code_value)} | {cell(summary)} | {cell(guidance)} |")
    for root_state in root_states:
        if root_state in displayed_codes:
            continue
        lines.append(
            f"| {code(root_state)} | {cell(NO_OFFER_ROOT_STATE_COPY.get(root_state, 'Root state reported by offer diagnostics.'))} | Review the machine page, listing state, active rentals, and offer visibility in the Console. |"
        )
    return "\n".join(lines)


def render_runtime_failure_table(catalog: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Code | Area | Meaning | Remediation | Suggested steps |",
        "| --- | --- | --- | --- | --- |",
    ]
    for code_value, entry in catalog.items():
        suggested = "<br />".join(cell(step) for step in entry.get("suggested_steps") or [])
        lines.append(
            "| "
            + " | ".join(
                [
                    code(code_value),
                    cell(failure_area(code_value)),
                    cell(entry["summary"]),
                    cell(entry["remediation"]),
                    suggested,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def render_result_interpretation() -> str:
    return "\n".join(
        [
            "## How To Read The Result",
            "",
            "Self-test output has two distinct parts: preflight qualification checks and the runtime workload.",
            "",
            "| Result | What it means | What to do next |",
            "| --- | --- | --- |",
            "| Normal pass | The CLI preflight checks and runtime workload passed. This result alone does not guarantee platform verification. | Keep the host stable and listed. Verification remains automated and also depends on the platform’s other criteria. |",
            "| Normal preflight failure | The CLI found one or more requirement failures before renting a temporary instance. | Fix the measured values shown in the CLI, then rerun without `--ignore-requirements`. |",
            "| Runtime failure | The CLI could not complete instance creation, startup, progress collection, or a runtime test stage. The failure code and stage show how far the run reached. | Use the failure code, last reported stage, and available diagnostic bundle to choose the next check. |",
            "| Pass with `--ignore-requirements` | The runtime workload passed, but the CLI did not enforce its preflight requirements as a pass/fail gate. This does not qualify the machine for verification. | Treat this as runtime validation only. Rerun without `--ignore-requirements` to check the normal preflight gate. |",
            "",
            "<Tip>",
            "If you use `--ignore-requirements`, still review any requirement diagnostics from a normal run. A runtime pass proves the container workload can run; it does not prove the machine meets the verification gate.",
            "</Tip>",
        ]
    )


def render_ports_guidance() -> str:
    return "\n".join(
        [
            "### Direct Ports And Port Mapping",
            "",
            "The self-test needs direct public connectivity to the temporary instance. The progress service runs inside the self-test container on `5000/tcp`, but the CLI connects to the mapped external public IP and external port reported by the instance.",
            "",
            "- Minimum gate: at least 3 direct ports per listed GPU.",
            "- Advisory: the CLI flags more than 64 direct ports per listed GPU as an oversized mapping. This advisory does not fail the self-test.",
            "- Port forwarding should target the host's LAN address, not its public address.",
            "- Keep TCP and UDP forwarding symmetric where your network setup requires both protocols.",
            "- If the CLI reports a tested external IP:port, troubleshoot that external mapping first.",
            "- If the host and CLI are on the same LAN, a local failure to reach the public IP can be NAT hairpinning. Retest from an outside network before assuming the port is closed globally.",
            "",
            "<Note>",
            "The CLI can report the external progress port it tested when that mapping is available. That result is not a scan of every direct port; the self-test does not provide a per-port failure list for the entire configured range.",
            "</Note>",
        ]
    )


def render_no_response_guidance() -> str:
    return "\n".join(
        [
            '<span id="no-response-120s" aria-hidden="true" />',
            "### No Response Or Progress Timeout",
            "",
            "A `no response` or progress timeout means the CLI did not receive usable progress from the temporary self-test instance. Check whether the endpoint was never reachable, returned no output, or became unreachable after connecting; then use the failure code and last stage to guide diagnosis.",
            "",
            "Possible causes to check:",
            "",
            "- Router or firewall forwards the external port to the wrong LAN IP.",
            "- The external TCP port is closed, blocked, or not hairpin-accessible from the CLI's network.",
            "- The self-test container never started, crashed, or did not bind the progress service.",
            "- Docker, NVIDIA runtime, or the host daemon stalled during startup.",
            "- The GPU or system hung under load before progress could be reported.",
            "- Upload/network instability prevented progress responses from reaching the CLI.",
            "",
            "First checks:",
            "",
            "- Look at the failure code and the tested external IP:port in CLI output when present.",
            "- Confirm the router/firewall forwards that external port to the host machine.",
            "- Inspect the diagnostic bundle for `instance/container.log`, `instance/daemon.log`, and `instance/show-instance.json` when the instance existed.",
            "- If you ran the CLI from the same LAN as the host, retry from a different network to rule out NAT loopback/hairpinning.",
        ]
    )


def render_not_rentable_guidance() -> str:
    return "\n".join(
        [
            '<span id="machine-not-rentable" aria-hidden="true" />',
            "### Not Found Or Not Rentable",
            "",
            "The CLI uses visible offer and machine state to suggest a likely reason before giving guidance. Treat the reported root state as a diagnostic hint, with the confidence and evidence shown in the output.",
            "",
            "Possible states inferred from CLI-visible data:",
            "",
            "- The machine is currently rented.",
            "- The machine is visible, but no active on-demand offers are visible to the API account.",
            "- The machine is offline, unlisted, or not visible to the API account.",
            "- The machine is deverified, below the reliability threshold, or has offer-side error metadata.",
            "- The API key or account cannot inspect the required host or offer state; check both key validity and permissions.",
            "",
            "Start with the machine page in the Console. Check whether the host is online, listed, already rented, below the reliability gate, missing an active on-demand offer, or being viewed from an account that cannot see the host state.",
        ]
    )


def render_vericode_guidance() -> str:
    return "\n".join(
        [
            '<span id="vericode-8" aria-hidden="true" />',
            "## vericode=8 And Port Networking Issues",
            "",
            "[Glossary: vericode](/host/glossary#vericode)",
            "",
            "`vericode=8` means the machine has a host-facing `error_msg` in platform state. If the visible message is `Port Networking Issues`, `Port issue`, or similar wording, treat it as a direct-port or connectivity problem. Other `vericode=8` cases can point to Docker/NVIDIA runtime, CDI, PCIe, daemon, or other machine errors, so use the exact Console message when choosing the next fix.",
            "",
            "For port-networking cases, check closed external ports, forwarding to the wrong LAN IP, CGNAT or double NAT, missing inbound public IP, host firewall rules, TCP/UDP mismatch, asymmetric protocol handling, and stale port ranges. See [Network & Ports](/host/network-ports) and [Machine Error Reference](/host/machine-errors).",
        ]
    )


def render_nccl_guidance() -> str:
    return "\n".join(
        [
            '<span id="nccl-failed" aria-hidden="true" />',
            "### `nccl_failed` Deep Dive",
            "",
            "`nccl_failed` is the CLI’s NCCL-related failure classification, based on the runtime stage or error text. Inspect the original error and last stage: the code alone does not prove that NCCL initialized, that more than one GPU was visible, or that one specific subsystem caused the failure.",
            "",
            "Start with the support bundle, confirm every GPU is visible to `nvidia-smi` and Docker, then check driver/CUDA/PyTorch/NCCL compatibility, peer-to-peer communication, PCIe/NVLink topology, Xid errors, GPU resets, and bus errors.",
            "",
            "On HGX, DGX, or other NVSwitch systems, also check Fabric Manager or NVLSM on the host. The self-test container can show NCCL symptoms, but it cannot confirm whether host services such as `nvidia-fabricmanager` are healthy.",
            "",
            "```bash",
            "systemctl status nvidia-fabricmanager",
            'journalctl -u nvidia-fabricmanager --since "-24h"',
            "nvidia-smi -q | grep -i -A 2 Fabric",
            "nvidia-smi topo -m",
            "```",
        ]
    )


def render_bundle_boundary(support: dict[str, Any]) -> str:
    return "\n".join(
        [
            "## Diagnostic Bundles",
            "",
            "When a self-test fails, the CLI attempts to build a redacted diagnostic tarball unless bundle creation is disabled. Check the reported path or bundle-creation warning.",
            "",
            "- Default output directory: `" + support["default_bundle_dir"] + "`.",
            "- Disable automatic bundles with `--no-support-bundle` or `VAST_SELF_TEST_SUPPORT_BUNDLE=0`.",
            "- Choose another directory with `--support-bundle-dir <dir>`.",
            "- Create a manual CLI-visible bundle with `vastai dump-logs <machine>`.",
            "- Include local host OS/kaalia artifacts only when running on the actual host with `vastai dump-logs <machine> --include-local-host-artifacts`.",
            "",
            "Default self-test bundles include `self-test-output.log`, `self-test-result.json`, `manifest.json`, and `collection-errors.json`. Runtime failures with a created instance can also include `instance/show-instance.json`, `instance/container.log`, and `instance/daemon.log` from the Vast instance logs API.",
            "",
            "<Warning>",
            "When the CLI is run from a laptop or other third-party machine, it cannot collect host-local files such as `/var/lib/vastai_kaalia/kaalia.log*`, `dmesg`, `journalctl`, `/etc/docker/daemon.json`, or `/proc/mounts` from the Vast host. Those artifacts require running the helper on the actual host or adding a future daemon/backend log-collection feature.",
            "</Warning>",
            "",
            f"The bundle uses {support['max_text_bytes']:,}-byte truncation limits for collected text/log content; truncation notices can add bytes, and JSON artifacts are not uniformly capped by that limit. It redacts recognized secret fields, assignments, and explicitly supplied secrets, but hosts should still review the tarball before sharing it with support.",
        ]
    )


def render_page(vast_cli: Path, self_test: Path) -> str:
    cli = load_cli_metadata(vast_cli)
    event_catalog = literal_assignment(self_test / "remote.py", "EVENT_CATALOG")
    image_config = parse_cli_image_config(vast_cli)
    image_catalog = parse_self_test_image_catalog(self_test)
    system_ram_cap_mib = cli["system_ram_cap_mib"]
    support = cli["support_bundle"]

    vast_cli_ref = repo_ref(vast_cli)
    self_test_ref = repo_ref(self_test)

    lines = [
        "---",
        'title: "Verification / Self-test Reference"',
        'sidebarTitle: "Self-test Reference"',
        'description: "Generated reference for host self-test checks, thresholds, failure codes, and guidance."',
        '"canonical": "/host/self-test-reference"',
        "personas:",
        "  - pro-operator",
        "  - headless-operator",
        "---",
        "",
        '<div className="persona-chips"><span className="persona-chip">Pro Operator</span><span className="persona-chip">Headless / DC</span></div>',
        "",
        "{/*",
        "  This page is generated by scripts/generate_self_test_reference.py.",
        "  Do not edit this file by hand; update the Vast CLI/self-test source metadata, then regenerate.",
        f"  Source: {vast_cli_ref['label']} {vast_cli_ref['branch']}@{vast_cli_ref['commit']} dirty={vast_cli_ref['dirty']}.",
        f"  Source: {self_test_ref['label']} {self_test_ref['branch']}@{self_test_ref['commit']} dirty={self_test_ref['dirty']}.",
        "*/}",
        "",
        "The host self-test checks a listed machine against the CLI’s preflight requirements and runs a temporary diagnostic workload.",
        "",
        "When you run `vastai self-test machine <machine>`, the CLI selects a rentable offer for that machine and checks its preflight requirements. If those checks pass, it rents one temporary diagnostic instance, starts the self-test image, polls its progress endpoint, reports the result, and attempts to destroy the instance. Check any cleanup warning and destroy the temporary instance manually if cleanup failed.",
        "",
        "<Note>",
        "Passing this self-test alone does not guarantee verification. The platform also evaluates ongoing health, reliability, supply and demand, and its other verification criteria.",
        "</Note>",
        "",
        "<Warning>",
        "`--ignore-requirements` is for advanced runtime diagnostics only. A pass with requirement checks ignored does not qualify the machine for verification.",
        "</Warning>",
        "",
        render_result_interpretation(),
        "",
        "## Preflight Checks",
        "",
        "These checks run before the CLI rents the temporary self-test instance. Failed required checks stop the normal flow before that instance is created.",
        "",
        render_preflight_table(cli["preflight_checks"], system_ram_cap_mib),
        "",
        "<Note>",
        f"For B300 and other very-high-VRAM hosts, the system RAM gate stops scaling at {system_ram_cap_mib:,} MiB (about 2 TB).",
        "</Note>",
        "",
        render_ports_guidance(),
        "",
        "### Bandwidth Formula",
        "",
        "Upload and download thresholds scale with total machine VRAM:",
        "",
        "```text",
        "required_mbps = min(500, max(100, 500 * total_vram_gib / 192))",
        "```",
        "",
        render_bandwidth_examples(cli["bandwidth_examples"]),
        "",
        "## Self-test Image Selection",
        "",
        "The CLI selects from the self-test image family unless `--test-image` or `VAST_SELF_TEST_IMAGE` overrides the image for controlled testing.",
        "",
        render_image_table(image_config, image_catalog),
        "",
        "Selection rules:",
        "",
        "- Pre-Volta GPUs (`compute_cap < 700`) use the CUDA 11.8 image.",
        "- Volta GPUs (`compute_cap < 750`) are capped at CUDA 12.8 because newer PyTorch CUDA 13 wheels do not include sm_70 support.",
        "- Other hosts use the newest supported self-test image that is less than or equal to `cuda_max_good`.",
        "",
        "## Runtime Stages",
        "",
        "After preflight passes, the CLI starts the self-test image and polls the runtime progress service on container port `5000/tcp`.",
        "",
        render_runtime_stage_table(event_catalog, runtime_thresholds(system_ram_cap_mib)),
        "",
        "## Offer Selection And Preflight Issues",
        "",
        "The CLI reports stable preflight failure codes and, when possible, a likely root state for machines that are not currently rentable.",
        "",
        render_not_rentable_guidance(),
        "",
        render_preflight_failure_table(cli["no_offer_root_states"]),
        "",
        render_vericode_guidance(),
        "",
        "## Runtime Failure Codes",
        "",
        "Runtime failure codes are stable identifiers intended for CLI output, support workflows, and host-facing guidance.",
        "",
        render_no_response_guidance(),
        "",
        render_runtime_failure_table(cli["failure_catalog"]),
        "",
        render_nccl_guidance(),
        "",
        render_bundle_boundary(support),
        "",
    ]

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vast-cli",
        default=os.environ.get("VAST_CLI_REPO", str(DEFAULT_VAST_CLI)),
        type=Path,
        help="Path to a vast-ai/vast-cli checkout or PR worktree.",
    )
    parser.add_argument(
        "--self-test",
        default=os.environ.get("VAST_SELF_TEST_REPO", str(DEFAULT_SELF_TEST)),
        type=Path,
        help="Path to a vast-ai/self-test checkout.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        type=Path,
        help="MDX file to write.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the output is not byte-for-byte current; do not write it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vast_cli = args.vast_cli.resolve()
    self_test = args.self_test.resolve()
    output = args.output.resolve()

    if not (vast_cli / "vastai" / "cli" / "self_test").exists():
        raise SystemExit(f"vast-cli self-test diagnostics not found: {vast_cli}")
    if not (self_test / "remote.py").exists():
        raise SystemExit(f"self-test remote.py not found: {self_test}")

    page = render_page(vast_cli, self_test)
    if args.check:
        if not output.is_file():
            print(f"FAIL: generated output does not exist: {output}", file=sys.stderr)
            return 1
        current = output.read_text(encoding="utf-8")
        if current != page:
            expected_digest = hashlib.sha256(page.encode("utf-8")).hexdigest()
            current_digest = hashlib.sha256(current.encode("utf-8")).hexdigest()
            print(
                "FAIL: generated output is stale: "
                f"{output} (current sha256={current_digest}, expected sha256={expected_digest})",
                file=sys.stderr,
            )
            return 1
        print(f"PASS: generated output is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
