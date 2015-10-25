# coding: utf-8
from datetime import datetime
import requests
import socket

from .base import BaseReporter, CheckResultCode

__all__ = ['TelegramChannelReporter']


class TelegramSenderBot(object):
    """
    Telegram bot only capable of sending messages
    """
    TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(self, bot_token):
        """
        Create new TelegramSenderBot using given `bot_token`.
        """
        self._send_url = self.TELEGRAM_URL.format(token=bot_token)

    def send_message(self, chat_id, message, markdown=False):
        """
        Send message to Telegram chat, group or channel.
        """
        return requests.post(
            self.send_url,
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown" if markdown else "",
            })

    @property
    def send_url(self):
        """
        Telegram API url to send POSTs with message data
        """
        return self._send_url


class TelegramChannelReporter(BaseReporter):
    """
    Reporter sending messages with failed checks data to Telegram channel
    """
    DEFAULT_MESSAGE_TEMPLATE = '''
    {result_type} from domain {domain}
    _Time:_ {error_time_str}

    *[{check_name}]* `{report_message}`
    '''.replace('    ', '')
    RESULT_TYPES = {
        CheckResultCode.SUCCESS: 'Report',
        CheckResultCode.INFO: 'Info message',
        CheckResultCode.FAILURE: 'Error'
    }

    def __init__(self, bot_token, channel, **optionals):
        """
        Create new TelegramChannelReporter.

        :param bot_token: Telegram Bot API token
        :param channel: name of Telegram channel to send reports to
        :param optionals: optional parameters like `custom_template`
        """
        super(TelegramChannelReporter, self).__init__(**optionals)
        self._tg_bot = TelegramSenderBot(bot_token)

        self._channel = channel
        self._template = optionals.get('custom_template',
                                       self.DEFAULT_MESSAGE_TEMPLATE)

    def report(self, result):
        """
        Report failed check.
        """
        if result is None:
            # TODO send|log unknown check result info
            return
        if result.code >= self.report_level:
            self._tg_bot.send_message(**self.compose_message(result))

    def compose_message(self, result):
        """
        Prepare all data needed for TelegramSenderBot.
        """
        hostname = socket.getfqdn()
        error_time = datetime.now()

        return {
            'chat_id': '@{0}'.format(self.channel),
            'message': self.template.format(
                domain=hostname,
                report_message=result.message,
                check_name=result.check_name,
                error_dt=error_time,
                error_time_str=error_time.strftime('%d %b %Y, %H:%M:%S'),
                result_type=self.RESULT_TYPES.get(result.code, result.code),
            ),
            'markdown': True,
        }

    @property
    def channel(self):
        return self._channel

    @property
    def template(self):
        return self._template
