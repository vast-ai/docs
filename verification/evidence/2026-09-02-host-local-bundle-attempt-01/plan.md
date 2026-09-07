# Host-local diagnostic bundle attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-LOCAL-BUNDLE-01`
- Scope: `CLM-321e05cb87fdcbe0` and `CLM-444903dafc2f1f6e`
- Target: authorized idle Host; exact identity stays in restricted evidence
- CLI setup: install Vast CLI `1.5.6` into a temporary Host-local virtual environment under `/tmp`

## Command under test

```bash
vastai dump-logs <authorized-machine> --include-local-host-artifacts
```

The execution may add `--output-dir <restricted-temporary-directory>` and `--raw` to make evidence retention deterministic. It must run on the actual Host. Do not pass an instance ID or API key.

## Safety and privacy

- Require zero running containers and zero GPU compute processes before execution.
- Install only into the attempt-owned temporary virtual environment; do not alter system Python.
- The helper is read-only against Host logs/configuration, but its archive is sensitive.
- Copy the archive to restricted local evidence, scan it without printing contents, and remove the attempt-owned Host bundle and virtual environment.
- Do not commit or externally share the raw archive without human review.

## Outcome

- `PASS`: the Host-local command exits `0`, creates a readable archive whose manifest says local Host artifacts were included, records individual collection errors, and leaves no temporary Host process or attempt-owned files after cleanup.
- `FAIL`: the command runs on the correct Host but does not provide the documented local-artifact behavior.
- `BLOCKED`: package/network, permission, or collection prerequisites prevent reaching the behavior.

PASS supports only the Host-local bundle command and its collection boundary. It does not validate an affected rental or prove that every optional artifact exists on every Host.
