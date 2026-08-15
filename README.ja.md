# SteamFreeBot

[English](README.md) | 日本語

Steam Storeのセール情報を収集し、80%以上OFFの作品をWeb画面で検索・絞り込みできるFastAPIアプリです。100% OFFかつ現在価格0円の作品はメール通知できます。

## 主な機能

- Steam Storeのセール作品を定期取得
- 英語/日本語の表示切替（初期値は英語）
- 割引率、価格、英語または日本語対応、ジャンル、ゲーム本体/DLCで絞り込み
- 一覧表示とカード表示
- 期間限定無料作品のメール通知
- 配信先メールアドレスの登録・変更・削除
- 配信終了日と配信停止フラグの管理
- Steam取得方式、User-Agent、Session Cookieなどの管理設定
- SQLiteによるデータ保存

## Dockerで起動

1. リポジトリをクローンします。
2. `.env.example` を `.env` にコピーします。
3. 必要に応じてSMTP設定を入力します。
4. 次のコマンドを実行します。

```bash
docker compose up -d --build
```

起動後、`http://localhost:8000` を開きます。

配信先管理画面は `http://localhost:8000/admin/recipients` です。

## Gmailを利用する場合

通常のGoogleアカウントパスワードではなく、Googleが発行するアプリパスワードを `SMTP_PASSWORD` に設定してください。秘密情報を `.env` 以外へ書かないでください。

## テスト

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## セキュリティ

この公開版には利用者認証を組み込んでいません。付属のDocker Composeは既定で127.0.0.1:8000のみにバインドするため、他のLAN端末からも直接アクセスできません。LANやインターネットへ意図的に公開する場合は、先に認証付きリバースプロキシ、VPN、アクセス制御などを追加してください。

次のデータはGitへ追加しないでください。

- `.env`
- SQLiteデータベース
- SMTPパスワード
- Steam Session Cookie
- ログやバックアップ

## 注意事項

- SteamのHTMLやAPI仕様変更により取得できなくなる場合があります。
- SteamおよびValve Corporationの公式プロジェクトではありません。
- 各サービスの利用規約、レート制限、メール送信事業者の規約を確認して利用してください。

## コントリビューション

IssueやPull Requestを歓迎します。秘密情報や個人情報を含めないよう確認してから投稿してください。

## ライセンス

ライセンスはまだ指定していません。利用・改変・再配布条件を明確にするため、公開者が適切なOSSライセンスを選択してください。
