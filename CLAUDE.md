# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

定期的な掃除タスクを管理するLINE Bot。ユーザーはLINEメッセージを通じて家事を追加・完了・確認できます。タスクには「duration（日数）」があり、その期間が経過すると再度実行すべきタスクとして表示されます。

## コマンド

### 開発

```bash
# 依存関係のインストール
pip install -r requirements.txt

# テスト実行（プロジェクトルートから）
pytest test/

# 特定のテストファイルを実行
pytest test/lib/s3_client_test.py

# 特定のテストケースを実行
pytest test/lib/s3_client_test.py::test_get_object_body
```

### デプロイ

```bash
# AWS SAMでビルド
sam build

# デプロイ（AWS認証情報が必要）
sam deploy
```

### デプロイ状況確認

```bash
# Lambda関数一覧
aws lambda list-functions --region ap-northeast-1 --output table

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

### リージョン

ap-northeast-1（東京）

### Lambda関数

| 関数名 | ハンドラー | ランタイム |
|--------|-----------|-----------|
| `process_user_message` | line_clean_bot.process_user_message | Python 3.11 |
| `push-message-periodically` | line_clean_bot.push_message_periodically | Python 3.11 |

### API Gateway

- **API ID**: bqmf13lp70
- **エンドポイント**: https://bqmf13lp70.execute-api.ap-northeast-1.amazonaws.com
- **ルート**: ANY /process_user_message
- **LINE Webhook URL**: https://bqmf13lp70.execute-api.ap-northeast-1.amazonaws.com/process_user_message

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

- `CHANNEL_ACCESS_TOKEN` - LINEチャンネルアクセストークン
- `BUCKET_NAME` - タスク保存用S3バケット名（本番: `bossagyu-lambda-line-clean-bot`）

## テスト

テストは`moto`でS3をモック化し、`pytest`フィクスチャを使用。テストデータは`test/data/`に配置。
