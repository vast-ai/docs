# Independent source-binding and reader audit

Date: 2026-09-05  
Repository: `vast-ai/docs` working tree for PR 185 / CON-1518  
HEAD during the audit: `3e1e30e2221b65d7ce1e901d9ae305f63af5b64b`

## Scope and safety

This was a repository-local, loopback-only adversarial review of the Host-page
reader, its material-claim `sourcePassages`, and
`scripts/check_host_review_reading.mjs`. It inspected all 40 primary Host pages.
Browser actions only opened rendered pages, selected review cards, and inspected
DOM ranges. No documented Host command was executed. No credentialed, paid,
WAN, privileged, mutating, destructive, or workload-affecting operation was
performed.

Source identities:

- complete 40-page DOM audit server snapshot:
  `review-server.mjs` SHA-256
  `4e4b491b102e5d1ec8345f1d15f78bfe05325013872cafda32e37e06eefd5886`;
- focused intermediate retest server snapshot:
  `review-server.mjs` SHA-256
  `1ac4586359749c6786d8dda86a7bcc89a7a7dc3d0636e5772d249d93e5f905b5`;
- focused final retest server snapshot:
  `review-server.mjs` SHA-256
  `972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`;
- runner reviewed after the final server change:
  `scripts/check_host_review_reading.mjs` SHA-256
  `98450124e3d807e6644cb1191ebae9f6ed4f902c4a4896156bc486644a32247f`.

The full audit used an isolated browser session against a fixed review server on
`127.0.0.1:41877`, proxying the existing Mintlify preview on
`127.0.0.1:3000`. Focused retests used newly started servers on
`127.0.0.1:41878` and, for the final identity, `127.0.0.1:41879`. The final
server returned its exact source identity in `x-vast-review-source-sha256`.

## Result summary

- 40 of 40 inventory pages returned available primary V&V context.
- 1,687 material claims produced 1,746 literal source passages.
- On the complete snapshot, 1,678 claims located their page wording and nine
  did not. Seven were the declared masked-section fallback. The other two were
  the CLI-option typography cases described below.
- Every one of the 1,678 located claims passed the stronger audit invariants:
  range count equalled passage count, displayed-passage count equalled passage
  count, the selected card owned the result, every range had a visible client
  rectangle, and no range crossed its paragraph/list/table/code block.
- The final focused retest located the two typography cases and displayed an
  explicit warning that location is not proof of option spelling. The underlying
  customer-visible documentation defect remains.
- Current API disposition counts were 167 `PASS`, 153 `FAIL`, 23 `BLOCKED`, and
  1,344 `UNVALIDATED`. This audit checked presentation and binding behavior; it
  did not independently establish the semantic truth of all 1,687 claims.

## Verified findings

### 1. Existing canonical binding defect: `VOL-C35` does not bind its full claim

`VOL-C35` says: “All local Related Pages and command-reference destinations
exist.” Its canonical source location is only
`host/volume-offers.mdx:111-118`, under `Related Pages`. The `Command Map` and
its nine command-reference destinations are at lines 97-109 and are absent from
the claim's source spans, checked sections, and citation refs.

On the final server, **Show on page** highlighted only the four Related Pages
rows and reported “Highlighted 4 passages for this statement on the page.” It
did not highlight or navigate to any Command Map row. The final UI now adds an
honest source-location note and a `Command Map` link; that mitigates reviewer
confusion but does not repair the canonical binding.

This is not a new navigator-created status defect. It is a pre-existing
claim/scope defect in the generated V&V contracts. Prefer splitting it into two
atomic navigation claims, or bind both `Command Map` and `Related Pages` with
their exact spans and destinations, then regenerate hashes/manifests and retest.

### 2. Two bare CLI flags render incorrectly, and prose folding can hide it

`host/self-test-reference.mdx:155` contains bare
`--ignore-requirements`; line 198 contains bare `--debugging`. Mintlify renders
each two-hyphen prefix as one em dash:

