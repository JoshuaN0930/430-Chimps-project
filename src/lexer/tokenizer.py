from .token import Token, TokenType, Symbol


def tokenize(source: str) -> list [Token]:
    tokens = []
    i = 0
    line = 1

    while i < len(source):
        ch = source[i]

        if ch == '\n':
            line += 1
            i += 1
            continue

        if ch.isspace():
            i += 1
            continue

        #chekng single-char symbols
        if ch in Symbol.SINGLE:
            tokens.append(Token(Symbol.SINGLE[ch], ch, line))
            i += 1
            continue

        #for unknown char 
        raise ValueError(f"unexpected char '{ch}' at line {line}")
    
    return tokens