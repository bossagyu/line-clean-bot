import boto3
from botocore.exceptions import ClientError

import json

# bucket = s3.Bucket('bossagyu-lambda-line-clean-bot')
# object = bucket.Object('U41d88cec660cef7591e767296e44df3b.json')
# response = object.get()
# body = response['Body'].read().decode('utf-8')
# print(body)
# json_obj = json.loads(body)
# print(json_obj)
#
# json_obj['tasks'][0]['duration'] = 4
# print(json_obj)
#
#
# bucket.Object('U41d88cec660cef7591e767296e44df3b.json').put(Body=json.dumps(json_obj))
# response2 = object.get()
# print(response2['Body'].read().decode('utf-8'))

# objectの存在確認
s3 = boto3.resource('s3')
try:
    s3.Object('bossagyu-lambda-line-clean-bot', 'U4188cec660cef7591e767296e44df3b.json').load()
    print("True")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print("Object does not exist.")
    else:
        print(f"An error occurred: {e}")

s3client = boto3.client('s3')
try:
    s3client.head_object(Bucket='bossagyu-lambda-line-clean-bot', Key='U41d8cec660cef7591e767296e44df3b.json')
    print("True")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print("Object does not exist.")
    else:
        print(f"An error occurred: {e}")

