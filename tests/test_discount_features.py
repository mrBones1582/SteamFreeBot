import unittest
from types import SimpleNamespace

# This file documents core v1.2.0 expectations; runtime integration is exercised on NAS.


class DiscountFeatureSourceTests(unittest.TestCase):
    def test_source_contains_new_filters_and_sorting(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        source = (root / 'app' / 'main.py').read_text(encoding='utf-8')
        template = (root / 'app' / 'templates' / 'index.html').read_text(encoding='utf-8')
        self.assertIn('MIN_DISCOUNT_PERCENT', source)
        self.assertIn('japanese_supported', source)
        self.assertIn('genre_keys', source)
        self.assertIn('90% off or more', template)
        self.assertIn('Free only', template)
        self.assertIn('Language support', template)
        self.assertIn('English only', template)
        self.assertIn('Japanese only', template)
        self.assertIn('data-genre="{{ key }}"', template)
        self.assertIn('Current price', template)
        self.assertIn('sort-dir', template)
        self.assertIn('list-view', template)
        self.assertIn('card-view', template)
        self.assertIn('header_image', source)


if __name__ == '__main__':
    unittest.main()


def test_list_view_has_thumbnail():
    from pathlib import Path
    html = (Path(__file__).parents[1] / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    assert ".list-view .thumb{display:block" in html
    assert "grid-template-columns:112px minmax(0,1fr)" in html
    assert "v1.4.2" in html


def test_product_type_filter_and_discount_end_ui():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "main.py").read_text(encoding="utf-8")
    html = (root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'product_type' in source
    assert 'discount_end_ts' in source
    assert 'Games only' in html
    assert 'DLC only' in html
    assert 'sale-end' in html
    assert 'urgent' in html and 'soon' in html


def test_daily_scan_schedule_is_fixed_time():
    from pathlib import Path
    source = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert 'AUTO_SCAN_HOUR' in source
    assert 'AUTO_SCAN_MINUTE' in source
    assert '"cron"' in source
    assert 'CHECK_INTERVAL_HOURS' not in source


def test_default_filters_and_compact_links():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    assert '<option value="game" selected data-i18n="games_only">Games only</option>' in html
    assert '<option value="en" selected data-i18n="english_only">English only</option>' in html
    assert '<option value="price" selected data-i18n="current_price">Current price</option>' in html
    assert '<option value="asc" selected data-i18n="ascending">Ascending</option>' in html
    assert "typeFilter.value='game'" in html
    assert "languageFilter.value='en'" in html
    assert "sortKey.value='price'" in html
    assert "sortDir.value='asc'" in html
    assert 'Steamで開く ↗' not in html
    assert 'grid-template-areas:"title discount" "price saleend" "meta meta"' in html


def test_fixed_header_contains_result_controls_and_card_meta_is_compact():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    header = html.split("</header>", 1)[0]
    assert 'class="resultbar header-resultbar"' in header
    assert 'id="visible-count"' in header
    assert 'data-view="list"' in header and 'data-view="card"' in header
    assert 'white-space:nowrap;flex:0 0 auto' in html
    assert 'text-overflow:ellipsis' in html


def test_bilingual_language_controls_are_present():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    index = (root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    recipients = (root / "app" / "templates" / "recipients.html").read_text(encoding="utf-8")
    translations = (root / "app" / "static" / "i18n.js").read_text(encoding="utf-8")
    for html in (index, recipients):
        assert '<html lang="en">' in html
        assert 'class="ui-language"' in html
        assert '<option value="en">English</option>' in html
        assert '<option value="ja">Japanese</option>' in html
        assert '/static/i18n.js' in html
    assert 'steamfree-language' in translations
    assert 'language_support: "Language support"' in translations
    assert 'language_support: "言語対応"' in translations
