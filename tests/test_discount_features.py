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
        self.assertIn('data-i18n="discount_90"', template)
        self.assertIn('data-i18n="free_only"', template)
        self.assertIn('id="language-filter"', template)
        self.assertIn('data-genre="{{ key }}"', template)
        self.assertIn('data-i18n="current_price"', template)
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
    assert "v1.5.0" in html


def test_product_type_filter_and_discount_end_ui():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "main.py").read_text(encoding="utf-8")
    html = (root / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'product_type' in source
    assert 'discount_end_ts' in source
    assert 'data-i18n="games_only"' in html
    assert 'data-i18n="dlc_only"' in html
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
    assert "ui_defaults.product_type == 'game'" in html
    assert "ui_defaults.language_support == 'ja'" in html
    assert "ui_defaults.sort == 'price'" in html
    assert "ui_defaults.order == 'asc'" in html
    assert "typeFilter.value=defaults.product_type" in html
    assert "languageFilter.value=defaults.language_support" in html
    assert "sortKey.value=defaults.sort" in html
    assert "sortDir.value=defaults.order" in html
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
