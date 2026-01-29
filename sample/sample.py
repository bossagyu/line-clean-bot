import re
from datetime import datetime
import logging

def __get_task_name(message):
    """タスク名を取得する
    :param message: message
    :return: task name
    """
    elements = re.split(r'\s|\u3000', message)
    return elements[1] if len(elements) > 1 else None

print(__get_task_name("完了 task1"))

tasks = [{"a": "aaaa"}, {"b": "bbbbb"}, {"c": "ccccc"}]


print(tasks)

class TaskManager:
    def __init__(self):
        self.date_format = '%Y-%m-%d %H:%M:%S'
        self.tasks = [
            {'task_name': 'Task1', 'updated_at': '2024-01-01 00:00:00'},
            {'task_name': 'Task2', 'updated_at': '2024-01-01 00:00:00'}
        ]

    def update_task(self, task_name):
        for task in self.tasks:
            if task['task_name'] == task_name:
                task['updated_at'] = datetime.now().strftime(self.date_format)
                break

# 使用例
task_manager = TaskManager()
task_manager.update_task('Task1')
print(task_manager.tasks)

print("aaaaa")
logging.warning("logging test")