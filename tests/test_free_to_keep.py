from types import SimpleNamespace
from unittest.mock import patch

from app import main


def _response(*, json_data=None, text="", status_code=200, headers=None):
    def raise_for_status():
        if status_code >= 400:
            raise main.requests.HTTPError(f"HTTP {status_code}")
    return SimpleNamespace(
        text=text,
        status_code=status_code,
        headers=headers or {},
        json=lambda: json_data,
        raise_for_status=raise_for_status,
    )


def test_free_to_keep_parser_accepts_english_purchase_block():
    html = """
    <div class="game_area_purchase_game">
      <h1>Get Deponia</h1>
      <p>Free to keep when you get it before 21 Aug @ 2:00am.</p>
      <div class="discount_pct">-100%</div>
      <a>Add to Account</a>
    </div>
    """
    assert main._is_free_to_keep_html(html) is True


def test_free_to_keep_parser_accepts_japanese_purchase_block():
    html = """
    <div class="game_area_purchase_game">
      <h1>Deponiaをもらう</h1>
      <p>8月21日2時までにゲットすれば、今後も無料でキープできる！</p>
      <div class="discount_pct">-100%</div>
      <a>アカウントに追加</a>
    </div>
    """
    assert main._is_free_to_keep_html(html) is True


def test_permanent_free_to_play_text_is_not_free_to_keep():
    html = """
    <div class="game_area_purchase_game">
      <h1>Play Example Game</h1>
      <div class="game_purchase_price price">Free To Play</div>
      <a>Play Game</a>
    </div>
    """
    assert main._is_free_to_keep_html(html) is False


def test_verify_prefers_store_free_to_keep_over_appdetails_sale_price():
    appid = 214340
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Deponia",
        "type": "game",
        "is_free": False,
        "supported_languages": "English<strong>*</strong>, German<strong>*</strong>",
        "genres": [{"id": "25", "description": "Adventure"}],
        "header_image": "https://example.com/deponia.jpg",
        "price_overview": {
            "initial": 980,
            "final": 98,
            "discount_percent": 90,
            "initial_formatted": "¥ 980",
            "final_formatted": "¥ 98",
        },
    }}})
    store = _response(text="""
    <div class="game_area_purchase_game">
      <p>Free to keep when you get it before 21 Aug @ 2:00am.</p>
      <div class="discount_pct">-100%</div>
      <a>Add to Account</a>
      <script>InitDailyDealTimer('x', 1790000000);</script>
    </div>
    """)
    with patch.object(main.requests, "get", side_effect=[api, store]):
        result = main.verify(appid, "https://store.steampowered.com/app/214340/")

    assert result is not None
    assert result["discount_percent"] == 100
    assert result["current_price_value"] == 0
    assert result["current_price"] == "無料"
    assert result["product_type"] == "game"
    assert result["japanese_supported"] == 0
    assert result["english_supported"] == 1


def test_verify_still_excludes_permanent_free_to_play():
    appid = 999001
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Permanent F2P",
        "type": "game",
        "is_free": True,
    }}})
    with patch.object(main.requests, "get", return_value=api) as get:
        assert main.verify(appid, "") is None
        assert get.call_count == 1


def test_discover_has_independent_free_price_candidate_path():
    """A free-search row must become a candidate even without -100% markup."""
    free_html = """
    <a class="search_result_row" data-ds-appid="214340" href="https://store.steampowered.com/app/214340/Deponia/">
      <span class="title">Deponia</span><div class="search_price">Free</div>
    </a>
    """
    empty_html = "<html></html>"

    def fake_fetch(_session, params, preferred=None):
        html = free_html if params.get("maxprice") == "free" else empty_html
        return _response(text=html), "normal"

    with patch.object(main, "_fetch_search_response", side_effect=fake_fetch):
        found, scanned, _parsed, _max_discount = main.discover()

    assert 214340 in found
    assert found[214340].startswith("https://store.steampowered.com/app/214340")
    assert scanned == 1


def test_free_search_candidate_is_still_verified_before_acceptance():
    """Dedicated discovery must not turn permanent F2P into Free-to-Keep."""
    appid = 999002
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Permanent F2P",
        "type": "game",
        "is_free": True,
    }}})
    with patch.object(main.requests, "get", return_value=api):
        assert main.verify(appid, "https://store.steampowered.com/app/999002/") is None


