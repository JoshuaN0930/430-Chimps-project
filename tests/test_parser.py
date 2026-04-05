import pytest
from src.lexer.tokenizer import tokenize
from src.parser.parser import Parser
from src.parser.parser import *

# helper func for tokenizing input and getting back its AST
def parse(source: str):
    tokens = tokenize(source)
    return Parser(tokens).parse_program()


"""
    test for type::= int, void, struct name, (*type) pointer
"""
@pytest.mark.parametrize("source, expected", [
    ("int", IntType()),
    ("void", VoidType()),
    ("Node", StructType(name="Node")),
    ("(*int)", PointerType(inner=IntType())),
], ids=["int type", "void type", "struct type", "pointer type"])
def test_type(source, expected):
    token = tokenize(source)
    parseTok = Parser(token)
    result = parseTok.parse_type()
    assert result == expected

"""
    test for rule param::= (type var)
    
"""
@pytest.mark.parametrize("source, expected", [
    ("(int x)", Param(type=IntType(), name="x")),
    ("(void y)", Param(type=VoidType(), name="y")),
    ("(Node z)", Param(type=StructType(name="Node"), name="z")),
    ("((*int) p)", Param( type=PointerType(inner=IntType()), name="p"))
], ids=["int param", "void param", "struct param", "pointer param"])
def test_param(source, expected):
    tokens = tokenize(source)
    parser = Parser(tokens)
    result = parser.parse_param()
    assert result == expected

"""
    test for structDef ::= (struct structname param*)
"""
def test_struct_def():
    result = parse("(struct Node (int head))")
    assert result.structs == [StructDef(name="Node", params=[Param(type=IntType(), name="head")])]

"""
    test for funcDef ::= (func funcname (param*) type stmt* )
"""

def test_func_def():
    result = parse("(func addNums ((int x) (int y)) int (return (+ x y)))")
    assert result.funcs == [
        FuncDef(
            name="addNums",
            params=[
                Param(type=IntType(), name="x"), 
                Param(type=IntType(), name="y")
            ],
            Rtype=IntType(),
            body=[
                ReturnStmt(exp=BinaryOpExp(
                    op=AddOp(),
                    first_exp=LhsExp(lhs=VarAssign(var="x")),
                    second_exp=LhsExp(lhs=VarAssign(var="y"))
                ))
            ]
        )
    ]

"""
    test for rule stmt::= (vardec type var)
"""

@pytest.mark.parametrize("source, expected", [
    ("(vardec int x)", VarDecStmt(type=IntType(), name="x")),
    ("(vardec void y)", VarDecStmt(type=VoidType(), name="y")),
    ("(vardec Node z)", VarDecStmt(type=StructType(name="Node"), name="z")),
    ("(vardec (*int) p)", VarDecStmt(type=PointerType(inner=IntType()), name="p"))
], ids=["int vardec", "void vardec", "struct vardec", "pointer vardec"])
def test_vardec(source, expected):
    result = parse(source)
    assert result.stmts == [expected]

