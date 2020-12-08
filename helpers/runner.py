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
from helpers.parsing.word import Word, Raw, Quoted, Variable


class RunnerVisitor:
    runner: 'Runner'
    exit: int

    def __init__(self, runner):
        self.runner = runner
        self.exit = 0

    def visit_command(self, command: CommandNode):
        print('> ' + ' '.join(str(argument) for argument in command.arguments))
        self.exit = self.runner(command.arguments)

    def visit_sequence(self, sequence: SequenceNode):
        for command in sequence.commands:
            command.apply(self)
            if self.exit != 0:
                break


class RunnerResolver:
    runner: 'Runner'
    result: str

    def __init__(self, runner):
        self.runner = runner
        self.result = ''

    def visit_word(self, word: Word):
        for segment in word.segments:
            segment.apply(self)

    def visit_raw(self, word: Raw):
        self.result += word.value

    def visit_quoted(self, quoted: Quoted):
        for segment in quoted.segments:
            segment.apply(self)

    def visit_variable(self, variable: Variable):
        self.result += self.runner.get_variable(variable.name)


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

    def resolve(self, argument: Word):
        """
        Resolve an argument, meaning expand variables, escaped characters...
        :param argument: The argument to resolve
        :return: The resolved argument
        """

        resolver = RunnerResolver(self)
        argument.apply(resolver)
        return resolver.result
