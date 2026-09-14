# Execution notes

These are implementation/check attempts, not product findings or human approval.

- The first template patch used a relative target from the parent workspace and
  failed before touching the template. Reapplied with the absolute repository
  path. The server patch in the same tool invocation had already succeeded.
- focused-01.json and checks-01.json retain a failing assertion that expected
  the September 9 display date. The report now explicitly says its presentation
  was refreshed September 10, while evidence dates remain attached to sources.
  focused-02.json passes 46 tests; checks-02.json passes 15 check groups.
- browser-final-01 retains two page timeouts. Read-only diagnosis found no
  listener on port 3000 and an HTTP 502 from the review proxy. Stopped only the
  task-created audit process, PID30737. This interrupted run has no final summary
  and is not a completed coverage check. Closed its isolated browser session.
- A plain `node scripts/mint-dev-loopback.mjs --port 3000` launch exited1:
  `mint dev is not supported on node versions 25+`. The shell Node was26.5.0.
  No dependency was installed or changed. preview-restored-01.json retains the
  missing-listener check. browser-final-02 was started before readiness was
  confirmed, then interrupted (PID35677); it is not completed coverage. Closed
  that isolated browser too.
- Used the available bundled Node24.19.0 with the existing loopback-only Mint
  launcher. preview-start-02.json records startup and a verified127.0.0.1 bind,
  but its bounded readiness probe expired during startup. The preview was left
  running for a separate readiness retest, not reported as ready by that record.
- preview-restored-02.json returned HTTP200 but failed a mistaken assertion:
  the Host element is created by JavaScript, not present in raw response HTML.
  Inspection found the actual `/__review__/overlay.js` script injection. The
  readiness retest uses that observed script and checks current-review API
  availability separately; browser checks still establish the rendered element.
- Read-only independent review found no semantic promotion: five pending policy
  requests, one policy-reference exception and one already-supported product
  description. Policy confirmation cannot silently resolve the required citation;
  exact recorded status remains in details. Two draft pages are not independent
  authority. “Should be dedicated” is not strengthened to “must”.
- Visual inspection of policy-card-01.png shows the exact instruction, pending
  acknowledgement label, source-first next action and unresolved citation note.
  It is an interface observation, not a policy-owner acknowledgement.
