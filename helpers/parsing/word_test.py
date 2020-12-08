import pytest

from helpers.parsing.lexer_error import LexerError
from helpers.parsing.word import Word, Raw, Quoted, Variable


@pytest.mark.parametrize(['input', 'expected'], [
    pytest.param('test', Word([Raw('test')]), id="simple"),
    pytest.param('"test"', Word([Quoted([Raw('test')])]), id="simple quotes"),
    pytest.param('${test}', Word([Variable('test')]), id="simple variable"),
    pytest.param('"${test}"', Word([Quoted([Variable('test')])]), id="simple quoted variable"),

    pytest.param('first"second"', Word([Raw('first'), Quoted([Raw('second')])]), id="mixed not quoted and quoted"),
    pytest.param('"first"second', Word([Quoted([Raw('first')]), Raw('second')]), id="mixed quoted and not quoted"),
    pytest.param('first${second}', Word([Raw('first'), Variable('second')]), id="mixed not quoted and variable"),
    pytest.param('${first}second', Word([Variable('first'), Raw('second')]), id="mixed variable and not quoted"),
])
def test_word_successful(input: str, expected: Word):
    i, result = Word.parse(input, 0)
    assert i == len(input)
    assert result == expected


@pytest.mark.parametrize(['raw', 'escaped'], [
    pytest.param('n', '\n', id='n'),
    pytest.param('t', '\t', id='t'),
    pytest.param('a', '\a', id='a'),
    pytest.param('b', '\b', id='b'),
    pytest.param('f', '\f', id='f'),
    pytest.param('r', '\r', id='r'),
    pytest.param('v', '\v', id='v'),

    pytest.param('\\', '\\', id='backslash'),
    pytest.param('$', '$', id='dollar'),
    pytest.param('"', '"', id='quote'),
])
def test_word_escaped(raw: str, escaped: str):
    i, result = Word.parse(f'\\{raw}', 0)
    assert i == 2
    assert result == Word([Raw(escaped)])


@pytest.mark.parametrize(['input', 'expected', 'stop'], [
    pytest.param('first second', Word([Raw('first')]), len('first'), id="two words"),
    pytest.param('"first second" third', Word([Quoted([Raw('first second')])]), len('"first second"'),
                 id="two words with quotes"),
])
def test_word_successful_stop(input: str, expected: Word, stop: int):
    i, result = Word.parse(input, 0)
    assert i == stop
    assert result == expected


@pytest.mark.parametrize(['input', 'error'], [
    pytest.param('"', 'missing quote end', id="unfinished quote"),
    pytest.param('$', 'missing variable start', id="unfinished quote"),
    pytest.param('${', 'missing variable end', id="unfinished quote"),

    pytest.param('\\', 'missing escaped character', id="missing escaped character"),
    pytest.param('\\z', 'invalid escaped character', id="wrong escaped character"),
])
def test_word_unsuccessful(input: str, error: str):
    with pytest.raises(LexerError, match=error):
        Word.parse(input, 0)
