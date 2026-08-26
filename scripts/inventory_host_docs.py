#!/usr/bin/env python3
"""Inventory Host Docs commands, errors, thresholds, and behavior claims.

This script deliberately does not execute documented commands. It performs
read-only extraction, parses fenced Bash examples with ``bash -n``, checks
local image targets, and writes reviewer-friendly Markdown plus machine-
readable JSON and CSV outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOST_ROOT = ROOT / "host"
DEFAULT_JSON = ROOT / "host-docs-verification-inventory.json"
DEFAULT_CSV = ROOT / "host-docs-verification-inventory.csv"
DEFAULT_MARKDOWN = ROOT / "HOST-DOCS-VERIFICATION.md"

FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
HTML_IMAGE_RE = re.compile(r"<(?:img|source)\b[^>]+(?:src|srcSet)=[\"']([^\"']+)[\"']", re.I)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\((/host/[^)\s#]+)(?:#[^)\s]+)?\)")

COMMAND_PREFIX_RE = re.compile(
    r"^(?:\$\s*)?(?:"
    r"vastai|sudo|docker|systemctl|journalctl|nvidia-smi|nvidia-ctk|lspci|dmesg|"
    r"ip|ss|df|du|findmnt|mount|umount|xfs_[\w-]+|lsblk|lscpu|free|curl|wget|"
    r"python(?:3)?|pip(?:3)?|npm|npx|node|git|gh|jq|grep|egrep|awk|sed|cat|"
    r"cp|mv|rm|mkdir|chmod|chown|tail|head|watch|ps|kill|reboot|shutdown|ufw|"
    r"firewall-cmd|iptables|nft|nc|netcat|tcpdump|ping|traceroute|ethtool|"
    r"modprobe|update-grub|apt|apt-get|dnf|yum|snap|tee|echo|export|source|"
    r"Test-NetConnection|Get-NetTCPConnection|Get-NetUDPEndpoint|Get-NetFirewallRule"
    r")\b",
    re.I,
)

ERROR_RE = re.compile(
    r"(?:\berror\b|_error\b|\bfailed\b|_failed\b|\bfailure\b|\btimeout\b|"
    r"_timeout\b|timed out|no response|not found|not rentable|not available|"
    r"unavailable|unreachable|not mapped|no space left|denied|unauthorized|"
    r"unhealthy|deverified|offline|unknown flag|invalid runtime|unresolvable|"
    r"cannot connect|fallen off|fell off|bad bandwidthtest2|port issue|"
    r"networking issues|interrupted|missing_public_ip|no_offer|no_rentable_offer)",
    re.I,
)

THRESHOLD_RE = re.compile(
    r"(?:>=|<=|&gt;=?|&lt;=?|\bat least\b|\bmore than\b|\bless than\b|"
    r"\bminimum\b|\bmaximum\b|\bup to\b|\bcapped? at\b|\bthreshold\b|"
    r"\bper (?:listed )?gpu\b|\bper instance\b|\bwithin\b)"
    r".{0,120}?(?:\d|one|two|three|four|five|six|seven|eight|nine|ten)",
    re.I,
)
NUMBER_UNIT_RE = re.compile(
    r"\b\d[\d,.]*(?:\.\d+)?\s*(?:%|GiB|GB|MiB|MB|TiB|TB|Mb/s|Gbps|Mbps|"
    r"seconds?|minutes?|hours?|days?|ports?|GPUs?|cores?|bytes?|GB/s|MiB/s)\b",
    re.I,
)
BEHAVIOR_RE = re.compile(
    r"\b(?:must|requires?|automatically|cannot|can only|does not|do not|never|"
    r"always|only when|takes? effect|clears?|refresh(?:es)?|remain(?:s)?|"
    r"is disabled|is enabled|is created|is written|is stored|is uploaded|"
    r"is removed|is released|is billed|is charged|is paid)\b",
    re.I,
)

DESTRUCTIVE_RE = re.compile(
    r"(?:\brm\s+-|\bmkfs\b|\bwipefs\b|\bdelete\b|\bdestroy\b|\bunlist\b|"
    r"\bcleanup\b|\bdefrag\b|\bremove-defjob\b|\bumount\b|\breboot\b|"
    r"\bshutdown\b|systemctl\s+(?:stop|restart|disable)|\bkill\b)",
    re.I,
)
PAID_LIVE_RE = re.compile(
    r"vastai\s+(?:self-test\s+machine|create\s+instance|create\s+bid|rent\b)",
    re.I,
)
MUTATING_RE = re.compile(
    r"vastai\s+(?:schedule[- ]maint|cancel[- ]maint|set[- ]min[- ]bid|set[- ]defjob|"
    r"remove[- ]defjob|cleanup[- ]machine|delete[- ]machine|unlist[- ]machine|defrag[- ]machines)",
    re.I,
)
PRIVILEGED_RE = re.compile(
    r"(?:\bsudo\b|/etc/|/var/lib/|apt(?:-get)?\s+(?:install|remove|update|upgrade)|"
    r"dnf\s+install|yum\s+install|curl[^\n|]*\|\s*(?:sudo\s+)?(?:ba)?sh)",
    re.I,
)
ENVIRONMENT_RE = re.compile(
    r"(?:nvidia-smi|nvidia-ctk|docker|systemctl|journalctl|dmesg|lspci|lsblk|"
    r"findmnt|xfs_|tcpdump|iptables|firewall-cmd|ufw|Test-NetConnection|"
    r"Get-NetTCPConnection|Get-NetUDPEndpoint|/proc/|/sys/)",
    re.I,
)
ACCOUNT_READ_RE = re.compile(
    r"vastai\s+(?:show|list|search|metrics|show-maints|show-machine|show-machines)",
    re.I,
)
SECRET_RE = re.compile(r"(?:api[_ -]?key|setup[_ -]?key|token|password|secret)", re.I)


def clean_markdown(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = value.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    value = value.replace("\\|", "|").strip(" |\t")
    return re.sub(r"\s+", " ", value).strip()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def item_id(kind: str, value: str) -> str:
    digest = hashlib.sha256(f"{kind}\0{normalize(value)}".encode()).hexdigest()[:10]
    return f"{kind[:3]}-{digest}"


def source_type(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith(("host/cli/", "host/sdk/", "snippets/host/cli/", "snippets/host/sdk/")):
        return "generated-cli-sdk"
    if relative == "host/self-test-reference.mdx":
        return "generated-self-test"
    return "authored"


def canonical_route(path: Path) -> str:
    relative = path.relative_to(HOST_ROOT).with_suffix("").as_posix()
    return f"/host/{relative}"


def command_tier(command: str) -> tuple[str, str]:
    if PAID_LIVE_RE.search(command):
        return (
            "paid-live",
            "Use an approved test machine/account and budget; record CLI SHA, image digest, machine, instance, cost, and result.",
        )
    if DESTRUCTIVE_RE.search(command) or MUTATING_RE.search(command):
        return (
            "destructive-or-mutating",
            "Verify in a disposable/non-production environment with peer review and recorded before/after state.",
        )
    if SECRET_RE.search(command):
        return (
            "credential-bearing",
            "Verify only with redacted placeholders and an approved test credential; confirm no secret appears in logs or history.",
        )
    if PRIVILEGED_RE.search(command):
        return (
            "privileged-host",
            "Verify on a disposable supported Ubuntu host; record OS version, command output, and expected postcondition.",
        )
    if ENVIRONMENT_RE.search(command):
        return (
            "environment-dependent",
            "Verify on the matching Linux/GPU/network environment and capture representative output or an error fixture.",
        )
    if ACCOUNT_READ_RE.search(command):
        return (
            "account-read-only",
            "Verify against current CLI help and a non-production authenticated account; confirm flags and output shape without mutation.",
        )
    return (
        "local-safe",
        "Verify command availability/help and static syntax locally; use placeholders and do not supply production credentials.",
    )


def bash_syntax(command: str) -> tuple[str, str]:
    parsed_command = re.sub(r"<[A-Za-z0-9_.:/-]+>", "'DOC_PLACEHOLDER'", command)
    try:
        result = subprocess.run(
            ["bash", "-n"],
            input=parsed_command,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return "not-run", "bash is not available"
    if result.returncode == 0:
        return "pass", "Parsed with bash -n after replacing angle-bracket placeholders; no command was executed."
    message = re.sub(r"\s+", " ", result.stderr).strip()
    return "fail", message or f"bash -n exited {result.returncode}"


def verification_for(kind: str, value: str, path: Path) -> tuple[str, str, str]:
    source = source_type(path)
    if kind == "command":
        tier, method = command_tier(value)
        return tier, method, "inventoried-not-executed"
    if source == "generated-self-test":
        return (
            "generated-source",
            "Regenerate from exact Vast CLI and self-test revisions, then compare output and run their source tests.",
            "generator-check-required",
        )
    if source == "generated-cli-sdk":
        return (
            "generated-source",
            "Regenerate from the current CLI/SDK schema or command registry and compare the generated page.",
            "upstream-generator-check-required",
        )
    if kind == "error":
        return (
            "source-or-fixture",
            "Match the literal string/category to CLI, daemon, backend, or console source and retain a redacted captured fixture.",
            "source-confirmation-required",
        )
    if kind == "threshold":
        return (
            "source-owner",
            "Confirm against the enforcing source/config and an exact revision; use an edge-case test at, below, and above the boundary.",
            "source-confirmation-required",
        )
    return (
        "source-owner",
        "Confirm with the owning code, product policy, or named stakeholder and record the source/date in Jira or the PR.",
        "source-confirmation-required",
    )


def add_item(
    items: dict[tuple[str, str], dict[str, Any]],
    *,
    kind: str,
    value: str,
    path: Path,
    line_start: int,
    line_end: int,
    section: str,
    language: str | None = None,
) -> None:
    value = value.strip()
    if not value:
        return
    key = (kind, normalize(value))
    relative = path.relative_to(ROOT).as_posix()
    location = {
        "file": relative,
        "line_start": line_start,
        "line_end": line_end,
        "section": section,
        "source_type": source_type(path),
    }
    if key not in items:
        tier, method, status = verification_for(kind, value, path)
        items[key] = {
            "id": item_id(kind, value),
            "kind": kind,
            "text": value,
            "verification_tier": tier,
            "verification_method": method,
            "status": status,
            "locations": [],
        }
        if language:
            items[key]["language"] = language
        if kind == "command" and language in {"bash", "sh", "shell"}:
            syntax_status, syntax_detail = bash_syntax(value)
            items[key]["static_syntax"] = {
                "tool": "bash -n",
                "status": syntax_status,
                "detail": syntax_detail,
            }
            if syntax_status == "pass":
                items[key]["status"] = "static-syntax-passed-not-executed"
            elif syntax_status == "fail":
                items[key]["status"] = "static-syntax-failed"
    if location not in items[key]["locations"]:
        items[key]["locations"].append(location)


def looks_like_command(value: str) -> bool:
    value = value.strip()
    if value.casefold().startswith("vastai/"):
        return False
    return bool(COMMAND_PREFIX_RE.search(value)) and len(value) <= 1200


def looks_like_error(value: str) -> bool:
    value = clean_markdown(value)
    return 2 <= len(value) <= 240 and bool(ERROR_RE.search(value))


def extract_table_first_cell(line: str) -> str | None:
    if not line.lstrip().startswith("|"):
        return None
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    if not cells:
        return None
    first = clean_markdown(cells[0])
    if not first or re.fullmatch(r"[-: ]+", first):
        return None
    return first


def extract_host_items(paths: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items: dict[tuple[str, str], dict[str, Any]] = {}
    structural_issues: list[dict[str, Any]] = []

    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        section = "Introduction"
        in_fence = False
        fence_language = ""
        fence_start = 0
        fence_section = section
        fence_lines: list[str] = []

        for line_number, line in enumerate(lines, start=1):
            fence_match = FENCE_RE.match(line)
            if fence_match:
                if not in_fence:
                    in_fence = True
                    fence_language = fence_match.group(1).casefold()
                    fence_start = line_number
                    fence_section = section
                    fence_lines = []
                else:
                    content = "\n".join(fence_lines).strip()
                    if not content:
                        structural_issues.append(
                            {
                                "kind": "empty-code-fence",
                                "file": path.relative_to(ROOT).as_posix(),
                                "line": fence_start,
                                "detail": "Empty fenced code block.",
                            }
                        )
                    elif fence_language in {"bash", "sh", "shell", "powershell", "pwsh"}:
                        add_item(
                            items,
                            kind="command",
                            value=content,
                            path=path,
                            line_start=fence_start + 1,
                            line_end=line_number - 1,
                            section=fence_section,
                            language=fence_language,
                        )
                    elif fence_language in {"text", "console", "output"}:
                        for offset, output_line in enumerate(fence_lines, start=fence_start + 1):
                            if looks_like_error(output_line):
                                add_item(
                                    items,
                                    kind="error",
                                    value=clean_markdown(output_line),
                                    path=path,
                                    line_start=offset,
                                    line_end=offset,
                                    section=fence_section,
                                )
                    in_fence = False
                    fence_language = ""
                    fence_lines = []
                continue

            if in_fence:
                fence_lines.append(line)
                continue

            heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
            if heading:
                section = clean_markdown(heading.group(1))

            if line_number <= 8 and ":" in line and not line.lstrip().startswith(("|", "#")):
                continue

            for inline_match in INLINE_CODE_RE.finditer(line):
                inline = inline_match.group(1).strip()
                if looks_like_command(inline):
                    add_item(
                        items,
                        kind="command",
                        value=inline,
                        path=path,
                        line_start=line_number,
                        line_end=line_number,
                        section=section,
                        language="inline",
                    )
                if looks_like_error(inline):
                    add_item(
                        items,
                        kind="error",
                        value=clean_markdown(inline),
                        path=path,
                        line_start=line_number,
                        line_end=line_number,
                        section=section,
                    )

            first_cell = extract_table_first_cell(line)
            if (
                path.name in {"machine-errors.mdx", "self-test-reference.mdx", "common-errors-diagnostics.mdx"}
                and first_cell
                and looks_like_error(first_cell)
            ):
                add_item(
                    items,
                    kind="error",
                    value=first_cell,
                    path=path,
                    line_start=line_number,
                    line_end=line_number,
                    section=section,
                )

            cleaned = clean_markdown(line)
            if cleaned and not cleaned.startswith(("import ", "export ")):
                if (THRESHOLD_RE.search(cleaned) and NUMBER_UNIT_RE.search(cleaned)) or (
                    NUMBER_UNIT_RE.search(cleaned) and any(token in cleaned for token in (">", "<", ">=", "<="))
                ):
                    add_item(
                        items,
                        kind="threshold",
                        value=cleaned,
                        path=path,
                        line_start=line_number,
                        line_end=line_number,
                        section=section,
                    )
                elif BEHAVIOR_RE.search(cleaned) and len(cleaned) <= 700:
                    add_item(
                        items,
                        kind="behavior-claim",
                        value=cleaned,
                        path=path,
                        line_start=line_number,
                        line_end=line_number,
                        section=section,
                    )

        if in_fence:
            structural_issues.append(
                {
                    "kind": "unclosed-code-fence",
                    "file": path.relative_to(ROOT).as_posix(),
                    "line": fence_start,
                    "detail": f"Unclosed {fence_language or 'plain'} code fence.",
                }
            )

    ordered = sorted(
        items.values(),
        key=lambda item: (
            {"command": 0, "error": 1, "threshold": 2, "behavior-claim": 3}[item["kind"]],
            item["locations"][0]["file"],
            item["locations"][0]["line_start"],
            item["text"].casefold(),
        ),
    )
    return ordered, structural_issues


def check_local_references(paths: list[Path], route_paths: list[Path]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    routes = {canonical_route(path).rstrip("/") for path in route_paths}
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            image_targets = MARKDOWN_IMAGE_RE.findall(line) + HTML_IMAGE_RE.findall(line)
            for target in image_targets:
                clean_target = target.split("?", 1)[0].split("#", 1)[0]
                if clean_target.startswith(("http://", "https://", "data:")):
                    continue
                if clean_target.startswith("/"):
                    resolved = ROOT / clean_target.lstrip("/")
                else:
                    resolved = path.parent / clean_target
                if not resolved.exists():
                    issues.append(
                        {
                            "kind": "missing-local-image",
                            "file": path.relative_to(ROOT).as_posix(),
                            "line": line_number,
                            "detail": target,
                        }
                    )
            for target in LINK_RE.findall(line):
                if target.rstrip("/") not in routes:
                    issues.append(
                        {
                            "kind": "missing-host-route",
                            "file": path.relative_to(ROOT).as_posix(),
                            "line": line_number,
                            "detail": target,
                        }
                    )
    return issues


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def build_inventory() -> dict[str, Any]:
    page_paths = sorted(HOST_ROOT.rglob("*.mdx"))
    snippet_paths = sorted((ROOT / "snippets" / "host").rglob("*.mdx"))
    content_paths = page_paths + snippet_paths
    items, structural_issues = extract_host_items(content_paths)
    for item in items:
        syntax = item.get("static_syntax")
        if syntax and syntax["status"] == "fail":
            first_location = item["locations"][0]
            structural_issues.append(
                {
                    "kind": "bash-syntax-failure",
                    "file": first_location["file"],
                    "line": first_location["line_start"],
                    "detail": f"{item['id']}: {syntax['detail']}",
                }
            )
    reference_issues = check_local_references(content_paths, page_paths)
    kind_counts = Counter(item["kind"] for item in items)
    tier_counts = Counter(item["verification_tier"] for item in items)
    status_counts = Counter(item["status"] for item in items)
    source_counts = Counter(source_type(path) for path in page_paths)
    content_source_counts = Counter(source_type(path) for path in content_paths)
    occurrence_count = sum(len(item["locations"]) for item in items)
    return {
        "schema_version": 1,
        "source_revision": git_revision(),
        "scope": {
            "root": "host",
            "pages": len(page_paths),
            "rendered_dependency_files": len(snippet_paths),
            "source_pages": dict(sorted(source_counts.items())),
            "source_content_files": dict(sorted(content_source_counts.items())),
            "unique_items": len(items),
            "occurrences": occurrence_count,
        },
        "summary": {
            "items_by_kind": dict(sorted(kind_counts.items())),
            "items_by_verification_tier": dict(sorted(tier_counts.items())),
            "items_by_status": dict(sorted(status_counts.items())),
            "structural_or_reference_issues": len(structural_issues) + len(reference_issues),
        },
        "safety": {
            "executed_documented_commands": False,
            "static_check": "Fenced Bash examples were parsed with bash -n only.",
            "excluded_from_execution": [
                "paid/live rental commands",
                "destructive or state-mutating commands",
                "privileged host commands",
                "credential-bearing commands",
                "GPU, Docker, network, and account-dependent commands",
            ],
        },
        "known_source_owner_gates": [
            {
                "area": "Machine errors",
                "owner": "Backend source owner",
                "needs_confirmation": "Catalog completeness, host-visible fields, impact level, and clearing/TTL behavior.",
                "tracking": "CON-1531",
            },
            {
                "area": "Network and ports",
                "owner": "Backend/daemon/network source owner",
                "needs_confirmation": "Per-GPU versus per-instance wording, TCP/UDP behavior, release timing, and exact failed-port evidence.",
                "tracking": "CON-1514",
            },
            {
                "area": "Verification and self-test",
                "owner": "Verification/backend source owner",
                "needs_confirmation": "Authoritative queue and wait-time behavior; generated thresholds require exact-source drift verification.",
                "tracking": "CON-1515, CON-1513",
            },
            {
                "area": "Host Teams",
                "owner": "Teams/account engineering",
                "needs_confirmation": "Migration, machine registration, billing-role, earnings, and payout ownership behavior.",
                "tracking": "CON-1581",
            },
            {
                "area": "Pricing and business guidance",
                "owner": "Solutions Engineering/business",
                "needs_confirmation": "Pricing positioning and named ongoing content ownership.",
                "tracking": "CON-1256",
            },
        ],
        "issues": sorted(
            structural_issues + reference_issues,
            key=lambda issue: (issue["file"], issue["line"], issue["kind"]),
        ),
        "items": items,
    }


def markdown_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("|", "\\|")
        .replace("\n", "<br />")
    )


def compact_text(value: str, limit: int = 220) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def location_link(location: dict[str, Any]) -> str:
    label = f"{location['file']}:{location['line_start']}"
    return f"[{label}](./{location['file']}#L{location['line_start']})"


def render_markdown(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    scope = inventory["scope"]
    lines = [
        "# Host Docs verification inventory",
        "",
        "> Generated by `python3 scripts/inventory_host_docs.py`. Do not hand-edit the inventory tables.",
        "",
        "This inventory answers two separate questions: whether documented examples are structurally valid, and whether their claimed runtime/product behavior has authoritative evidence. A static pass does **not** prove a command was executed successfully on a real host.",
        "",
        "## Coverage and current result",
        "",
        f"- Source revision: `{inventory['source_revision']}`",
        f"- Pages scanned: **{scope['pages']}** ({', '.join(f'{count} {name}' for name, count in scope['source_pages'].items())})",
        f"- Imported Host snippet dependencies scanned: **{scope['rendered_dependency_files']}**",
        f"- Unique verification targets: **{scope['unique_items']}** across **{scope['occurrences']}** occurrences",
        f"- Structural/local-reference issues: **{summary['structural_or_reference_issues']}**",
        "- Documented commands executed: **0** (intentional safety boundary)",
        "",
        "| Kind | Unique items |",
        "|---|---:|",
    ]
    for kind, count in summary["items_by_kind"].items():
        lines.append(f"| {kind} | {count} |")

    lines.extend(
        [
            "",
            "## Reproduce the audit",
            "",
            "```bash",
            "python3 scripts/inventory_host_docs.py",
            "python3 scripts/inventory_host_docs.py --check",
            "npm run check-persona-chips",
            "npm run test-review-context",
            "git diff --check",
            "```",
            "",
            "The first command regenerates this Markdown report plus JSON and CSV. `--check` fails when committed outputs are stale. The remaining commands validate repository-specific review tooling and whitespace. Run Mint validation with a supported Node version as a separate documentation build check.",
            "",
            "## Safety and verification tiers",
            "",
            "| Tier | Count | Meaning |",
            "|---|---:|---|",
        ]
    )
    tier_meanings = {
        "local-safe": "Help/availability and static syntax can be checked locally; placeholders must remain non-production.",
        "account-read-only": "Needs current CLI plus a non-production authenticated account; should not mutate state.",
        "environment-dependent": "Needs matching OS, GPU, Docker, storage, or network conditions.",
        "privileged-host": "Needs a disposable supported host and records of before/after state.",
        "credential-bearing": "Needs an approved test credential and redaction/logging review.",
        "destructive-or-mutating": "Needs disposable/non-production state and peer-reviewed execution.",
        "paid-live": "Can create billable resources; requires explicit budget/target approval and exact evidence metadata.",
        "generated-source": "Must be regenerated from the exact upstream source revision.",
        "source-or-fixture": "Needs a code source and/or captured redacted runtime fixture.",
        "source-owner": "Needs the owning code, policy, or stakeholder confirmation.",
    }
    for tier, count in summary["items_by_verification_tier"].items():
        lines.append(f"| {tier} | {count} | {tier_meanings.get(tier, '')} |")

    lines.extend(["", "## Issues found by the generator", ""])
    if inventory["issues"]:
        lines.extend(["| Type | Location | Detail |", "|---|---|---|"])
        for issue in inventory["issues"]:
            location = f"[{issue['file']}:{issue['line']}](./{issue['file']}#L{issue['line']})"
            lines.append(
                f"| {issue['kind']} | {location} | {markdown_escape(compact_text(issue['detail']))} |"
            )
    else:
        lines.append("No unclosed/empty fences, missing Host routes, or missing local image targets were found.")

    lines.extend(
        [
            "",
            "## Product/source-owner confirmations still required",
            "",
            "These remain open even if every local test passes.",
            "",
            "| Area | Owner | Confirmation needed | Tracking |",
            "|---|---|---|---|",
        ]
    )
    for gate in inventory["known_source_owner_gates"]:
        tickets = ", ".join(
            f"[{ticket}](https://vastai.atlassian.net/browse/{ticket})"
            for ticket in re.findall(r"CON-\d+", gate["tracking"])
        )
        lines.append(
            f"| {gate['area']} | {gate['owner']} | {gate['needs_confirmation']} | {tickets} |"
        )

    for kind, title in (
        ("command", "Command and executable-snippet inventory"),
        ("error", "Error-string inventory"),
        ("threshold", "Numeric threshold inventory"),
        ("behavior-claim", "Behavior-claim candidates"),
    ):
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| ID | Source | Target | Tier | Status |",
                "|---|---|---|---|---|",
            ]
        )
        for item in (candidate for candidate in inventory["items"] if candidate["kind"] == kind):
            locations = ", ".join(location_link(location) for location in item["locations"][:3])
            if len(item["locations"]) > 3:
                locations += f" (+{len(item['locations']) - 3} more in JSON/CSV)"
            lines.append(
                "| {id} | {locations} | {text} | {tier} | {status} |".format(
                    id=item["id"],
                    locations=locations,
                    text=markdown_escape(compact_text(item["text"])),
                    tier=item["verification_tier"],
                    status=item["status"],
                )
            )

    lines.extend(
        [
            "",
            "## Reviewer completion rule",
            "",
            "A target is complete only when its status links to reproducible evidence: a static/parser result, an upstream generator comparison, a captured non-production run, a source-code fixture, or a named owner confirmation. Feedback can cite the stable inventory ID and source line so corrections are unambiguous.",
            "",
        ]
    )
    return "\n".join(lines)


def render_csv(inventory: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "id",
            "kind",
            "text",
            "verification_tier",
            "verification_method",
            "status",
            "static_syntax",
            "file",
            "line_start",
            "line_end",
            "section",
            "source_type",
        ]
    )
    for item in inventory["items"]:
        syntax = item.get("static_syntax", {})
        syntax_value = ""
        if syntax:
            syntax_value = f"{syntax.get('status', '')}: {syntax.get('detail', '')}"
        for location in item["locations"]:
            writer.writerow(
                [
                    item["id"],
                    item["kind"],
                    item["text"],
                    item["verification_tier"],
                    item["verification_method"],
                    item["status"],
                    syntax_value,
                    location["file"],
                    location["line_start"],
                    location["line_end"],
                    location["section"],
                    location["source_type"],
                ]
            )
    return output.getvalue()


def expected_outputs(inventory: dict[str, Any]) -> dict[Path, str]:
    return {
        DEFAULT_JSON: json.dumps(inventory, indent=2, sort_keys=False) + "\n",
        DEFAULT_CSV: render_csv(inventory),
        DEFAULT_MARKDOWN: render_markdown(inventory),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if generated inventory files are missing or stale.",
    )
    args = parser.parse_args()

    inventory = build_inventory()
    outputs = expected_outputs(inventory)
    if args.check:
        stale = [path for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(
            f"Host Docs inventory is current: {inventory['scope']['pages']} pages, "
            f"{inventory['scope']['unique_items']} unique targets."
        )
        return 0

    for path, content in outputs.items():
        path.write_text(content)
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
