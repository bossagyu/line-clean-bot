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
