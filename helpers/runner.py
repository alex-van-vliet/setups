import sys
from pathlib import Path
from typing import Mapping, List

from helpers.colors import rgb, number, reset
from helpers.commands.abstract_command import AbstractCommand
from helpers.commands.ask import Ask
from helpers.commands.command import Command
from helpers.commands.echo import Echo
from helpers.commands.file import File
from helpers.commands.set import Set
from helpers.parsing.parser import Sequence as SequenceNode, Command as CommandNode


class PrinterVisitor:
    def visit_command(self, command: CommandNode):
        print(' '.join(command.arguments), end='')

    def visit_sequence(self, sequence: SequenceNode):
        for command in sequence.commands:
            command.apply(self)
            print()


class RunnerVisitor:
    runner: 'Runner'
    exit: int

    def __init__(self, runner):
        self.runner = runner
        self.exit = 0

    def visit_command(self, command: CommandNode):
        print('> ' + ' '.join(command.arguments))
        self.exit = self.runner(command.arguments)

    def visit_sequence(self, sequence: SequenceNode):
        for command in sequence.commands:
            command.apply(self)
            if self.exit != 0:
                break


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

    def run(self, ast: SequenceNode):
        """
        Run an ast
        :param ast: The ast
        :return: The result from the commands
        """
        visitor = RunnerVisitor(self)
        ast.apply(visitor)
        return visitor.exit

    def __call__(self, command: List[str]):
        """
        Run a command
        :param command: The command
        :return: The result from the command, if there is one
        """
        arguments = [self.resolve(argument) for argument in command]
        try:
            command = self.commands[arguments[0]]
        except KeyError:
            raise ValueError(f'invalid command {arguments[0]}')
        arguments = command.parse(arguments[1:])
        try:
            result = command(self, **arguments)
            return 0 if result is None else result
        except ValueError as e:
            print(f"{number(1)}{str(e).capitalize()}{reset()}", file=sys.stderr)
            return 1

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

    def resolve(self, argument: str):
        """
        Resolve an argument, meaning expand variables, escaped characters...
        :param argument: The argument to resolve
        :return: The resolved argument
        """

        def resolve_variable(i: int):
            i += 1
            if argument[i] != '{':
                raise ValueError("invalid character after $")
            i += 1
            name = ''
            while i < len(argument) and argument[i] != '}':
                if argument[i] == '\\':
                    i, subtoken = resolve_escaped(i)
                    name += subtoken
                else:
                    name += argument[i]
                    i += 1
            if i == len(argument):
                raise ValueError("missing closing }")
            i += 1
            return i, self.get_variable(name)

        def resolve_escaped(i: int):
            i += 1
            if i == len(argument):
                raise ValueError("missing character after \\")
            characters = {
                'n': '\n',
                't': '\t',
                '$': '$',
                '\\': '\\',
                '"': '"',
                'a': '\a',
                'b': '\b',
                'f': '\f',
                'r': '\r',
                'v': '\v',
            }
            if argument[i] in characters:
                return i + 1, characters[argument[i]]
            raise ValueError('invalid character after \\')

        def resolve_quotes(i: int):
            token = ''
            i += 1
            while i < len(argument) and argument[i] != '"':
                if argument[i] == '\\':
                    i, subtoken = resolve_escaped(i)
                    token += subtoken
                elif argument[i] == '$':
                    i, subtoken = resolve_variable(i)
                    token += subtoken
                else:
                    token += argument[i]
                    i += 1
            if i == len(argument):
                raise ValueError("missing closing \"")
            i += 1
            return i, token

        def resolve_str(i: int):
            token = ''
            while i < len(argument):
                if argument[i] == '"':
                    i, subtoken = resolve_quotes(i)
                    token += subtoken
                elif argument[i] == '$':
                    i, subtoken = resolve_variable(i)
                    token += subtoken
                elif argument[i] == '\\':
                    i, subtoken = resolve_escaped(i)
                    token += subtoken
                else:
                    token += argument[i]
                    i += 1
            return i, token

        return resolve_str(0)[1]
