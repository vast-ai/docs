# Payout wording and citation corrections

14 September 2026. CON-1518 / PR #185.

Completed locally. Two exact payout statements are corrected. Source binding,
both reviewer views and all 38 payout-page passage locators passed, along with
91 Python tests and 39 JavaScript tests. No project acceptance is recorded.

## Current findings

- MCL-06956d724f70d2a3, Host Payouts / Payout Account, line 46: PASS for a
  description of three named Terms sections. The note includes the
  reasonable-control and state-law qualifications. It does not establish a
  blanket exemption from payout liability.
- MCL-9826b26393329d27, Host Payouts / Can Vast send direct bank transfers?,
  line 101: PASS for an attributed description of Vast's published FAQ.
  That publication says direct bank transfers, ACH, wire and SWIFT are
  unavailable. The check does not exercise or independently rule out payment
  routes. The screenshot remains proof of the displayed provider options only.

The model now has 313 PASS, 30 FAIL, 23 BLOCKED, 87 NOT_APPLICABLE and
1,560 UNVALIDATED claim records. Only these two claims changed; the other
2,011 records and all 3,767 prior evidence files are unchanged. These are
claim dispositions, not 313 completed Host workflows.

## Proof and retests

- [Exact source decision and limits](source-review.md)
- [Terms capture, version September 1, 2026](terms-source-02.json), sections
  /sections/0/text (Disclaimer of Website), /sections/2/text (Miscellaneous),
  and /sections/1/text (Limitations of Liability)
- [Published payout FAQ capture](published-payout-faq-01.json), /text.
  The live publication identifies the same docs repository as its source.
  Shared ancestry is not independent implementation evidence.
- [Original Terms finding](before-01.json) and [passing live retest](after-02.json)
- [Original missing FAQ](before-faq-01.json) and [passing two-view retest](after-faq-01.json)
- [Passing offline Terms proof controls](offline-01.json)
- [All 38 rendered payout-page claim locators](rendered-payment-01/summary.json)
- [91 passing Python tests](integrated-python-02.json)
- [39 passing JavaScript tests, including isolated loopback integration](integrated-js-03.json)
- [Claim/source/history integrity check](final-audit-01.json)
- [Test-environment and assertion corrections](setup-findings.md)

The failed punctuation assertion in after-01.json and the initial regression
attempts remain available. Mint displayed a typographic apostrophe; the checker
was corrected without changing the customer wording. The historical fixtures now
use their correct source snapshots and inspect the retained nested history. The
full retests pass without weakening the production source guards.

Checks ran on macOS arm64 with Node v26.5.0, Python 3.14.6 and agent-browser
0.26.0. The [code-only graph refresh](graph-update-01.json) completed. It skipped
the oversized HTML graph and reported JSON files with no extracted nodes; it
does not validate documentation semantics or payout behavior.

The HTML embeds the two exact source captures. Detailed command and browser
logs linked here remain in the repository evidence package.

No account, payment, rental or Host operation was performed. No legal approval,
individual dispute decision, enforceability ruling, agreement-priority decision,
push, merge or human acceptance is implied.

[Plan](plan.md) · [Baseline](baseline.json) · [Original pre-integration status](result-pre-integration.md)
