import unittest
from pathlib import Path


class I18nSourceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_language_switcher_is_available_on_both_pages(self):
        for name in ("index.html", "recipients.html"):
            html = (self.root / "app" / "templates" / name).read_text(encoding="utf-8")
            self.assertIn('<html lang="en">', html)
            self.assertIn('class="ui-language"', html)
            self.assertIn('<option value="en">English</option>', html)
            self.assertIn('<option value="ja">Japanese</option>', html)
            self.assertIn('/static/i18n.js', html)

    def test_language_support_filter_defaults_to_english(self):
        html = (self.root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="language-filter"', html)
        self.assertIn('<option value="all" data-i18n="any">Any</option>', html)
        self.assertIn('<option value="en" selected data-i18n="english_only">English only</option>', html)
        self.assertIn('<option value="jp" data-i18n="japanese_only">Japanese only</option>', html)
        self.assertIn("languageFilter.value='en'", html)
        self.assertIn('data-en="{{ 1 if r.english_supported else 0 }}"', html)

    def test_translation_catalog_contains_both_languages(self):
        source = (self.root / "app" / "static" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn('steamfree-language', source)
        self.assertIn('language_support: "Language support"', source)
        self.assertIn('language_support: "言語対応"', source)
        self.assertIn('=== "ja" ? "ja" : "en"', source)


if __name__ == "__main__":
    unittest.main()
