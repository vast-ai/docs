# Baseline capture attempt 01

The read-only Node capture failed with `spawnSync git ENOBUFS` while hashing `git diff --cached --binary`: the default subprocess buffer was too small. No baseline artifact was produced. Repeated with a 128 MiB buffer; `baseline.json` retains the successful full status and hashes. The only preceding repository edit in this turn was this attempt's plan. No index or product changes were made.
