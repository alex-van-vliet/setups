from enum import Enum
from typing import Optional, TextIO


def is_whitespace(char):
    return char == ' '


def is_special(char):
    return char in [';']


class TOKEN(Enum):
    NONE = 0
    END = 1
    SEPARATOR = 2
    WORD = 3


class Token:
    type: TOKEN
    value: Optional[str]

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Token(type={repr(self.type)}, value={repr(self.value)})"

    @classmethod
    def none(cls):
        return cls(TOKEN.NONE)

    @classmethod
    def end(cls):
        return cls(TOKEN.END)

    @classmethod
    def separator(cls):
        return cls(TOKEN.SEPARATOR)

    @classmethod
    def word(cls, word):
        return cls(TOKEN.WORD, word)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value

    def __ne__(self, other):
        return not (self == other)


class LexerError(BaseException):
    error: str
    line: str

    def __init__(self, error, line):
        self.error = error
        self.line = line

    def __str__(self):
        return f"{self.error} on line {repr(self.line)}"


class Lexer:
    file: TextIO
    pos: int
    line: str

    token: Token

    def __init__(self, file):
        self.file = file
        self.line = ''
        self.pos = 0
        self.token = Token.none()

        self.eat()

    def current(self):
        return self.token

    def eat_escaped(self):
        self.pos += 1
        if self.pos == len(self.line):
            raise LexerError("missing escaped character", self.line)
        if self.line[self.pos] not in ['n', 't', '$', '\\', '"', 'a', 'b', 'f', 'r', 'v']:
            raise LexerError("invalid escaped character", self.line)
        self.pos += 1

    def eat_quoted(self):
        self.pos += 1
        while self.pos < len(self.line) and self.line[self.pos] != '"':
            if self.line[self.pos] == '$':
                self.eat_variable()
            elif self.line[self.pos] == '\\':
                self.eat_escaped()
            else:
                self.pos += 1
        if self.pos == len(self.line):
            raise LexerError("missing quote end", self.line)
        self.pos += 1

    def eat_variable(self):
        self.pos += 1
        if self.pos == len(self.line) or self.line[self.pos] != '{':
            raise LexerError("missing variable start", self.line)
        self.pos += 1
        while self.pos < len(self.line) and self.line[self.pos] != '}':
            self.pos += 1
        if self.pos == len(self.line):
            raise LexerError("missing variable end", self.line)
        self.pos += 1

    def eat_str(self):
        while self.pos < len(self.line) and not is_whitespace(self.line[self.pos]) and not is_special(
                self.line[self.pos]):
            if self.line[self.pos] == '"':
                self.eat_quoted()
            elif self.line[self.pos] == '$':
                self.eat_variable()
            elif self.line[self.pos] == '\\':
                self.eat_escaped()
            else:
                self.pos += 1

    def eat_once(self):
        if self.token == TOKEN.END:
            return self.token

        while self.pos < len(self.line) and is_whitespace(self.line[self.pos]):
            self.pos += 1

        if self.pos == len(self.line):
            if self.token.type == TOKEN.SEPARATOR or self.token.type == TOKEN.NONE:
                self.pos = 0
                self.line = self.file.readline()
                if self.line == '':
                    self.token = Token.end()
                    return self.token
                if self.line[-1] == '\n':
                    self.line = self.line[:-1]
                return self.eat_once()
            else:
                self.token = Token.separator()
                return self.token
        if self.line[self.pos] == '#':
            self.pos = len(self.line)
            return self.eat_once()
        elif self.line[self.pos] == ';':
            self.pos += 1
            self.token = Token.separator()
            return self.token
        else:
            start = self.pos
            self.eat_str()
            self.token = Token.word(self.line[start:self.pos])
            return self.token

    def eat(self):
        return self.eat_once()
