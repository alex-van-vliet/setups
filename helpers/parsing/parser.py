from typing import Union, List

from helpers.parsing.lexer import Lexer, TOKEN
from helpers.parsing.parser_error import ParserError


class Node:
    def apply(self, visitor):
        name = ''.join((f"_{c.lower()}" if c.isupper() else c) for c in self.__class__.__name__).lstrip('_')
        fun = getattr(visitor, f"visit_{name}")
        fun(self)


class Command(Node):
    arguments: List[str]

    def __init__(self, arguments=None):
        self.arguments = [] if arguments is None else arguments

    def append(self, argument: str):
        self.arguments.append(argument)
        return self

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f'Command(arguments={repr(self.arguments)})'

    def __eq__(self, other):
        if not isinstance(other, Command):
            return False
        return self.arguments == other.arguments

    def __ne__(self, other):
        return not (self == other)


class Sequence(Node):
    commands: List[Union[Command]]

    def __init__(self, commands=None):
        self.commands = [] if commands is None else commands

    def append(self, command: Union[Command]):
        self.commands.append(command)
        return self

    def __str__(self):
        return repr(self)

    def __repr__(self):
        commands = ",\n".join(f'    {c}' for c in self.commands)
        return f'Sequence(commands=[\n{commands}\n])'

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False
        return self.commands == other.commands

    def __ne__(self, other):
        return not (self == other)


class Parser:
    lexer: Lexer

    def __init__(self, lexer):
        self.lexer = lexer

    def parse_command(self):
        command = Command()
        command.append(self.lexer.current().value)
        self.lexer.eat()
        while self.lexer.current().type not in [TOKEN.SEPARATOR, TOKEN.END]:
            command.append(self.lexer.current().value)
            self.lexer.eat()
        self.lexer.eat()
        return command

    def parse_sequence_element(self):
        if self.lexer.current().type == TOKEN.WORD:
            return self.parse_command()
        else:
            raise ParserError("unexpected token", self.lexer.current())

    def parse_sequence(self):
        commands = Sequence()
        while self.lexer.current().type != TOKEN.END:
            if self.lexer.current().type == TOKEN.WORD:
                element = self.parse_sequence_element()
                commands.append(element)
            elif self.lexer.current().type == TOKEN.SEPARATOR:
                self.lexer.eat()
            else:
                raise ParserError("unexpected token", self.lexer.current())
        return commands

    def parse(self):
        return self.parse_sequence()
