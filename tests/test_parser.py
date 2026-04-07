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
    test for lhs:: = var
                    (. lhs var)
                    (* lhs)
"""

@pytest.mark.parametrize("source, expected", [
    ("x", VarAssign(var="x")),
    ("(. x field)", FieldStructAssign(lhs=VarAssign(var="x"), var="field")), 
    ("(* x)", AssignToAddress(lhs=VarAssign(var="x")))
], ids=["lhs var", "lhs field struct", "lhs address"])
def test_lhs(source, expected):
    tokens = tokenize(source)
    parser = Parser(tokens)
    result = parser.parse_lhs()
    assert result == expected

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

"""
AssignStmt tests
"""

@pytest.mark.parametrize("source, expected", [("(assign x 5)", AssignStmt(lhs=VarAssign(var='x'), exp=IntLiteralExp(int_value=5))),
    ("(assign y false)", AssignStmt(lhs=VarAssign(var='y'), exp=BooleanLiteralExp(boolean=False))),
    ("(assign foo (+ 2 2))", AssignStmt(lhs=VarAssign(var="foo"), exp=BinaryOpExp(op=AddOp(), first_exp=IntLiteralExp(int_value=2), second_exp=IntLiteralExp(int_value=2))))
    
    ], ids=["assign int", "assign boolean", "assign Addop"])

def test_assign(source, expected):
    result = parse(source)
    assert result.stmts == [expected]

"""
    tesst for stmt:: = `(` `while` exp stmt `)` | While loops
"""
@pytest.mark.parametrize("source, expected", [
    ("(while true (vardec int x))", WhileStmt(exp=BooleanLiteralExp(boolean=True), stmt=VarDecStmt(type=IntType(), name="x"))),
    ("(while (< x 10) (assign x (+ x 1)))", WhileStmt(exp=BinaryOpExp(
        op=LessThanOp(),
        first_exp=LhsExp(lhs=VarAssign(var="x")),
        second_exp=IntLiteralExp(int_value=10)
    ),
     stmt=AssignStmt(lhs=VarAssign(var="x"), exp=BinaryOpExp(
         op=AddOp(),
         first_exp=LhsExp(lhs=VarAssign(var="x")),
         second_exp=IntLiteralExp(int_value=1)
     )))),
     ("(while (== x 1) (block (vardec int y) (assign y false)))", WhileStmt(
         exp=BinaryOpExp(
            op=EqualOp(),
            first_exp=LhsExp(lhs=VarAssign(var="x")),
            second_exp=IntLiteralExp(int_value=1)
        ),
        stmt=BlockStmt(stmt=[
                VarDecStmt(type=IntType(), name="y"),
                AssignStmt(lhs=VarAssign(var="y"), exp=BooleanLiteralExp(boolean=False))
        ])
     ))
], ids=["bool condition", "comparison condition", "equals condition"])
def test_while_stmt(source, expected):
    result = parse(source)
    assert result.stmts == [expected]


"""
    test for stmt::= `(` `if` exp stmt [stmt] `)` | if
"""

@pytest.mark.parametrize("source, expected", [
    ("(if (!= x null) (vardec int y))", IfStmt(exp=BinaryOpExp(op=NotEqualOp(), first_exp=LhsExp(lhs=VarAssign(var="x")), second_exp=NullExp()), 
                                               then_stmt=VarDecStmt(type=IntType(), name="y"), 
                                               else_stmt=None)),
    ("(if false (vardec int x) (vardec int y))", IfStmt(exp=BooleanLiteralExp(boolean=False), 
                                                        then_stmt=VarDecStmt(type=IntType(), name="x"), 
                                                        else_stmt=VarDecStmt(type=IntType(), name="y"))),
], ids=["no else stmt", "with else stmt"])
def test_if_stmt(source, expected):
    result = parse(source)
    assert result.stmts == [expected]

"""
    test for stmt:: = `(` `return` [exp] `)` | Return
"""
@pytest.mark.parametrize("source, expected", [
    ("(return 5)", ReturnStmt(exp=IntLiteralExp(int_value=5))),
    ("(return)", ReturnStmt(exp=None))
], ids=["return int", "return empty"])
def test_return_stmt(source, expected):
    result = parse(source)
    assert result.stmts == [expected]

