from typing import List

import pytest

from helpers.parsing.lexer import Token
from helpers.parsing.parser import Parser, Sequence, Command


class MockedLexer:
    selected: int
    tokens: List[Token]

    def __init__(self, tokens):
        self.tokens = tokens
        self.selected = 0

    def current(self):
        if self.selected == len(self.tokens):
            return Token.end()
        return self.tokens[self.selected]

    def eat(self):
        if self.selected == len(self.tokens):
            return Token.end()
        self.selected += 1
        return self.current()


@pytest.mark.parametrize(['input', 'expected'], [
    pytest.param([], Sequence(), id="nothing"),
    pytest.param([Token.separator()], Sequence(), id="only a separator"),
    pytest.param([Token.separator(), Token.separator(), Token.separator()], Sequence(), id="only separators"),

    pytest.param([Token.word('my word')], Sequence([Command(['my word'])]), id='a word'),
    pytest.param([Token.word('first'), Token.word('second'), Token.word('third')],
                 Sequence([Command(['first', 'second', 'third'])]),
                 id='several words'),
    pytest.param([Token.word('first'), Token.separator(), Token.word('second')],
                 Sequence([Command(['first']), Command(['second'])]),
                 id='several commands'),
])
def test_parser_successful(input: List[Token], expected: Sequence):
    lexer = MockedLexer(input)
    parser = Parser(lexer)
    assert parser.parse() == expected
