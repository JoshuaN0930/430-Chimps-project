from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    Plus = auto()

class Symbol:
    SINGLE = {
        '+' : TokenType.Plus
    }
    

@dataclass
class Token:
    type: TokenType
    value: str
    line: int

    def __repr__(self):
        return f"{self.type.name}Token"