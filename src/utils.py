# -*- coding: utf-8 -*-
import subprocess
from subprocess import PIPE

from functools import wraps
from logging import getLogger

logger = getLogger(__name__)


def cmd_exists(cmd):
    """
    Check if `cmd` can be called.

    :type cmd: str
    """
    return subprocess.call(
        ["which", cmd],
        stdout=PIPE,
        stderr=PIPE) == 0


def need_cmds(*cmds):
    """
    Create decorator, that runs wrapped function only if `cmds` is available
    in this environment.

    :raises RuntimeError: if any cmd from `cmds` is not present
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            missing = filter(lambda cmd: not cmd_exists(cmd), cmds)
            if missing:
                raise RuntimeError(
                    'Cannot run `{0}` without following binaries: {1}'.format(
                        f.__name__, missing
                    )
                )
            return f(*args, **kwargs)
        return wrapped
    return decorator


def execute_cmd(cmd, stdin_text=None):
    """
    Execute `cmd` and return its output.

    :param cmd: command as single string or as list of arguments
    :type cmd: str | list of str
    """
    process = subprocess.Popen(
        cmd,
        shell=isinstance(cmd, str),  # shell mode should be on if `cmd` is str
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
    )
    str_stdout, str_stderr = process.communicate(stdin_text)

    logger.debug('%s stdout: %s', cmd, str_stdout)
    logger.debug('%s stderr: %s', cmd, str_stderr)
    return str_stdout
