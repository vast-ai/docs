# CLI diagnostic bundle attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-CLI-DUMP-LOGS-01`
- Scope: `CLM-ac5731cde3180fca` and `CLM-6b3d212806990265`
- Method: run the documented manual bundle command from the local CLI against the authorized Host identifier
- CLI: Vast CLI `1.4.2.post7+54c1b69`

## Command

```bash
vastai dump-logs <authorized-machine> --output-dir <restricted-evidence-directory> --raw
```

`--output-dir` and `--raw` make evidence retention deterministic without changing the documented behavior. Do not supply `--instance-id` and do not request local Host artifacts from the laptop.

## Outcome

- `PASS`: command exits `0`, returns structured output, writes a readable archive with the documented manifest/error structure, and the retained archive passes a secret-pattern scan.
- `FAIL`: command executes but does not create the stated bundle behavior.
- `BLOCKED`: authorization or another dependency prevents bundle creation.

The result can validate manual CLI-visible bundle creation only. It cannot validate Host-local collection, instance-log retrieval, or completeness of a self-test failure bundle.
