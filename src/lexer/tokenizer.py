from .token import Token, TokenType, Symbol, Keyword


def tokenize(source: str) -> list[Token]:
    """
    Convert source code into a list of tokens.

    Parameters
    ----------
    source : str
        The input source code to scan.

    Returns
    -------
    list[Token]
        A list of tokens produced from the source code.

    Raises
    ------
    ValueError
        Raised when an unexpected character is found in the source.
    """
    tokens = []
    i = 0
    line = 1

    while i < len(source):
        ch = source[i]

        #check if current char is a newline, increment line counter and move on
        if ch == '\n':
            line += 1
            i += 1
            continue

        #check if current char is whitespace (space and tab) and skip it
        if ch.isspace():
            i += 1
            continue

        #check for double char symbols like == and !=
        twoCh = source[i:i+2]
        if twoCh in Symbol.DOUBLE:
            tokens.append(Token(Symbol.DOUBLE[twoCh], twoCh, line))
            i += 2
            continue

        #checking single-char symbols look it in symbol.single
        elif ch in Symbol.SINGLE:
            tokens.append(Token(Symbol.SINGLE[ch], ch, line))
            i += 1
            continue

        #handle keywords (keywords and identifiers)
        if ch.isalpha() or ch == '_':
            start = i
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            token_type = Keyword.WORDS.get(word, TokenType.IDENTIFIER)
            tokens.append(Token(token_type, word, line))
            continue

        #handle integer literals like in case of (assign x 5)
        if ch.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            number = source[start:i]
            tokens.append(Token(TokenType.INTEGER, int(number), line))
            continue

        #for unknown char 
        raise ValueError(f"unexpected char '{ch}' at line {line}")

    return tokens
