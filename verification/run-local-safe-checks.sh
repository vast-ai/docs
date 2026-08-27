#!/usr/bin/env bash

set -u
set -o pipefail

usage() {
  echo "Usage: $0 <unique-run-id> <clean-vast-cli-checkout>" >&2
  exit 2
}

[[ $# -eq 2 ]] || usage

run_id="$1"
vast_cli="$2"
case "$run_id" in
  *[!A-Za-z0-9._-]*|'')
    echo "Run ID may contain only letters, numbers, dot, underscore, and hyphen." >&2
    exit 2
    ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vast_cli="$(cd "$vast_cli" && pwd)"
evidence_dir="$repo_root/verification/evidence/$run_id"
node24_bin="${NODE24_BIN:-$(command -v node)}"
node24_dir="$(dirname "$node24_bin")"

[[ -x "$node24_bin" ]] || {
  echo "Node 24 executable not found: $node24_bin" >&2
  exit 2
}
[[ "$("$node24_bin" -p 'process.versions.node.split(".")[0]')" == "24" ]] || {
  echo "Node 24 is required; set NODE24_BIN to a Node 24 executable." >&2
  exit 2
}
[[ -f "$vast_cli/vastai/cli/main.py" ]] || {
  echo "Not a Vast CLI checkout: $vast_cli" >&2
  exit 2
}
[[ -z "$(git -C "$vast_cli" status --porcelain)" ]] || {
  echo "Vast CLI checkout must be clean." >&2
  exit 2
}
[[ -z "$(git -C "$repo_root" status --porcelain --untracked-files=no)" ]] || {
  echo "Tracked docs worktree must be clean before evidence execution." >&2
  exit 2
}
[[ ! -e "$evidence_dir" ]] || {
  echo "Evidence directory already exists; choose a new run ID: $evidence_dir" >&2
  exit 2
}

mkdir -p "$evidence_dir"
results_file="$evidence_dir/results.tsv"
printf 'id\texpected_exit\tactual_exit\tstarted_utc\tfinished_utc\tstdout\tstderr\n' > "$results_file"
unexpected=0
clean_snapshot="$(mktemp -d "${TMPDIR:-/tmp}/host-docs-vv.XXXXXX")"
cleanup() {
  rm -rf -- "$clean_snapshot"
}
trap cleanup EXIT
git -C "$repo_root" archive HEAD | tar -x -C "$clean_snapshot"

run_check() {
  local id="$1"
  local expected_exit="$2"
  local workdir="$3"
  shift 3
  local started finished actual_exit
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  (
    cd "$workdir"
    PATH="$node24_dir:$PATH" "$@"
  ) > "$evidence_dir/$id.stdout.txt" 2> "$evidence_dir/$id.stderr.txt"
  actual_exit=$?
  finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$expected_exit" "$actual_exit" "$started" "$finished" \
    "$id.stdout.txt" "$id.stderr.txt" >> "$results_file"
  if [[ "$actual_exit" -ne "$expected_exit" ]]; then
    unexpected=1
  fi
}

{
  echo "run_id=$run_id"
  echo "performed_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "docs_revision=$(git -C "$repo_root" rev-parse HEAD)"
  echo "docs_tree=$(git -C "$repo_root" rev-parse HEAD^{tree})"
  echo "docs_branch=$(git -C "$repo_root" branch --show-current)"
  echo "docs_untracked_state_begin"
  git -C "$repo_root" status --short
  echo "docs_untracked_state_end"
  echo "vast_cli_revision=$(git -C "$vast_cli" rev-parse HEAD)"
  echo "vast_cli_tree=$(git -C "$vast_cli" rev-parse HEAD^{tree})"
  echo "vast_cli_branch=$(git -C "$vast_cli" branch --show-current)"
  echo "platform=$(uname -s)"
  echo "architecture=$(uname -m)"
  sw_vers
  python3 --version
  bash --version | sed -n '1p'
  "$node24_bin" --version
  PATH="$node24_dir:$PATH" npm --version
  git --version
  PATH="$node24_dir:$PATH" "$repo_root/node_modules/.bin/mint" --version
  shasum -a 256 "$repo_root/package-lock.json"
  shasum -a 256 \
    "$repo_root/HOST-DOCS-QA-SUMMARY.md" \
    "$repo_root/HOST-DOCS-VERIFICATION.md" \
    "$repo_root/HOST-DOCS-COMMAND-ACCESS.md" \
    "$repo_root/HOST-DOCS-CLI-COMMAND-CHECK.md" \
    "$repo_root/host-docs-verification-inventory.json" \
    "$repo_root/host-docs-command-access.json" \
    "$repo_root/host-docs-cli-command-check.json"
} > "$evidence_dir/environment.txt" 2> "$evidence_dir/environment.stderr.txt"

run_check VV-HOST-001 0 "$repo_root" python3 -B scripts/inventory_host_docs.py --check
run_check VV-HOST-002 0 "$repo_root" python3 -B scripts/verify_host_cli_commands.py --vast-cli "$vast_cli" --check
run_check VV-HOST-003 0 "$repo_root" npm run check-persona-chips
run_check VV-HOST-004 0 "$repo_root" npm run test-review-context
run_check VV-HOST-005 0 "$repo_root" node --check review-server.mjs
run_check VV-HOST-006 0 "$repo_root" npm run check-openapi
run_check VV-HOST-007 1 "$clean_snapshot" "$repo_root/node_modules/.bin/mint" broken-links
run_check VV-HOST-008 1 "$clean_snapshot" "$repo_root/node_modules/.bin/mint" a11y
run_check VV-HOST-009 0 "$repo_root" git diff --check

if [[ "$unexpected" -ne 0 ]]; then
  echo "One or more checks returned an unexpected exit code. Preserve this attempt and review results.tsv." >&2
  exit 1
fi

echo "Evidence captured in $evidence_dir"