def test_lowest_price_search_row_detects_deponia_zero_yen():
    from bs4 import BeautifulSoup

    html = """
    <a class="search_result_row" data-ds-appid="214340" href="https://store.steampowered.com/app/214340/Deponia/">
      <span class="title">Deponia</span>
      <div class="search_discount"><span>-100%</span></div>
      <div class="search_price"><span>¥980</span> ¥0</div>
    </a>
    """
    row = BeautifulSoup(html, "html.parser").select_one("a.search_result_row")
    assert main._search_row_looks_zero_price(row) is True


def test_lowest_price_specials_add_deponia_when_other_discovery_paths_miss():
    """Reproduce the Store UI path: Price_ASC shows Deponia as -100% / ¥0."""
    deponia_html = """
    <a class="search_result_row" data-ds-appid="214340" href="https://store.steampowered.com/app/214340/Deponia/">
      <span class="title">Deponia</span>
      <div class="search_discount"><span>-100%</span></div>
      <div class="search_price"><span class="discount_original_price">¥980</span> ¥0</div>
    </a>
    <a class="search_result_row" data-ds-appid="123456" href="https://store.steampowered.com/app/123456/Other/">
      <span class="title">Other</span><div class="search_discount"><span>-90%</span></div><div class="search_price">¥60</div>
    </a>
    """
    empty_html = "<html></html>"

    def fake_fetch(_session, params, preferred=None):
        if params.get("sort_by") == "Price_ASC" and "maxprice" not in params:
            return _response(text=deponia_html), "normal"
        return _response(text=empty_html), "normal"

    with patch.object(main, "_fetch_search_response", side_effect=fake_fetch):
        found, scanned, parsed, max_discount = main.discover()

    assert 214340 in found
    assert 123456 not in found
    assert scanned == 2
    assert parsed == 2
    assert max_discount == 100


def test_lowest_price_search_does_not_admit_nonzero_90_percent_sale():
    from bs4 import BeautifulSoup

    html = """
    <a class="search_result_row" data-ds-appid="123456">
      <span class="title">90 percent sale</span>
      <div class="search_discount"><span>-90%</span></div>
      <div class="search_price"><span>¥600</span> ¥60</div>
    </a>
    """
    row = BeautifulSoup(html, "html.parser").select_one("a.search_result_row")
    assert main._search_row_looks_zero_price(row) is False

class _FakeSearchResponse:
    def __init__(self, text, payload=None):
        self.text = text
        self._payload = payload

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


def test_search_rows_from_ajax_results_html():
    html = "<a class='search_result_row' data-ds-appid='214340' href='https://store.steampowered.com/app/214340/Deponia/'><div class='discount_pct'>-100%</div><div class='discount_final_price'>JPY 0</div></a>"
    response = _FakeSearchResponse('{\"success\":1,\"results_html\":\"...\"}', {"success": 1, "results_html": html})
    rows = main._search_rows_from_response(response)
    assert len(rows) == 1
    assert rows[0].get("data-ds-appid") == "214340"
    assert main._search_row_looks_zero_price(rows[0])


def test_search_rows_from_normal_html_still_works():
    html = "<a class='search_result_row' data-ds-appid='214340' href='https://store.steampowered.com/app/214340/Deponia/'><div class='discount_pct'>-100%</div><div class='discount_final_price'>JPY 0</div></a>"
    rows = main._search_rows_from_response(_FakeSearchResponse(html))
    assert len(rows) == 1
    assert rows[0].get("data-ds-appid") == "214340"



def test_verify_retains_deponia_stage_diagnostics():
    appid = 214340
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Deponia", "type": "game", "is_free": False,
        "supported_languages": "English", "genres": [],
        "price_overview": {"initial": 980, "final": 98, "discount_percent": 90,
                           "initial_formatted": "¥980", "final_formatted": "¥98"},
    }}})
    store = _response(text="""<div class='game_area_purchase_game'>
      <p>Free to keep</p><span>-100%</span><a>Add to Account</a></div>""")
    debug = {}
    with patch.object(main.requests, "get", side_effect=[api, store]):
        result = main.verify(appid, "", debug)
    assert result["discount_percent"] == 100
    assert debug["appdetails_http"] == 200
    assert debug["appdetails_discount"] == 90
    assert debug["appdetails_final"] == 98
    assert debug["store_http"] == 200
    assert debug["store_free_to_keep"] == 1
    assert debug["verify_status"] == "verified"
    assert debug["verify_reason"] == "free_to_keep_store_confirmed"


