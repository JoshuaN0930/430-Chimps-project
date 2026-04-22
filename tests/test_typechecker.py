import pytest

from src.lexer.tokenizer import tokenize
from src.parser.parser import Parser
from src.typechecker.typechecker import Typechecker
from src.parser.nodes import *


def typechecker_tester(program=None, struct_dict=None, func_dict=None):
    typechecker = Typechecker(program or Program([], [], []))
    typechecker.struct_dict = struct_dict or {}
    typechecker.func_dict = func_dict or {}
    return typechecker

# tests get_struct
@pytest.mark.parametrize(
    "program_source, expected_struct_dict",
    [
        (
            "(struct Node (int value) ((* Node) next))",
            {
                "Node": {
                    "value": IntType(),
                    "next": PointerType(StructType("Node")),
                }
            },
        ),
    ]
)
def test_get_struct(program_source, expected_struct_dict):
    program = Parser(tokenize(program_source)).parse_program()
    test = Typechecker(program)

    test.get_struct()

    assert test.struct_dict == expected_struct_dict

# tests get_func
@pytest.mark.parametrize(
    "program_source, expected_func_dict",
    [
        (
            "(func add_one ((int value)) int (vardec int retval) (assign retval (+ value 1)) (return retval))",
            {
                "add_one": {
                    "param_types": [IntType()],
                    "return": IntType(),
                }
            },
        ),
    ]
)
def test_get_func(program_source, expected_func_dict):
    program = Parser(tokenize(program_source)).parse_program()
    test = Typechecker(program)

    test.get_func()

    assert test.func_dict == expected_func_dict

# Tests typecheck_func
@pytest.mark.parametrize(
    "func_def, func_dict",
    [
        (
            FuncDef(
                name="add_one",
                params=[Param(type=IntType(), name="value")],
                Rtype=IntType(),
                body=[
                    VarDecStmt(type=IntType(), name="retval"),
                    AssignStmt(
                        lhs=VarAssign("retval"),
                        exp=BinaryOpExp(
                            op=AddOp(),
                            first_exp=LhsExp(lhs=VarAssign("value")),
                            second_exp=IntLiteralExp(int_value=1),
                        ),
                    ),
                    ReturnStmt(exp=LhsExp(lhs=VarAssign("retval"))),
                ],
            ),
            {
                "add_one": {
                    "param_types": [IntType()],
                    "return": IntType(),
                }
            },
        ),
    ]
)
def test_typecheck_func(func_def, func_dict):
    typechecker = typechecker_tester(func_dict=func_dict)
    typechecker.typecheck_func(func_def)
    assert typechecker.func_dict == func_dict

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



@pytest.mark.parametrize(
    "struct_def, struct_dict, expected_struct_dict",
    [
        (
            StructDef(
                name="Node",
                params=[
                    Param(type=IntType(), name="value"),
                    Param(type=PointerType(StructType("Node")), name="next"),
                ]
            ),
            {"Node": {}},
            {
                "Node": {
                    "value": IntType(),
                    "next": PointerType(StructType("Node"))
                }
            }
        ),
        (
            StructDef(
                name="Pair",
                params=[
                    Param(type=IntType(), name="x"),
                    Param(type=IntType(), name="y"),
                ]
            ),
            {"Pair": {}},
            {
                "Pair": {
                    "x": IntType(),
                    "y": IntType()
                }
            }
        ),
    ]
)
def test_typecheck_struct(struct_def, struct_dict, expected_struct_dict):
    typechecker = typechecker_tester(struct_dict=struct_dict)
    typechecker.typecheck_struct(struct_def)
    assert typechecker.struct_dict == expected_struct_dict