- `MCL-c99f9ecb5ea4e15a`: `—ignore-requirements`
- `MCL-22a1a520d989a59f`: `—debugging`

The final locator deliberately folds prose typography, so it reports both as
`LOCATED` and highlights the em-dash rendering. These strings are CLI option
tokens, not ordinary prose punctuation; accepting the substitution is therefore
a false positive for exact rendered-token fidelity. The final reader now places
an explicit formatting-defect warning on both cards, gives the correct literal
option, and says that locating the text is not proof that the spelling works.
That is an honest guard, not a correction to the Host page.

Wrap both flags in inline code, regenerate their source hashes/bindings, and
retest. As a defensive check, option-shaped `--name` segments should remain
literal even when an author forgot backticks, so the browser audit fails until
the documentation is corrected.

### 3. Sanitization is safe but over-broad in two current passages

Seven claims are intentionally withheld from exact browser matching because
`vvText` changed the source passage. Five contain the expected local path,
address, or long numeric example. Two are false-positive redactions:

- `host/notifications.mdx:62`: the documented notification key
  ``host:machine_offline`` becomes `host=[identifier]`;
- `host/reliability-uptime.mdx:20`: ordinary prose
  “account: machines with lower earnings ...” becomes
  `account=[identifier] with lower earnings ...`.

The final UI correctly discloses the masking before interaction, shows no fake
quote, keeps the section fallback, and does not leak the raw value through the
review API. Keep that safe fallback. Narrow the scoped-identifier sanitizer or
add safe syntax handling so these two non-sensitive strings remain accurate.

### 4. Contained-block splitting loses part of three declared spans

The source-passage builder replaces a declared span with only the generic blocks
fully contained by it. Across all 1,687 claims, this changed line coverage for
three volume claims:

- `VOL-C21`: only blank lines 52 and 59 are omitted;
- `VOL-C22`: only blank line 63 is omitted;
- `VOL-C35`: the heading, blank line, table delimiter, and the meaningful table
  header `Topic | Read next` at line 113 are omitted.

No other substantive source words were lost by splitting in this inventory.
However, `sourceLocation.textSha256` authenticates the whole declared span while
`sourcePassages` can silently present only a subset. Export explicit coverage
metadata (or preserve the original span alongside derived blocks) and make the
UI say when **Show on page** is a partial locator rather than the complete claim
scope.

### 5. Final source-identity safeguard is effective

The old server on port 4000 returned no source-identity header. The final server
on port 41879 returned
`972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`.
The final runner checks that header before browser work, checks it again for each
page, and fails if the file changes during the run. This closes the earlier risk
of attributing stale port-4000 behavior to the current on-disk source.

### 6. Runner safeguards and remaining scope limit

The final runner now rejects duplicate, unknown, and wrong-shard requested
routes; clears the previous highlight and notice before every click; requires
the selected-card marker; checks passage/highlight counts; checks source identity
before and during the run; fails on source changes; and calls its action-link
result `sectionLinksPass`.

`sectionLinksPass` intentionally validates only the reader's **Open section**
actions. It does not validate documentation destinations named by a navigation
claim and therefore cannot prove `VOL-C35`'s link-existence assertion. Keep that
scope explicit, or add a separate bound-navigation-destination result. The
runner also does not generally compare rendered CLI-token bytes with source
bytes; the two known bare-option cases are disclosed by targeted reader guards,
but a new unguarded bare `--option` could still pass prose location matching.

## Security checks and limits

The evidence endpoint returned 200 for a claim/evidence pair actually attached
to that claim, 404 for the same evidence path under an unrelated claim binding,
and 404 for a traversal-style `../../etc/passwd` reference. Source-passage text
is escaped before HTML insertion, the review server is loopback-bound, and no
path traversal or cross-claim evidence-access defect was found in this audit.

This was not a penetration test. It did not test malicious local filesystem
replacement, browser-extension interference, or an externally exposed proxy.
It also did not re-perform Product, Finance, Legal, account-owner, paid runtime,
or privileged operator validation. Those claim statuses remain exactly as
recorded by the canonical V&V package.
