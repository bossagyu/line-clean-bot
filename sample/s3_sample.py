import boto3
import json

s3 = boto3.resource('s3')
bucket = s3.Bucket('bossagyu-lambda-line-clean-bot')
object = bucket.Object('s3_test_file.json')
response = object.get()
body = response['Body'].read().decode('utf-8')
str = '{"message": "s3のデータですこんにちは。"}'

print(str)
print(body)
json = json.loads(body)
print(json)
print(json['message'])