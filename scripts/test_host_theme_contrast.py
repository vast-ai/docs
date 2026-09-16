#!/usr/bin/env python3
"""Regression checks for the Mint theme's configured color contrast."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "docs.json"
AA_NORMAL_TEXT = 4.5
MINT_DARK_BASE = "#09090B"
PREVIOUS_LIGHT = "#315FFF"


def rgb(color: str) -> tuple[int, int, int]:
    assert color.startswith("#") and len(color) == 7, f"Expected #RRGGBB, got {color}"
    return tuple(int(color[index : index + 2], 16) for index in (1, 3, 5))


def mint_dark_background(light: str) -> str:
    """Match Mint's default 98% #09090B / 2% light-color dark background."""
    blended = tuple(
        round(base_channel * 0.98 + light_channel * 0.02)
        for base_channel, light_channel in zip(rgb(MINT_DARK_BASE), rgb(light))
    )
    return "#" + "".join(f"{channel:02X}" for channel in blended)


def relative_luminance(color: str) -> float:
    def linear(channel: int) -> float:
        normalized = channel / 255
        return (
            normalized / 12.92
            if normalized <= 0.04045
            else ((normalized + 0.055) / 1.055) ** 2.4
        )

    red, green, blue = (linear(channel) for channel in rgb(color))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


class HostThemeContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cls.colors = config["colors"]

    def test_theme_colors_preserve_primary_and_dark(self) -> None:
        self.assertEqual(self.colors["primary"], "#315FFF")
        self.assertEqual(self.colors["dark"], "#315FFF")
        self.assertEqual(self.colors["light"], "#3F6DFF")

    def test_mint_default_dark_background_formula(self) -> None:
        self.assertEqual(mint_dark_background(self.colors["light"]), "#0A0B10")

    def test_light_color_clears_aa_on_mint_dark_background(self) -> None:
        dark_background = mint_dark_background(self.colors["light"])
        before = contrast_ratio(PREVIOUS_LIGHT, dark_background)
        after = contrast_ratio(self.colors["light"], dark_background)

        self.assertLess(before, AA_NORMAL_TEXT)
        self.assertGreaterEqual(after, AA_NORMAL_TEXT)

    def test_primary_color_clears_aa_on_white(self) -> None:
        self.assertGreaterEqual(
            contrast_ratio(self.colors["primary"], "#FFFFFF"), AA_NORMAL_TEXT
        )


def contrast_metrics() -> dict[str, float | str]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    colors = config["colors"]
    dark_background = mint_dark_background(colors["light"])
    return {
        "dark_background": dark_background,
        "before": contrast_ratio(PREVIOUS_LIGHT, dark_background),
        "after": contrast_ratio(colors["light"], dark_background),
        "primary_on_white": contrast_ratio(colors["primary"], "#FFFFFF"),
    }


if __name__ == "__main__":
    unittest.main(verbosity=2)
