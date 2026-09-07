#!/usr/bin/env python3
"""Check or repair empty Host MDX anchors without changing fragment IDs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EMPTY_ANCHOR = re.compile(
    r'^(?P<indent>[ \t]*)<a id="(?P<anchor>[A-Za-z0-9][A-Za-z0-9._:-]*)"[ \t]*/>[ \t]*$',
    re.MULTILINE,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace empty link elements with aria-hidden span targets",
    )
    args = parser.parse_args()

    repository = Path(__file__).resolve().parents[1]
    host_dir = repository / "host"
    matches: list[tuple[Path, int, str]] = []

    for path in sorted(host_dir.rglob("*.mdx")):
        text = path.read_text(encoding="utf-8")
        file_matches = list(EMPTY_ANCHOR.finditer(text))
        for match in file_matches:
            line = text.count("\n", 0, match.start()) + 1
            matches.append((path, line, match.group("anchor")))

        if args.write and file_matches:
            replacement = EMPTY_ANCHOR.sub(
                lambda match: (
                    f'{match.group("indent")}<span id="{match.group("anchor")}" '
                    'aria-hidden="true" />'
                ),
                text,
            )
            path.write_text(replacement, encoding="utf-8")

    if matches and not args.write:
        for path, line, anchor in matches:
            print(f"{path.relative_to(repository)}:{line}: empty named anchor #{anchor}")
        print(f"FAIL: {len(matches)} empty Host anchor(s) require accessible markup")
        return 1

    if args.write:
        print(f"Replaced {len(matches)} empty Host anchor(s); fragment IDs are unchanged")
    else:
        print("PASS: no empty link elements are used as Host fragment targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
