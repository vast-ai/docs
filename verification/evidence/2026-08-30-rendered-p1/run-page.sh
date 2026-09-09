#!/usr/bin/env bash
set -euo pipefail

session="host-docs-p1-rendered"
base_url="http://127.0.0.1:4000"
evidence_dir="verification/evidence/2026-08-30-rendered-p1"

for route in "$@"; do
  slug="${route#/}"
  slug="${slug//\//-}"

  agent-browser --session "$session" open "$base_url$route" > "$evidence_dir/${slug}-open.txt"
  agent-browser --session "$session" wait --load networkidle > "$evidence_dir/${slug}-wait.txt"
  agent-browser --session "$session" screenshot --full --annotate "$evidence_dir/screenshots/${slug}.png" > "$evidence_dir/${slug}-screenshot.txt"
  agent-browser --session "$session" snapshot > "$evidence_dir/${slug}-snapshot.txt"
  agent-browser --session "$session" errors > "$evidence_dir/${slug}-errors.txt"
  agent-browser --session "$session" console > "$evidence_dir/${slug}-console.txt"
  printf '%s\tCAPTURED_UNREVIEWED\n' "$route" >> "$evidence_dir/coverage.tsv"
  printf 'captured %s\n' "$route"
done
