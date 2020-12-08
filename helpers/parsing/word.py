from typing import Union, List

from helpers.parsing.characters import is_whitespace, is_special
from helpers.parsing.lexer_error import LexerError


class Node:
    def apply(self, visitor):
        name = ''.join((f"_{c.lower()}" if c.isupper() else c) for c in self.__class__.__name__).lstrip('_')
        fun = getattr(visitor, f"visit_{name}")
        fun(self)


def parse_escaped(line: str, i: int):
    i += 1
    if i == len(line):
        raise LexerError("missing escaped character", line)
    characters = {
        'n': '\n', 't': '\t', '$': '$', '\\': '\\', '"': '"', 'a': '\a', 'b': '\b', 'f': '\f', 'r': '\r', 'v': '\v',
    }
    try:
        return i + 1, characters[line[i]]
    except KeyError:
        raise LexerError("invalid escaped character", line)


class Variable(Node):
    name: str

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'${{{self.name}}}'

    def __repr__(self):
        return f'Variable(name={repr(self.name)})'

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def parse(cls, line: str, i: int):
        i += 1
        if i == len(line) or line[i] != '{':
            raise LexerError("missing variable start", line)
        i += 1
        name = ''
        while i < len(line) and line[i] != '}':
            name += line[i]
            i += 1
        if i == len(line):
            raise LexerError("missing variable end", line)
        i += 1
        return i, cls(name)


class Raw(Node):
    value: str

    def __init__(self, value):
        self.value = value

    def __str__(self):
        s = ''
        characters = {
            '\n': '\\n',
            '\t': '\\t',
            '$': '\\$',
            '\\': '\\\\',
            '"': '\\"',
            '\a': '\\a',
            '\b': '\\b',
            '\f': '\\f',
            '\r': '\\r',
            '\v': '\\v',
        }
        for char in self.value:
            if char in characters:
                s += characters[char]
            else:
                s += char
        return s

    def __repr__(self):
        return f'Raw(value={repr(self.value)})'

    def __eq__(self, other):
        if not isinstance(other, Raw):
            return False
        return self.value == other.value

    def __ne__(self, other):
        return not (self == other)


class Quoted(Node):
    segments: List[Union[Variable, Raw]]

    def __init__(self, segments):
        self.segments = segments

    def __str__(self):
        s = '"'
        for segment in self.segments:
            s += str(segment)
        s += '"'
        return s

    def __repr__(self):
        return f'Quoted(segments={repr(self.segments)})'

    def __eq__(self, other):
        if not isinstance(other, Quoted):
            return False
        return self.segments == other.segments

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def parse(cls, line: str, i: int):
        tokens = []
        current_token = ''
        i += 1
        while i < len(line) and line[i] != '"':
            if line[i] == '$':
                if current_token:
                    tokens.append(Raw(current_token))
                    current_token = ''
                i, variable = Variable.parse(line, i)
                tokens.append(variable)
            elif line[i] == '\\':
                i, subtoken = parse_escaped(line, i)
                current_token += subtoken
            else:
                current_token += line[i]
                i += 1
        if i == len(line):
            raise LexerError("missing quote end", line)
        i += 1
        if current_token:
            tokens.append(Raw(current_token))
        return i, cls(tokens)


class Word(Node):
    segments: List[Union[Raw, Variable]]

    def __init__(self, segments):
        self.segments = segments

    def __str__(self):
        return ''.join(str(segment) for segment in self.segments)

    def __repr__(self):
        return f'Word(segments={repr(self.segments)})'

    def __eq__(self, other):
        if not isinstance(other, Word):
            return False
        return self.segments == other.segments

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def parse(cls, line: str, i: int):
        tokens = []
        current_token = ''
        while i < len(line) and not is_whitespace(line[i]) and not is_special(line[i]):
            if line[i] == '"':
                if current_token:
                    tokens.append(Raw(current_token))
                    current_token = ''
                i, quoted = Quoted.parse(line, i)
                tokens.append(quoted)
            elif line[i] == '$':
                if current_token:
                    tokens.append(Raw(current_token))
                    current_token = ''
                i, variable = Variable.parse(line, i)
                tokens.append(variable)
            elif line[i] == '\\':
                i, subtoken = parse_escaped(line, i)
                current_token += subtoken
            else:
                current_token += line[i]
                i += 1
        if current_token:
            tokens.append(Raw(current_token))

        return i, Word(tokens)
