from pathlib import Path


def test_admin_contains_steam_fetch_settings():
    html = Path("app/templates/recipients.html").read_text(encoding="utf-8")
    assert 'data-i18n="steam_settings"' in html
    assert "steam-fetch-mode" in html
    assert "steam-ua-preset" in html
    assert 'data-i18n="steam_connection_test"' in html
    assert 'data-i18n="fallback_403"' in html


def test_main_has_normal_search_fallback():
    source = Path("app/main.py").read_text(encoding="utf-8")
    assert '"https://store.steampowered.com/search/"' in source
    assert '"https://store.steampowered.com/search/results/"' in source
    assert 'steam_fallback_403' in source
    assert '/api/steam-settings/test' in source
