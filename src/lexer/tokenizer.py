from .token import Token, TokenType, Symbol, Keyword


def tokenize(source: str) -> list [Token]:
    tokens = []
    i = 0
    line = 1

    while i < len(source):
        ch = source[i]

        #check if current char is a newline, incremetn line coutner and move on
        if ch == '\n':
            line += 1
            i += 1
            continue

        #check if current char is whitespace (space and tab) and skip it 
        if ch.isspace():
            i += 1
            continue

        #chekng single-char symbols look it in symbol.single 
        if ch in Symbol.SINGLE:
            tokens.append(Token(Symbol.SINGLE[ch], ch, line))
            i += 1
            continue

        #handel keywords (keywords and identifiers)
        if ch.isalpha():
            start = i
            while i < len(source) and source[i].isalpha():
                i += 1
            word = source[start:i]
            token_type = Keyword.WORDS.get(word, TokenType.IDENTIFIER)
            tokens.append(Token(token_type, word, line))
            continue

        #handel integer literals like in case of (assign x 5)
        if ch.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            number = source[start:i]
            tokens.append(Token(TokenType.INTEGER, number, line))
            continue

        #for unknown char 
        raise ValueError(f"unexpected char '{ch}' at line {line}")
    
    return tokens