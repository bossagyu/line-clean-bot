# 通知カスタマイズ機能 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** ユーザーがLINEから通知設定（曜日・時間・ON/OFF）をカスタマイズできる機能を実装する

**Architecture:** CleanTaskクラスに通知設定の管理機能を追加し、Messageクラスで通知設定コマンドを処理。定期実行Lambdaを毎時実行に変更し、各ユーザーの設定に基づいて通知を送信。

**Tech Stack:** Python 3.11, AWS Lambda, S3, EventBridge, pytest

---

## Task 1: CleanTaskに通知設定の読み書き機能を追加

**Files:**
- Modify: `lib/clean_task.py`
- Test: `test/lib/clean_task_test.py`

### Step 1: テストを書く（通知設定の初期化）

`test/lib/clean_task_test.py` に追加:

```python
def test_get_notification_settings_default():
    """通知設定がない場合はデフォルト値を返す"""
    task_json = json.dumps({"tasks": []})
    clean_task = CleanTask(task_json)
    settings = clean_task.get_notification_settings()
    assert settings['enabled'] == False
    assert settings['days'] == []
    assert settings['hour'] == 10
    assert settings['last_notified_at'] is None


def test_get_notification_settings_with_existing():
    """既存の通知設定を読み込める"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["月", "水", "金"],
            "hour": 7,
            "last_notified_at": "2026-01-31 07:05:00"
        }
    })
    clean_task = CleanTask(task_json)
    settings = clean_task.get_notification_settings()
    assert settings['enabled'] == True
    assert settings['days'] == ["月", "水", "金"]
    assert settings['hour'] == 7
    assert settings['last_notified_at'] == "2026-01-31 07:05:00"
```

### Step 2: テスト実行（失敗を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_get_notification_settings_default -v
```

Expected: FAIL with "AttributeError: 'CleanTask' object has no attribute 'get_notification_settings'"

### Step 3: 実装

`lib/clean_task.py` の `__init__` を修正し、メソッドを追加:

```python
def __init__(self, task_json):
    task_data = json.loads(task_json)
    self.tasks = task_data['tasks']
    self.notification = task_data.get('notification', {
        'enabled': False,
        'days': [],
        'hour': 10,
        'last_notified_at': None
    })
    self.date_format = "%Y-%m-%d %H:%M:%S"
    self.now = datetime.now() + timedelta(hours=9)

def get_notification_settings(self):
    """通知設定を取得する"""
    return self.notification
```

`get_json` メソッドも修正:

```python
def get_json(self):
    """Get json string"""
    task_data = {
        'tasks': self.tasks,
        'notification': self.notification
    }
    return json.dumps(task_data)
```

### Step 4: テスト実行（成功を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_get_notification_settings_default test/lib/clean_task_test.py::test_get_notification_settings_with_existing -v
```

Expected: PASS

### Step 5: コミット

```bash
git add lib/clean_task.py test/lib/clean_task_test.py
git commit -m "feat: CleanTaskに通知設定の読み込み機能を追加"
```

---

## Task 2: CleanTaskに通知設定の更新機能を追加

**Files:**
- Modify: `lib/clean_task.py`
- Test: `test/lib/clean_task_test.py`

### Step 1: テストを書く

```python
def test_set_notification_settings():
    """通知設定を更新できる"""
    task_json = json.dumps({"tasks": []})
    clean_task = CleanTask(task_json)
    clean_task.set_notification_settings(["月", "水", "金"], 7)
    settings = clean_task.get_notification_settings()
    assert settings['enabled'] == True
    assert settings['days'] == ["月", "水", "金"]
    assert settings['hour'] == 7


def test_set_notification_enabled():
    """通知のON/OFFを切り替えられる"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {"enabled": True, "days": ["月"], "hour": 7, "last_notified_at": None}
    })
    clean_task = CleanTask(task_json)
    clean_task.set_notification_enabled(False)
    assert clean_task.get_notification_settings()['enabled'] == False
    clean_task.set_notification_enabled(True)
    assert clean_task.get_notification_settings()['enabled'] == True
```

### Step 2: テスト実行（失敗を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_set_notification_settings -v
```

Expected: FAIL

### Step 3: 実装

```python
def set_notification_settings(self, days, hour):
    """通知設定を更新する"""
    self.notification['enabled'] = True
    self.notification['days'] = days
    self.notification['hour'] = int(hour)