def test_diagnostic_scan_does_not_blanket_deactivate_previous_rows(tmp_path):
    old_db = main.DB
    try:
        main.DB = tmp_path / "diag.db"
        with main.conn() as c:
            c.execute(
                """INSERT INTO promotions(appid,title,url,original_price,discount_percent,first_seen,last_seen,active,notified)
                   VALUES(1,'Existing','https://example.com','¥100',90,'x','x',1,0)"""
            )
            c.commit()
        with patch.object(main, "discover", return_value=({}, 0, 0, 0)):
            main._scan_impl(send_new=False)
        with main.conn() as c:
            row = c.execute("SELECT active FROM promotions WHERE appid=1").fetchone()
        assert row["active"] == 1
    finally:
        main.DB = old_db



def test_deponia_is_free_true_with_100_percent_search_is_not_treated_as_permanent_f2p():
    appid = 214340
    main.LAST_DISCOVERY_DEBUG.clear()
    main.LAST_DISCOVERY_DEBUG[appid] = {
        "sources": ["maxprice_free"],
        "search_discount": 100,
        "search_row_text": "Deponia 2012年8月6日 -100% ¥980 ¥0",
        "url": "https://store.steampowered.com/app/214340/Deponia/",
    }
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Deponia", "type": "game", "is_free": True,
        "supported_languages": "English", "genres": [{"id":"25","description":"Adventure"}],
        "header_image": "https://example.com/deponia.jpg",
    }}})
    store = _response(text="<html><body>Deponia</body></html>")
    debug = {}
    with patch.object(main.requests, "get", side_effect=[api, store]):
        result = main.verify(appid, "https://store.steampowered.com/app/214340/", debug)
    assert result is not None
    assert result["discount_percent"] == 100
    assert result["current_price_value"] == 0
    assert result["original_price"].replace(" ", "") == "¥980"
    assert debug["appdetails_is_free"] == 1
    assert debug["verify_reason"] == "free_to_keep_search_confirmed"


def test_is_free_true_without_100_percent_search_remains_permanent_f2p():
    appid = 999003
    main.LAST_DISCOVERY_DEBUG.clear()
    main.LAST_DISCOVERY_DEBUG[appid] = {
        "sources": ["maxprice_free"], "search_discount": None,
        "search_row_text": "Permanent F2P Free", "url": "",
    }
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Permanent F2P", "type": "game", "is_free": True,
    }}})
    with patch.object(main.requests, "get", return_value=api) as get:
        debug = {}
        assert main.verify(appid, "", debug) is None
        assert debug["verify_reason"] == "permanent_free_to_play"
        assert get.call_count == 1


def test_appdetails_429_is_retried_and_then_succeeds_without_sleeping():
    appid = 999004
    main.LAST_DISCOVERY_DEBUG.clear()
    main.LAST_DISCOVERY_DEBUG[appid] = {
        "sources": ["discount_desc"], "search_discount": 90,
        "search_row_text": "Example -90% ¥1000 ¥100", "url": "",
    }
    throttled = _response(status_code=429, headers={"Retry-After": "0"})
    api = _response(json_data={str(appid): {"success": True, "data": {
        "name": "Example", "type": "game", "is_free": False,
        "supported_languages": "English", "genres": [],
        "price_overview": {"initial":1000,"final":100,"discount_percent":90,
                           "initial_formatted":"¥1000","final_formatted":"¥100"},
    }}})
    store = _response(text="<html></html>")
    debug = {}
    with patch.object(main.requests, "get", side_effect=[throttled, api, store]), patch.object(main.time, "sleep"):
        result = main.verify(appid, "", debug)
    assert result is not None
    assert debug["appdetails_http"] == 200
    assert debug["appdetails_attempts"] == 2
