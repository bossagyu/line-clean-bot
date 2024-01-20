class Message:
    def __init__(self, clean_task, user_id):
        """Initiate message class
        :param clean_task: clean task
        :param user_id: user id
        """
        self.clean_task = clean_task
        self.user_id = user_id

    def get_return_message(self, message):
        """LINEで受け取ったメッセージから処理する内容を判別し、メッセージを返却する関数
        :param message: message
        :return: return message
        """
        if message == 'タスク確認':
            return self.__get_task_check_message()

    def __get_task_check_message(self):
        """タスクの詳細情報を返却する関数"""
        push_message = ''
        push_message += 'タスクのステータスは以下の通りです。\n'
        for task in self.clean_task.get_all_tasks():
            push_message += f"{task['task_name']}\n"
            push_message += f"  updated_at: {task['updated_at']}\n"
            push_message += f"  duration  : {task['duration']}\n\n"
        return push_message

    def get_periodically_push_message(self):
        """todo状況にあるタスクを返却する関数"""
        push_message = ''
        push_message += '今日のタスクは以下の通りです。\n'
        for task in self.clean_task.get_todo_tasks():
            push_message += task['task_name'] + '\n'
        return push_message
