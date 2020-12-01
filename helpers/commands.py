from pathlib import Path
from subprocess import Popen
from typing import List
from shutil import copy

from helpers.colors import rgb, number, reset
from helpers.parser import parse


def run_command(directory: Path, arguments: List[str]):
    """
    Runs a command
    :param directory: The setup directory
    :param arguments: The command arguments
    """
    if len(arguments) == 0:
        raise ValueError("invalid arguments for command")
    process = Popen(arguments)
    process.wait()
    if process.returncode != 0:
        raise ValueError(f"command returned a non-zero exit code: {process.returncode}")


def run_file(directory: Path, arguments: List[str]):
    """
    Copies a file from the setup directory
    :param directory: The setup directory
    :param arguments: The command arguments
    """
    if len(arguments) != 1:
        raise ValueError("invalid arguments for file")
    file = directory / arguments[0]
    copy(file, ".")


def run_echo(directory: Path, arguments: List[str]):
    """
    Echo the arguments
    :param directory: The setup directory
    :param arguments: The command arguments
    """
    print(' '.join(arguments))


def run(directory: Path, command: str):
    """
    Run a command
    :param directory: The setup directory
    :param command: The command
    :return: The result from the command, if there is one
    """
    commands = {
        'command': run_command,
        'file': run_file,
        'echo': run_echo,
    }

    def variables(name: str) -> str:
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
        raise ValueError(f'variable {name} not found')

    command = list(parse(command, variables))
    return commands[command[0]](directory, command[1:])
