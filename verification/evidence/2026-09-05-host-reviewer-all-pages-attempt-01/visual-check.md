# Final rendered visual check

2026-09-05 · macOS/Chromium through agent-browser · loopback only

Server source: `972a7be02697f90fbdcf52bc8054663affbf7515daf31c8261f2c09d141833f8`.
No documentation commands were executed and no review feedback was submitted.

Opened `http://127.0.0.1:4001/host/volume-offers#related-pages` in isolated session
`host-final-visual`, waited for `.vv-reading`, and used fresh accessibility-tree
references to open the review panel and click **Show on page**. At 1600×1000,
the four Related Pages rows were highlighted while the readable claim, source
scope note, Command Map link, evidence status and recorded-check link were
visible together. `volume-offers-reader.png` retains the result; the main agent
inspected the screenshot.

Set viewport to 430×932. The semantic-locator command
`agent-browser --session host-final-visual find role button click --name "Show on page" --exact`
failed to find the shadow-root button. This is a browser-harness locator failure,
not proof of a broken UI control. `volume-offers-mobile-located.png` preserves
that first attempt's still-open panel (despite the filename, it is not evidence
of a successful mobile click).

After a fresh `snapshot -i -d 2`, the button was exposed as `@e55`. Clicking that
reference succeeded. The panel closed, all four bound table rows remained
highlighted, and an outside-panel notice explained how to return to the review.
`volume-offers-mobile-retest-02.png` retains the correction retest; the main agent
inspected it. No full mobile-device, keyboard, or screen-reader acceptance is
claimed by these two viewport checks.
