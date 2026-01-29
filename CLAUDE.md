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

## LINE Botコマンド

- `完了 [タスク名]` - タスクを完了にする（複数指定可）
- `追加 [タスク名] [日数]` - 新しいタスクを間隔指定で追加
- `削除 [タスク名]` - タスクを削除
- `確認` - 全タスクの詳細を表示
- `残り` - 期限切れのタスクを表示
- `使い方` - ヘルプを表示

## 環境変数

- `CHANNEL_ACCESS_TOKEN` - LINEチャンネルアクセストークン
- `BUCKET_NAME` - タスク保存用S3バケット名

## テスト

テストは`moto`でS3をモック化し、`pytest`フィクスチャを使用。テストデータは`test/data/`に配置。
