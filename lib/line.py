from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage


class Line:
    def __init__(self, token, to):
        """Initiate line class
        :param to: user id
        """
        self.line_bot_api = LineBotApi(token)
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

