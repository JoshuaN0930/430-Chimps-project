from dataclasses import dataclass
from typing import List
from src.lexer.token import Token, TokenType
from src.parser.nodes import (
    IntType, VoidType, StructType, PointerType, Type,
    Param, StructDef, FuncDef, Stmt,
    Program, VarDecStmt, AssignStmt, Lhs, VarAssign, FieldStructAssign, AssignToAddress, BooleanLiteralExp, Exp,
    IntLiteralExp, NullExp, LhsExp, WhileStmt, IfStmt, ReturnStmt, BlockStmt, PrintlnStmt, ExpStmt
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
    
    #look at keyword
    def peek_keyword(self) -> Token:
        return self.tokens[self.pos + 1].type
    
    #"Grab the current token and advance pos by 1
    def consume(self, expected: TokenType = None) -> Token:
        token = self.tokens[self.pos]
        if expected and token.type != expected:
            return None
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

            if not self.consume(TokenType.Star):
                raise ParserError("expected '*' for pointer type", self.peek().line)
            
            inner = self.parse_type()

            if not self.consume(TokenType.RParen):
                raise ParserError("missing closing ')' in pointer type", self.peek().line)
            
            return PointerType(inner=inner)
        
        raise ParserError(
            f"'{token.value}' is not a valid type: expected int, void, struc name, or (* type) pointer",
            token.line
        )
    
    """
        Param Parsing
        param :: = `(` type var `)`
    """
    def parse_param(self):
        if not self.consume(TokenType.LParen):
            raise ParserError("missing opening '(' in parameter", self.peek().line)
        
        type_node = self.parse_type()
        name_tok = self.consume(TokenType.IDENTIFIER)
        if not name_tok:
            raise ParserError("missing parameter name", self.peek().line)
        
        if not self.consume(TokenType.RParen):
            raise ParserError("missing closing ')' in parameter", self.peek().line)
        
        return Param(type=type_node, name=name_tok.value)

    """
        Structure Parsing
        structdef ::= `(` `struct` structname param* `)`
    """
    def parse_struct(self):
        if not self.consume(TokenType.LParen):
            raise ParserError("missing opening '(' in struct definition", self.peek().line)
        
        if not self.consume(TokenType.STRUCT):
            raise ParserError("expected 'struct' keyword", self.peek().line)

        name_tok = self.consume(TokenType.IDENTIFIER)
        if not name_tok:
            raise ParserError("expected struct name after 'struct'", self.peek().line)
        
        params = [] 
        while self.peek().type != TokenType.RParen:
            if self.at_end():
                raise ParserError("missing closing ')' in struct definition", self.peek().line)
            params.append(self.parse_param())
        
        if not self.consume(TokenType.RParen):
            raise ParserError("missing closing ')' in struct definition", self.peek().line)
                
        return StructDef(name=name_tok.value, params=params)
    
    def parse_structDefs(self) -> list[StructDef]:
        result = []
        while self.peek().type == TokenType.LParen:
            if self.peek_keyword() == TokenType.STRUCT:
                result.append(self.parse_struct())
            else: 
                break 
        return result
    

    """
        Fucntion Parsing
        fdef ::= `(` `func` funcname `(` param* `)` type stmt* `)`
    """
    def parse_func(self):
        if not self.consume(TokenType.LParen):
            raise ParserError("missing opening '(' in function definition", self.peek().line)
        
        if not self.consume(TokenType.FUNC):
            raise ParserError("expected 'func' keyword", self.peek().line)
        
        name_tok = self.consume(TokenType.IDENTIFIER)
        if not name_tok:
            raise ParserError("expected function name after 'func'", self.peek().line)
        
        if not self.consume(TokenType.LParen):
            raise ParserError("missing opening '(' in parameter list", self.peek().line)
        
        params = []
        while self.peek().type != TokenType.RParen:
            if self.at_end():
                raise ParserError("missing closing ')' in parameter list", self.peek().line)
            params.append(self.parse_param())

        if not self.consume(TokenType.RParen):
            raise ParserError("missing closing ')' in paramter list", self.peek().line)
        
        token_type = self.parse_type()

        body = []
        while self.peek().type != TokenType.RParen:
            if self.at_end():
                raise ParserError("missing closing ')' in function body", self.peek().line)
            body.append(self.parse_stmt())

        if not self.consume(TokenType.RParen):
            raise ParserError("missing closing ')' in function body", self.peek().line)
        
        return FuncDef(name=name_tok.value, params=params, Rtype=token_type, body=body)
    
    def parse_funcDefs(self) -> list[FuncDef]:
        result = []
        while self.peek().type == TokenType.LParen:
            if self.peek_keyword() == TokenType.STRUCT:
                raise ParserError("struct definitions come before functions", self.peek().line)
            elif self.peek_keyword() == TokenType.FUNC:
                result.append(self.parse_func())
            else:
                break
        return result

    """
     ##################### Left Hand Side Parsing #####################
    """

    def parse_lhs(self) -> Lhs:
        token = self.peek()

        if token.type == TokenType.IDENTIFIER:
            self.consume(TokenType.IDENTIFIER)
            return VarAssign(token.value)

        elif token.type == TokenType.LParen:
            self.consume(TokenType.LParen)

            if self.peek().type == TokenType.DOT:
                self.consume(TokenType.DOT)
                inner = self.parse_lhs()
                field_value = self.consume(TokenType.IDENTIFIER)
                self.consume(TokenType.RParen)
                return FieldStructAssign(var= field_value.value, lhs=inner)

            elif self.peek().type == TokenType.Star:
                self.consume(TokenType.Star)
                inner = self.parse_lhs()
                self.consume(TokenType.RParen)
                return AssignToAddress(lhs=inner)

            raise ParserError(
                f"Expected '.' or '*' after '(', got {self.peek().type.name}",
                self.peek().line
            )

        raise ParserError(
            f"Expected a LHS , got {token.type.name}",
            token.line
        )
    """
    ##############################################################
    """


    """
    ##################### Expression Parsing #####################
    """

    def parse_exp(self) -> Exp:
        token = self.peek()

        if token.type == TokenType.INTEGER:
            self.consume(TokenType.INTEGER)
            return IntLiteralExp(int_value= token.value)

        elif token.type == TokenType.TRUE:
            self.consume(TokenType.TRUE)
            return BooleanLiteralExp(boolean=True)

        elif token.type == TokenType.FALSE:
            self.consume(TokenType.FALSE)
            return BooleanLiteralExp(boolean=False)

    ################### LHS Expression ###################:
        elif token.type == TokenType.IDENTIFIER:
            return LhsExp(lhs=self.parse_lhs())

        elif token.type == TokenType.LParen:
            if self.pos + 1 >= len(self.tokens):
                raise ParserError("Unexpected end of input in expression", token.line)
            next_token = self.tokens[self.pos + 1]
            if next_token.type == TokenType.DOT or next_token.type == TokenType.Star:
                return LhsExp(lhs=self.parse_lhs())
            raise ParserError(
                f"Unknown parenthesized expression starting with {next_token.type.name}",
                next_token.line
            )
    ######################################################

        elif token.type == TokenType.NULL:
            self.consume(TokenType.NULL)
            return NullExp()
        raise ParserError(
            f"Expected an expression , got {token.type.name}",
            token.line
        )
    """
    ###################################################################
    """

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

        # Statement Dictionary
        stmt_dict = {
            TokenType.VARDEC: self.parse_vardec,
            TokenType.ASSIGN: self.parse_assign,
            TokenType.WHILE: self.parse_while,
            TokenType.IF: self.parse_if,
            TokenType.RETURN: self.parse_return,
            TokenType.BLOCK: self.parse_block,
            TokenType.PRINTLN: self.parse_println,
            TokenType.STMT: self.parse_exp_stmt
        }
        if head.type in stmt_dict:
            return stmt_dict[head.type]()
        
        raise ParserError(f"Unknown statement '{head.value}'", head.line)

    """
        stmt ::= (vardec type var) 
    """
    def parse_vardec(self) -> VarDecStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.VARDEC)
        type_node = self.parse_type()
        name_tok = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.RParen)
        return VarDecStmt(type=type_node, name=name_tok.value)

    """
        stmt ::= (assign lhs exp)
    """
    def parse_assign(self) -> AssignStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.ASSIGN)
        lhs = self.parse_lhs()
        exp = self.parse_exp()
        self.consume(TokenType.RParen)
        return AssignStmt(lhs= lhs, exp= exp)

    """
        stmt ::= (while exp stmt)
    """
    def parse_while(self) -> WhileStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.WHILE)
        exp = self.parse_exp()
        stmt = self.parse_stmt()
        self.consume(TokenType.RParen)
        return WhileStmt(exp=exp, stmt=stmt)

    """
        stmt ::= (if exp stmt [stmt])
    """
    def parse_if(self) -> IfStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.IF)
        exp = self.parse_exp()
        then_stmt = self.parse_stmt()
        if not self.at_end() and self.peek().type == TokenType.LParen:
            else_stmt = self.parse_stmt()
        else:
            else_stmt = None
        self.consume(TokenType.RParen)
        return IfStmt(exp=exp, then_stmt=then_stmt, else_stmt=else_stmt)

    """
        stmt ::= (return [exp])
    """

    def parse_return(self) -> ReturnStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.RETURN)
        if self.peek().type == TokenType.RParen:
            exp = None
        else:
            exp = self.parse_exp()
        self.consume(TokenType.RParen)
        return ReturnStmt(exp=exp)

    """
        stmt ::= (block stmt*)
    """
    def parse_block(self) -> BlockStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.BLOCK)
        stmts = []
        while self.peek().type != TokenType.RParen:
            stmts.append(self.parse_stmt())

        self.consume(TokenType.RParen)
        return BlockStmt(stmt=stmts)

    """
        stmt ::= (println exp)
    """
    def parse_println(self) -> PrintlnStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.PRINTLN)
        exp = self.parse_exp()
        self.consume(TokenType.RParen)
        return PrintlnStmt(exp=exp)

    """
        stmt ::= (stmt exp)
    """
    def parse_exp_stmt(self) -> ExpStmt:
        self.consume(TokenType.LParen)
        self.consume(TokenType.STMT)
        exp = self.parse_exp()
        self.consume(TokenType.RParen)
        return ExpStmt(exp=exp)
    
    def parse_stmts(self) -> list[Stmt]:
        result = []
        while not self.at_end():
            if self.peek().type == TokenType.LParen:
                if self.peek_keyword() == TokenType.STRUCT:
                    raise ParserError("struct definitions must come before statements", self.peek().line)
                if self.peek_keyword() == TokenType.FUNC:
                    raise ParserError("functions definitions must come before statemets", self.peek().line)
            result.append(self.parse_stmt())
        return result




















    """
        Program  Parsing
        program ::= structdef* fdef* stmt* - stmt* is the entry point
    """
    def parse_program(self) -> Program:
        structs = self.parse_structDefs()
        funcs = self.parse_funcDefs()
        stmts = self.parse_stmts()
        return Program(structs=structs, funcs=funcs, stmts=stmts)




