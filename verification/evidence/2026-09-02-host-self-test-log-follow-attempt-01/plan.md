# Host self-test log follower attempt 01

- Attempt ID: `ATTEMPT-2026-09-02-HOST-SELF-TEST-LOG-FOLLOW-01`
- Scope: `CLM-c36aed4218dd8d33` and `CLM-aa852c9bcbb5b005`
- Method: execute the documented follower under a four-second interrupting timeout, then confirm no follower remains

## Command under test

```bash
sudo tail -f /var/lib/vastai_kaalia/self_test.log
```

The operator-facing source says to stop the follower with `Ctrl+C`. This automated attempt uses `timeout --signal=INT` only as a bounded substitute for that exact interruption; the child command itself is unchanged.

## Outcome

- `PASS`: the follower opens the documented path without a permission/path error, produces bounded initial output, receives the planned interrupt, and leaves no process behind.
- `FAIL`: it cannot open/follow the documented file or persists after interruption.
- `BLOCKED`: the Host becomes active or safe interruption cannot be established.

Because no self-test is running, this attempt can support functional PASS and semantic score `2` only. It does not prove that new progress appears during an active installer/self-test procedure and cannot promote either parent procedure.

Raw log text stays restricted and is not quoted in public evidence.
