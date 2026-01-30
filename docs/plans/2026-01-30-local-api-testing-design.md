# ローカルAPI動作確認環境 設計書

## 概要

`sam local start-api`を使用してローカルでAPIサーバーを起動し、curlでLINE Webhookをシミュレートしてテストできる環境を構築する。

## 要件

- ローカルでAPIエンドポイントを起動
- テスト用S3バケット（`bossagyu-lambda-line-clean-bot-test`）に接続
- LINE API呼び出しはスキップし、ログ出力のみ

## 構成

### 新規ファイル

| ファイル | 内容 |
|----------|------|
| `env.json` | ローカル実行用環境変数 |
| `events/line_message.json` | テスト用Webhookイベント |

### 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `lib/line.py` | DRY_RUN環境変数対応 |
| `Makefile` | local-api, local-invokeコマンド追加 |
| `CLAUDE.md` | ローカル実行手順追加 |

## 環境変数

| 変数名 | ローカル値 | 本番値 |
|--------|-----------|--------|
| `BUCKET_NAME` | bossagyu-lambda-line-clean-bot-test | bossagyu-lambda-line-clean-bot |
| `CHANNEL_ACCESS_TOKEN` | dummy-token | 実際のトークン |
| `DRY_RUN` | true | 未設定 |

## 使用方法

```bash
# ローカルAPIサーバー起動
make local-api

# 別ターミナルでテスト
curl -X POST http://localhost:3000/process_user_message \
  -H "Content-Type: application/json" \
  -d @events/line_message.json
```

## 前提条件

- Docker インストール済み
- AWS認証情報設定済み
