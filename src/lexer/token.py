"""
Token definitions and lookup tables for language lexer/parser.
"""

from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    """
    Enumeration of all token types recognized by the language.

    This enum groups tokens into operators, symbols, keywords,
    identifiers, and literals.
    """

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
    RParen = auto()
    ADDRESS = auto()
    DOT = auto()

    #keywords
    VARDEC = auto()
    INT = auto()
    ASSIGN = auto()
    PRINTLN = auto()
    IDENTIFIER = auto()
    # INTEGER USED FOR LITERALS
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
    """
    Stores symbol lookup tables used to convert source characters
    into token types.

    Attributes
    ----------
    SINGLE : dict[str, TokenType]
        Maps single-character symbols to token types.
    DOUBLE : dict[str, TokenType]
        Maps double-character symbols to token types.
    """

    SINGLE = {
        '+': TokenType.Plus,
        '(': TokenType.LParen,
        ')': TokenType.RParen,
        '-': TokenType.Minus,
        '*': TokenType.Star,
        '/': TokenType.Division,
        '<': TokenType.LessThan,
        '&': TokenType.ADDRESS, # address of
        '.': TokenType.DOT      # field access
    }

    DOUBLE = {
        '==': TokenType.EQ,
        '!=': TokenType.NEQ
    }


class Keyword:
    """
    Stores reserved words for the language and maps them
    to their corresponding token types.

    Attributes
    ----------
    WORDS : dict[str, TokenType]
        Dictionary of keyword strings and their token types.
    """

    WORDS = {
        'int': TokenType.INT,
        'vardec': TokenType.VARDEC,
        'assign': TokenType.ASSIGN,
        'println': TokenType.PRINTLN,

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
    """
    Represents a single token created during analysis.

    Parameters
    ----------
    type : TokenType
        The kind of token.
    value : str | int
        The token's stored value.
    line : int
        The line number where the token appears.
    """

    type: TokenType
    value: str | int
    line: int

    #controls how a token is displayed when printed
    #returns the token type name followed by "Token", example + -> PlusToken
    def __repr__(self):
        """
        Return a readable string representation of the token.

        Returns
        -------
        str
            For identifiers and integer literals, includes the value.
            For all other tokens, returns the token type name.
        """
        if self.type in (TokenType.IDENTIFIER, TokenType.INTEGER):
            return f"{self.type.name}({self.value})"
        if self.value in Keyword.WORDS:
            return f"{self.type.name}"
        return f"{self.type.name}"