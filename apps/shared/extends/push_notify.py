__all__ = [
    'TeleBotPushNotify',
]

import os
import asyncio

from datetime import datetime

import telegram

from django.utils import timezone


class TeleBotPushNotify:
    @classmethod
    def pretty_datetime(cls, data=None, d_format='%d/%m/%Y, %H:%M:%S'):
        if not data:
            data = timezone.now()

        if isinstance(data, datetime):
            return data.strftime(d_format)
        return ''

    @classmethod
    def generate_msg(cls, idx, status, group_name, **kwargs):
        site_name = os.environ.get('SITE_NAME', 'XXX').upper()
        msg = f'[{site_name}][{group_name}][{str(idx)}] {str(status)}'
        for key, value in kwargs.items():
            msg += f'\n- {str(key)} : {str(value)}'
        return msg

    def __init__(self, **kwargs):
        self.token = kwargs.get('token', os.environ.get('TELEGRAM_TOKEN', None))
        self.chat_id = kwargs.get('chat_id', os.environ.get('TELEGRAM_CHAT_ID', None))

    def send_msg(self, msg):
        if self.token and self.chat_id:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._send_msg(msg=msg))

    async def _send_msg(self, msg, **kwargs):
        try:
            bot = telegram.Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id, text=msg,
                # parse_mode='Markdown'
            )
        except Exception as err:
            print(err)
