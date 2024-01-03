import boto3
import json

s3 = boto3.resource('s3')
bucket = s3.Bucket('bossagyu-lambda-line-clean-bot')
object = bucket.Object('U41d88cec660cef7591e767296e44df3b.json')
response = object.get()
body = response['Body'].read().decode('utf-8')
str = '{"message": "s3のデータですこんにちは。"}'

print(str)
print(body)
json = json.loads(body)
print(json)
print(json['message'])