# Setup findings

The initial baseline helper failed with ENOBUFS while buffering the existing
large dirty Git diff (32 MiB limit). No baseline or claim/source change was
written by that invocation. Retest hashes the diff as a stream instead.

The first task browser invocation failed before navigation because its default
socket directory was outside the writable sandbox. Use a task-owned temporary
socket directory; do not change user browser configuration or financial accounts.

Graph query navigation located the payout transition and existing Terms bindings.
The literal vocabulary includes payout, payment, terms, third and party, but not
liability. The first query mistakenly included the absent liability term. Graph
results are navigation only; the source inspection does not rely on those edges.

The first Terms capture retained correct section text but its version parser
matched the in-body phrase Last updated instead of the visible Version Date.
It is retained as terms-source.json. Fresh corrected capture terms-source-02.json
records Version Date: September 1, 2026; all three section hashes are unchanged.
Only source-02 may support the correction.

The baseline inventory used a broad substring filter, so it also includes
reliability statements. This is a screening superset, not a 79-item liability
review or closure count. Independent review selected only MCL-06956d724f70d2a3.
The four other Host Payouts FAILs concern threshold, schedule and invoice rules;
none is established by these Terms clauses.
# Integration findings and retests

The first integrated Python suite rejected a historical fixture that copied the
new Terms registry alongside old Payment source. This correctly triggered the
source hash guard; repair the fixture's historical slice, not the production guard.
See integrated-python-01.json and its subsequent retest.

The first integrated JavaScript suite could not bind a temporary loopback server
inside the sandbox (EPERM). integrated-js-02.json retries with loopback permission.
This was a local test-environment restriction, not a payout failure.

after-01.json failed one rendered wording assertion because Mint displays a
typographic apostrophe in "Vast's". Direct browser inspection confirmed the complete
reasonable-control qualification. The checker now normalizes that punctuation;
after-02.json passes all 11 checks. The customer wording did not change for this retry.

The implementation review also caught and corrected the missing allowance for
the exact Miscellaneous /sections/2/text citation, a digest-comparison parenthesis
error, a vacuous Map comparison, stale export metadata, and a duplicate FAQ anchor.
The new live source checks exercise all three Terms proof links. The prior failed
checks and original source/model remain retained.
