import os
import json

from lib.s3_client import S3client
from lib.line import Line
from lib.clean_task import CleanTask
from lib.message import Message

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
        user_id = obj_list.key.split('.json')[0]

        # タスクを取得しメッセージを生成
        clean_task = CleanTask(obj_body)
        return_message = Message(clean_task, user_id)
        line_message = return_message.get_periodically_push_message()
        # メッセージを送信
        line = Line(CHANNEL_ACCESS_TOKEN, user_id)
        line.push_message(line_message)


def process_user_message(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(event)
    print(context)

    # LINEのメッセージを取得
    body = json.loads(event.get('body'))
    print(body)

    # uidとメッセージを取得
    user_id = body['events'][0]['source']['userId']
    message = body['events'][0]['message']['text']

    print(user_id)
    print(message)

    # s3からデータを取得
    s3client = S3client(BUCKET_NAME)
    obj_key = user_id + '.json'
    obj_body = s3client.get_object_body(obj_key)
    clean_task_obj = CleanTask(obj_body)

    # メッセージを処理
    message_obj = Message(clean_task_obj, user_id)
    line_return_message = message_obj.get_return_message(message)

    # メッセージがからの場合は処理を終了
    if line_return_message == "":
        return

    line = Line(CHANNEL_ACCESS_TOKEN, user_id)
    line.push_message(line_return_message)


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


