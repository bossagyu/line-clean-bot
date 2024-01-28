import json
from datetime import datetime


class CleanTask(object):
    def __init__(self, task_json):
        task_data = json.loads(task_json)
        self.tasks = task_data['tasks']
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def __evaluate_cleanup_timing(self, task):
        """Evaluate cleanup timing
        :param task: task
        :return: boolean
        """

        # 現在の日時を取得
        now = datetime.now()
        task_time = datetime.strptime(task['updated_at'], self.date_format)
        if (now - task_time).days >= task['duration']:
            return True

    def get_todo_tasks(self):
        """Get todo task
        :return: list of exception tasks
        """
        todo_tasks = []
        for task in self.tasks:
            if self.__evaluate_cleanup_timing(task):
                todo_tasks.append(task)
        return todo_tasks

    def get_all_tasks(self):
        """Get all task
        :return: list of exception tasks
        """
        return self.tasks

    def update_task_updated_at(self, task_name):
        """Update task status
        :param task_name: task name
        """
        for task in self.tasks:
            if task['task_name'] == task_name:
                task['updated_at'] = datetime.now().strftime(self.date_format)
                break

    def get_json(self):
        """Get json string
        :return: json string
        """
        task_data = {'tasks': self.tasks}
        return json.dumps(task_data)

    def add_task(self, task_name, duration):
        """Add task
        :param task_name: task name
        :param duration: duration
        """
        self.tasks.append({'task_name': task_name, 'updated_at': datetime.now().strftime(self.date_format), 'duration': duration})
