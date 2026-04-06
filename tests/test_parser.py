import pytest

from src.parser.parser import Parser
from src.lexer.token import Token, TokenType
from src.lexer.tokenizer import tokenize
from src.parser.nodes import *

def parse(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse_program()

@pytest.mark.parametrize("source, expected", [("(vardec int x)", VarDecStmt(type=IntType(), name="x")),
    ("(vardec void y)", VarDecStmt(type=VoidType(), name="y")),
    ("(vardec Node z)", VarDecStmt(type=StructType(name="Node"), name="z")),
    ("(vardec (*int) p)", VarDecStmt(type=PointerType(inner=IntType()), name="p"))
], ids=["int vardec", "void vardec", "struct vardec", "pointer vardec"])

def test_vardec(source, expected):
    result = parse(source)
    assert result.stmts == [expected]

@pytest.mark.parametrize("source, expected", [("(assign x 5)", AssignStmt(lhs=VarAssign(var='x'), exp=IntLiteralExp(int_value=5))),
    ("(assign y False)", AssignStmt(lhs=VarAssign(var='y'), exp=LhsExp(lhs=VarAssign(var='False')))),
    ("(assign foo + 2 2)", AssignStmt(lhs=VarAssign(var="foo"), exp=BinaryOpExp(op=AddOp(), first_exp=IntLiteralExp(int_value=2), second_exp=IntLiteralExp(int_value=2))))
    
    ], ids=["assign int", "assign boolean", "assign Addop"])

def test_assign(source, expected):
    result = parse(source)
    assert result.stmts == [expected]