import re
from pathlib import Path
from subprocess import Popen
from typing import List, Mapping
from shutil import copy

from helpers.colors import rgb, number, reset
from helpers.parser import parse


class Runner:
    variables: Mapping[str, str]
    directory: Path

    def __init__(self, directory):
        """
        Create a runner
        :param directory: The setup directory
        """
        self.variables = {}
        self.directory = directory

    def __call__(self, command: str):
        """
        Run a command
        :param command: The command
        :return: The result from the command, if there is one
        """
        commands = {
            'command': run_command,
            'file': run_file,
            'echo': run_echo,
            'set': run_set,
        }

        command = list(parse(self, command))
        return commands[command[0]](self, command[1:])

    def get_directory(self):
        """
        Get the directory
        :return: The directory
        """
        return self.directory

    def set_variable(self, name: str, value: str):
        """
        Set the value of a variable
        :param name: The name of the variable
        :param value: The value of the variable
        """
        self.variables[name] = value

    def get_variable(self, name: str):
        """
        Get the value of a variable
        :param name: The name of the variable
        :return: The value of the variable
        """
        if name.startswith('COLOR:'):
            try:
                return number(int(name[len('COLOR:'):]))
            except ValueError:
                pass

            values = name[len('COLOR:'):].split(':')
            if len(values) == 3:
                try:
                    return rgb(*(int(value) for value in values))
                except ValueError:
                    pass
        elif name == 'RESET':
            return reset()
        elif name in self.variables:
            return self.variables[name]
        raise ValueError(f'variable {name} not found')


def run_command(runner: Runner, arguments: List[str]):
    """
    Runs a command
    :param runner: The runner
    :param arguments: The command arguments
    """
    if len(arguments) == 0:
        raise ValueError("invalid arguments for command")
    process = Popen(arguments)
    process.wait()
    if process.returncode != 0:
        raise ValueError(f"command returned a non-zero exit code: {process.returncode}")


def run_file(runner: Runner, arguments: List[str]):
    """
    Copies a file from the setup directory
    :param runner: The runner
    :param arguments: The command arguments
    """
    if len(arguments) != 1:
        raise ValueError("invalid arguments for file")
    file = runner.get_directory() / arguments[0]
    copy(file, ".")


def run_echo(runner: Runner, arguments: List[str]):
    """
    Echo the arguments
    :param runner: The runner
    :param arguments: The command arguments
    """
    print(' '.join(arguments))


def run_set(runner: Runner, arguments: List[str]):
    """
    Set a variable
    :param runner: The runner
    :param arguments: The command arguments
    """
    if len(arguments) != 2:
        raise ValueError("invalid arguments for set")
    REGEX = re.compile(r'^([a-zA-Z])*')
    name = arguments[0]
    value = arguments[1]
    if not REGEX.match(name):
        raise ValueError("invalid name for variable")
    runner.set_variable(name, value)
