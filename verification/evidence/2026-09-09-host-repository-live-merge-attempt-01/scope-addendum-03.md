# Shared Host preview contrast — addendum 03

Before implementation: the current retained Mint accessibility run confirms the
light link-color token against the dark background is 3.94:1, below the 4.5:1
threshold. This also affects Host pages; it is a repository presentation defect,
not a missing operator or owner-authority prerequisite.

A11Y-01: Adjust only docs.json colors.light to a close, brighter blue that meets
4.5:1 on the documented dark background. Preserve primary/dark colors and all
navigation/schema/other configuration exactly. Add a narrow contrast regression
using the actual Mint background/threshold. Retest current model freshness and
rendered Host reviewer so a visual change cannot silently invalidate bindings.

The 74 non-Host missing-alt observations are a separate, explicitly uncompleted
content/accessibility batch, not part of this one-token Host presentation fix.
