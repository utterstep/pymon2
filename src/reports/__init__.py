from .base import CheckResult, CheckResultCode
from .logstash_reporter import LogstashReporter
from .mailgun import MailgunReporter
from .telegram_channel import TelegramChannelReporter

__all__ = [
    'CheckResult', 'CheckResultCode', 'create_reporters'
]


TYPES = {
    'logstash': LogstashReporter,
    'mailgun': MailgunReporter,
    'telegram_channel': TelegramChannelReporter,
}


def create_reporters(reporter_configs):
    reporters = {}

    for reporter in reporter_configs:
        reporter_type = reporter.get('type')
        reporter_name = reporter.get('name')
        reporter_params = reporter.get('params')

        reporter_cls = TYPES.get(reporter_type)
        if not reporter_cls:
            raise ValueError('reporter type {0} is unknown'
                             .format(reporter_type))
        if not reporter_name:
            raise ValueError('reporter must have name')

        try:
            reporters[reporter_name] = reporter_cls(**reporter_params)
        except (TypeError, ValueError) as e:
            raise ValueError('some error in reporters specification: {0}'
                             .format(e))

    return reporters
