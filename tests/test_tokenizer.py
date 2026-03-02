from src.lexer.token import TokenType
from src.lexer.tokenizer import tokenize

def test_minus():
    tokens = tokenize('-')


    assert len(tokens) == 1
    assert tokens[0].type == TokenType.Minus

def test_notEqual():
    tokens = tokenize('!=')

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.NEQ