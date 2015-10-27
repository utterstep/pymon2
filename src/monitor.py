# coding: utf-8
import yaml

from tasks import PeriodicTask
from utils import execute_cmd
from reports import CheckResult, CheckResultCode, create_reporters


class ShellChecker(object):
    CODE_MAP = {
        '0': CheckResultCode.SUCCESS,
        '1': CheckResultCode.INFO,
        '2': CheckResultCode.FAILURE,
    }

    def __init__(self, name, shell_cmd, reporters):
        self._name = name
        self._reporters = reporters
        self._shell_cmd = shell_cmd

    def run_check(self):
        output = execute_cmd(self.shell_cmd).strip()
        result = self.check(output)
        self.report(result)

    def check(self, output):
        message_index = output.find(';')
        data_index = output.find(';', message_index + 1)
        data_index = data_index if data_index > 0 else len(output)

        message = output[message_index + 1:data_index]
        data = output[data_index + 1:]
        code = self.CODE_MAP.get(output[:message_index], None)

        if code is not None:
            if code == CheckResultCode.FAILURE:
                print 'FAIL', output
            return CheckResult(self.name, message, data, code)
        else:
            # unknown check result
            return None

    def report(self, result):
        for reporter in self.reporters:
            reporter.report(result)

    @property
    def reporters(self):
        return self._reporters

    @property
    def name(self):
        return self._name

    @property
    def shell_cmd(self):
        return self._shell_cmd


class ShellMonitor(PeriodicTask):
    def __init__(self, period, name, shell_cmd, reporters):
        super(ShellMonitor, self).__init__()

        self._period = period
        self._checker = ShellChecker(name, shell_cmd, reporters)

    def start(self):
        super(ShellMonitor, self).start(self._period)

    def task(self):
        self._checker.run_check()


def create_monitor(check, reporters):
    reporters_for_check = [reporters[name] for name in check['reporters']]

    return ShellMonitor(
        check['period'], check['name'], check['command'],
        reporters_for_check,
    )


def monitors_from_yaml(filename):
    with open(filename) as f:
        config = yaml.safe_load(f)

    reporter_configs = config.get('reporters')
    if not reporter_configs:
        raise ValueError('reporter_configs must be specified')

    reporters = create_reporters(reporter_configs)

    return [
        create_monitor(check, reporters) for check in config['checks']
    ]
