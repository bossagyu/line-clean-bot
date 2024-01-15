import json


def get_api_gateway_request(event, context):
    print("event: ")
    print(event)
    print("context: ")
    print(context)
    print("aaaaaaa")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda2!')
    }
