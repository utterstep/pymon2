# coding: utf-8
from abc import ABCMeta, abstractmethod


class CheckResult(object):
    """
    Simple wrapper for console check results
    """
    def __init__(self, check_name, message, success):
        self._check_name = check_name
        self._message = message
        self._success = success

    @property
    def message(self):
        """
        Human-readable message
        """
        return self._message

    @property
    def success(self):
        """
        Was result "successful" (not obligatory to report)
        or not (report as soon as possible)
        """
        return self._success

    @property
    def check_name(self):
        """
        Name of check
        """
        return self._check_name


class BaseReporter(object):
    """
    Abstract base class for reporter.

    It just shows interface that reporter should have.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def report(self, result):
        raise NotImplementedError
