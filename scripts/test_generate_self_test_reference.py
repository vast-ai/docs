#!/usr/bin/env python3
"""Focused regressions for self-test reference MDX rendering."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_generator():
    path = Path(__file__).with_name("generate_self_test_reference.py")
    spec = importlib.util.spec_from_file_location("generate_self_test_reference", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_generator()


class CellRenderingTests(unittest.TestCase):
    def test_wraps_bare_cli_flags_in_inline_code(self) -> None:
        rendered = generator.cell(
            "Rerun with --ignore-requirements, then retry with --debugging enabled."
        )

        self.assertEqual(
            rendered,
            "Rerun with `--ignore-requirements`, then retry with `--debugging` enabled.",
        )

    def test_preserves_already_backticked_cli_flags(self) -> None:
        rendered = generator.cell("Rerun with `--ignore-requirements` for diagnostics.")

        self.assertEqual(
            rendered,
            "Rerun with `--ignore-requirements` for diagnostics.",
        )

    def test_does_not_rewrite_cli_flags_inside_fenced_code(self) -> None:
        rendered = generator.cell(
            "Try --debugging first.\n```bash\nvastai self-test machine 1 --ignore-requirements\n```"
        )

        self.assertEqual(
            rendered,
            "Try `--debugging` first.<br />```bash<br />"
            "vastai self-test machine 1 --ignore-requirements<br />```",
        )


class BandwidthRoundingTests(unittest.TestCase):
    def test_only_inexact_display_values_are_marked_rounded(self) -> None:
        examples = [(f"{gib} GiB total VRAM", min(500, max(100, 500 * gib / 192)))
                    for gib in (8, 48, 80, 96, 160, 192)]
        original = list(examples)
        rendered = generator.render_bandwidth_examples(examples)
        self.assertEqual(rendered.splitlines(), [
            "| Total machine VRAM | Required upload and download |",
            "| --- | --- |",
            "| 8 GiB total VRAM | 100 Mb/s |",
            "| 48 GiB total VRAM | 125 Mb/s |",
            "| 80 GiB total VRAM | 208.33 Mb/s (rounded) |",
            "| 96 GiB total VRAM | 250 Mb/s |",
            "| 160 GiB total VRAM | 416.67 Mb/s (rounded) |",
            "| 192 GiB total VRAM | 500 Mb/s |",
        ])
        self.assertEqual(examples, original)
        self.assertLess(208.33, examples[2][1])
        self.assertGreater(416.67, examples[4][1])


if __name__ == "__main__":
    unittest.main()
