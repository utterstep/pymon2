# coding: utf-8
from datetime import datetime
import requests
import socket

from .base import BaseReporter, CheckResultCode

__all__ = ['MailgunReporter']


class MailgunSender(object):
    """
    Simple email sender based on Mailgun API
    """
    MAILGUN_URL = "https://api.mailgun.net/v3/{domain}/messages"

    def __init__(self, domain, api_key):
        """
        Create new sender for given mailgun `domain` and `api_key`.
        """
        self._send_url = self.MAILGUN_URL.format(domain=domain)
        self._api_key = api_key

    def send_message(self, sender, to, subject, message, html=False):
        """
        Send email via Mailgun API.
        """
        return requests.post(
            self.send_url,
            auth=("api", self.api_key),
            data={
                "from": sender,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html" if html else "text": message
            })

    @property
    def send_url(self):
        """
        URL to send POSTs with message data
        """
        return self._send_url

    @property
    def api_key(self):
        """
        API key for this sender
        """
        return self._api_key


class MailgunReporter(BaseReporter):
    """
    Reporter sending email with failed checks data via Mailgun
    """
    DEFAULT_EMAIL_SUBJECT = """[{check_name}] error on {domain}"""
    DEFAULT_EMAIL_TEMPLATE = """
        <h3>{result_type} from domain {domain}</h3>
        <h4>[{check_name}]</h4>
        <time style="float:right;" datetime="{error_dt}">
            [{error_time_str}]
        </time>
        <code>{report_message}</code>
    """
    RESULT_TYPES = {
        CheckResultCode.SUCCESS: 'Report',
        CheckResultCode.INFO: 'Info message',
        CheckResultCode.FAILURE: 'Error',
    }

    def __init__(self, domain, api_key, sender, recepients, **optionals):
        """
        Create new MailgunReporter.

        :param domain: Mailgun domain
        :param api_key: Mailgun API secret key
        :param sender: Email of reports sender
        :param recepients: `list` of emails of recepients
        :param optionals: optional parameters like `custom_template`
        """
        super(MailgunReporter, self).__init__(**optionals)
        self._mg_client = MailgunSender(domain, api_key)

        self._sender = sender
        self._recepients = recepients
        self._email_subject = optionals.get('custom_subject',
                                            self.DEFAULT_EMAIL_SUBJECT)
        self._email_template = optionals.get('custom_template',
                                             self.DEFAULT_EMAIL_TEMPLATE)

    def report(self, result):
        """
        Report failed checks.
        """
        if result is None:
            # TODO send|log unknown check result info
            return
        if result.code >= self.report_level:
            self._mg_client.send_message(**self.compose_message(result))

    def compose_message(self, result):
        """
        Prepare all data needed for MailgunSender.
        """
        hostname = socket.getfqdn()
        error_time = datetime.now()

        return {
            'sender': self._sender,
            'to': self._recepients,
            'subject': self.email_subject.format(
                domain=hostname,
                check_name=result.check_name),
            'message': self.email_template.format(
                domain=hostname,
                report_message=result.message,
                check_name=result.check_name,
                error_dt=error_time,
                error_time_str=error_time.strftime('%d %b %Y, %H:%M:%S'),
                result_type=self.RESULT_TYPES.get(result.code, result.code),
            ),
            'html': True,
        }

    @property
    def email_template(self):
        return self._email_template

    @property
    def email_subject(self):
        return self._email_subject
