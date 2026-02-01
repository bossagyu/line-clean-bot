import os
import json
from datetime import datetime, timedelta

from lib.s3_client import S3client
from lib.line import Line
from lib.clean_task import CleanTask
from lib.message import Message

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
BUCKET_NAME = os.getenv('BUCKET_NAME')


def push_message_periodically(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(event)
    print(context)

    # 現在時刻を取得（JST）
    current_time = datetime.now() + timedelta(hours=9)
    print(f"Current time (JST): {current_time}")

    # s3からデータを取得
    s3client = S3client(BUCKET_NAME)
    obj_lists = s3client.list_objects()

    # オブジェクトごとに通知判定
    for obj_list in obj_lists:
        obj_body = s3client.get_object_body(obj_list.key)
        user_id = obj_list.key.split('.json')[0]

        # タスクを取得
        clean_task = CleanTask(obj_body)

        # 通知すべきか判定
        if not clean_task.should_notify(current_time):
            print(f"Skip notification for {user_id}")
            continue

        # メッセージを生成
        return_message = Message(clean_task, user_id)
        line_message = return_message.get_periodically_push_message()

        # メッセージを送信
        line = Line(CHANNEL_ACCESS_TOKEN, user_id)
        line.push_message(line_message)

        # last_notified_atを更新
        clean_task.update_last_notified()
        s3client.update_object(obj_list.key, clean_task.get_json())
        print(f"Notification sent to {user_id}")


def process_user_message(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(event)
    print(context)

    # LINEのメッセージを取得
    body = json.loads(event.get('body'))
    print(body)

    # uidとメッセージを取得
    if body['events'][0]['source']['type'] == 'user':
        line_id = body['events'][0]['source']['userId']
    else:
        line_id = body['events'][0]['source']['groupId']

    message = body['events'][0]['message']['text']

    print(line_id)
    print(message)

    # s3からデータを取得
    s3client = S3client(BUCKET_NAME)
    obj_key = line_id + '.json'
    # オブジェクトが存在しない場合はからタスクを作成
    if not s3client.check_exist_object(obj_key):
        s3client.update_object(obj_key, '{"tasks": []}')
    obj_body = s3client.get_object_body(obj_key)
    clean_task_obj = CleanTask(obj_body)

    # メッセージを処理
    message_obj = Message(clean_task_obj, line_id)
    line_return_message = message_obj.get_return_message(message, s3client)

    # メッセージがからの場合は処理を終了
    if line_return_message == "":
        return

    # メッセージを送信
    line = Line(CHANNEL_ACCESS_TOKEN, line_id)
    line.push_message(line_return_message)

