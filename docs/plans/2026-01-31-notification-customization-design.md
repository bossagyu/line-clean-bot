# 通知カスタマイズ機能 設計書

## 概要

ユーザーがLINEから通知設定（曜日・時間・ON/OFF）をカスタマイズできる機能を追加する。

## 要件

- 通知の曜日をユーザーが選択可能（複数可）
- 通知の時間をユーザーが選択可能（0-23時）
- 通知のON/OFFを切り替え可能
- 1日最大1回の通知に制限
- デフォルトは通知OFF

## データ構造

### S3に保存するJSONの変更

```json
{
  "tasks": [...],
  "notification": {
    "enabled": true,
    "days": ["月", "水", "金"],
    "hour": 7,
    "last_notified_at": "2026-01-31 07:05:00"
  }
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| enabled | boolean | 通知ON/OFF（デフォルト: false） |
| days | string[] | 通知する曜日の配列 |
| hour | int | 通知する時間（0-23、JST） |
| last_notified_at | string | 最終通知日時 |

## コマンド

| コマンド | 例 | 説明 |
|---------|-----|------|
| `通知設定 [曜日] [時間]` | `通知設定 月水金 7` | 曜日と時間を設定しONにする |
| `通知停止` | `通知停止` | 通知をOFFにする |
| `通知開始` | `通知開始` | 通知をONにする |
| `通知確認` | `通知確認` | 現在の設定を表示 |

## インフラ変更

### EventBridgeスケジュール

**現在:**
```
毎週土曜 10:00 JST (cron(0 1 ? * SAT *))
```

**変更後:**
```
毎時0分 (cron(0 * * * ? *))
```

### 通知判定ロジック

```
今日の通知予定時刻 = 今日の日付 + 設定時刻(hour)

条件:
1. enabled=true かつ 今日が設定曜日
2. 現在時刻 >= 今日の通知予定時刻
3. last_notified_at < 今日の通知予定時刻
→ 全て満たせば通知し、last_notified_atを現在時刻で更新
```

## コード変更

### 変更ファイル

| ファイル | 変更内容 |
|---------|---------|
| `lib/clean_task.py` | 通知設定の読み書き、判定ロジック追加 |
| `lib/message.py` | 通知設定コマンドの処理追加 |
| `line_clean_bot.py` | 定期実行の通知判定ロジック変更 |
| `template.yaml` | EventBridgeスケジュールを毎時に変更 |

### CleanTaskクラスに追加するメソッド

- `get_notification_settings()` - 通知設定を取得
- `set_notification_settings(days, hour)` - 通知設定を保存
- `set_notification_enabled(enabled)` - ON/OFF切り替え
- `should_notify(current_time)` - 通知すべきか判定
- `update_last_notified()` - last_notified_at更新

### Messageクラスに追加

- `通知設定`コマンドの処理
- `通知停止`/`通知開始`/`通知確認`コマンドの処理

## テスト

### CleanTaskのテスト

- 通知設定の保存・読み込み
- `should_notify()`の判定ロジック
  - 曜日が一致/不一致
  - 時刻前/時刻後
  - last_notified_atが今日/過去
  - enabled=true/false

### Messageのテスト

- `通知設定 月水金 7` → 正常に設定される
- `通知設定 月水金` → 時間がないエラー
- `通知停止`/`通知開始` → enabled切り替え
- `通知確認` → 現在の設定が表示される

## コスト影響

- Lambda実行: 24回/日 → 月720回（無料枠内）
- 1回の実行時間は短い（ユーザー数が少なければ数秒）
