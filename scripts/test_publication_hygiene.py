#!/usr/bin/env python3
"""Regression coverage for publication-safe repository exclusions."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_ignore(path: str, *options: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "check-ignore", "--no-index", *options, "--", path],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class PublicationHygieneTests(unittest.TestCase):
    def test_private_generated_roots_exclude_nested_files(self) -> None:
        paths_by_rule = {
            "node_modules/": "site/node_modules/.cache/private-package.json",
            "__pycache__/": "scripts/__pycache__/test_host_theme_contrast.cpython-314.pyc",
            ".orchestra/": "runs/.orchestra/archive/private.diff",
            "graphify-out/": "docs/graphify-out/cache/graph.json",
            "review-feedback/": "review-feedback/pr-153/private-comment.patch",
        }

        for rule, path in paths_by_rule.items():
            with self.subTest(rule=rule, path=path):
                result = check_ignore(path, "--verbose")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(rule, result.stdout)
                self.assertTrue(result.stdout.rstrip().endswith(f"\t{path}"))

    def test_verification_docs_scripts_and_review_maps_remain_visible(self) -> None:
        visible_paths = (
            "verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/result.json",
            "host/cli-api-sdk.mdx",
            "scripts/verify_host_cli_commands.py",
            "host-docs-command-access.json",
            "host-docs-verification-inventory.json",
        )

        for path in visible_paths:
            with self.subTest(path=path):
                result = check_ignore(path, "--quiet")
                self.assertEqual(result.returncode, 1, result.stderr)

    def test_mint_excludes_internal_records_without_hiding_git_files(self) -> None:
        mintignore_lines = (ROOT / ".mintignore").read_text(encoding="utf-8").splitlines()
        internal_records = (
            "REVIEW-TRACEABILITY.md",
            "REVIEW-QUESTIONS.md",
            "HOST-DOCS-VV-HANDOFF.md",
        )
        for path in internal_records:
            with self.subTest(mint_excluded=path):
                self.assertIn(path, mintignore_lines)
        self.assertNotIn("review-questions.mdx", mintignore_lines)

        for path in (*internal_records, "review-questions.mdx"):
            with self.subTest(git_visible=path):
                result = check_ignore(path, "--quiet")
                self.assertEqual(result.returncode, 1, result.stderr)

        for path in (
            "verification/evidence/2026-09-09-host-repository-live-merge-attempt-01/result.json",
        ):
            with self.subTest(path=path):
                result = check_ignore(path, "--quiet")
                self.assertEqual(result.returncode, 1, result.stderr)


if __name__ == "__main__":
    unittest.main()
