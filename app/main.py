from __future__ import annotations

import json
import os
import re
import sqlite3
import smtplib
import ssl
import threading
from datetime import date, datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

load_dotenv()
BASE = Path(__file__).resolve().parent.parent
DB = BASE / "data" / "steam_free.db"
DB.parent.mkdir(exist_ok=True)
DEFAULT_CHROME_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
DEFAULT_FIREFOX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0"
COUNTRY = os.getenv("STEAM_COUNTRY", "JP")
LANG = os.getenv("STEAM_LANGUAGE", "english")
MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT_PERCENT", "80"))
MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "12"))

app = FastAPI(title="Steam Free Bot", version="1.5.3")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))



STEAM_SETTING_DEFAULTS = {
    "steam_fetch_mode": "auto",
    "steam_ua_preset": "chrome",
    "steam_custom_ua": "",
    "steam_use_session": "1",
    "steam_use_referer": "1",
    "steam_fallback_403": "1",
    "steam_accept_language": "en-US,en;q=0.9,ja;q=0.6",
}

class SteamSettingsPayload(BaseModel):
    fetch_mode: str = Field(pattern="^(auto|ajax|normal)$")
    ua_preset: str = Field(pattern="^(chrome|firefox|custom)$")
    custom_ua: str = ""
    use_session: bool = True
    use_referer: bool = True
    fallback_403: bool = True
    accept_language: str = "en-US,en;q=0.9,ja;q=0.6"


UI_DEFAULTS = {
    "ui_default_language": "en",
    "ui_default_genre": "all",
    "ui_default_discount": "all",
    "ui_default_type": "game",
    "ui_default_language_support": "ja",
    "ui_default_sort": "price",
    "ui_default_order": "asc",
}


class UiDefaultsPayload(BaseModel):
    language: str = Field(pattern="^(en|ja)$")
    genre: str = Field(pattern="^(all|rpg|slg|action|adventure|casual|sports|racing|other)$")
    discount: str = Field(pattern="^(all|90plus|free)$")
    product_type: str = Field(pattern="^(all|game|dlc)$")
    language_support: str = Field(pattern="^(all|en|ja)$")
    sort: str = Field(pattern="^(discount|name|price)$")
    order: str = Field(pattern="^(asc|desc)$")

GENRE_ID_TO_KEY = {
    "1": "action",
    "2": "slg",      # Strategy
    "3": "rpg",
    "4": "casual",
    "9": "racing",
    "18": "sports",
    "25": "adventure",
    "28": "slg",     # Simulation
}
GENRE_LABELS = {
    "all": "All",
    "rpg": "RPG",
    "slg": "SLG",
    "action": "Action",
    "adventure": "Adventure",
    "casual": "Casual",
    "sports": "Sports",
    "racing": "Racing",
    "other": "Other",
}
GENRE_TAB_ORDER = ["all", "rpg", "slg", "action", "adventure", "casual", "sports", "racing", "other"]


