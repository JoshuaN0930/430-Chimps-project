import pytest
from src.lexer.token import TokenType, Symbol, Keyword
from src.lexer.tokenizer import tokenize


#test for detecting whitespace 
def test_whiteSpace():
    tokens = tokenize('     ')

    assert not tokens

#test for integer literal like 5,6,12 etc
def test_integerLit():
    tokens = tokenize('34')

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.INTEGER
    assert tokens[0].value == 34

#test for indentifier tokens
def test_identifier():
    tokens = tokenize('x')

    assert len(tokens) == 1
    assert tokens[0].type ==TokenType.IDENTIFIER
    assert tokens[0].value == "x"


# Runs a test on each single symbol found in token.py
@pytest.mark.parametrize("input_symbol, expected", Symbol.SINGLE.items())
def test_single_symbols(input_symbol, expected):
    tokens = tokenize(input_symbol)
    assert len(tokens) == 1
    assert tokens[0].type == expected
    assert tokens[0].value == input_symbol
    assert tokens[0].line == 1

# Test on double symbols in token.py
@pytest.mark.parametrize("input_symbol, expected", Symbol.DOUBLE.items())
def test_double_symbols(input_symbol, expected):
    tokens = tokenize(input_symbol)
    assert len(tokens) == 1
    assert tokens[0].type == expected
    assert tokens[0].value == input_symbol
    assert tokens[0].line == 1

@pytest.mark.parametrize("input_keyword, expected", Keyword.WORDS.items())
def test_keywords(input_keyword, expected):
    tokens = tokenize(input_keyword)
    assert len(tokens) == 1
    assert tokens[0].type == expected
    assert tokens[0].value == input_keyword
    assert tokens[0].line == 1