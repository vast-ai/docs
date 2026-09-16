#!/usr/bin/env python3
"""Check that persona frontmatter and visible persona chips stay in sync.

Every authored host page (host/*.mdx) carries the persona taxonomy twice:
machine-readable `personas:` frontmatter and a hand-written chip div rendered
top-right of the page. This check fails when the two drift apart.

Conventions enforced (matching the CON-1518 IA rulings):
  - slug -> chip label: pro-operator "Pro Operator", headless-operator
    "Headless / DC", business-owner "Business", hobbyist "Hobbyist"
  - all four personas collapse to a single "All host personas" chip
  - chip order within the div is free; membership must match exactly
  - generated host/cli/* and host/sdk/* pages are exempt (untagged by design)

Usage: python3 scripts/check_persona_chips.py   (exit 0 = in sync)
"""

import glob
import re
import sys

SLUG_TO_LABEL = {
    "pro-operator": "Pro Operator",
    "headless-operator": "Headless / DC",
    "business-owner": "Business",
    "hobbyist": "Hobbyist",
}
ALL_PERSONAS_LABEL = "All host personas"

FRONTMATTER_RE = re.compile(r"^personas:\n((?:[ \t]+- .+\n)+)", re.M)
SLUG_RE = re.compile(r"[ \t]+- (.+)")
CHIP_DIV_RE = re.compile(r'<div className="persona-chips">(.*?)</div>', re.S)
CHIP_RE = re.compile(r'<span className="persona-chip">([^<]+)</span>')


def check_file(path):
    errors = []
    src = open(path, encoding="utf-8").read()

    fm = FRONTMATTER_RE.search(src)
    slugs = [s.strip() for s in SLUG_RE.findall(fm.group(1))] if fm else []
    divs = CHIP_DIV_RE.findall(src)

    if not slugs:
        errors.append("missing or empty `personas:` frontmatter")
    if not divs:
        errors.append("missing persona-chips div")
    if len(divs) > 1:
        errors.append(f"expected 1 persona-chips div, found {len(divs)}")
    if not slugs or not divs:
        return errors

    unknown = [s for s in slugs if s not in SLUG_TO_LABEL]
    if unknown:
        errors.append(f"unknown persona slug(s) in frontmatter: {unknown}")
        return errors
    if len(set(slugs)) != len(slugs):
        errors.append(f"duplicate persona slug(s) in frontmatter: {slugs}")

    chips = CHIP_RE.findall(divs[0])
    if set(slugs) == set(SLUG_TO_LABEL):
        expected = [ALL_PERSONAS_LABEL]
    else:
        expected = [SLUG_TO_LABEL[s] for s in slugs]

    if sorted(chips) != sorted(expected):
        errors.append(
            f"chips {chips} do not match personas frontmatter "
            f"(expected {sorted(expected)} in any order)"
        )
    return errors


def main():
    pages = sorted(glob.glob("host/*.mdx"))
    if not pages:
        print("check_persona_chips: no host/*.mdx pages found — run from the repo root")
        return 1

    failed = 0
    for path in pages:
        for err in check_file(path):
            print(f"FAIL {path}: {err}")
            failed += 1
    if failed:
        print(f"\ncheck_persona_chips: {failed} problem(s) across {len(pages)} pages")
        return 1
    print(f"check_persona_chips: OK — {len(pages)} pages, frontmatter and chips in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
