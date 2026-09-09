# Internal review-link dependency — addendum 05

PUB-02's actual retest returns100 findings, not99: REVIEW-QUESTIONS.md links to
the now-unpublished traceability record. HOST-DOCS-VV-HANDOFF.md in turn links
to REVIEW-QUESTIONS.md. Both are explicitly internal review/handoff records,
not customer workflows; the separate review-questions.mdx route is untouched.

Add exactly these two Markdown records to .mintignore alongside traceability,
preserving their Git files and local reviewer functionality. The repository-wide
backlink inspection found no further ordinary Markdown links into this pair.
Retest raw Mint output before generated-route reconciliation. Preserve the
original140 and intermediate100 findings; do not suppress a product page.
