from pathlib import Path

from app import main


def test_filter_toolbar_is_sticky_below_site_header():
    html = (Path(__file__).parents[1] / 'app/templates/index.html').read_text(encoding='utf-8')
    assert '.toolbar{position:sticky' in html
    assert 'top:var(--steamfree-header-height,0px)' in html
    assert 'syncStickyHeaderHeight' in html


def test_appdetails_rate_limit_defaults_are_conservative():
    assert main.STEAM_REQUEST_MIN_INTERVAL['appdetails'] >= 1.0
    assert main.STEAM_REQUEST_MIN_INTERVAL['store'] >= 0.25


def test_fix032_version():
    assert main.app.version == '1.6.0'
