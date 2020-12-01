from typing import Callable


def get_variable(command: str, i: int, variables: Callable[[str], str]):
    """
    Parse a variable
    :param command: The command string
    :param i: The cursor in the string
    :param variables: The variables callback
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
    return i, variables(name)


def get_escaped(command: str, i: int):
    """
    Parse an escaped character
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


def get_token_quoted(command: str, i: int, variables: Callable[[str], str]):
    """
    Parse quotes
    :param command: The command string
    :param i: The cursor in the string
    :param variables: The variables callback
    :return: The index after the ending quote, the content of the quotes
    """
    token = ''
    i += 1
    while i < len(command) and command[i] != '"':
        if command[i] == '\\':
            i, subtoken = get_escaped(command, i)
            token += subtoken
        elif command[i] == '$':
            i, subtoken = get_variable(command, i, variables)
            token += subtoken
        else:
            token += command[i]
            i += 1
    if i == len(command):
        raise ValueError("missing closing \"")
    i += 1
    return i, token


def get_token(command: str, variables: Callable[[str], str]):
    """
    Parse a token
    :param command: The command string
    :param variables: The variables callback
    :return: The index after the ending quote, the content of the quotes
    """
    token = ''
    i = 0
    while i < len(command) and command[i] != ' ':
        if command[i] == '"':
            i, subtoken = get_token_quoted(command, i, variables)
            token += subtoken
        elif command[i] == '$':
            i, subtoken = get_variable(command, i, variables)
            token += subtoken
        elif command[i] == '\\':
            i, subtoken = get_escaped(command, i)
            token += subtoken
        else:
            token += command[i]
            i += 1
    return token, command[i:].lstrip(' ')


def parse(command: str, variables: Callable[[str], str]):
    """
    Parse the command by yielding all its tokens
    :param command: The command string
    :param variables: The variables callback
    """
    command = command.lstrip(' ').rstrip(' ')
    while command:
        token, command = get_token(command, variables)
        yield token
