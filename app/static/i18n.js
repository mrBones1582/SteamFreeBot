(() => {
  const messages = {
    en: {
      language: "Language",
      description: "Collects Steam Store titles at {discount}% off or more and verifies price, language support, genre, type, and sale end time.",
      last_checked: "Last checked:", never: "Never", check_now: "Check now", check: "Check",
      change_filters: "Filters", close_filters: "Close filters", showing: "Showing", items: "items",
      scan_info: "Scan details", search: "Search", parsed_discounts: "discounts parsed", maximum: "max", candidates: "candidates", verified: "verified", errors: "errors", fetch: "Fetch", list: "List", card: "Cards", view_format: "View format",
      filter_area: "Filters and sorting", reset_filters: "Reset filters",
      discount: "Discount", discount_all: "80% off or more", discount_90: "90% off or more", free_only: "Free only",
      type: "Type", any: "Any", games_only: "Games only", dlc_only: "DLC only",
      language_support: "Language support", english_only: "English only", japanese_only: "Japanese only",
      sort: "Sort by", discount_rate: "Discount rate", name: "Name", current_price: "Current price",
      order: "Order", descending: "Descending", ascending: "Ascending",
      genre_all: "All", genre_rpg: "RPG", genre_slg: "SLG", genre_action: "Action",
      genre_adventure: "Adventure", genre_casual: "Casual", genre_sports: "Sports",
      genre_racing: "Racing", genre_other: "Other", game: "Game", other: "Other",
      english: "English", no_english: "No English", japanese: "Japanese", no_japanese: "No Japanese",
      free: "Free", end: "Ends", date_unknown: "Date TBD", ended: "Ended",
      remaining: "Remaining", day: "day", days: "days", hour: "hour", hours: "hours", minute: "minute", minutes: "minutes",
      open_steam: "Open {title} on Steam", no_results: "No titles match the current filters.",
      recipient_admin: "Recipient administration", scanning: "Scanning…", scan_failed: "Steam scan failed.",
      back_to_games: "← Back to games", recipient_title: "Email recipient administration",
      recipient_description: "Delivery stops automatically the day after the end date. Resuming an expired recipient clears the old end date.",
      new_recipient: "New recipient", email_address: "Email address", delivery_end_optional: "Delivery end date (optional)", register: "Add",
      steam_settings: "Steam fetch settings",
      steam_settings_help: "Configure the fetch method and browser-like headers used to handle HTTP 403 responses. Auto (Ajax → normal search) with a Chrome-like User-Agent is recommended.",
      fetch_mode: "Fetch mode", fetch_auto: "Auto (Ajax → normal search)", fetch_ajax: "Prefer Ajax", fetch_normal: "Normal search only",
      chrome_recommended: "Chrome-like (recommended)", firefox: "Firefox-like", custom: "Custom", custom_user_agent: "Custom User-Agent",
      custom_user_agent_placeholder: "Used only when Custom is selected", use_session: "Use Session Cookie", add_referer: "Send Referer",
      fallback_403: "Fall back to normal search on HTTP 403", save_settings: "Save settings", steam_connection_test: "Test Steam connection",
      last: "Last", settings_saved: "Steam fetch settings saved.", testing: "Testing…", connecting: "Checking connection…",
      success: "Success", failure: "Failed", registered_recipients: "Registered recipients",
      delivery_end: "Delivery end date", active: "Active", stopped: "Stopped", edit: "Save", resume: "Resume", stop: "Stop", delete: "Delete",
      no_recipients: "No recipients are registered.", operation_failed: "The operation failed.", delete_confirm: "Delete this recipient?"
    },
    ja: {
      language: "言語",
      description: "Steam Storeで{discount}%以上OFFの作品を収集し、価格・言語対応・ジャンル・種別・割引終了日時を再確認して表示します。",
      last_checked: "最終確認:", never: "未実行", check_now: "今すぐ確認", check: "確認",
      change_filters: "条件変更", close_filters: "条件を閉じる", showing: "表示", items: "件",
      scan_info: "スキャン情報", search: "検索", parsed_discounts: "割引率解析", maximum: "最大", candidates: "候補", verified: "確定", errors: "エラー", fetch: "取得", list: "一覧", card: "カード", view_format: "表示形式",
      filter_area: "絞り込みと並び替え", reset_filters: "条件をリセット",
      discount: "割引", discount_all: "80%以上すべて", discount_90: "90%以上", free_only: "無料のみ",
      type: "種別", any: "不問", games_only: "ゲーム本体のみ", dlc_only: "DLCのみ",
      language_support: "言語対応", english_only: "英語のみ", japanese_only: "日本語のみ",
      sort: "ソート", discount_rate: "割引率", name: "名前", current_price: "現在価格",
      order: "順序", descending: "降順", ascending: "昇順",
      genre_all: "すべて", genre_rpg: "RPG", genre_slg: "SLG", genre_action: "アクション",
      genre_adventure: "アドベンチャー", genre_casual: "カジュアル", genre_sports: "スポーツ",
      genre_racing: "レース", genre_other: "その他", game: "ゲーム本体", other: "その他",
      english: "英語", no_english: "英語なし", japanese: "日本語", no_japanese: "日本語なし",
      free: "無料", end: "終了", date_unknown: "日時未定", ended: "終了",
      remaining: "残り", day: "日", days: "日", hour: "時間", hours: "時間", minute: "分", minutes: "分",
      open_steam: "{title}をSteamで開く", no_results: "現在の条件に一致する作品はありません。",
      recipient_admin: "配信先管理", scanning: "確認中…", scan_failed: "Steamの確認に失敗しました。",
      back_to_games: "← ゲーム一覧に戻る", recipient_title: "メール配信先管理",
      recipient_description: "配信終了日の翌日から自動的に停止します。期限切れの配信先を再開すると、古い終了日はクリアされます。",
      new_recipient: "新しい配信先", email_address: "メールアドレス", delivery_end_optional: "配信終了日（任意）", register: "登録",
      steam_settings: "Steam取得設定",
      steam_settings_help: "403対策用の取得方法とブラウザ相当ヘッダを設定します。通常は「自動（Ajax→通常検索）」＋「Chrome相当」を推奨します。",
      fetch_mode: "取得モード", fetch_auto: "自動（Ajax→通常検索）", fetch_ajax: "Ajax優先", fetch_normal: "通常検索のみ",
      chrome_recommended: "Chrome相当（推奨）", firefox: "Firefox相当", custom: "カスタム", custom_user_agent: "カスタムUser-Agent",
      custom_user_agent_placeholder: "カスタムを選んだ場合のみ使用", use_session: "Session Cookieを利用", add_referer: "Refererを付与",
      fallback_403: "403時に通常検索へフォールバック", save_settings: "設定を保存", steam_connection_test: "Steam接続テスト",
      last: "最終", settings_saved: "Steam取得設定を保存しました。", testing: "テスト中…", connecting: "接続確認中…",
      success: "成功", failure: "失敗", registered_recipients: "登録済み配信先",
      delivery_end: "配信終了日", active: "配信中", stopped: "停止中", edit: "変更", resume: "停止解除", stop: "配信停止", delete: "削除",
      no_recipients: "配信先は登録されていません。", operation_failed: "操作に失敗しました。", delete_confirm: "この配信先を削除しますか？"
    }
  };

  const interpolate = (text, values = {}) => text.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? `{${key}}`);
  const t = (key, values) => interpolate((messages[currentLanguage] || messages.en)[key] || messages.en[key] || key, values);
  let currentLanguage = localStorage.getItem("steamfree-language") === "ja" ? "ja" : "en";

  function applyLanguage(language) {
    currentLanguage = language === "ja" ? "ja" : "en";
    localStorage.setItem("steamfree-language", currentLanguage);
    document.documentElement.lang = currentLanguage;
    document.querySelectorAll("[data-i18n]").forEach((element) => {
      element.textContent = t(element.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
      element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
      element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
    });
    document.querySelectorAll("[data-i18n-title]").forEach((element) => {
      element.setAttribute("title", t(element.dataset.i18nTitle));
    });
    document.querySelectorAll(".ui-language").forEach((select) => { select.value = currentLanguage; });
    document.dispatchEvent(new CustomEvent("steamfree:languagechange", { detail: { language: currentLanguage } }));
  }

  window.SteamFreeI18n = { applyLanguage, get language() { return currentLanguage; }, t };
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".ui-language").forEach((select) => {
      select.addEventListener("change", () => applyLanguage(select.value));
    });
    applyLanguage(currentLanguage);
  });
})();
