from pathlib import Path
from typing import Mapping

from helpers.colors import rgb, number, reset
from helpers.commands.abstract_command import AbstractCommand
from helpers.commands.ask import Ask
from helpers.commands.command import Command
from helpers.commands.echo import Echo
from helpers.commands.file import File
from helpers.commands.set import Set
from helpers.parser import parse


class Runner:
    variables: Mapping[str, str]
    commands: Mapping[str, AbstractCommand]
    directory: Path

    def __init__(self, directory):
        """
        Create a runner
        :param directory: The setup directory
        """
        self.variables = {}
        self.directory = directory
        self.commands = {
            f'{command.get_name()}': command for command in [
                Ask(),
                Command(),
                Echo(),
                File(),
                Set()
            ]
        }

    def __call__(self, command: str):
        """
        Run a command
        :param command: The command
        :return: The result from the command, if there is one
        """
        arguments = list(parse(self, command))
        try:
            command = self.commands[arguments[0]]
        except KeyError:
            raise ValueError(f'invalid command {arguments[0]}')
        arguments = command.parse(arguments[1:])
        return command(self, **arguments)

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
