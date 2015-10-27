# coding: utf-8
from abc import ABCMeta, abstractmethod


class CheckResultCode(object):
    """
    Constants for check result codes
    """
    SUCCESS = 0
    INFO = 1
    FAILURE = 2


class CheckResult(object):
    """
    Simple wrapper for console check results
    """
    def __init__(self, check_name, message, data, code):
        self._check_name = check_name
        self._message = message
        self._data = data
        self._code = code

    @property
    def message(self):
        """
        Human-readable message
        """
        return self._message

    @property
    def data(self):
        """
        Variouse report data in machine-readable format
        """
        return self._data

    @property
    def code(self):
        """
        Severity level code of result
        """
        return self._code

    @property
    def check_name(self):
        """
        Name of check
        """
        return self._check_name


class BaseReporter(object):
    """
    Abstract base class for reporter.
    """
    __metaclass__ = ABCMeta
    DEFAULT_REPORT_LEVEL = CheckResultCode.FAILURE

    def __init__(self, **optionals):
        self._report_level = optionals.get('report_level',
                                           self.DEFAULT_REPORT_LEVEL)

    @abstractmethod
    def report(self, result):
        """
        Stub just to show interface that reporter should have.
        """
        raise NotImplementedError

    @property
    def report_level(self):
        return self._report_level
