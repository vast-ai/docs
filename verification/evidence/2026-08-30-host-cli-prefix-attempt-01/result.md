# Host Docs CLI prefix notation attempt 01 — result

- Evidence ID: `EV-CLI-PREFIX-01-METRICS`
- Command form: `vastai metrics --help`
- Process exit code: `2`
- V&V status: `NOT_APPLICABLE`
- Output: nonempty argparse usage/error text

The installed CLI rejects `metrics` as a standalone command prefix and lists the
three registered leaf commands: `metrics gpu`, `metrics gpu-trends`, and
`metrics gpu-locations`. The Host pages use `vastai metrics ...` as an ellipsis
notation introducing those leaf commands, not as a runnable instruction. The
42 leaf-command help checks remain the applicable static syntax evidence.

This result is therefore neither a command failure nor behavioral proof for a
metrics endpoint. It records why the prefix notation is excluded from runtime
coverage.
