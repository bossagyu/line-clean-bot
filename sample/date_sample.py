from datetime import datetime
import json
import pytz

# 現在の日時を取得
now = datetime.now()
print(now)

start_date = datetime(2020, 1, 1)
print(start_date)

delta = (now - start_date).days

print(delta)

with open('../test/data/s3_test_file.json', 'r') as f:
    result = json.load(f)

# 日付と時刻の文字列
date_string = "2024-01-07 19:44:24.885866"
# 日付と時刻のフォーマット
date_format = "%Y-%m-%d %H:%M:%S"

print(result['tasks'][0]['updated_at'])
result_time = datetime.strptime(result['tasks'][0]['updated_at'], date_format)
tokyo_timezone = pytz.timezone('Asia/Tokyo')
task_time = tokyo_timezone.localize(result_time)

print(task_time)