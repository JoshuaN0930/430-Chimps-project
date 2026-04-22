from __future__ import annotations
from dataclasses import dataclass, field

#--types--
@dataclass
class IntType:
    """Represents integer type."""
    pass

@dataclass
class VoidType:
    """Represents void type."""
    pass

@dataclass
class StructType:
    """
    Represents struct type.

    Parameters
    ----------
    name : str
        The name of the struct type.
    """
    name: str

@dataclass
class PointerType:
    """
    Represents pointer type.

    Parameters
    ----------
    inner : Type
        The type pointed to by this pointer.
    """
    inner: Type

@dataclass
class BoolType:
    """Represents boolean type."""
    pass

@dataclass
class NullType:
    """Represents null type."""
    pass

#union of types
Type = IntType | VoidType | StructType | PointerType | BoolType | NullType

#--Params--
@dataclass
class Param:
    """
    Represents a parameter declaration.

    Parameters
    ----------
    type : Type
        The parameter type.
    name : str
        The parameter name.
    """
    type: Type
    name: str

############ Statements ############
@dataclass
class VarDecStmt:
    """
    Represents a variable declaration statement.

    Parameters
    ----------
    type : Type
        The declared variable type.
    name : str
        The declared variable name.
    """
    type: Type
    name: str

@dataclass
class AssignStmt:
    """
    Represents an assignment statement.

    Parameters
    ----------
    lhs : Lhs
        The assignment target.
    exp : Exp
        The expression being assigned.
    """
    lhs: "Lhs"
    exp: "Exp"

@dataclass
class WhileStmt:
    """
    Represents a while statement.

    Parameters
    ----------
    exp : Exp
        The loop condition.
    stmt : Stmt
        The statement executed while the condition is true.
    """
    exp: "Exp"
    stmt: "Stmt"

@dataclass
class IfStmt:
    """
    Represents an if statement.

    Parameters
    ----------
    exp : Exp
        The condition expression.
    then_stmt : Stmt
        The statement executed when the condition is true.
    else_stmt : Stmt | None
        The optional statement executed when the condition is false.
    """
    exp: "Exp"
    then_stmt: "Stmt"
    else_stmt: "Stmt | None"

@dataclass
class ReturnStmt:
    """
    Represents a return statement.

    Parameters
    ----------
    exp : Exp | None
        The optional expression returned by the statement.
    """
    exp: "Exp | None"

@dataclass
class BlockStmt:
    """
    Represents a block of statements.

    Parameters
    ----------
    stmt : list[Stmt]
        The list of statements inside the block.
    """
    stmt: list["Stmt"]

@dataclass
class PrintlnStmt:
    """
    Represents a println statement.

    Parameters
    ----------
    exp : Exp
        The expression to print.
    """
    exp: "Exp"

@dataclass
class ExpStmt:
    """
    Represents a statement consisting of a single expression.

    Parameters
    ----------
    exp : Exp
        The expression used as a statement.
    """
    exp: "Exp"

Stmt = VarDecStmt | AssignStmt | WhileStmt | IfStmt | ReturnStmt | BlockStmt | PrintlnStmt | ExpStmt


############ Left Hand Side (Assignments) ############
@dataclass
class VarAssign:
    """
    Represents assignment to a variable.

    Parameters
    ----------
    var : str
        The variable name.
    """
    var: str

@dataclass
class FieldStructAssign:
    """
    Represents assignment to a struct field.

    Parameters
    ----------
    lhs : Lhs
        The left-hand side expression producing the struct value.
    var : str
        The field name being assigned.
    """
    lhs: "Lhs"
    var: str

@dataclass
class AssignToAddress:
    """
    Represents assignment through an address or pointer target.

    Parameters
    ----------
    lhs : Lhs
        The left-hand side being dereferenced or addressed.
    """
    lhs: "Lhs"

Lhs = VarAssign | FieldStructAssign | AssignToAddress


############ Operators ############
@dataclass
class AddOp:
    """Represents addition operator."""
    pass

@dataclass
class MinusOp:
    """Represents subtraction operator."""
    pass

@dataclass
class MultiplyOp:
    """Represents multiplication operator."""
    pass

@dataclass
class DivideOp:
    """Represents division operator."""
    pass

@dataclass
class LessThanOp:
    """Represents less-than operator."""
    pass

@dataclass
class EqualOp:
    """Represents equality operator."""
    pass

@dataclass
class NotEqualOp:
    """Represents not-equal operator."""
    pass

Op = AddOp | MinusOp | MultiplyOp | DivideOp | LessThanOp | EqualOp | NotEqualOp


############ Expressions ############
@dataclass
class IntLiteralExp:
    """
    Represents an integer literal expression.

    Parameters
    ----------
    int_value : int
        The integer value.
    """
    int_value: int

@dataclass
class BooleanLiteralExp:
    """
    Represents a boolean literal expression.

    Parameters
    ----------
    boolean : bool
        The boolean value.
    """
    boolean: bool

@dataclass
class LhsExp:
    """
    Represents an expression built from a left-hand side value.

    Parameters
    ----------
    lhs : Lhs
        The left-hand side value used as an expression.
    """
    lhs:"Lhs"

@dataclass
class NullExp:
    """Represents a null expression."""
    pass

@dataclass
class AddressOfExp:
    """
    Represents an address-of expression.

    Parameters
    ----------
    lhs : Lhs
        The left-hand side whose address is taken.
    """
    lhs: Lhs

@dataclass
class DerefExp:
    """
    Represents a dereference expression.

    Parameters
    ----------
    exp : Exp
        The expression being dereferenced.
    """
    exp: Exp

@dataclass
class BinaryOpExp:
    """
    Represents a binary operation expression.

    Parameters
    ----------
    op : Op
        The operator applied to the expressions.
    first_exp : Exp
        The left operand.
    second_exp : Exp
        The right operand.
    """
    op: Op
    first_exp: Exp
    second_exp: Exp

@dataclass
class FunctionCallExp:
    """
    Represents a function call expression.

    Parameters
    ----------
    func_name : str
        The name of the function being called.
    exp : list[Exp]
        The list of argument expressions.
    """
    func_name: str
    exp: list["Exp"]

Exp = IntLiteralExp | BooleanLiteralExp | LhsExp | NullExp | AddressOfExp | DerefExp | BinaryOpExp | FunctionCallExp


#--struct--
@dataclass
class StructDef:
    """
    Represents a struct definition.

    Parameters
    ----------
    name : str
        The name of the struct.
    params : list[Param]
        The fields or parameters of the struct.
    """
    name: str
    params: list[Param]


#--func--
@dataclass
class FuncDef:
    """
    Represents a function definition.

    Parameters
    ----------
    name : str
        The function name.
    params : list[Param]
        The function parameters.
    Rtype : Type
        The return type of the function.
    body : list[Stmt]
        The list of statements in the function body.
    """
    name: str
    params: list[Param]
    Rtype: Type
    body: list[Stmt]

#--program root--
@dataclass
class Program:
    """
    Represents the root of the program.

    Parameters
    ----------
    structs : list[StructDef]
        The list of struct definitions.
    funcs : list[FuncDef]
        The list of function definitions.
    stmts : list[Stmt]
        The top-level statements in the program.
    """
    structs: list[StructDef]
    funcs: list[FuncDef]
    stmts: list[Stmt]
