import os

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('USER_ID')


def push_message_periodically(event, context):
    print(CHANNEL_ACCESS_TOKEN)
    print(USER_ID)
    print(event)
    print(context)
    line = Line(USER_ID)
    line.push_message("Hello World")


class Line:
    def __init__(self, to):
        """Initiate line class
        :param to: user id
        """
        self.line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
        self.to = to

    def push_message(self, message):
        """Push messages to specified user
        :param message: messages
        """
        try:
            self.line_bot_api.push_message(self.to, TextSendMessage(text=message))

        except LineBotApiError as e:
            print(e.status_code)
            print(e.error.message)
            print(e.error.details)
