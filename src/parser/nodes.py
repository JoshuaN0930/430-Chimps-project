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
class VarDec:
    type: Type
    name: str

@dataclass
class Assign:
    lhs: "Lhs"
    exp: "Exp"

@dataclass
class While:
    exp: "Exp"
    stmt: "Stmt"

@dataclass
class If:
    exp: "Exp"
    then_stmt: "Stmt"
    else_stmt: "Stmt | None"

@dataclass
class Return:
    exp: "Exp | None"

@dataclass
class Block:
    stmt: list["Stmt"]

@dataclass
class Println:
    exp: "Exp"

@dataclass
class ExprStmt:
    exp: "Exp"

Stmt = VarDec | Assign | While | If | Return | Block | Println | ExprStmt


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
class IntLiteral:
    int_value: int

@dataclass
class BooleanLiteral:
    boolean: bool

Exp = IntLiteral | BooleanLiteral


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
