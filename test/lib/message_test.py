from pathlib import Path
from unittest.mock import MagicMock

import pytest

from lib.clean_task import CleanTask
from lib.message import Message


@pytest.fixture
def load_task_json():
    test_data_path = Path(__file__).parent.parent / 'data' / 's3_test_file.json'
    with open(test_data_path, 'r') as f:
        return f.read()


@pytest.fixture
def message_instance(load_task_json):
    clean_task = CleanTask(load_task_json)
    return Message(clean_task, 'test_user_id')


@pytest.fixture
def mock_s3client():
    return MagicMock()


def test_unrecognized_command_returns_help_message(message_instance, mock_s3client):
    """認識されないコマンドの場合、ヘルプメッセージを返す"""
    result = message_instance.get_return_message('不明なコマンド', mock_s3client)
    assert result == 'コマンドを認識できませんでした。「使い方」と入力してください。'


def test_unrecognized_command_with_random_text(message_instance, mock_s3client):
    """ランダムなテキストの場合もヘルプメッセージを返す"""
    result = message_instance.get_return_message('あいうえお', mock_s3client)
    assert result == 'コマンドを認識できませんでした。「使い方」と入力してください。'


def test_usage_command_returns_usage_message(message_instance, mock_s3client):
    """使い方コマンドは通常の使い方メッセージを返す"""
    result = message_instance.get_return_message('使い方', mock_s3client)
    assert '使い方' in result
    assert '完了' in result
    assert '追加' in result


def test_periodically_push_message_shows_overdue_days(message_instance):
    """残りタスクのメッセージに超過日数が表示される"""
    result = message_instance.get_periodically_push_message()
    # task1は期限切れなので表示される
    assert 'task1' in result
    # 超過日数がカッコで表示される（例: task1 (+N日)）
    assert '(+' in result
    assert '日)' in result
