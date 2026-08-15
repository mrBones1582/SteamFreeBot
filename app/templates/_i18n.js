(() => {
  const messages = {
    en: {
      language:"Language", description:"Collects Steam Store titles at {discount}% off or more and verifies price, language support, genre, type, and sale end time.", last_checked:"Last checked:", never:"Never", check_now:"Check now", check:"Check", change_filters:"Filters", close_filters:"Close filters", showing:"Showing", items:"items", scan_info:"Scan details", list:"List", card:"Cards", view_format:"View format",
      filter_area:"Filters and sorting", reset_filters:"Reset filters", discount:"Discount", discount_all:"80% off or more", discount_90:"90% off or more", free_only:"Free only", type:"Type", any:"Any", games_only:"Games only", dlc_only:"DLC only", language_support:"Language support", english_only:"English only", japanese_only:"Japanese only", sort:"Sort by", discount_rate:"Discount rate", name:"Name", current_price:"Current price", order:"Order", descending:"Descending", ascending:"Ascending",
      genre_all:"All", genre_rpg:"RPG", genre_slg:"SLG", genre_action:"Action", genre_adventure:"Adventure", genre_casual:"Casual", genre_sports:"Sports", genre_racing:"Racing", genre_other:"Other", game:"Game", dlc:"DLC", other:"Other", english:"English", japanese:"Japanese", free:"Free", end:"Ends", date_unknown:"Date TBD", remaining:"Remaining", no_results:"No titles match the current filters.", recipient_admin:"Recipient administration", scanning:"Scanning…", scan_failed:"Steam scan failed.",
      back_to_games:"← Back to games", recipient_title:"Email recipient administration", recipient_description:"Delivery stops automatically the day after the end date. Resuming an expired recipient clears the old end date.", new_recipient:"New recipient", email_address:"Email address", delivery_end_optional:"Delivery end date (optional)", register:"Add", registered_recipients:"Registered recipients", delivery_end:"Delivery end date", active:"Active", stopped:"Stopped", edit:"Save", resume:"Resume", stop:"Stop", delete:"Delete", no_recipients:"No recipients are registered.", operation_failed:"The operation failed.", delete_confirm:"Delete this recipient?",
      steam_settings:"Steam fetch settings", steam_settings_help:"Configure the fetch method and browser-like headers used to handle HTTP 403 responses. Auto (Ajax → normal search) with a Chrome-like User-Agent is recommended.", fetch_mode:"Fetch mode", fetch_auto:"Auto (Ajax → normal search)", fetch_ajax:"Prefer Ajax", fetch_normal:"Normal search only", chrome_recommended:"Chrome-like (recommended)", firefox:"Firefox-like", custom:"Custom", custom_user_agent:"Custom User-Agent", custom_user_agent_placeholder:"Used only when Custom is selected", use_session:"Use Session Cookie", add_referer:"Send Referer", fallback_403:"Fall back to normal search on HTTP 403", save_settings:"Save settings", steam_connection_test:"Test Steam connection", last:"Last", settings_saved:"Steam fetch settings saved.", testing:"Testing…", connecting:"Checking connection…", success:"Success", failure:"Failed",
      ui_defaults:"Default display & filter settings", ui_defaults_help:"These values are used for a new browser session and by Reset filters. A browser that has already selected another display language may keep its local preference until it is changed again.", default_display_language:"Default display language", default_genre:"Default genre", default_discount:"Default discount", default_type:"Default type", default_language_support:"Default language support", default_sort:"Default sort", default_order:"Default order", save_defaults:"Save defaults", defaults_saved:"Default display and filter settings saved."
    },
    ja: {
      language:"言語", description:"Steam Storeで{discount}%以上OFFの作品を収集し、価格・言語対応・ジャンル・種別・割引終了日時を再確認して表示します。", last_checked:"最終確認:", never:"未実行", check_now:"今すぐ確認", check:"確認", change_filters:"条件変更", close_filters:"条件を閉じる", showing:"表示", items:"件", scan_info:"スキャン情報", list:"一覧", card:"カード", view_format:"表示形式",
      filter_area:"絞り込みと並び替え", reset_filters:"条件をリセット", discount:"割引", discount_all:"80%以上すべて", discount_90:"90%以上", free_only:"無料のみ", type:"種別", any:"不問", games_only:"ゲーム本体のみ", dlc_only:"DLCのみ", language_support:"言語対応", english_only:"英語のみ", japanese_only:"日本語のみ", sort:"ソート", discount_rate:"割引率", name:"名前", current_price:"現在価格", order:"順序", descending:"降順", ascending:"昇順",
      genre_all:"すべて", genre_rpg:"RPG", genre_slg:"SLG", genre_action:"アクション", genre_adventure:"アドベンチャー", genre_casual:"カジュアル", genre_sports:"スポーツ", genre_racing:"レース", genre_other:"その他", game:"ゲーム本体", dlc:"DLC", other:"その他", english:"英語", japanese:"日本語", free:"無料", end:"終了", date_unknown:"日時未定", remaining:"残り", no_results:"現在の条件に一致する作品はありません。", recipient_admin:"配信先管理", scanning:"確認中…", scan_failed:"Steamの確認に失敗しました。",
      back_to_games:"← ゲーム一覧に戻る", recipient_title:"メール配信先管理", recipient_description:"配信終了日の翌日から自動的に停止します。期限切れの配信先を再開すると、古い終了日はクリアされます。", new_recipient:"新しい配信先", email_address:"メールアドレス", delivery_end_optional:"配信終了日（任意）", register:"登録", registered_recipients:"登録済み配信先", delivery_end:"配信終了日", active:"配信中", stopped:"停止中", edit:"変更", resume:"停止解除", stop:"配信停止", delete:"削除", no_recipients:"配信先は登録されていません。", operation_failed:"操作に失敗しました。", delete_confirm:"この配信先を削除しますか？",
      steam_settings:"Steam取得設定", steam_settings_help:"403対策用の取得方法とブラウザ相当ヘッダを設定します。通常は「自動（Ajax→通常検索）」＋「Chrome相当」を推奨します。", fetch_mode:"取得モード", fetch_auto:"自動（Ajax→通常検索）", fetch_ajax:"Ajax優先", fetch_normal:"通常検索のみ", chrome_recommended:"Chrome相当（推奨）", firefox:"Firefox相当", custom:"カスタム", custom_user_agent:"カスタムUser-Agent", custom_user_agent_placeholder:"カスタムを選んだ場合のみ使用", use_session:"Session Cookieを利用", add_referer:"Refererを付与", fallback_403:"403時に通常検索へフォールバック", save_settings:"設定を保存", steam_connection_test:"Steam接続テスト", last:"最終", settings_saved:"Steam取得設定を保存しました。", testing:"テスト中…", connecting:"接続確認中…", success:"成功", failure:"失敗",
      ui_defaults:"表示・検索条件の初期値", ui_defaults_help:"新しいブラウザで開いた時の初期値と「条件をリセット」の戻り先を設定します。すでに表示言語を変更済みのブラウザでは、その端末の選択が優先されます。", default_display_language:"表示言語の初期値", default_genre:"ジャンルの初期値", default_discount:"割引の初期値", default_type:"種別の初期値", default_language_support:"言語対応の初期値", default_sort:"ソートの初期値", default_order:"順序の初期値", save_defaults:"初期値を保存", defaults_saved:"表示・検索条件の初期値を保存しました。"
    }
  };
  let currentLanguage='en';
  const interpolate=(text,values={})=>text.replace(/\{(\w+)\}/g,(_,key)=>values[key]??`{${key}}`);
  const t=(key,values)=>interpolate((messages[currentLanguage]||messages.en)[key]||messages.en[key]||key,values);
  function serverDefault(){const v=document.documentElement.dataset.defaultLanguage||document.body?.dataset.defaultLanguage;return v==='ja'?'ja':'en'}
  function safeStorageGet(key){try{return window.localStorage?localStorage.getItem(key):null}catch(_){return null}}
  function safeStorageSet(key,value){try{if(window.localStorage)localStorage.setItem(key,value)}catch(_){/* Display switching must not depend on storage availability. */}}
  function applyLanguage(language,persist=true){
    currentLanguage=language==='ja'?'ja':'en';
    document.documentElement.lang=currentLanguage;
    document.querySelectorAll('[data-i18n]').forEach(el=>{const values={discount:el.dataset.discount};el.textContent=t(el.dataset.i18n,values)});
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>el.setAttribute('placeholder',t(el.dataset.i18nPlaceholder)));
    document.querySelectorAll('[data-i18n-aria-label]').forEach(el=>el.setAttribute('aria-label',t(el.dataset.i18nAriaLabel)));
    document.querySelectorAll('[data-i18n-title]').forEach(el=>el.setAttribute('title',t(el.dataset.i18nTitle)));
    document.querySelectorAll('.ui-language').forEach(s=>s.value=currentLanguage);
    if(persist)safeStorageSet('steamfree-language',currentLanguage);
    document.dispatchEvent(new CustomEvent('steamfree:languagechange',{detail:{language:currentLanguage}}));
  }
  function initializeLanguage(){
    const saved=safeStorageGet('steamfree-language');
    currentLanguage=saved==='ja'||saved==='en'?saved:serverDefault();
    applyLanguage(currentLanguage,false);
  }
  window.SteamFreeI18n={applyLanguage,get language(){return currentLanguage},t,serverDefault};

  // Use delegated handlers as well as direct handlers. This keeps language
  // switching reliable even if a template re-renders/replaces the select.
  document.addEventListener('change',event=>{
    const select=event.target.closest?.('.ui-language');
    if(select) applyLanguage(select.value,true);
  });
  document.addEventListener('input',event=>{
    const select=event.target.closest?.('.ui-language');
    if(select) applyLanguage(select.value,true);
  });
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',initializeLanguage,{once:true});
  else initializeLanguage();
})();
