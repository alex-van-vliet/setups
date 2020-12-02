import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from helpers.commands import Runner


def is_variable(name: str):
    REGEX = re.compile(r'^([a-zA-Z0-9_])*$')
    return REGEX.match(name)


def get_variable(runner: 'Runner', command: str, i: int):
    """
    Parse a variable
    :param runner: The runner
    :param command: The command string
    :param i: The cursor in the string
    :return: The index after parsing the variable name, the content of the variable
    """
    i += 1
    if command[i] != '{':
        raise ValueError("invalid character after $")
    i += 1
    name = ''
    while i < len(command) and command[i] != '}':
        if command[i] == '\\':
            i += 1
            if i == len(command):
                raise ValueError("missing character after \\")
        name += command[i]
        i += 1
    if i == len(command):
        raise ValueError("missing closing }")
    i += 1
    return i, runner.get_variable(name)


def get_escaped(runner: 'Runner', command: str, i: int):
    """
    Parse an escaped character
    :param runner: The runner
    :param command: The command string
    :param i: The cursor in the string
    :return: The index after parsing the escaped character, the new character
    """
    i += 1
    if i == len(command):
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
    if command[i] in characters:
        return i + 1, characters[command[i]]

    raise ValueError('invalid character after \\')


def get_token_quoted(runner: 'Runner', command: str, i: int):
    """
    Parse quotes
    :param runner: The runner
    :param command: The command string
    :param i: The cursor in the string
    :return: The index after the ending quote, the content of the quotes
    """
    token = ''
    i += 1
    while i < len(command) and command[i] != '"':
        if command[i] == '\\':
            i, subtoken = get_escaped(runner, command, i)
            token += subtoken
        elif command[i] == '$':
            i, subtoken = get_variable(runner, command, i)
            token += subtoken
        else:
            token += command[i]
            i += 1
    if i == len(command):
        raise ValueError("missing closing \"")
    i += 1
    return i, token


def get_token(runner: 'Runner', command: str):
    """
    Parse a token
    :param runner: The runner
    :param command: The command string
    :return: The index after the ending quote, the content of the quotes
    """
    token = ''
    i = 0
    while i < len(command) and command[i] != ' ':
        if command[i] == '"':
            i, subtoken = get_token_quoted(runner, command, i)
            token += subtoken
        elif command[i] == '$':
            i, subtoken = get_variable(runner, command, i)
            token += subtoken
        elif command[i] == '\\':
            i, subtoken = get_escaped(runner, command, i)
            token += subtoken
        else:
            token += command[i]
            i += 1
    return token, command[i:].lstrip(' ')


def parse(runner: 'Runner', command: str):
    """
    Parse the command by yielding all its tokens
    :param runner: The runner
    :param command: The command string
    """
    command = command.lstrip(' ').rstrip(' ')
    while command:
        token, command = get_token(runner, command)
        yield token
