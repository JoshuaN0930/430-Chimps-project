from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    #op
    Plus = auto()
    Minus = auto()
    Star = auto()
    Division = auto()
    LessThan = auto()
    EQ = auto()
    NEQ = auto()


    #symbols
    LParen = auto()
    RParen = auto ()
    ADDRESS = auto()
    DOT = auto()

    #keywords
    VARDEC = auto()
    INT = auto()
    ASSIGN = auto()
    PRINTLN = auto()
    IDENTIFIER = auto()
    INTEGER = auto()

    TRUE = auto()
    FALSE = auto()

    WHILE = auto()
    IF = auto()
    RETURN = auto()
    BLOCK = auto()
    STMT = auto()
    VOID = auto()
    STRUCT = auto()
    FUNC = auto()
    CALL = auto()
    NULL = auto()



class Symbol:
    SINGLE = {
        '+' : TokenType.Plus,
        '(' : TokenType.LParen,
        ')' : TokenType.RParen,
        '-' :TokenType.Minus,
        '*' :TokenType.Star,
        '/' :TokenType.Division,
        '<' :TokenType.LessThan,
        '&' : TokenType.ADDRESS, # address of
        '.' : TokenType.DOT      # field access
    }

    DOUBLE = {
        '==' : TokenType.EQ,
        '!=' : TokenType.NEQ
    }

class Keyword:
    WORDS = {
        'int' :TokenType.INT,
        'vardec' :TokenType.VARDEC,
        'assign' :TokenType.ASSIGN,
        'println' :TokenType.PRINTLN,

        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'while': TokenType.WHILE,      # while statement
        'if': TokenType.IF,            # if statement
        'block': TokenType.BLOCK,      # block statement
        'return': TokenType.RETURN,    # return statement
        'stmt': TokenType.STMT,
        'void': TokenType.VOID,
        'struct': TokenType.STRUCT,
        'func': TokenType.FUNC,
        'call': TokenType.CALL,
        'null': TokenType.NULL

    }

@dataclass
class Token:
    type: TokenType
    value: str | int
    line: int

#controls how a token is displayed when printed
#returns the token type name followed by "Token", example + -> PlusToken
    def __repr__(self):
        if self.type in (TokenType.IDENTIFIER, TokenType.INTEGER):
            return f"{self.type.name}({self.value})"
        if self.value in Keyword.WORDS:
            return f"{self.type.name}"
        return f"{self.type.name}"
