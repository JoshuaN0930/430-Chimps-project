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

#--stmt--
@dataclass 
class VarDec:
    type: Type
    name: str

Stmt = VarDec

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
