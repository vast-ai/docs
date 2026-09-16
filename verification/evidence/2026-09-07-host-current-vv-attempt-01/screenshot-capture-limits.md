# Supplementary screenshot capture limits

The Verification Stages screenshot was saved and visually inspected as
`current-review-verification-stages.png`. It shows the current section filter,
literal statement, plain-language status, location control and collapsed history.

The first screenshot request used a relative path without `./`; it did not
complete and was stopped. The absolute-path retest produced the retained image.

A separate absolute-path capture of the Volume Offers contextual evidence view
returned `CDP command timed out: Page.captureScreenshot`. No screenshot PASS is
claimed for that view. The browser did load the correct “Evidence — Volume
Offers” title and URL. The scoped HTTP tests separately confirmed the return
link and claim/evidence pairing; those results are not a visual screenshot test.

Both screenshot commands were loopback-only. No document command or Host/API
operation was executed. The complete 44-page statement-location browser result
is recorded separately in `browser-final/summary.json`.