def set_notification_enabled(self, enabled):
    """通知のON/OFFを切り替える"""
    self.notification['enabled'] = enabled
```

### Step 4: テスト実行（成功を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_set_notification_settings test/lib/clean_task_test.py::test_set_notification_enabled -v
```

Expected: PASS

### Step 5: コミット

```bash
git add lib/clean_task.py test/lib/clean_task_test.py
git commit -m "feat: CleanTaskに通知設定の更新機能を追加"
```

---

## Task 3: CleanTaskに通知判定ロジックを追加

**Files:**
- Modify: `lib/clean_task.py`
- Test: `test/lib/clean_task_test.py`

### Step 1: テストを書く

```python
from datetime import datetime
from unittest.mock import patch

def test_should_notify_returns_true_when_conditions_met():
    """条件を満たす場合はTrueを返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["金"],
            "hour": 7,
            "last_notified_at": "2026-01-30 07:00:00"
        }
    })
    clean_task = CleanTask(task_json)
    # 2026-01-31は金曜日、時刻は7:05
    test_time = datetime(2026, 1, 31, 7, 5, 0)
    assert clean_task.should_notify(test_time) == True


def test_should_notify_returns_false_when_disabled():
    """enabled=falseの場合はFalseを返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": False,
            "days": ["金"],
            "hour": 7,
            "last_notified_at": None
        }
    })
    clean_task = CleanTask(task_json)
    test_time = datetime(2026, 1, 31, 7, 5, 0)
    assert clean_task.should_notify(test_time) == False


def test_should_notify_returns_false_when_wrong_day():
    """曜日が一致しない場合はFalseを返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["月"],
            "hour": 7,
            "last_notified_at": None
        }
    })
    clean_task = CleanTask(task_json)
    # 金曜日だが設定は月曜日
    test_time = datetime(2026, 1, 31, 7, 5, 0)
    assert clean_task.should_notify(test_time) == False


def test_should_notify_returns_false_when_before_hour():
    """設定時刻前はFalseを返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["金"],
            "hour": 10,
            "last_notified_at": None
        }
    })
    clean_task = CleanTask(task_json)
    # 7時だが設定は10時
    test_time = datetime(2026, 1, 31, 7, 5, 0)
    assert clean_task.should_notify(test_time) == False


def test_should_notify_returns_false_when_already_notified_today():
    """今日すでに通知済みの場合はFalseを返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["金"],
            "hour": 7,
            "last_notified_at": "2026-01-31 07:05:00"
        }
    })
    clean_task = CleanTask(task_json)
    # 今日の8時だが、7:05に通知済み
    test_time = datetime(2026, 1, 31, 8, 0, 0)
    assert clean_task.should_notify(test_time) == False
```

### Step 2: テスト実行（失敗を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_should_notify_returns_true_when_conditions_met -v
```

Expected: FAIL

### Step 3: 実装

```python
def should_notify(self, current_time):
    """通知すべきか判定する
    :param current_time: 現在時刻（datetime）
    :return: 通知すべきならTrue
    """
    if not self.notification['enabled']:
        return False

    # 曜日の確認
    weekday_map = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}
    current_weekday = weekday_map[current_time.weekday()]
    if current_weekday not in self.notification['days']:
        return False

    # 時刻の確認
    if current_time.hour < self.notification['hour']:
        return False

    # 今日の通知予定時刻
    today_notification_time = current_time.replace(
        hour=self.notification['hour'],
        minute=0,
        second=0,
        microsecond=0
    )

    # last_notified_atの確認
    last_notified = self.notification.get('last_notified_at')
    if last_notified:
        last_notified_time = datetime.strptime(last_notified, self.date_format)
        if last_notified_time >= today_notification_time:
            return False

    return True
