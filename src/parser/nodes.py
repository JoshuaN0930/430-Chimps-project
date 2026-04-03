from __future__ import annotations
from dataclasses import dataclass, field

#--types--
@dataclass
class IntType:
    pass

@dataclass
class VoidType:
    pass

@dataclass
class StructType:
    name: str

@dataclass
class PointerType:
    inner: Type 

#union of types 
Type = IntType | VoidType | StructType | PointerType

#--Params--
@dataclass
class Param:
    type: Type
    name: str

############ Statements ############
@dataclass 
class VarDecStmt:
    type: Type
    name: str

@dataclass
class AssignStmt:
    lhs: "Lhs"
    exp: "Exp"

@dataclass
class WhileStmt:
    exp: "Exp"
    stmt: "Stmt"

@dataclass
class IfStmt:
    exp: "Exp"
    then_stmt: "Stmt"
    else_stmt: "Stmt | None"

@dataclass
class ReturnStmt:
    exp: "Exp | None"

@dataclass
class BlockStmt:
    stmt: list["Stmt"]

@dataclass
class PrintlnStmt:
    exp: "Exp"

@dataclass
class ExprStmt:
    exp: "Exp"

Stmt = VarDecStmt | AssignStmt | WhileStmt | IfStmt | ReturnStmt | BlockStmt | PrintlnStmt | ExprStmt


############ Left Hand Side (Assignments) ############
@dataclass
class VarAssign:
    var: str

@dataclass
class FieldStructAssign:
    lhs: "Lhs"
    var: str

@dataclass
class AssignToAddress:
    lhs: "Lhs"

Lhs = VarAssign | FieldStructAssign | AssignToAddress


############ Expressions ############
@dataclass
class IntLiteralExp:
    int_value: int

@dataclass
class BooleanLiteralExp:
    boolean: bool

@dataclass
class LhsExp:
    lhs:"Lhs"

@dataclass
class NullExp:
    pass

Exp = IntLiteralExp | BooleanLiteralExp | LhsExp | NullExp


#--struct--
@dataclass
class StructDef:
    name: str
    params: list[Param]


#--func--
@dataclass
class FuncDef:
    name: str
    params: list[Param]
    Rtype: Type
    body: list[Stmt]

#--program root--
@dataclass
class Program:
    structs: list[StructDef]
    funcs: list[FuncDef]
    stmts: list[Stmt]
