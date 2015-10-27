# coding: utf-8
from datetime import datetime
import logging
import logstash
import json
import socket

from .base import BaseReporter, CheckResultCode

__all__ = ['LogstashReporter']


class LogstashSender(object):
    """
    Logstash report sender
    """
    def __init__(self, host, port):
        """
        Create new LogstashSender using given `host` and `port`.
        """
        logger = logging.getLogger('pymon2-logstash-logger')
        logger.setLevel(logging.INFO)
        logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))
        self._logger = logger

    def send_message(self, result, data):
        """
        Send message to Logstash instance.
        """
        res_data = result.data or "{}"
        try:
            res_data = json.loads(res_data)
        except ValueError:
            res_data = {}
        data.update(res_data)

        return self.get_log_method(result.code)(result.message,
                                                extra=data)

    def get_log_method(self, code):
        """
        Return suitable `self.logger` method based on code.
        """
        if code == CheckResultCode.SUCCESS:
            return self.logger.debug
        elif code == CheckResultCode.INFO:
            return self.logger.info
        elif code == CheckResultCode.FAILURE:
            return self.logger.error
        else:
            return self.logger.warning

    @property
    def logger(self):
        """
        Logstash logger
        """
        return self._logger


class LogstashReporter(BaseReporter):
    """
    Reporter sending messages with failed checks data to Logstash
    """
    def __init__(self, host, port, **optionals):
        """
        Create new LogstashReporter.

        :param host: Logstash instance host
        :param port: Logstash instance port
        :param optionals: optional parameters
        """
        super(LogstashReporter, self).__init__(**optionals)
        self._sender = LogstashSender(host, port)

    def report(self, result):
        """
        Report failed check.
        """
        if result is None:
            # TODO send|log unknown check result info
            return
        if result.code >= self.report_level:
            self._sender.send_message(**self.compose_message(result))

    def compose_message(self, result):
        """
        Prepare all data needed for LogstashSender.
        """
        hostname = socket.getfqdn()
        error_time = datetime.now()

        return {
            'result': result,
            'data': {
                'hostname': hostname,
                'check_name': result.check_name,
                'error_time': error_time.isoformat(),
            }
        }
