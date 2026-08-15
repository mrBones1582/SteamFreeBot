# Security Policy

## English

Do not include credentials, email addresses, Session Cookies, environment-variable values, private deployment details, databases, or logs in public issues and pull requests.

This public repository intentionally excludes production configuration, NAS deployment scripts, private keys, passwords, databases, and logs.

## 日本語

公開IssueやPull Requestには、認証情報、メールアドレス、Session Cookie、環境変数の値、非公開のデプロイ情報、データベース、ログを含めないでください。

この公開リポジトリには、本番環境の設定、NASデプロイスクリプト、秘密鍵、パスワード、データベース、ログを含めていません。

## Default network exposure / 既定のネットワーク公開範囲

The supplied Docker Compose file binds the application to `127.0.0.1:8000` by default. The administration APIs are not authenticated, so do not change that bind to a LAN/public address without adding access control.

付属のDocker Composeは既定で `127.0.0.1:8000` のみにバインドします。管理APIには認証がないため、アクセス制御を追加せずLAN向け・外部向けアドレスへ変更しないでください。