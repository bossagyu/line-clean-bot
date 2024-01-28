import re
from lib.s3_client import S3client

class Message:
    def __init__(self, clean_task, user_id):
        """Initiate message class
        :param clean_task: clean task
        :param user_id: user id
        """
        self.clean_task = clean_task
        self.user_id = user_id

    def get_return_message(self, message, s3client):
        """LINEで受け取ったメッセージから処理する内容を判別し、メッセージを返却する関数
        :param message: message
        :param s3client: s3 client
        :return: return message
        """
        # 操作とタスク名を取得
        task_operation = self.__get_task_operation_name(message)
        task_name = self.__get_task_name(message)

        print("message: ", message)
        print("task_operation: ", task_operation)
        print("task_name: ", task_name)

        # タスク確認の場合はタスクの詳細情報を返却する
        if message == '確認':
            return self.__get_task_check_message()

        # 完了の場合はs3のタスクの時刻を更新する
        if task_operation == '完了':
            self.clean_task.update_task_updated_at(task_name)
            print(self.clean_task.get_json())
            s3client.update_object(self.user_id + ".json", self.clean_task.get_json())
            message = f"{task_name}を完了しました。\n"
            return message + self.get_periodically_push_message()

        # タスクの追加
        if task_operation == '追加':
            duration = self.__get_duration(message)
            self.clean_task.add_task(task_name, duration)
            print(self.clean_task.get_json())
            s3client.update_object(self.user_id + ".json", self.clean_task.get_json())
            message = f"{task_name}を追加しました。\n"
            return message + self.__get_task_check_message()


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
        """todo状況にあるタスクの一覧のメッセージを返却する関数"""
        push_message = ''
        push_message += 'タスクは以下の通りです。\n'
        for task in self.clean_task.get_todo_tasks():
            push_message += task['task_name'] + '\n'
        return push_message

    def __get_task_operation_name(self, message):
        """操作を取得する
        :param message: message
        :return: task operation
        """
        elements = re.split(r'\s|\u3000', message)
        # TODO: ここでtask_operation_nameのチェックを行う
        return elements[0] if len(elements) > 0 else None

    def __get_task_name(self, message):
        """タスク名を取得する
        :param message: message
        :return: task name
        """
        elements = re.split(r'\s|\u3000', message)
        return elements[1] if len(elements) > 1 else None

    def __get_duration(self, message):
        """タスク名を取得する
        :param message: message
        :return: task name
        """
        elements = re.split(r'\s|\u3000', message)
        return elements[2] if len(elements) > 2 else None
