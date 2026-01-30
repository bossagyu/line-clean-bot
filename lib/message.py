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
        self.object_keyname = user_id + ".json"

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

        # 使い方の場合は使い方を返却する
        if task_operation == '使い方':
            return self.__get_usage_message()

        # タスク確認の場合はタスクの詳細情報を返却する
        if message == '確認':
            return self.__get_task_check_message()

        # 完了の場合はs3のタスクの時刻を更新する
        if task_operation == '完了':
            return_message = ""
            for done_task_name in self.__get_all_task_name(message):
                self.clean_task.update_task_updated_at(done_task_name)
                return_message = f"{done_task_name}を完了しました。\n"
                print(return_message)
            print(self.clean_task.get_json())
            s3client.update_object(self.object_keyname, self.clean_task.get_json())
            return return_message + self.get_periodically_push_message()

        # タスクの追加
        if task_operation == '追加':
            duration = self.__get_duration(message)
            self.clean_task.add_task(task_name, duration)
            print(self.clean_task.get_json())
            s3client.update_object(self.object_keyname, self.clean_task.get_json())
            return_message = f"{task_name}を追加しました。\n"
            return return_message + self.__get_task_check_message()

        if task_operation == '削除':
            self.clean_task.delete_task(task_name)
            print(self.clean_task.get_json())
            s3client.update_object(self.object_keyname, self.clean_task.get_json())
            return_message = f"{task_name}を削除しました。\n"
            return return_message + self.__get_task_check_message()

        # 残りの場合はtodo状況にあるタスクの一覧を返却する
        if task_operation == '残り':
            return self.get_periodically_push_message()

        # コマンドが認識されなかった場合
        return 'コマンドを認識できませんでした。「使い方」と入力してください。'

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
        tasks = self.clean_task.get_todo_tasks_sorted_by_elapsed_days()

        if len(tasks) == 0:
            push_message += '残りのタスクはありません。\n'
            push_message += 'おつかれさまでした！\n'
            return push_message

        push_message += 'タスクは以下の通りです。\n'
        for task in tasks:
            elapsed_days = self.clean_task.get_elapsed_days(task)
            push_message += f"{task['task_name']} ({elapsed_days}日)\n"
        return push_message

    def __get_usage_message(self):
        """使用方法を返却する関数"""
        return '使い方\n' \
               '完了 [タスク名] : タスクを完了にする\n' \
               '追加 [タスク名] [日数] : タスクを追加する\n' \
               '削除 [タスク名] : タスクを削除する\n' \
               '確認 : タスクの詳細情報を確認する\n' \
               '残り : 残りのタスクを確認する'

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

    def __get_all_task_name(self, message):
        """タスク名を取得する
        :param message: message
        """
        elements = re.split(r'\s|\u3000', message)
        return elements[1:]
