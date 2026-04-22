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


@pytest.mark.parametrize(
    "types, struct_dict, expected",
    [
        (IntType(), {}, IntType()),
        (VoidType(), {}, VoidType()),
        (
            StructType("Node"),
            {
                "Node": {
                    "value": IntType(),
                    "next": PointerType(StructType("Node")),
                }
            },
            StructType("Node"),
        ),
        (
            PointerType(IntType()),
            {},
            PointerType(IntType()),
        ),
        (
            PointerType(StructType("Node")),
            {
                "Node": {
                    "value": IntType(),
                    "next": PointerType(StructType("Node")),
                }
            },
            PointerType(StructType("Node")),
        ),
    ]
)
def test_check_type(types, struct_dict, expected):
    typechecker = typechecker_tester(struct_dict=struct_dict)
    result = typechecker.check_type(types)
    assert result == expected

# test for exp = int 
@pytest.mark.parametrize("exp, env, expected", [
    (IntLiteralExp(5), {}, IntType()),
    (IntLiteralExp(0), {}, IntType()),
    (IntLiteralExp(-1), {}, IntType())
])
def test_exp_int_lit(exp, env, expected):
    tc = typechecker_tester()
    assert tc.typechecker_exp(exp, env) == expected

#test for exp = true/false 
@pytest.mark.parametrize("exp, env, expected", [
    (BooleanLiteralExp(True), {}, BoolType()),
    (BooleanLiteralExp(False), {}, BoolType())
])
def test_exp_bool_lit(exp, env, expected):
    tc = typechecker_tester()
    assert tc.typechecker_exp(exp, env) == expected

#test for exp = null
@pytest.mark.parametrize("exp, env, expected", [
    (NullExp(), {}, NullType()),
])
def test_exp_null(exp, env, expected):
    tc = typechecker_tester()
    assert tc.typechecker_exp(exp, env) == expected

#test for exp = ( & lhs)
@pytest.mark.parametrize("exp, env, struct_dict, expected", [
    #(& x) where x: int -> *int
    (
        AddressOfExp(VarAssign("x")),
        {"x": IntType()},
        {},
        PointerType(IntType()),
    ),
    # (& (. first value)) → *int (address of a struct field)
    (
        AddressOfExp(FieldStructAssign(VarAssign("first"), "value")), 
        {"first": StructType("Node")},
        {"Node": {"value": IntType()}},
        PointerType(IntType()),
    ),
    # (& (* p)) where p: *int -> *int (address of a deref)
    (
        AddressOfExp(AssignToAddress(VarAssign("p"))),
        {"p": PointerType(IntType())},
        {},
        PointerType(IntType()),
    )
])
def test_exp_addressOf(exp, env,struct_dict, expected):
    tc = typechecker_tester(struct_dict=struct_dict)
    assert tc.typechecker_exp(exp, env) == expected

#test for exp = (* exp)
@pytest.mark.parametrize("exp, env, expected", [
    #(* p) where p: *int -> int
    (
        DerefExp(LhsExp(VarAssign("p"))),
        {"p" : PointerType(IntType())},
        IntType(),
    )
])
def test_exp_deref(exp, env, expected):
    tc = typechecker_tester()
    assert tc.typechecker_exp(exp, env) == expected

# test exp = (op exp exp)
@pytest.mark.parametrize("exp, env, expected", [
    #(+ 1 2 ) -> int
    (
        BinaryOpExp(AddOp(), IntLiteralExp(1), IntLiteralExp(2)),
        {},
        IntType(),
    ),
    #(< 1 2) -> bool 
    (
        BinaryOpExp(LessThanOp(), IntLiteralExp(1), IntLiteralExp(2)),
        {},
        BoolType(),
    ),
    #(== ptr null) -> bool
    (
        BinaryOpExp(EqualOp(), LhsExp(VarAssign("ptr")), NullExp()),
        {"ptr": PointerType(IntType())},
        BoolType(),
    )
])
def test_exp_op(exp, env, expected):
    tc = typechecker_tester()
    assert tc.typechecker_exp(exp, env) == expected

#test for exp = (call funcname exp* )
@pytest.mark.parametrize("exp, env,func_dict, expected", [
    #(call add_nums x y) where add_nums: (int) -> int ==> int 
    (
        FunctionCallExp(func_name="add_nums", exp=[LhsExp(VarAssign("x")), LhsExp(VarAssign("y"))]),
        {"x" : IntType(), "y": IntType()},
        {"add_nums": {"param_types": [IntType(), IntType()], "return": IntType()}},
        IntType(),
    )
])
def test_exp_callFunc(exp, env, func_dict, expected):
    tc = typechecker_tester(func_dict=func_dict)
    assert tc.typechecker_exp(exp, env) == expected