# Repository correction scope — addendum 01

Recorded before implementation, 2026-09-09T11:23Z.

PUB-01: Missing Git exclusions expose local dependencies, private orchestration
archives/binary diffs, generated navigation graphs and reviewer feedback to
accidental staging. These four roots are not tracked. Add root .gitignore rules
for node_modules/, .orchestra/, graphify-out/ and review-feedback/ only; preserve
all existing files and all verification/evidence. Retest actual Git exclusion
and non-exclusion semantics. No deletion or blanket staging is authorized.

REPORT-01: The HTML embeds current claim counts but calls the September 8
client-unblocking result its full result and displays that run's 124/35/9 check
counts without sufficient current-versus-historical distinction. Bind the latest
sealed two-defect result explicitly, display its 176 Python/81 reviewer tests
with scoped limits, and retain the older result as clearly historical. Update
exporter/template regression tests and regenerate only the HTML. No model,
customer passage, historical result, authority or acceptance verdict changes.

Implementation will use separate isolated worker checkouts. The root agent will
independently verify and integrate only the declared files. Broader inherited
non-Host API-route and image-alt findings remain an explicit audit workstream;
they are not falsely reported as credentials or external-runtime blockers.
