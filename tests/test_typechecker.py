import pytest
from src.typechecker.typechecker import Typechecker
from src.parser.nodes import *


def typechecker_tester(struct_dict=None, func_dict=None):
    typechecker = Typechecker(Program([], [], []))
    typechecker.struct_dict = struct_dict or {}
    typechecker.func_dict = func_dict or {}
    return typechecker


@pytest.mark.parametrize(
    "lhs, env, struct_dict, expected",
    [
        (
            VarAssign("x"),
            {"x": IntType()},
            {},
            IntType()
        ),
        (
            FieldStructAssign(VarAssign("first"), "value"),
            {"first": StructType("Node")},
            {"Node": {"value": IntType()}},
            IntType()
        ),
        (
            AssignToAddress(VarAssign("p")),
            {"p": PointerType(IntType())},
            {},
            IntType()
        ),
    ]
)
def test_typecheck_lhs(lhs, env, struct_dict, expected):
    test = typechecker_tester(struct_dict= struct_dict)
    result = test.typecheck_lhs(lhs, env)
    assert result == expected


@pytest.mark.parametrize(
    "stmt, env, return_type, expected_env",
    [
            # (vardec int sum)
        (
            VarDecStmt(type=IntType(), name='sum'),
            {},
            VoidType(),
            {"sum": IntType()}
        ),
            # (assign num 1)
        (
            AssignStmt(lhs= VarAssign(var= "num") ,exp= IntLiteralExp(int_value= 1)),
            {"num": IntType()},
            VoidType(),
            {"num": IntType()}
        ),
            # (while true
            #   (block
            #       (vardec int x)))
        (
            WhileStmt(
                exp=BooleanLiteralExp(True),
                stmt=BlockStmt(stmt=[
                    VarDecStmt(type=IntType(), name="x")
                ])
            ),
            {},
            VoidType(),
            {}, # while body uses a copied env
        ),
            # (if true
            #   (block
            #     (vardec int x))
            #   (block
            #     (vardec int y)))
        (
            IfStmt(
                exp=BooleanLiteralExp(True),
                then_stmt=BlockStmt(stmt=[
                    VarDecStmt(type=IntType(), name="x")
                ]),
                else_stmt=BlockStmt(stmt=[
                    VarDecStmt(type=IntType(), name="y")
                ]),
            ),
            {},
            VoidType(),
            {},   # if/else use copied envs
        ),
            # (return 1)
        (
            ReturnStmt(exp=IntLiteralExp(int_value= 1)),
            {},
            IntType(),
            {}
        ),
            # (return)
        (
            ReturnStmt(exp=None),
            {},
            VoidType(),
            {}
        ),
            # (block
            #   (vardec int x)
            #   (assign x 1))
        (
            BlockStmt(stmt=[
                VarDecStmt(type=IntType(), name="x"),
                AssignStmt(lhs=VarAssign("x"), exp=IntLiteralExp(1)),
            ]),
            {},
            VoidType(),
            {},   # outer env should not change because block uses a copy
        ),
            # (println 5)
        (
            PrintlnStmt(exp=IntLiteralExp(5)),
            {},
            VoidType(),
            {},
        ),
            # (stmt 10)
        (
            ExpStmt(exp=IntLiteralExp(10)),
            {},
            VoidType(),
            {},
        ),
    ]
)
def test_typechecker_stmt(stmt, env, return_type, expected_env):
    typechecker = typechecker_tester()
    typechecker.typecheck_stmt(stmt, env, return_type)
    assert env == expected_env
