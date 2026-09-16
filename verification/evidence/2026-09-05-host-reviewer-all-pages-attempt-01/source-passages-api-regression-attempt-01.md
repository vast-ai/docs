# Review-context source-passage API regression record

Date: 2026-09-05 (Africa/Johannesburg)  
Repository: `vast-ai/docs` working tree for PR 185 / CON-1518  
HEAD during verification: `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`

## Scope, authority, and safety

This is a repository-local API regression record for the review context. It
adds seven tests to the 26-test starting suite, preserving all prior tests, for
a final total of 33. The tests start an isolated review server and target server
on ephemeral loopback ports and read real repository documentation and V&V
inputs. They do not execute any documented Host command, use Host credentials,
contact WAN services, mutate a Host, perform paid work, or alter reviewer
feedback outside a disposable temporary directory.

The final test source used here had SHA-256
`6317d3f9b03c3fa9e60149b98c439b0a1655034fd865203ea081b5ea817d75d1`.
The environment was Node.js `v26.5.0` on arm64 macOS/Darwin 25.6.0.

This record verifies the review API and static overlay contract only. It does
not establish the product, policy, pricing, legal, payment, account, or runtime
truth of any Host claim. The separate browser sweep owns rendered-page
coverage.

## Added regression coverage

The seven added tests establish that:

1. `GET /__review__/api/context` identifies the exact
   `review-server.mjs` bytes loaded at process startup through
   `X-Vast-Review-Source-SHA256`, and the running source still matches disk.
2. A one-line material claim exposes a literal, source-bound passage without
   changing its `UNVALIDATED` status or disposition evidence.
3. `VOL-C06`, `VOL-C07`, and `VOL-C13` preserve every declared source span and
   section, including multi-span and multi-section claims, while retaining
   their prior status and evidence.
4. `VOL-C21` and `VOL-C22` split spans containing prose and fenced commands
   into contained generic blocks without moving any block outside its declared
   source span.
5. The repeated Network Ports sentence at lines 79 and 100 has stable
   zero-based occurrence ordinals `0/2` and `1/2`.
6. Numeric and scoped-identifier sanitizers remain active for the Maintenance
   Windows and Notifications fixtures; exact raw values are absent and
   `redacted` is true, with status and evidence unchanged.
7. The Account Hosting Agreement passage retains literal `<Frame ...>` wrapper
   markup while the overlay maps `sourcePassages` through reader wording and
   recognizes the Frame caption.

Every passage is also checked for the exact seven-field contract (`text`,
`section`, `start`, `end`, `redacted`, `occurrence`, `occurrences`), valid line
bounds, membership in a declared claim span and checked section, literal source
equality when not redacted, and unchanged current status/evidence.

## Failure and correction history

No failure was hidden or bypassed.

- The first header-inclusive focused run against server source
  `841e3d2c37fc42808d9253cb7ec21934813f7cd7b92089a8ef76549a11c52b80`
  ran from `2026-09-04T23:04:44Z` to `2026-09-04T23:04:45Z` and exited 1:
  6 passed and 1 failed. The Frame overlay test expected an unnecessarily
  specific local-variable assignment. The implementation correctly applies a
  redaction conditional before mapping source passages. The test expectation
  was narrowed to the actual public invariant,
  `(claim.sourcePassages || []).map(passageWording)`.
- The focused correction retest ran from `2026-09-04T23:05:04Z` to
  `2026-09-04T23:05:05Z` against the same server source and exited 0: 7 of 7
  passed.
- A subsequent full run started against server source `841e3d2c...`, but
  `review-server.mjs` changed on disk to `1ac4586359...` while the spawned
  process was still running. It ran from `2026-09-04T23:05:11Z` to
  `2026-09-04T23:06:21Z` and correctly exited 1: 32 passed and the source-header
  identity test failed. The response reported the loaded source
  `841e3d2c...`; disk contained `1ac4586359...`. This is the intended fail-closed
  behavior.
- With server source frozen at
  `1ac4586359749c6786d8dda86a7bcc89a7a7dc3d0636e5772d249d93e5f905b5`,
  the focused run exited 0 with 7 of 7 passing and the full run exited 0 with
  33 of 33 passing. Both server and test hashes were unchanged across each run.
- After that complete run, the server owner intentionally advanced only the
  presentation source to
  `972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`
  to add guarded notes for two existing Self-Test bare-option rendering issues;
  the owner reported no API, matcher, status, or canonical-binding change. A
  fresh focused run against those exact final bytes passed 7 of 7 with hashes
  stable across the run. The repository-level final-validation record owns the
  subsequent complete 33-test run for that superseding presentation source.

## Commands and outcomes

### Frozen `1ac458...` focused result

Command:

```text
node --test --test-name-pattern='Context responses identify|source passage|Source passage|Volume source|Repeated identical|Frame-caption' scripts/review-context.test.mjs
```

Window: `2026-09-04T23:06:29Z` to `2026-09-04T23:06:30Z`  
Exit: `0`  
Counts: 7 tests, 7 pass, 0 fail

Raw TAP summary:

