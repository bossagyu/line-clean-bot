import json
from pathlib import Path

import pytest

from lib.clean_task import CleanTask


@pytest.fixture
def load_task_json():
    test_data_path = Path(__file__).parent.parent / 'data' / 's3_test_file.json'
    with open(test_data_path, 'r') as f:
        return f.read()


def test_get_todo_tasks(load_task_json):
    task_json = load_task_json
    clean_task = CleanTask(task_json)
    todo_tasks = clean_task.get_todo_tasks()
    assert len(todo_tasks) == 1
    assert todo_tasks[0]['task_name'] == 'task1'


def test_get_elapsed_days(load_task_json):
    """経過日数を取得できる"""
    task_json = load_task_json
    clean_task = CleanTask(task_json)
    tasks = clean_task.get_all_tasks()
    # task1は2024-01-01なので、現在時刻からかなりの日数が経過しているはず
    elapsed = clean_task.get_elapsed_days(tasks[0])
    assert elapsed > 0


def test_get_todo_tasks_sorted_by_elapsed_days():
    """経過日数が長い順にソートされたタスク一覧を取得できる"""
    # 異なる経過日数を持つテストデータを作成
    task_json = json.dumps({
        "tasks": [
            {"task_name": "task_5days", "updated_at": "2020-01-10 00:00:00", "duration": 1},
            {"task_name": "task_10days", "updated_at": "2020-01-05 00:00:00", "duration": 1},
            {"task_name": "task_3days", "updated_at": "2020-01-12 00:00:00", "duration": 1},
        ]
    })
    clean_task = CleanTask(task_json)
    sorted_tasks = clean_task.get_todo_tasks_sorted_by_elapsed_days()

    # 経過日数が長い順（task_10days > task_5days > task_3days）
    assert len(sorted_tasks) == 3
    assert sorted_tasks[0]['task_name'] == 'task_10days'
    assert sorted_tasks[1]['task_name'] == 'task_5days'
    assert sorted_tasks[2]['task_name'] == 'task_3days'


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


def test_get_json_includes_notification():
    """get_jsonが通知設定を含んで返す"""
    task_json = json.dumps({
        "tasks": [],
        "notification": {
            "enabled": True,
            "days": ["土"],
            "hour": 9,
            "last_notified_at": None
        }
    })
    clean_task = CleanTask(task_json)
    result = json.loads(clean_task.get_json())
    assert 'notification' in result
    assert result['notification']['enabled'] == True
    assert result['notification']['days'] == ["土"]
    assert result['notification']['hour'] == 9


def test_get_json_includes_default_notification():
    """get_jsonがデフォルト通知設定を含んで返す"""
    task_json = json.dumps({"tasks": []})
    clean_task = CleanTask(task_json)
    result = json.loads(clean_task.get_json())
    assert 'notification' in result
    assert result['notification']['enabled'] == False
    assert result['notification']['days'] == []
    assert result['notification']['hour'] == 10
    assert result['notification']['last_notified_at'] is None
