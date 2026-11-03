"""Lightweight static checks for the documentation portal's dark theme.

These checks prevent obvious contrast regressions; they are not a WCAG audit.
"""
import re
import unittest
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "style.css"


def tokens(stylesheet):
    return dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*[;}]", stylesheet))


def luminance(value):
    rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    return sum(a * b for a, b in zip(linear, (.2126, .7152, .0722)))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = CSS.read_text()
        cls.colors = tokens(cls.css)

    def test_normal_text_contrast(self):
        pairs = [
            ("text", "canvas-raised"),
            ("text-secondary", "surface"),
            ("muted", "surface"),
            ("accent", "surface"),
        ]
        for text, background in pairs:
            with self.subTest(text=text, background=background):
                self.assertGreaterEqual(contrast(self.colors[text], self.colors[background]), 4.5)

    def test_border_contrast(self):
        self.assertGreaterEqual(contrast(self.colors["border"], self.colors["surface"]), 3)

    def test_keyboard_and_media_preferences(self):
        compact = re.sub(r"\s+", "", self.css)
        for feature in (
            ":focus-visible",
            ".skip:focus",
            "prefers-reduced-motion",
            "forced-colors",
            "max-width:48rem",
            "min-height:44px",
        ):
            with self.subTest(feature=feature):
                self.assertIn(feature, compact)

    def test_no_remote_css_dependencies(self):
        self.assertNotRegex(self.css, r"(?i)@import\b|url\s*\(")


if __name__ == "__main__":
    unittest.main()
