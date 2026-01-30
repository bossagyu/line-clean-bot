# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

定期的な掃除タスクを管理するLINE Bot。ユーザーはLINEメッセージを通じて家事を追加・完了・確認できます。タスクには「duration（日数）」があり、その期間が経過すると再度実行すべきタスクとして表示されます。

## コマンド

### 開発

```bash
# 依存関係のインストール（uv使用）
uv sync

# テスト実行（プロジェクトルートから）
uv run pytest test/
# または
make test

# 特定のテストファイルを実行
uv run pytest test/lib/s3_client_test.py

# 特定のテストケースを実行
uv run pytest test/lib/s3_client_test.py::test_get_object_body
```

### デプロイ（Makefile使用）

```bash
# ビルド
make build

# デプロイ（CHANNEL_ACCESS_TOKENが必要）
CHANNEL_ACCESS_TOKEN=your_token make deploy

# 確認なしでデプロイ
CHANNEL_ACCESS_TOKEN=your_token make deploy-no-confirm

# テンプレート検証
make validate

# ビルドキャッシュ削除
make clean
```

### デプロイ（SAMコマンド直接）

```bash
# ビルド
sam build

# デプロイ
sam deploy --parameter-overrides ChannelAccessToken=your_token
```

### ログ確認

```bash
# process_user_messageのログをリアルタイム表示
make logs

# push-message-periodicallyのログ
make logs-push
```

### ローカル実行

```bash
# ローカルAPIサーバー起動（Docker必要）
make local-api

# 別ターミナルでテスト
curl -X POST http://localhost:3000/process_user_message \
  -H "Content-Type: application/json" \
  -d @events/line_message.json

# Lambda単体実行
make local-invoke
```

ローカル実行時はテスト用S3バケットに接続し、LINE送信はスキップされます（ログ出力のみ）。

### デプロイ状況確認

```bash
# スタックのステータス
make status

# Lambda関数の詳細
aws lambda get-function-configuration --function-name process_user_message --region ap-northeast-1

# S3バケット内のタスクデータ確認
aws s3 ls s3://bossagyu-lambda-line-clean-bot/
```

## アーキテクチャ

### Lambdaエントリーポイント (line_clean_bot.py)

- `push_message_periodically` - 定期実行関数。全ユーザーのタスクをチェックし、期限切れのタスクをリマインド
- `process_user_message` - LINEメッセージのWebhookハンドラ。ユーザーコマンドを処理

### コアモジュール (lib/)

- **CleanTask** - タスク状態管理。`duration`（日数）と`updated_at`からタスクの期限を評価
- **S3client** - 永続化レイヤー。各LINEユーザー/グループごとにJSONファイル（`{line_id}.json`）をS3に保存
- **Line** - LINE Bot APIラッパー。メッセージ送信を担当
- **Message** - コマンドパーサーとレスポンス生成

### データフロー

1. LINE webhook → API Gateway → `process_user_message` Lambda
2. LambdaがS3からユーザーのタスクJSON（`{line_id}.json`）を読み込み
3. MessageクラスがコマンドをパースしCleanTaskを更新
4. 更新されたタスクをS3に保存、LINEでレスポンス送信

### タスクJSONの構造

```json
{
  "tasks": [
    {
      "task_name": "掃除機",
      "updated_at": "2024-01-01 12:00:00",
      "duration": 7
    }
  ]
}
```

## AWS デプロイ構成

### SAMテンプレート構成

- `template.yaml` - Lambda、API Gateway、IAMポリシー、スケジュール定義
- `samconfig.toml` - デプロイパラメータ（リージョン、スタック名など）

### リージョン

ap-northeast-1（東京）

### Lambda関数

| 関数名 | ハンドラー | トリガー |
|--------|-----------|----------|
| `process_user_message` | line_clean_bot.process_user_message | API Gateway (HTTP API) |
| `push-message-periodically` | line_clean_bot.push_message_periodically | EventBridge Schedule |

### CloudFormationスタック

- **スタック名**: line-clean-bot

### API Gateway

- **API ID**: 1k6enr57pi
- **ルート**: ANY /process_user_message
- **LINE Webhook URL**: https://1k6enr57pi.execute-api.ap-northeast-1.amazonaws.com/process_user_message

### S3バケット

- `bossagyu-lambda-line-clean-bot` - 本番用タスクデータ
- `bossagyu-lambda-line-clean-bot-test` - テスト用

## LINE Botコマンド

- `完了 [タスク名]` - タスクを完了にする（複数指定可）
- `追加 [タスク名] [日数]` - 新しいタスクを間隔指定で追加
- `削除 [タスク名]` - タスクを削除
- `確認` - 全タスクの詳細を表示
- `残り` - 期限切れのタスクを表示
- `使い方` - ヘルプを表示

## 環境変数

- `CHANNEL_ACCESS_TOKEN` - LINEチャンネルアクセストークン（デプロイ時にパラメータで指定）
- `BUCKET_NAME` - タスク保存用S3バケット名（デフォルト: `bossagyu-lambda-line-clean-bot`）
- `DRY_RUN` - `true`でLINE送信をスキップ（ローカル実行用）

## プロジェクト構造

```
clean-bot/
├── lib/                      # コアモジュール
│   ├── clean_task.py         # タスク状態管理
│   ├── line.py               # LINE Bot APIラッパー（DRY_RUN対応）
│   ├── message.py            # コマンドパーサー
│   └── s3_client.py          # S3永続化レイヤー
├── test/
│   ├── data/                 # テストデータ
│   │   └── s3_test_file.json
│   └── lib/                  # ユニットテスト
│       ├── clean_task_test.py
│       └── s3_client_test.py
├── events/                   # ローカル実行用イベント
│   └── line_message.json     # テスト用LINEメッセージ
├── line_clean_bot.py         # Lambdaエントリーポイント
├── template.yaml             # SAMテンプレート
├── samconfig.toml            # SAMデプロイ設定
├── env.json                  # ローカル実行用環境変数
├── pyproject.toml            # uv/Python設定
└── Makefile                  # 開発コマンド
```

## テスト

テストは`moto`でS3をモック化し、`pytest`フィクスチャを使用。テストデータは`test/data/`に配置。

### テスト設定

- **moto 5.x**: `mock_aws`デコレータを使用（旧`mock_s3`は非推奨）
- **pythonpath**: `pyproject.toml`で`["."]`を設定し、プロジェクトルートからのインポートを有効化

```toml
# pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

### テストの実行

```bash
# 全テスト実行
uv run pytest test/

# 詳細出力
uv run pytest test/ -v

# 特定のテスト
uv run pytest test/lib/s3_client_test.py::test_get_object_body
```