```text
✔ Context responses identify the exact review-server source loaded at startup (805.781167ms)
✔ Material claim source passages expose the exact bound block without changing disposition (5.099625ms)
✔ Volume source passages preserve every declared multi-span section and disposition (5.786958ms)
✔ Source passages split spans containing prose and fenced commands into contained blocks (5.000375ms)
✔ Repeated identical source passages expose stable source occurrence ordinals (8.243583ms)
✔ Source passage projection keeps numeric and scoped-identifier sanitizers active (6.555167ms)
✔ Frame-caption source passages retain wrapper markup for the reader projection (5.65775ms)
ℹ tests 7
ℹ suites 0
ℹ pass 7
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 915.711916
```

### Frozen `1ac458...` full result

Command:

```text
npm run test-review-context
```

Window: `2026-09-04T23:06:36Z` to `2026-09-04T23:07:39Z`  
Exit: `0`  
Counts: 33 tests, 33 pass, 0 fail

Raw TAP result:

```text
> test-review-context
> node --test scripts/review-context.test.mjs

✔ Review server rejects non-loopback bind addresses (905.380166ms)
✔ Context responses identify the exact review-server source loaded at startup (5.422875ms)
✔ Host Teams shows its Jira sources and only its page blockers (10.027666ms)
✔ Self-Test reference links both epics without stale implementation blockers (7.734708ms)
✔ Diagnostics no longer reports merged dump-logs documentation as missing (8.957667ms)
✔ Network page receives network blockers without unrelated Teams blockers (2.888708ms)
✔ Page context joins only sanitized page-scoped V&V evidence (17.918709ms)
✔ Self-test command proof keeps pinned source signatures separate from runtime status (5.542542ms)
✔ VM command proof does not promote incomplete parent procedures (4.867875ms)
✔ Exact CLI-signature and retained-evidence links preserve command proof context (30.663958ms)
✔ Host V&V context separates non-command checks, executable targets, and display-only references (28.50925ms)
✔ Canonical material-claim, citation, and page dispositions remain fully accounted (102.905042ms)
✔ Material claims expose exact documentation source locations without promoting status (2.574541ms)
✔ Material claim source passages expose the exact bound block without changing disposition (4.23625ms)
✔ Volume source passages preserve every declared multi-span section and disposition (4.26175ms)
✔ Source passages split spans containing prose and fenced commands into contained blocks (4.785375ms)
✔ Repeated identical source passages expose stable source occurrence ordinals (4.461667ms)
✔ Source passage projection keeps numeric and scoped-identifier sanitizers active (7.754667ms)
✔ Frame-caption source passages retain wrapper markup for the reader projection (5.40625ms)
✔ Material-claim evidence links accept only evidence attached to that wording (16.462917ms)
✔ Blocker causes and access-derived evidence hints stay separate and conservative (1637.154083ms)
✔ Retained V&V references are repository-relative and do not depend on .orchestra state (64.386625ms)
✔ Missing or malformed verification input fails closed (53945.926625ms)
✔ Current status projection preserves frozen execution status and supports procedure evidence (1226.350291ms)
✔ Current evidence and score text are sanitized before reaching the review context (1197.328708ms)
✔ Approved NOT_APPLICABLE semantic assessment remains separate from numeric scores (1216.851584ms)
✔ Semantic score evidence can remain UNVALIDATED while current execution separately supplies PASS (1245.428875ms)
✔ Procedure history retains the failed attempt and linked correction retest (1163.748708ms)
✔ Unmapped Host pages retain epic provenance without invented blockers (2.706708ms)
✔ Non-Host pages do not inherit Host Jira context (0.842916ms)
✔ Only the review proxy injects the overlay (10.165584ms)
✔ JSON import restores multiple reviewers and keeps newer server items (14.960042ms)
✔ JSON import rejects an invalid backup before writing any reviewer state (4.39575ms)
ℹ tests 33
ℹ suites 0
ℹ pass 33
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 63001.257125
```

### Superseding `972a7...` focused result

Command:

```text
node --test --test-name-pattern='Context responses identify|source passage|Source passage|Volume source|Repeated identical|Frame-caption' scripts/review-context.test.mjs
```

Window: `2026-09-04T23:09:10Z` to `2026-09-04T23:09:10Z`  
Exit: `0`  
Stable source identities:

```text
972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8  review-server.mjs
6317d3f9b03c3fa9e60149b98c439b0a1655034fd865203ea081b5ea817d75d1  scripts/review-context.test.mjs
```

Raw TAP result:

```text
✔ Context responses identify the exact review-server source loaded at startup (649.6385ms)
✔ Material claim source passages expose the exact bound block without changing disposition (4.3345ms)
✔ Volume source passages preserve every declared multi-span section and disposition (5.593166ms)
✔ Source passages split spans containing prose and fenced commands into contained blocks (3.805125ms)
✔ Repeated identical source passages expose stable source occurrence ordinals (5.807458ms)
✔ Source passage projection keeps numeric and scoped-identifier sanitizers active (6.631083ms)
✔ Frame-caption source passages retain wrapper markup for the reader projection (5.677667ms)
ℹ tests 7
ℹ suites 0
ℹ pass 7
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 740.353375
```

## Result

PASS for the API/source-passage regression scope on the complete frozen
`1ac458...` source: 33 of 33 tests passed. PASS for all seven added regressions
on the superseding presentation-only `972a7...` source. Product acceptance and
the complete final-package run remain governed by their separate retained
records.
