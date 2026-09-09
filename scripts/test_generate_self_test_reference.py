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


if __name__ == "__main__":
    unittest.main()