class RecipientPayload(BaseModel):
    email: str
    delivery_end_date: str | None = None


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute(
        """CREATE TABLE IF NOT EXISTS promotions(
            appid INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            original_price TEXT,
            discount_percent INTEGER,
            first_seen TEXT,
            last_seen TEXT,
            active INTEGER DEFAULT 1,
            notified INTEGER DEFAULT 0
        )"""
    )
    columns = {row[1] for row in c.execute("PRAGMA table_info(promotions)")}
    additions = {
        "current_price": "TEXT",
        "current_price_value": "INTEGER",
        "japanese_supported": "INTEGER DEFAULT 0",
        "english_supported": "INTEGER DEFAULT 0",
        "genre_keys": "TEXT DEFAULT ''",
        "genre_names": "TEXT DEFAULT ''",
        "header_image": "TEXT DEFAULT ''",
        "product_type": "TEXT DEFAULT 'other'",
        "discount_end_ts": "INTEGER",
    }
    for name, definition in additions.items():
        if name not in columns:
            c.execute(f"ALTER TABLE promotions ADD COLUMN {name} {definition}")

    c.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY,v TEXT)")
    c.execute(
        """CREATE TABLE IF NOT EXISTS mail_recipients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            delivery_end_date TEXT,
            stopped INTEGER NOT NULL DEFAULT 0 CHECK(stopped IN (0,1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    c.commit()
    return c


def meta(k, v=None):
    with conn() as c:
        if v is not None:
            c.execute(
                "INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (k, str(v)),
            )
            c.commit()
        r = c.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return r["v"] if r else None


def steam_setting(key: str) -> str:
    value = meta(key)
    if value is None:
        return STEAM_SETTING_DEFAULTS[key]
    return value


def steam_settings_dict() -> dict:
    return {
        "fetch_mode": steam_setting("steam_fetch_mode"),
        "ua_preset": steam_setting("steam_ua_preset"),
        "custom_ua": steam_setting("steam_custom_ua"),
        "use_session": steam_setting("steam_use_session") == "1",
        "use_referer": steam_setting("steam_use_referer") == "1",
        "fallback_403": steam_setting("steam_fallback_403") == "1",
        "accept_language": steam_setting("steam_accept_language"),
        "last_method": meta("last_fetch_method") or "未実行",
        "last_http": meta("last_fetch_http") or "-",
        "last_test_rows": int(meta("last_fetch_test_rows") or 0),
    }


def ui_default(key: str) -> str:
    value = meta(key)
    return UI_DEFAULTS[key] if value is None else value


def ui_defaults_dict() -> dict:
    return {
        "language": ui_default("ui_default_language"),
        "genre": ui_default("ui_default_genre"),
        "discount": ui_default("ui_default_discount"),
        "product_type": ui_default("ui_default_type"),
        "language_support": ui_default("ui_default_language_support"),
        "sort": ui_default("ui_default_sort"),
        "order": ui_default("ui_default_order"),
    }


def _steam_user_agent() -> str:
    preset = steam_setting("steam_ua_preset")
    if preset == "firefox":
        return DEFAULT_FIREFOX_UA
    if preset == "custom":
        custom = steam_setting("steam_custom_ua").strip()
        if custom:
            return custom
    return DEFAULT_CHROME_UA


def _steam_headers(referer: str | None = None) -> dict:
    headers = {
        "User-Agent": _steam_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": steam_setting("steam_accept_language") or STEAM_SETTING_DEFAULTS["steam_accept_language"],
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if steam_setting("steam_use_referer") == "1":
        headers["Referer"] = referer or "https://store.steampowered.com/search/"
    return headers


def _steam_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(_steam_headers())
    session.cookies.update({
        "birthtime": "315532800",
        "lastagecheckage": "1-January-1980",
        "wants_mature_content": "1",
    })
    if steam_setting("steam_use_session") == "1":
        try:
            session.get("https://store.steampowered.com/", params={"cc": COUNTRY, "l": LANG}, timeout=15)
            session.get("https://store.steampowered.com/search/", params={"specials": "1", "cc": COUNTRY, "l": LANG}, timeout=15)
        except requests.RequestException:
            pass
    return session


def _fetch_search_response(session: requests.Session, params: dict, preferred: str | None = None):
    mode = preferred or steam_setting("steam_fetch_mode")
    fallback = steam_setting("steam_fallback_403") == "1"
    attempts = ["normal"] if mode == "normal" else ["ajax"]
    if mode == "auto":
        attempts = ["ajax", "normal"]
    elif mode == "ajax" and fallback:
        attempts = ["ajax", "normal"]

    last_exc = None
    for method in attempts:
        url = "https://store.steampowered.com/search/" if method == "normal" else "https://store.steampowered.com/search/results/"
        try:
            response = session.get(url, params=params, headers=_steam_headers("https://store.steampowered.com/search/"), timeout=25)
            meta("last_fetch_method", "通常検索" if method == "normal" else "Ajax検索")
            meta("last_fetch_http", response.status_code)
            if response.status_code == 403 and method == "ajax" and "normal" in attempts:
                continue
            response.raise_for_status()
            return response, method
        except requests.RequestException as exc:
            last_exc = exc
            if method == "ajax" and "normal" in attempts:
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("Steam search request failed")


def _search_rows_from_response(response):
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("a.search_result_row")


def local_zone():
    try:
        return ZoneInfo(os.getenv("TZ", "Asia/Tokyo"))
    except ZoneInfoNotFoundError:
        return timezone.utc


def local_today() -> date:
    return datetime.now(local_zone()).date()


def format_scan_time(value: str | None) -> str:
    if not value:
        return "未実行"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(local_zone()).strftime("%Y-%m-%d %H:%M:%S JST")
    except (ValueError, TypeError):
        return value


def normalize_recipient(email: str, delivery_end_date: str | None):
    email = email.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(400, "メールアドレスの形式が正しくありません。")
    end = (delivery_end_date or "").strip() or None
    if end:
        try:
            date.fromisoformat(end)
        except ValueError:
            raise HTTPException(400, "配信終了日はYYYY-MM-DD形式で指定してください。")
    return email, end


def expire_recipients() -> int:
    today = local_today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    with conn() as c:
        cur = c.execute(
            """UPDATE mail_recipients SET stopped=1,updated_at=?
            WHERE stopped=0 AND delivery_end_date IS NOT NULL AND delivery_end_date < ?""",
            (now, today),
        )
        c.commit()
        return cur.rowcount


def seed_initial_recipient():
    with conn() as c:
        seeded = c.execute("SELECT v FROM meta WHERE k='mail_recipients_seeded'").fetchone()
        if seeded:
            return
        now = datetime.now(timezone.utc).isoformat()
        raw = os.getenv("MAIL_TO", "")
        for email in re.split(r"[,;]", raw):
            email = email.strip()
            if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                c.execute(
                    """INSERT OR IGNORE INTO mail_recipients(email,delivery_end_date,stopped,created_at,updated_at)
                    VALUES(?,NULL,0,?,?)""",
                    (email, now, now),
                )
        c.execute("INSERT INTO meta(k,v) VALUES('mail_recipients_seeded','1')")
        c.commit()


def recipient_rows():
    expire_recipients()
    with conn() as c:
        return [dict(x) for x in c.execute("SELECT * FROM mail_recipients ORDER BY stopped,email COLLATE NOCASE")]


def active_recipient_emails():
    expire_recipients()
    with conn() as c:
        return [x["email"] for x in c.execute("SELECT email FROM mail_recipients WHERE stopped=0 ORDER BY email COLLATE NOCASE")]


def _discount_from_search_row(row) -> int | None:
    """Extract the discount percent from a Steam search result row.

    Steam has changed the search-result markup several times.  Do not depend
    on a single CSS class: try the current discount_pct element, older markup,
    the discount block, then finally the visible text of the whole row.
    """
    selectors = (
        ".discount_pct",
        ".search_discount span",
        ".search_discount",
        ".discount_block",
        ".search_price_discount_combined",
    )
    texts: list[str] = []
    for selector in selectors:
        node = row.select_one(selector)
        if node:
            texts.append(node.get_text(" ", strip=True))
    texts.append(row.get_text(" ", strip=True))

    values: list[int] = []
    for text in texts:
        for match in re.finditer(r"-\s*(\d{1,3})\s*%", text):
            value = int(match.group(1))
            if 0 <= value <= 100:
                values.append(value)
    return max(values) if values else None


def discover():
    """Discover Steam sale candidates using configurable request strategy."""
    found: dict[int, str] = {}
    start = 0
    scanned_rows = 0
    parsed_discount_rows = 0
    max_discount_seen = 0
    session = _steam_session()
    seen_first_appids: set[int] = set()
    for _ in range(MAX_SEARCH_PAGES):
        params = {
            "query": "",
            "start": start,
            "count": 100,
            "dynamic_data": "",
            "sort_by": "Discount_DESC",
            "specials": "1",
            "hidef2p": "1",
            "ignore_preferences": "1",
            "cc": COUNTRY,
            "l": LANG,
        }
        response, method = _fetch_search_response(session, params)
        rows = _search_rows_from_response(response)
        if not rows:
            break
        # Guard against a normal-search endpoint ignoring start and returning page 1 forever.
        first_ids = []
        for row in rows[:5]:
            raw = row.get("data-ds-appid") or ""
            m = re.search(r"\d+", raw)
            if m:
                first_ids.append(int(m.group()))
        if start and first_ids and all(x in seen_first_appids for x in first_ids):
            break
        seen_first_appids.update(first_ids)
        scanned_rows += len(rows)
        for row in rows:
            appid_raw = row.get("data-ds-appid") or ""
            discount = _discount_from_search_row(row)
            if discount is not None:
                parsed_discount_rows += 1
                max_discount_seen = max(max_discount_seen, discount)
            if not appid_raw or discount is None or discount < MIN_DISCOUNT:
                continue
            m = re.search(r"\d+", appid_raw)
            if m:
                found[int(m.group())] = row.get("href", "")
        if len(rows) < 20:
            break
        start += len(rows)
    return found, scanned_rows, parsed_discount_rows, max_discount_seen


def _extract_discount_expiration_from_html(html: str, now_ts: int | None = None) -> int | None:
    """Return the earliest future Steam discount countdown timestamp found in a store page.

    Steam store pages render sale countdowns by calling InitDailyDealTimer(..., unix_timestamp).
    A page can contain the base app plus bundles/packages, so using the earliest future
    timestamp is intentionally conservative.
    """
    if now_ts is None:
        now_ts = int(datetime.now(timezone.utc).timestamp())
    values = []
    for match in re.finditer(r"InitDailyDealTimer\s*\([^,]+,\s*(\d{9,12})\s*\)", html, re.IGNORECASE):
        value = int(match.group(1))
        if value >= now_ts - 60:
            values.append(value)
    return min(values) if values else None


def fetch_discount_expiration(appid: int) -> int | None:
    """Fetch the Steam store page and extract the sale-end countdown timestamp.

    Failure to obtain an end time must not discard an otherwise valid discount.
    """
    try:
        r = requests.get(
            f"https://store.steampowered.com/app/{appid}/",
            params={"cc": COUNTRY, "l": LANG},
            headers=_steam_headers(f"https://store.steampowered.com/app/{appid}/"),
            cookies={
                "birthtime": "315532800",
                "lastagecheckage": "1-January-1980",
                "wants_mature_content": "1",
            },
            timeout=20,
        )
        r.raise_for_status()
        return _extract_discount_expiration_from_html(r.text)
    except Exception:
        return None


def _product_type(data: dict) -> str:
    raw = str(data.get("type") or "").strip().lower()
    if raw == "game":
        return "game"
    if raw == "dlc":
        return "dlc"
    return "other"


def _genre_info(data: dict) -> tuple[str, str]:
    raw_genres = data.get("genres") or []
    keys: set[str] = set()
    names: list[str] = []
    for genre in raw_genres:
        gid = str(genre.get("id", ""))
        description = (genre.get("description") or "").strip()
        if description and description not in names:
            names.append(description)
        mapped = GENRE_ID_TO_KEY.get(gid)
        if mapped:
            keys.add(mapped)
    if not keys:
        keys.add("other")
    return ",".join(sorted(keys)), ", ".join(names)


def verify(appid: int, url: str):
    r = requests.get(
        "https://store.steampowered.com/api/appdetails",
        params={"appids": appid, "cc": COUNTRY, "l": LANG},
        headers=_steam_headers("https://store.steampowered.com/search/"),
        timeout=20,
    )
    r.raise_for_status()
    item = r.json().get(str(appid), {})
    data = item.get("data") if item.get("success") else None
    if not data or data.get("is_free"):
        return None
    p = data.get("price_overview") or {}
    discount = int(p.get("discount_percent") or 0)
    initial = int(p.get("initial") or 0)
    final = int(p.get("final") or 0)
    if discount < MIN_DISCOUNT or initial <= 0:
        return None

    supported = data.get("supported_languages") or ""
    japanese_supported = bool(re.search(r"\bJapanese\b|日本語", supported, re.IGNORECASE))
    english_supported = bool(re.search(r"\bEnglish\b|英語", supported, re.IGNORECASE))
    genre_keys, genre_names = _genre_info(data)
    return {
        "appid": appid,
        "title": data.get("name", f"App {appid}"),
        "url": url or f"https://store.steampowered.com/app/{appid}/",
        "original_price": p.get("initial_formatted", ""),
        "current_price": p.get("final_formatted", "無料" if final == 0 else ""),
        "current_price_value": final,
        "discount_percent": discount,
        "japanese_supported": 1 if japanese_supported else 0,
        "english_supported": 1 if english_supported else 0,
        "genre_keys": genre_keys,
        "genre_names": genre_names,
        "header_image": data.get("header_image") or "",
        "product_type": _product_type(data),
        "discount_end_ts": fetch_discount_expiration(appid),
    }


def send_mail(subject, body):
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASSWORD")
    frm = os.getenv("MAIL_FROM") or user
    recipients = active_recipient_emails()
    if not all([host, frm]):
        return False, "SMTP settings incomplete"
    if not recipients:
        return False, "No active recipients"
    port = int(os.getenv("SMTP_PORT", "587"))
    use_ssl = os.getenv("SMTP_SSL", "false").lower() == "true"
    tls = os.getenv("SMTP_STARTTLS", "true").lower() == "true"
    cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with cls(host, port, timeout=20) as s:
        if tls and not use_ssl:
            s.starttls(context=ssl.create_default_context())
        if user:
            s.login(user, pw or "")
        for recipient in recipients:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = frm
            msg["To"] = recipient
            msg.set_content(body)
            s.send_message(msg)
    return True, f"sent to {len(recipients)} recipient(s)"


def discount_end_view(value: int | None) -> dict:
    if not value:
        return {"end_display": "日時未定", "remaining_display": "", "end_level": "unknown", "expired": False}
    now_ts = int(datetime.now(timezone.utc).timestamp())
    dt = datetime.fromtimestamp(int(value), timezone.utc).astimezone(local_zone())
    end_display = f"{dt.month}/{dt.day} {dt.strftime('%H:%M')} JST"
    seconds = int(value) - now_ts
    if seconds <= 0:
        return {"end_display": end_display, "remaining_display": "終了", "end_level": "expired", "expired": True}
    days, rem = divmod(seconds, 86400)
    hours = rem // 3600
    if days:
        remaining = f"残り {days}日{hours}時間"
    else:
        minutes = max(1, (rem % 3600) // 60)
        remaining = f"残り {hours}時間{minutes}分"
    if seconds <= 86400:
        level = "urgent"
    elif seconds <= 3 * 86400:
        level = "soon"
    else:
        level = "normal"
    return {"end_display": end_display, "remaining_display": remaining, "end_level": level, "expired": False}


def format_mail(rows, heading="Steam 期間限定無料作品"):
    lines = [heading, ""]
    if not rows:
        return heading + "\n\n現在検出中の Free to Keep はありません。"
    for r in rows:
        lines += [
            r["title"],
            f"通常価格: {r['original_price'] or '-'}",
            "現在価格: 無料（100% OFF / 永久取得候補）",
            "日本語: " + ("対応" if r.get("japanese_supported") else "非対応/未確認"),
            "種別: " + ("DLC" if r.get("product_type") == "dlc" else "ゲーム本体" if r.get("product_type") == "game" else "その他"),
            "割引終了: " + discount_end_view(r.get("discount_end_ts"))["end_display"],
            r["url"],
            "",
        ]
    lines += ["※ メール配信は従来どおり100% OFF（無料）の作品だけを対象にしています。"]
    return "\n".join(lines)


def _scan_impl(send_new=True):
    now = datetime.now(timezone.utc).isoformat()
    candidates, scanned_rows, parsed_discount_rows, max_discount_seen = discover()
    verified = []
    errors = 0
    for appid, url in candidates.items():
        try:
            x = verify(appid, url)
            if x:
                verified.append(x)
        except Exception:
            errors += 1

    new_free = []
    with conn() as c:
        c.execute("UPDATE promotions SET active=0")
        for x in verified:
            old = c.execute("SELECT * FROM promotions WHERE appid=?", (x["appid"],)).fetchone()
            c.execute(
                """INSERT INTO promotions(
                    appid,title,url,original_price,current_price,current_price_value,
                    discount_percent,japanese_supported,english_supported,genre_keys,genre_names,header_image,
                    product_type,discount_end_ts,first_seen,last_seen,active,notified
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)
                ON CONFLICT(appid) DO UPDATE SET
                    title=excluded.title,
                    url=excluded.url,
                    original_price=excluded.original_price,
                    current_price=excluded.current_price,
                    current_price_value=excluded.current_price_value,
                    discount_percent=excluded.discount_percent,
                    japanese_supported=excluded.japanese_supported,
                    english_supported=excluded.english_supported,
                    genre_keys=excluded.genre_keys,
                    genre_names=excluded.genre_names,
                    header_image=excluded.header_image,
                    product_type=excluded.product_type,
                    discount_end_ts=excluded.discount_end_ts,
                    last_seen=excluded.last_seen,
                    active=1""",
                (
                    x["appid"], x["title"], x["url"], x["original_price"],
                    x["current_price"], x["current_price_value"], x["discount_percent"],
                    x["japanese_supported"], x["english_supported"], x["genre_keys"], x["genre_names"], x["header_image"],
                    x["product_type"], x["discount_end_ts"], now, now, 1,
                ),
            )
            if x["discount_percent"] == 100 and x["current_price_value"] == 0:
                if old is None or not old["notified"]:
                    new_free.append(x)
        c.commit()

    meta("last_scan", now)
    meta("last_count", len(verified))
    meta("last_search_rows", scanned_rows)
    meta("last_discount_parsed", parsed_discount_rows)
    meta("last_max_discount", max_discount_seen)
    meta("last_candidates", len(candidates))
    meta("last_errors", errors)

    if send_new and new_free and os.getenv("SEND_NEW_ITEM_IMMEDIATELY", "true").lower() == "true":
        ok, _ = send_mail(
            f"【Steam無料】新着 {len(new_free)}件",
            format_mail(new_free, "Steam Free to Keep 新着"),
        )
        if ok:
            with conn() as c:
                c.executemany("UPDATE promotions SET notified=1 WHERE appid=?", [(x["appid"],) for x in new_free])
                c.commit()

    return {
        "found": len(verified),
        "free": sum(1 for x in verified if x["discount_percent"] == 100 and x["current_price_value"] == 0),
        "new_free": len(new_free),
        "search_rows": scanned_rows,
        "discount_parsed": parsed_discount_rows,
        "max_discount": max_discount_seen,
        "candidates": len(candidates),
        "errors": errors,
    }


SCAN_LOCK = threading.Lock()
SCAN_START_GUARD = threading.Lock()
SCAN_STATE = {
    "running": False,
    "started_at": None,
    "completed_at": None,
    "error": None,
    "result": None,
}


def scan(send_new=True):
    with SCAN_LOCK:
        started = datetime.now(timezone.utc).isoformat()
        SCAN_STATE.update(running=True, started_at=started, error=None)
        try:
            result = _scan_impl(send_new)
            SCAN_STATE.update(
                running=False,
                completed_at=datetime.now(timezone.utc).isoformat(),
                error=None,
                result=result,
            )
            return result
        except Exception as exc:
            SCAN_STATE.update(
                running=False,
                completed_at=datetime.now(timezone.utc).isoformat(),
                error=f"{type(exc).__name__}: {exc}",
            )
            raise


def start_scan_background(send_new=True):
    with SCAN_START_GUARD:
        if SCAN_LOCK.locked() or SCAN_STATE.get("running"):
            return False
        SCAN_STATE.update(
            running=True,
            started_at=datetime.now(timezone.utc).isoformat(),
            completed_at=None,
            error=None,
            result=None,
        )
        def runner():
            # scan() owns the actual execution lock and final status update.
            try:
                scan(send_new)
            except Exception:
                pass
        threading.Thread(target=runner, name="steamfree-manual-scan", daemon=True).start()
        return True


def daily_mail():
    with conn() as c:
        rows = [
            dict(x)
            for x in c.execute(
                """SELECT * FROM promotions
                   WHERE active=1 AND discount_percent=100 AND COALESCE(current_price_value,0)=0
                     AND (discount_end_ts IS NULL OR discount_end_ts > ?)
                   ORDER BY first_seen DESC""",
                (int(datetime.now(timezone.utc).timestamp()),),
            )
        ]
    if not rows:
        return False, "No active Free to Keep promotions; daily mail skipped"
    return send_mail(f"【Steam無料】本日の期間限定無料 {len(rows)}件", format_mail(rows))


@app.on_event("startup")
def startup():
    conn().close()
    seed_initial_recipient()
    expire_recipients()
    sched = BackgroundScheduler(timezone=os.getenv("TZ", "Asia/Tokyo"))
    sched.add_job(
        scan,
        "cron",
        hour=int(os.getenv("AUTO_SCAN_HOUR", "6")),
        minute=int(os.getenv("AUTO_SCAN_MINUTE", "30")),
        id="scan",
        replace_existing=True,
    )
    sched.add_job(
        daily_mail,
        "cron",
        hour=int(os.getenv("DAILY_MAIL_HOUR", "7")),
        minute=int(os.getenv("DAILY_MAIL_MINUTE", "0")),
        id="daily",
        replace_existing=True,
    )
    sched.start()
    app.state.sched = sched


@app.get("/api/health")
def health():
    recipients = active_recipient_emails()
    return {
        "status": "ok",
        "version": app.version,
        "last_scan": meta("last_scan"),
        "active": int(meta("last_count") or 0),
        "active_recipients": len(recipients),
    }


@app.get("/api/promotions")
def promotions():
    with conn() as c:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        return [dict(x) for x in c.execute(
            "SELECT * FROM promotions WHERE active=1 AND (discount_end_ts IS NULL OR discount_end_ts > ?) ORDER BY discount_percent DESC,title COLLATE NOCASE",
            (now_ts,),
        )]


@app.post("/api/scan", status_code=202)
def api_scan():
    started = start_scan_background(True)
    return {"started": started, **SCAN_STATE}


@app.get("/api/scan/status")
def api_scan_status():
    return dict(SCAN_STATE)


@app.post("/api/test-mail")
def test_mail():
    ok, msg = send_mail("Steam Free Bot テストメール", "Steam Free Bot のメール設定は正常です。")
    return {"ok": ok, "message": msg}


@app.get("/api/recipients")
def api_recipients():
    return recipient_rows()


@app.post("/api/recipients", status_code=201)
def create_recipient(payload: RecipientPayload):
    email, end = normalize_recipient(payload.email, payload.delivery_end_date)
    now = datetime.now(timezone.utc).isoformat()
    try:
        with conn() as c:
            cur = c.execute(
                """INSERT INTO mail_recipients(email,delivery_end_date,stopped,created_at,updated_at)
                VALUES(?,?,0,?,?)""",
                (email, end, now, now),
            )
            c.commit()
            recipient_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "このメールアドレスは登録済みです。")
    expire_recipients()
    with conn() as c:
        return dict(c.execute("SELECT * FROM mail_recipients WHERE id=?", (recipient_id,)).fetchone())


@app.put("/api/recipients/{recipient_id}")
def update_recipient(recipient_id: int, payload: RecipientPayload):
    email, end = normalize_recipient(payload.email, payload.delivery_end_date)
    now = datetime.now(timezone.utc).isoformat()
    try:
        with conn() as c:
            cur = c.execute(
                "UPDATE mail_recipients SET email=?,delivery_end_date=?,updated_at=? WHERE id=?",
                (email, end, now, recipient_id),
            )
            if not cur.rowcount:
                raise HTTPException(404, "配信先が見つかりません。")
            c.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "このメールアドレスは登録済みです。")
    expire_recipients()
    with conn() as c:
        return dict(c.execute("SELECT * FROM mail_recipients WHERE id=?", (recipient_id,)).fetchone())


@app.delete("/api/recipients/{recipient_id}", status_code=204)
def delete_recipient(recipient_id: int):
    with conn() as c:
        cur = c.execute("DELETE FROM mail_recipients WHERE id=?", (recipient_id,))
        c.commit()
    if not cur.rowcount:
        raise HTTPException(404, "配信先が見つかりません。")


@app.post("/api/recipients/{recipient_id}/toggle")
def toggle_recipient(recipient_id: int):
    today = local_today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    with conn() as c:
        row = c.execute("SELECT * FROM mail_recipients WHERE id=?", (recipient_id,)).fetchone()
        if not row:
            raise HTTPException(404, "配信先が見つかりません。")
        if row["stopped"]:
            end = None if row["delivery_end_date"] and row["delivery_end_date"] < today else row["delivery_end_date"]
            c.execute(
                "UPDATE mail_recipients SET stopped=0,delivery_end_date=?,updated_at=? WHERE id=?",
                (end, now, recipient_id),
            )
        else:
            c.execute("UPDATE mail_recipients SET stopped=1,updated_at=? WHERE id=?", (now, recipient_id))
        c.commit()
        return dict(c.execute("SELECT * FROM mail_recipients WHERE id=?", (recipient_id,)).fetchone())


@app.get("/api/ui-defaults")
def api_ui_defaults():
    return ui_defaults_dict()


@app.put("/api/ui-defaults")
def update_ui_defaults(payload: UiDefaultsPayload):
    values = {
        "ui_default_language": payload.language,
        "ui_default_genre": payload.genre,
        "ui_default_discount": payload.discount,
        "ui_default_type": payload.product_type,
        "ui_default_language_support": payload.language_support,
        "ui_default_sort": payload.sort,
        "ui_default_order": payload.order,
    }
    for key, value in values.items():
        meta(key, value)
    return ui_defaults_dict()


@app.get("/api/steam-settings")
def api_steam_settings():
    return steam_settings_dict()


@app.put("/api/steam-settings")
def update_steam_settings(payload: SteamSettingsPayload):
    custom = payload.custom_ua.strip()
    if payload.ua_preset == "custom" and not custom:
        raise HTTPException(400, "カスタムUAを選んだ場合はUser-Agentを入力してください。")
    language = payload.accept_language.strip() or STEAM_SETTING_DEFAULTS["steam_accept_language"]
    values = {
        "steam_fetch_mode": payload.fetch_mode,
        "steam_ua_preset": payload.ua_preset,
        "steam_custom_ua": custom,
        "steam_use_session": "1" if payload.use_session else "0",
        "steam_use_referer": "1" if payload.use_referer else "0",
        "steam_fallback_403": "1" if payload.fallback_403 else "0",
        "steam_accept_language": language,
    }
    for key, value in values.items():
        meta(key, value)
    return steam_settings_dict()


@app.post("/api/steam-settings/test")
def test_steam_settings():
    params = {
        "query": "", "start": 0, "count": 50, "dynamic_data": "",
        "sort_by": "Discount_DESC", "specials": "1", "hidef2p": "1",
        "ignore_preferences": "1", "cc": COUNTRY, "l": LANG,
    }
    try:
        session = _steam_session()
        response, method = _fetch_search_response(session, params)
        rows = _search_rows_from_response(response)
        parsed = sum(1 for row in rows if _discount_from_search_row(row) is not None)
        meta("last_fetch_test_rows", len(rows))
        return {
            "ok": True,
            "method": "通常検索" if method == "normal" else "Ajax検索",
            "http": response.status_code,
            "rows": len(rows),
            "discount_rows": parsed,
        }
    except Exception as exc:
        return {
            "ok": False,
            "method": meta("last_fetch_method") or "-",
            "http": meta("last_fetch_http") or "-",
            "rows": 0,
            "discount_rows": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }


@app.get("/admin/recipients", response_class=HTMLResponse)
def recipients_admin(request: Request):
    return templates.TemplateResponse(
        "recipients.html",
        {"request": request, "rows": recipient_rows(), "today": local_today().isoformat(), "last_scan": format_scan_time(meta("last_scan")), "steam_settings": steam_settings_dict(), "ui_defaults": ui_defaults_dict()},
    )


@app.get("/admin", include_in_schema=False)
def admin_root():
    return RedirectResponse("/admin/recipients", status_code=302)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    with conn() as c:
        raw_rows = [dict(x) for x in c.execute("SELECT * FROM promotions WHERE active=1 ORDER BY discount_percent DESC,title COLLATE NOCASE")]
    rows = []
    for row in raw_rows:
        end = discount_end_view(row.get("discount_end_ts"))
        if end["expired"]:
            continue
        row.update(end)
        row["product_type_label"] = "DLC" if row.get("product_type") == "dlc" else "Game" if row.get("product_type") == "game" else "Other"
        rows.append(row)
    for row in rows:
        row["genre_key_list"] = [x for x in (row.get("genre_keys") or "").split(",") if x]
    diagnostics = {
        "search_rows": int(meta("last_search_rows") or 0),
        "discount_parsed": int(meta("last_discount_parsed") or 0),
        "max_discount": int(meta("last_max_discount") or 0),
        "candidates": int(meta("last_candidates") or 0),
        "verified": int(meta("last_count") or 0),
        "errors": int(meta("last_errors") or 0),
        "fetch_method": meta("last_fetch_method") or "-",
        "fetch_http": meta("last_fetch_http") or "-",
    }
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rows": rows,
            "last_scan": format_scan_time(meta("last_scan")),
            "genre_tabs": [(key, GENRE_LABELS[key]) for key in GENRE_TAB_ORDER],
            "diagnostics": diagnostics,
            "min_discount": MIN_DISCOUNT,
            "ui_defaults": ui_defaults_dict(),
        },
    )
