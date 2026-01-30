import os

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage


class Line:
    def __init__(self, token, to):
        """Initiate line class
        :param token: LINE channel access token
        :param to: user id
        """
        self.line_bot_api = LineBotApi(token)
        self.to = to
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

    def push_message(self, message):
        """Push messages to specified user
        :param message: messages
        """
        if self.dry_run:
            print(f"[DRY_RUN] Would send to {self.to}: {message}")
            return

        try:
            self.line_bot_api.push_message(self.to, TextSendMessage(text=message))

        except LineBotApiError as e:
            print(e.status_code)
            print(e.error.message)
            print(e.error.details)
