from io import StringIO
from typing import List

import pytest

from helpers.parsing.lexer import Lexer, Token, LexerError


@pytest.mark.parametrize(['input', 'expected'], [
    pytest.param(';', [Token.separator()], id="semicolon"),
    pytest.param('a', [Token.word('a'), Token.separator()], id="one letter"),
    pytest.param('test', [Token.word('test'), Token.separator()], id="several letters"),
    pytest.param('test123_:=&@', [Token.word('test123_:=&@'), Token.separator()], id="many regular characters"),
    pytest.param('first_word second_word', [Token.word('first_word'), Token.word('second_word'), Token.separator()],
                 id="two words"),
    pytest.param('first_word    second_word', [Token.word('first_word'), Token.word('second_word'), Token.separator()],
                 id="two words several spaces"),
    pytest.param('first_word second_word third_word fourth_word_with_123_weird@:_characters',
                 [Token.word('first_word'), Token.word('second_word'), Token.word('third_word'),
                  Token.word('fourth_word_with_123_weird@:_characters'), Token.separator()],
                 id="many words"),

    pytest.param(';',
                 [Token.separator()],
                 id="comma"),
    pytest.param('first ; second',
                 [Token.word('first'), Token.separator(), Token.word('second'), Token.separator()],
                 id="comma between two words with spaces"),
    pytest.param('first;second',
                 [Token.word('first'), Token.separator(), Token.word('second'), Token.separator()],
                 id="comma between two words without spaces"),

    pytest.param('\n',
                 [],
                 id="newline"),

    pytest.param('',
                 [],
                 id="nothing"),

    pytest.param('first second\nthird',
                 [Token.word('first'), Token.word('second'), Token.separator(), Token.word('third'), Token.separator()],
                 id="two lines with words"),
    pytest.param('first second\nthird\n',
                 [Token.word('first'), Token.word('second'), Token.separator(), Token.word('third'), Token.separator()],
                 id="two lines with words"),

    pytest.param('first second;\nthird\n',
                 [Token.word('first'), Token.word('second'), Token.separator(), Token.word('third'), Token.separator()],
                 id="separator at end of line"),

    pytest.param('${var}\n',
                 [Token.word('${var}'), Token.separator()],
                 id="a variable"),
    pytest.param('${my  variable123}\n',
                 [Token.word('${my  variable123}'), Token.separator()],
                 id="a variable with spaces"),

    pytest.param('"quotes"\n',
                 [Token.word('"quotes"'), Token.separator()],
                 id="a quoted word"),
    pytest.param('"first   word123"\n',
                 [Token.word('"first   word123"'), Token.separator()],
                 id="a quoted word with spaces"),
    pytest.param('"first  ${var} word123"\n',
                 [Token.word('"first  ${var} word123"'), Token.separator()],
                 id="a quoted word with a variable"),

    pytest.param('\\\\',
                 [Token.word('\\\\'), Token.separator()],
                 id="an escaped backslash"),
    pytest.param('\\n',
                 [Token.word('\\n'), Token.separator()],
                 id="an escaped n"),
    pytest.param('\\$',
                 [Token.word('\\$'), Token.separator()],
                 id="an escaped dollar"),
    pytest.param('\\"',
                 [Token.word('\\"'), Token.separator()],
                 id="an escaped quote"),
    pytest.param('\\a',
                 [Token.word('\\a'), Token.separator()],
                 id="an escaped a"),
    pytest.param('\\b',
                 [Token.word('\\b'), Token.separator()],
                 id="an escaped b"),
    pytest.param('\\f',
                 [Token.word('\\f'), Token.separator()],
                 id="an escaped f"),
    pytest.param('\\r',
                 [Token.word('\\r'), Token.separator()],
                 id="an escaped r"),
    pytest.param('\\v',
                 [Token.word('\\v'), Token.separator()],
                 id="an escaped v"),
])
def test_lexer_successful(input: str, expected: List[Token]):
    io = StringIO(input)
    lexer = Lexer(io)
    for token in expected:
        assert (lexer.current() == token)
        lexer.eat()
    assert lexer.current() == Token.end()


@pytest.mark.parametrize(['input', 'expected', 'error'], [
    pytest.param('"', [], 'missing quote end', id="unfinished quote"),
    pytest.param('$', [], 'missing variable start', id="unfinished quote"),
    pytest.param('${', [], 'missing variable end', id="unfinished quote"),

    pytest.param('\\', [], 'missing escaped character', id="missing escaped character"),
    pytest.param('\\z', [], 'invalid escaped character', id="wrong escaped character"),
])
def test_lexer_unsuccessful(input: str, expected: List[Token], error: str):
    io = StringIO(input)
    if not expected:
        with pytest.raises(LexerError, match=error):
            Lexer(io)
    else:
        lexer = Lexer(io)
        for i, token in enumerate(expected):
            assert (lexer.current() == token)
            if i + 1 == len(expected):
                with pytest.raises(LexerError, match=error):
                    lexer.eat()
            else:
                lexer.eat()
