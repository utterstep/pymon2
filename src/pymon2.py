#!/usr/bin/python
# coding: utf-8
import argparse
import os
from time import sleep

from monitor import monitors_from_yaml

DEFAULT_CONFIG_DIRECTORY = '/etc/pymon2'


def get_config_files(config_directory):
    config_files = []
    for current_dir, dirs, files in os.walk(config_directory):
        for f in files:
            if f.endswith('.conf.yaml'):
                config_files.append(os.path.join(current_dir, f))

    return config_files


def create_monitors(config_files):
    monitors = []
    for config_file in config_files:
        monitors.extend(monitors_from_yaml(config_file))

    return monitors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config-directory',
        help='config directory path',
        default=DEFAULT_CONFIG_DIRECTORY,
        type=str
    )
    config_directory = parser.parse_args().config_directory

    config_files = get_config_files(config_directory)
    monitors = create_monitors(config_files)

    for monitor in monitors:
        monitor.start()

    try:
        while True:
            sleep(1)
    finally:
        for monitor in monitors:
            monitor.stop()


if __name__ == '__main__':
    main()
