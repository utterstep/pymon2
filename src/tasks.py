# coding: utf-8
from abc import ABCMeta, abstractmethod
from threading import Timer

__all__ = ['PeriodicTask']


class PeriodicTask(object):
    """
    Abstract base class for periodically running generic tasks.

    Thread-based.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._running = False
        self._period = None

    def start(self, period, args=None, kwargs=None):
        """
        Starts task execution.
        Task will run each `period` seconds,
        untill `self.running` is falsy.
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self._running = True
        self._period = period
        self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        """
        Run one task iteration,
        checking that task is still running and its period is valid.

        If everything is OK, schedule next task run in `self.period` seconds.
        """
        if self.running and self.period:
            self.task(*args, **kwargs)

            self._timer = Timer(self.period, self.run, args, kwargs)
            self._timer.start()
        else:
            self._running = False
            self._period = None

    @abstractmethod
    def task(self, *args, **kwargs):
        """
        Implement this method, here you can specify any periodic task you wish.
        """
        raise NotImplementedError

    def stop(self):
        """
        Stops current task, cancelling next waiting thread.
        """
        self._running = False
        self._period = None

        self._timer.cancel()

    @property
    def running(self):
        """
        Indicates whether task running or not
        """
        return self._running

    @property
    def period(self):
        """
        Task period (in seconds)
        """
        return self._period