```

### Step 4: テスト実行（成功を確認）

```bash
uv run pytest test/lib/clean_task_test.py -k "should_notify" -v
```

Expected: PASS

### Step 5: コミット

```bash
git add lib/clean_task.py test/lib/clean_task_test.py
git commit -m "feat: CleanTaskに通知判定ロジックを追加"
```

---

## Task 4: CleanTaskにlast_notified_at更新機能を追加

**Files:**
- Modify: `lib/clean_task.py`
- Test: `test/lib/clean_task_test.py`

### Step 1: テストを書く

```python
def test_update_last_notified():
    """last_notified_atを更新できる"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["金"],
            "hour": 7,
            "last_notified_at": None
        }
    })
    clean_task = CleanTask(task_json)
    clean_task.update_last_notified()
    settings = clean_task.get_notification_settings()
    assert settings['last_notified_at'] is not None
```

### Step 2: テスト実行（失敗を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_update_last_notified -v
```

Expected: FAIL

### Step 3: 実装

```python
def update_last_notified(self):
    """last_notified_atを現在時刻で更新する"""
    self.notification['last_notified_at'] = self.now.strftime(self.date_format)
```

### Step 4: テスト実行（成功を確認）

```bash
uv run pytest test/lib/clean_task_test.py::test_update_last_notified -v
```

Expected: PASS

### Step 5: コミット

```bash
git add lib/clean_task.py test/lib/clean_task_test.py
git commit -m "feat: CleanTaskにlast_notified_at更新機能を追加"
```

---

## Task 5: Messageクラスに通知設定コマンドを追加

**Files:**
- Modify: `lib/message.py`
- Test: `test/lib/message_test.py`

### Step 1: テストを書く

```python
def test_notification_settings_command(message_instance, mock_s3client):
    """通知設定コマンドで曜日と時間を設定できる"""
    result = message_instance.get_return_message('通知設定 月水金 7', mock_s3client)
    assert '通知設定を更新しました' in result
    assert '月水金' in result
    assert '7時' in result


def test_notification_stop_command(message_instance, mock_s3client):
    """通知停止コマンドで通知をOFFにできる"""
    result = message_instance.get_return_message('通知停止', mock_s3client)
    assert '通知を停止しました' in result


def test_notification_start_command(message_instance, mock_s3client):
    """通知開始コマンドで通知をONにできる"""
    result = message_instance.get_return_message('通知開始', mock_s3client)
    assert '通知を開始しました' in result


def test_notification_check_command(message_instance, mock_s3client):
    """通知確認コマンドで現在の設定を表示できる"""
    result = message_instance.get_return_message('通知確認', mock_s3client)
    assert '通知設定' in result
```

### Step 2: テスト実行（失敗を確認）

```bash
uv run pytest test/lib/message_test.py::test_notification_settings_command -v
```

Expected: FAIL (コマンドが認識されない)

### Step 3: 実装

`lib/message.py` の `get_return_message` メソッドに追加:

```python
# 通知設定コマンド
if task_operation == '通知設定':
    days = self.__get_task_name(message)
    hour = self.__get_duration(message)
    if not days or not hour:
        return '通知設定の形式が正しくありません。\n例: 通知設定 月水金 7'
    days_list = list(days)
    self.clean_task.set_notification_settings(days_list, hour)
    s3client.update_object(self.object_keyname, self.clean_task.get_json())
    return f'通知設定を更新しました。\n曜日: {"".join(days_list)}\n時間: {hour}時'

if task_operation == '通知停止':
    self.clean_task.set_notification_enabled(False)
    s3client.update_object(self.object_keyname, self.clean_task.get_json())
    return '通知を停止しました。'

if task_operation == '通知開始':
    self.clean_task.set_notification_enabled(True)
    s3client.update_object(self.object_keyname, self.clean_task.get_json())
    return '通知を開始しました。'

if task_operation == '通知確認':
    return self.__get_notification_check_message()
```

通知確認メッセージのメソッドも追加:

```python
def __get_notification_check_message(self):
    """通知設定の確認メッセージを返却する関数"""
    settings = self.clean_task.get_notification_settings()
    enabled_str = 'ON' if settings['enabled'] else 'OFF'
    days_str = ''.join(settings['days']) if settings['days'] else '未設定'
    return f'通知設定\n状態: {enabled_str}\n曜日: {days_str}\n時間: {settings["hour"]}時'
```

### Step 4: テスト実行（成功を確認）

```bash
uv run pytest test/lib/message_test.py -k "notification" -v
```

Expected: PASS

### Step 5: コミット

```bash
git add lib/message.py test/lib/message_test.py
git commit -m "feat: Messageクラスに通知設定コマンドを追加"
```

---

## Task 6: 使い方メッセージを更新

**Files:**
- Modify: `lib/message.py`

### Step 1: 実装

`lib/message.py` の `__get_usage_message` を更新:

```python
def __get_usage_message(self):
    """使用方法を返却する関数"""
    return '使い方\n' \
           '完了 [タスク名] : タスクを完了にする\n' \
           '追加 [タスク名] [日数] : タスクを追加する\n' \
           '削除 [タスク名] : タスクを削除する\n' \
           '確認 : タスクの詳細情報を確認する\n' \
           '残り : 残りのタスクを確認する\n' \
           '通知設定 [曜日] [時間] : 通知を設定する\n' \
           '通知停止 : 通知を停止する\n' \
           '通知開始 : 通知を開始する\n' \
           '通知確認 : 通知設定を確認する'
```

### Step 2: テスト実行

```bash
uv run pytest test/lib/message_test.py -v
```

Expected: PASS

### Step 3: コミット

```bash
git add lib/message.py
git commit -m "feat: 使い方メッセージに通知コマンドを追加"
```

---

## Task 7: 定期実行Lambdaの通知判定ロジックを更新

**Files:**
- Modify: `line_clean_bot.py`

### Step 1: 実装

`line_clean_bot.py` の `push_message_periodically` を更新:

```python
def push_message_periodically(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(event)
    print(context)

    # 現在時刻を取得（JST）
    from datetime import datetime, timedelta
    current_time = datetime.now() + timedelta(hours=9)
    print(f"Current time (JST): {current_time}")

    # s3からデータを取得
    s3client = S3client(BUCKET_NAME)
    obj_lists = s3client.list_objects()

    # オブジェクトごとに通知判定
    for obj_list in obj_lists:
        obj_body = s3client.get_object_body(obj_list.key)
        user_id = obj_list.key.split('.json')[0]

        # タスクを取得
        clean_task = CleanTask(obj_body)

        # 通知すべきか判定
        if not clean_task.should_notify(current_time):
            print(f"Skip notification for {user_id}")
            continue

        # メッセージを生成
        return_message = Message(clean_task, user_id)
        line_message = return_message.get_periodically_push_message()

        # メッセージを送信
        line = Line(CHANNEL_ACCESS_TOKEN, user_id)
        line.push_message(line_message)

        # last_notified_atを更新
        clean_task.update_last_notified()
        s3client.update_object(obj_list.key, clean_task.get_json())
        print(f"Notification sent to {user_id}")
```

### Step 2: テスト実行

```bash
uv run pytest test/ -v
```

Expected: PASS

### Step 3: コミット

```bash
git add line_clean_bot.py
git commit -m "feat: 定期実行Lambdaに通知判定ロジックを追加"
```

---

## Task 8: EventBridgeスケジュールを毎時に変更

**Files:**
- Modify: `template.yaml`

### Step 1: 実装

`template.yaml` の `ScheduleExpression` デフォルト値を変更:

```yaml
ScheduleExpression:
  Type: String
  Default: cron(0 * * * ? *)
  Description: "Schedule for periodic push (default: every hour)"
```

また、`PushMessagePeriodicallyFunction` のポリシーをS3の書き込み権限に変更:

```yaml
Policies:
  - S3CrudPolicy:
      BucketName: !Ref BucketName
```

### Step 2: テンプレート検証

```bash
make validate
```

Expected: Template is valid

### Step 3: コミット

```bash
git add template.yaml
git commit -m "feat: EventBridgeスケジュールを毎時実行に変更"
```

---

## Task 9: 全テスト実行とデプロイ

### Step 1: 全テスト実行

```bash
uv run pytest test/ -v
```

Expected: All tests PASS

### Step 2: ビルドとデプロイ

```bash
make deploy-no-confirm
```

### Step 3: 最終コミットとプッシュ

```bash
git push origin main
```

---

## 完了確認チェックリスト

- [ ] 全テストがパス
- [ ] `通知設定 月水金 7` で設定可能
- [ ] `通知停止` / `通知開始` で切り替え可能
- [ ] `通知確認` で現在の設定を表示
- [ ] `使い方` に通知コマンドが表示される
- [ ] デプロイ成功
- [ ] LINEで動作確認
