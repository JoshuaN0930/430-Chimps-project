from dataclasses import dataclass
from typing import List 
from src.lexer.token import Token, TokenType
from src.parser.nodes import (
    IntType, VoidType, StructType, PointerType, Type,
    Param, StructDef, FuncDef,
    VarDec, Program
)

class ParserError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")

class Parser:
    #---Core Helpers---

    #entry point 
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    #look at current token without consuming it
    def peek(self) -> Token:
        return self.tokens[self.pos]
    
    #"Grab the current token and advance pos by 1
    def consume(self, expected: TokenType = None) -> Token:
        token = self.tokens[self.pos]
        if expected and token.type != expected:
            raise ParserError(
                f"Expected {expected.name}, got  {token.type.name}",
                token.line
            )
        
        self.pos += 1
        return token
    
    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)
    
    """
        Type Parsing
        type ::= int - integers
                 void
                 structname - indentifier used as type 
                 (* type ) pointer - recurses
        """
    def parse_type(self) -> Type:
       
        token = self.peek()

        if token.type == TokenType.INT:
            self.consume(TokenType.INT)
            return IntType()
        
        elif token.type == TokenType.VOID:
            self.consume(TokenType.VOID)
            return VoidType()
        
        elif token.type == TokenType.IDENTIFIER:
            token = self.consume(TokenType.IDENTIFIER)
            return StructType(name=token.value)
        
        elif token.type == TokenType.LParen:
            #(* type)
            self.consume(TokenType.LParen)
            self.consume(TokenType.Star)
            inner = self.parse_type()
            self.consume(TokenType.RParen)
            return PointerType(inner=inner)
        
        raise ParserError(
            f"Expected a type , got {token.type.name}",
            token.line
        )
    
    """
        Param Parsing
        param :: = `(` type var `)`
    """
    def parse_param(self):
        self.consume(TokenType.LParen)
        type_node = self.parse_type()
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.RParen)

        return Param(type=type_node, name=name_tok.value)
    

    """
        Structure Parsing
        structdef ::= `(` `struct` structname param* `)`
    """
    def parse_struct(self):
        self.consume(TokenType.LParen)
        self.consume(TokenType.STRUCT)
        name_tok = self.consume(TokenType.IDENTIFIER)
        
        params = [] 
        while self.peek().type != TokenType.RParen:
            params.append(self.parse_param())
        
        self.consume(TokenType.RParen)
        return StructDef(name=name_tok.value, params=params)
    

    """
        Fucntion Parsing
        fdef ::= `(` `func` funcname `(` param* `)` type stmt* `)`
    """
    def parse_funcs(self):
        self.consume(TokenType.LParen)
        self.consume(TokenType.FUNC)
        name_tok = self.consume(TokenType.IDENTIFIER)

        self.consume(TokenType.LParen)
        params = []
        while self.peek().type != TokenType.RParen:
            params.append(self.parse_param())
        self.consume(TokenType.RParen)

        token_type = self.parse_type()

        body = []
        while self.peek().type != TokenType.RParen:
            if self.at_end():
                raise ParserError("Unexpected EOF inside function body", self.peek().line)
            
            body.append(self.parse_stmt())
        
        self.consume(TokenType.RParen)
        return FuncDef(name=name_tok.value, params=params, Rtype=token_type, body=body)

















    
    """
        Statement Parsing
        stmt ::= (vardec type var) - variable decclaration
                 (assign lhs exp) - assignment
                 (while exp stmt) - while loops
                 (if exp stmt [stmt]) - if 
                 (return [exp]) - return 
                 (block stmt*) blocks
                 (println exp) - printing something
                 (stmt exp) - expression statements
    """
    def parse_stmt(self):
        if self.peek().type != TokenType.LParen:
            raise ParserError(f"Expected '(' to start statement", self.peek().line)
        
        
        head = self.tokens[self.pos + 1]

        if head.type == TokenType.VARDEC:
            return self.parse_vardec()
        
        raise ParserError(f"Unknown statement '{head.value}'", head.line)

    """
        stmt ::= (vardec type var) 
    """
    def parse_vardec(self) -> VarDec:
        self.consume(TokenType.LParen)
        self.consume(TokenType.VARDEC)
        type_node = self.parse_type()
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.RParen)
        return VarDec(type=type_node, name=name_tok.value)
    





















    """
        Program  Parsing
        program ::= structdef* fdef* stmt* - stmt* is the entry point
    """
    def parse_program(self) -> Program:
        structs = []
        funcs = []
        stmts = []
        
        while not self.at_end():
            next_tok = self.tokens[self.pos + 1]

            if next_tok.type == TokenType.STRUCT:
                structs.append(self.parse_struct())

            elif next_tok.type == TokenType.FUNC:
                funcs.append(self.parse_funcs())

            else :
                stmts.append(self.parse_stmt())
        return Program(structs=structs, funcs=funcs, stmts=stmts)