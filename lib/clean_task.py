import json
from datetime import datetime, timedelta


class CleanTask(object):
    DEFAULT_NOTIFICATION = {
        'enabled': False,
        'days': [],
        'hour': 10,
        'last_notified_at': None
    }

    def __init__(self, task_json):
        task_data = json.loads(task_json)
        self.tasks = task_data['tasks']
        self.notification = self._load_notification(task_data.get('notification'))
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.now = datetime.now() + timedelta(hours=9)

    def _load_notification(self, notification_data):
        """Load notification settings with defaults for missing fields
        :param notification_data: notification data from JSON or None
        :return: notification settings dict
        """
        if notification_data is None:
            return {**self.DEFAULT_NOTIFICATION}
        return {
            'enabled': notification_data.get('enabled', self.DEFAULT_NOTIFICATION['enabled']),
            'days': notification_data.get('days', self.DEFAULT_NOTIFICATION['days']),
            'hour': notification_data.get('hour', self.DEFAULT_NOTIFICATION['hour']),
            'last_notified_at': notification_data.get('last_notified_at', self.DEFAULT_NOTIFICATION['last_notified_at'])
        }

    def __evaluate_cleanup_timing(self, task):
        """Evaluate cleanup timing
        :param task: task
        :return: boolean
        """

        # 現在の日時を取得
        task_time = datetime.strptime(task['updated_at'], self.date_format)
        if (self.now - task_time).days >= int(task['duration']):
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

    def get_elapsed_days(self, task):
        """Get elapsed days since last update
        :param task: task
        :return: elapsed days
        """
        task_time = datetime.strptime(task['updated_at'], self.date_format)
        return (self.now - task_time).days

    def get_todo_tasks_sorted_by_elapsed_days(self):
        """Get todo tasks sorted by elapsed days (longest first)
        :return: list of todo tasks sorted by elapsed days descending
        """
        todo_tasks = self.get_todo_tasks()
        return sorted(todo_tasks, key=lambda task: self.get_elapsed_days(task), reverse=True)

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
                task['updated_at'] = self.now.strftime(self.date_format)
                break

    def get_notification_settings(self):
        """Get notification settings
        :return: notification settings dict
        """
        return {**self.notification}

    def set_notification_settings(self, days, hour):
        """通知設定を更新する
        :param days: 通知する曜日のリスト
        :param hour: 通知する時刻（時）
        """
        self.notification = {
            **self.notification,
            'enabled': True,
            'days': days,
            'hour': int(hour)
        }

    def set_notification_enabled(self, enabled):
        """通知のON/OFFを切り替える
        :param enabled: 通知を有効にするかどうか
        """
        self.notification = {
            **self.notification,
            'enabled': enabled
        }

    def get_json(self):
        """Get json string
        :return: json string
        """
        task_data = {
            'tasks': self.tasks,
            'notification': self.notification
        }
        return json.dumps(task_data)

    def add_task(self, task_name, duration):
        """Add task
        :param task_name: task name
        :param duration: duration
        """
        # durationが整数かどうかのチェック
        try:
            duration_int = int(duration)
        except ValueError:
            # durationが整数に変換できない場合のエラー処理
            raise ValueError(f"Duration must be an integer, got {duration}")

        self.tasks.append({'task_name': task_name, 'updated_at': self.now.strftime(self.date_format), 'duration': duration_int})

    def delete_task(self, task_name):
        """Delete task
        :param task_name: task name
        """
        for task in self.tasks:
            if task['task_name'] == task_name:
                self.tasks.remove(task)
                break

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

    def update_last_notified(self):
        """last_notified_atを現在時刻で更新する"""
        self.notification = {
            **self.notification,
            'last_notified_at': self.now.strftime(self.date_format)
        }
