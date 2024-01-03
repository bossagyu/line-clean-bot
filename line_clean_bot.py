import os
import json

from lib.s3_clien import S3client
from lib.line import Line

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
        line = Line(CHANNEL_ACCESS_TOKEN, user_id)
        message_json = json.loads(obj_body)
        line.push_message(message_json['message'])
