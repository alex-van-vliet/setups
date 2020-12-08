from io import StringIO
from typing import List

import pytest

from helpers.parsing.lexer import Lexer, Token
from helpers.parsing.lexer_error import LexerError
from helpers.parsing.word import Word, Raw, Variable, Quoted


@pytest.mark.parametrize(['input', 'expected'], [
    pytest.param(';', [Token.separator()], id="semicolon"),
    pytest.param('a', [Token.word(Word([Raw('a')])), Token.separator()], id="one letter"),
    pytest.param('test', [Token.word(Word([Raw('test')])), Token.separator()], id="several letters"),
    pytest.param('test123_:=&@', [Token.word(Word([Raw('test123_:=&@')])), Token.separator()],
                 id="many regular characters"),
    pytest.param('first_word second_word',
                 [Token.word(Word([Raw('first_word')])), Token.word(Word([Raw('second_word')])), Token.separator()],
                 id="two words"),
    pytest.param('first_word    second_word',
                 [Token.word(Word([Raw('first_word')])), Token.word(Word([Raw('second_word')])), Token.separator()],
                 id="two words several spaces"),
    pytest.param('first_word second_word third_word fourth_word_with_123_weird@:_characters',
                 [Token.word(Word([Raw('first_word')])), Token.word(Word([Raw('second_word')])),
                  Token.word(Word([Raw('third_word')])),
                  Token.word(Word([Raw('fourth_word_with_123_weird@:_characters')])),
                  Token.separator()],
                 id="many words"),

    pytest.param(';',
                 [Token.separator()],
                 id="comma"),
    pytest.param('first ; second',
                 [Token.word(Word([Raw('first')])), Token.separator(), Token.word(Word([Raw('second')])),
                  Token.separator()],
                 id="comma between two words with spaces"),
    pytest.param('first;second',
                 [Token.word(Word([Raw('first')])), Token.separator(), Token.word(Word([Raw('second')])),
                  Token.separator()],
                 id="comma between two words without spaces"),

    pytest.param('\n',
                 [],
                 id="newline"),

    pytest.param('',
                 [],
                 id="nothing"),

    pytest.param('first second\nthird',
                 [Token.word(Word([Raw('first')])), Token.word(Word([Raw('second')])), Token.separator(),
                  Token.word(Word([Raw('third')])), Token.separator()],
                 id="two lines with words"),
    pytest.param('first second\nthird\n',
                 [Token.word(Word([Raw('first')])), Token.word(Word([Raw('second')])), Token.separator(),
                  Token.word(Word([Raw('third')])), Token.separator()],
                 id="two lines with words"),

    pytest.param('first second;\nthird\n',
                 [Token.word(Word([Raw('first')])), Token.word(Word([Raw('second')])), Token.separator(),
                  Token.word(Word([Raw('third')])), Token.separator()],
                 id="separator at end of line"),

    pytest.param('${var}\n',
                 [Token.word(Word([Variable('var')])), Token.separator()],
                 id="a variable"),
    pytest.param('${my  variable123}\n',
                 [Token.word(Word([Variable('my  variable123')])), Token.separator()],
                 id="a variable with spaces"),

    pytest.param('"quotes"\n',
                 [Token.word(Word([Quoted([Raw('quotes')])])), Token.separator()],
                 id="a quoted word"),
    pytest.param('"first   word123"\n',
                 [Token.word(Word([Quoted([Raw('first   word123')])])), Token.separator()],
                 id="a quoted word with spaces"),
    pytest.param('"first  ${var} word123"\n',
                 [Token.word(Word([Quoted([Raw('first  '), Variable('var'), Raw(' word123')])])), Token.separator()],
                 id="a quoted word with a variable"),

    pytest.param('# This is a test',
                 [],
                 id="only a comment"),
    pytest.param('# This is a test\n# This is a second test',
                 [],
                 id="two comments on two lines"),
    pytest.param('myword # This is a test',
                 [Token.word(Word([Raw('myword')])), Token.separator()],
                 id="a command after words"),
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
