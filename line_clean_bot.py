import os
import json

from lib.s3_client import S3client
from lib.line import Line
from lib.clean_task import CleanTask

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('USER_ID')
BUCKET_NAME = 'bossagyu-lambda-line-clean-bot'


def push_message_periodically(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(USER_ID)
    print(event)
    print(context)

    # s3からデータを取得
    s3client = S3client(BUCKET_NAME)
    obj_lists = s3client.list_objects()

    # オブジェクトごとにLineに送信
    for obj_list in obj_lists:
        obj_body = s3client.get_object_body(obj_list.key)
        # タスクを取得しメッセージを生成
        clean_task = CleanTask(obj_body)
        line_message = __make_periodically_push_message(clean_task.get_todo_tasks())
        # メッセージを送信
        user_id = obj_list.key.split('.json')[0]
        line = Line(CHANNEL_ACCESS_TOKEN, user_id)
        line.push_message(line_message)


def process_user_message(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(USER_ID)
    print(event)
    print(context)

    body = json.loads(event.get('body'))
    print(body)

    user_id = body['events'][0]['source']['userId']
    message = body['events'][0]['message']['text']

    print(user_id)
    print(message)

    line = Line(CHANNEL_ACCESS_TOKEN, user_id)
    line.push_message(message)



def __make_periodically_push_message(tasks):
    """Make periodically push message
    :param tasks: tasks
    :return: periodically push message
    """
    message = ''
    message += '今日のタスクは以下の通りです。\n'
    for task in tasks:
        message += task['task_name'] + '\n'
    return message
