from pathlib import Path


def test_fix021_sources_have_bilingual_and_defaults_controls():
    root = Path(__file__).resolve().parents[1]
    main = (root / "app/main.py").read_text(encoding="utf-8")
    index = (root / "app/templates/index.html").read_text(encoding="utf-8")
    admin = (root / "app/templates/recipients.html").read_text(encoding="utf-8")
    i18n = (root / "app/static/i18n.js").read_text(encoding="utf-8")
    assert '"english_supported": "INTEGER DEFAULT 0"' in main
    assert '@app.put("/api/ui-defaults")' in main
    assert 'id="language-filter"' in index
    assert 'value="en"' in index and 'value="ja"' in index
    assert 'id="ui-defaults-form"' in admin
    assert 'default_display_language' in i18n
    assert 'Japanese only' in i18n and '日本語のみ' in i18n
