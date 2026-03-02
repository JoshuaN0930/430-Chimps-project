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

    #keywords
    VARDEC = auto()
    INT = auto()
    ASSIGN = auto()
    PRINTLN = auto()
    IDENTIFIER = auto()
    INTEGER = auto()



class Symbol:
    SINGLE = {
        '+' : TokenType.Plus,
        '(' : TokenType.LParen,
        ')' : TokenType.RParen,
        '-' :TokenType.Minus,
        '*' :TokenType.Star,
        '/' :TokenType.Division,
        '<' :TokenType.LessThan

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
        'println' :TokenType.PRINTLN

    }

@dataclass
class Token:
    type: TokenType
    value: str
    line: int

#controls how a token is displayed when printed
#returns the token type name followed by "Token", example + -> PlusToken
    def repr(self):
        if self.type in (TokenType.IDENTIFIER, TokenType.INTEGER):
            return f"{self.type.name}({self.value})"
        if self.value in Keyword.WORDS:
            return f"{self.type.name}"
        return f"{self.type.name}"
