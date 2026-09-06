# Focused reader-highlighting correction report

Date: 2026-09-05 (Africa/Johannesburg)

Scope: local review UI only. No documented Host command, credentialed request, paid operation, workload, or reviewer feedback mutation was performed.

## Findings

- The two remaining exact-location failures on `/host/self-test-reference` were prose table cells containing bare `--ignore-requirements` and `--debugging`. The rendered MDX replaces each double hyphen with one em dash. The earlier comparison incorrectly treated an em dash as three hyphens.
- Those two occurrences are CLI option names but are not marked as inline code in the MDX source (`host/self-test-reference.mdx:155` and `:198`). The locator now finds the customer-visible em-dash rendering as prose; that is not evidence that the displayed option spelling is correct. Backticking both tokens and regenerating their source bindings is the appropriate documentation correction.
- `/host/headless-install` contains no `Accordion`, `AccordionGroup`, `Tabs`, `Tab`, or HTML `details` disclosure in its MDX source. A current-code browser probe located all 91 claims without opening hidden content. No disclosure-clicking behavior was added.
- Typography folding now applies only to prose. Fenced code and inline code use literal comparisons, including when code appears inside an otherwise prose passage.
- The review context endpoint now returns `X-Vast-Review-Source-SHA256`, computed once from the running `review-server.mjs`, so an audit can reject a stale server process.
- Deliberately redacted source passages no longer appear as customer quotations. The card explains that the exact wording is hidden and labels the material claim as a summary; the existing masked-section fallback remains fail closed.
- `VOL-C35` retains its existing Related Pages source binding and four highlights. While its checked sections do not include `Command Map`, the reader shows: “This link check also covers Command Map. Its retained source location currently lists Related Pages only.” The notice links to `/host/volume-offers#command-map` and automatically disappears after a future binding includes that section.

## Retained browser results

The browser runner used real loopback-rendered pages, activated every **Show on page** control, inspected CSS ranges and notices, checked section filters and links, preserved recorded statuses, and did not execute page commands.

- `owner-tracked-change-audit-probe-01/`: `/host/headless-install`, 91 of 91 claims located before the punctuation correction.
- `owner-tracked-change-audit-probe-02/`: `/host/self-test-reference`, 123 of 125 claims located before correction. The two failures were the bare double-hyphen prose cases above.
- `owner-tracked-change-audit-retest-01/`: source SHA-256 `841e3d2c37fc42808d9253cb7ec21934813f7cd7b92089a8ef76549a11c52b80`; `/host/headless-install` 91 of 91 and `/host/self-test-reference` 125 of 125 located. Cards, status preservation, range counts, filters, and section links all passed. The served-source identity matched the on-disk source throughout the run.
- `owner-tracked-change-audit-final-01/`: final source SHA-256 `1ac4586359749c6786d8dda86a7bcc89a7a7dc3d0636e5772d249d93e5f905b5`; `/host/volume-offers` 39 of 39 claims located. Cards, status preservation, range counts, filters, and links all passed. The served-source identity matched and the file stayed unchanged throughout the run.

## Focused adverse observations

- On `/host/self-test-reference`, the inline-code occurrence `--ignore-requirements` located successfully. Changing only that rendered `code` node to an em dash in the isolated browser DOM produced zero ranges and the explicit exact-wording-not-found notice. This demonstrates that the prose normalization does not equate distinct literal code.
- A deliberately redacted claim on `/host/common-errors-diagnostics` rendered no blockquote, displayed the summary-not-quote notice, produced zero highlight ranges, and retained its valid section link and masked-data notice.
- On `/host/volume-offers`, `VOL-C35` displayed the guarded scope notice and valid `#command-map` link while highlighting only the four retained Related Pages passages. No unbound Command Map text was highlighted.

## Limitations

These results validate local reader navigation and presentation against the retained material-claim inventory. They do not validate Host commands, runtime behavior, product meaning, policy, pricing, contract terms, account behavior, or the truth of documentation claims. The full-page frozen-source sweep and canonical V&V status reconciliation remain separate checks.
