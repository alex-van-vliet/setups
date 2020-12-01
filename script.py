#!/usr/bin/env python3

import argparse
import sys

from commands.list import ListCommand
from commands.run import RunCommand


def main():
    """
    Run the script
    :return: The result of the command
    """
    commands = [
        RunCommand(),
        ListCommand(),
    ]

    parser = argparse.ArgumentParser(description='setup projects')
    subparsers = parser.add_subparsers(title="command", description="the command to run", dest="command", required=True)

    command_names = []
    for command in commands:
        name = command.get_name()
        command_names.append(name)
        subparser = subparsers.add_parser(name, help=command.get_help())
        command.setup_parser(subparser)
        subparser.set_defaults(func=command)

    arguments = sys.argv[1:]
    if arguments and arguments[0] not in command_names and not arguments[0].startswith('-'):
        arguments.insert(0, 'run')

    args = parser.parse_args(arguments)

    return args.func(**args.__dict__)


if __name__ == "__main__":
    sys.exit(main())
