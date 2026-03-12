from src.lexer.token import TokenType
from src.lexer.tokenizer import tokenize

#test for '-'
def test_minus():
    tokens = tokenize('-')

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.Minus

#test for '!='
def test_notEqual():
    tokens = tokenize('!=')

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.NEQ

#test for 'int' keyword
def test_int():
    tokens = tokenize('int')

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.INT

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