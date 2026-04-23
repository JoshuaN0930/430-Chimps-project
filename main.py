import sys
from dataclasses import fields, is_dataclass
from src.lexer.tokenizer import tokenize
from src.parser.parser import Parser
from src.typechecker.typechecker import Typechecker


def format_ast(node, indent=0):
    """
    Format an abstract syntax tree node into a readable string.

    Parameters
    ----------
    node
        The AST node or value to format.
    indent : int, optional
        The current indentation level.

    Returns
    -------
    str
        A formatted string representation of the AST.
    """
    pad = "  " * indent
    if is_dataclass(node):
        lines = [f"{pad}{type(node).__name__}"]
        for f in fields(node):
            val = getattr(node, f.name)
            if isinstance(val, list):
                lines.append(f"{pad}  {f.name}:")
                for item in val:
                    lines.append(format_ast(item, indent + 2))
            elif is_dataclass(val):
                formatted = format_ast(val, 0)
                if '\n' not in formatted:
                    lines.append(f"{pad}  {f.name}: {formatted.strip()}")
                else:
                    lines.append(f"{pad}  {f.name}:")
                    lines.append(format_ast(val, indent + 2))
            else:
                lines.append(f"{pad}  {f.name}: {val!r}")
        return "\n".join(lines)
    return f"{pad}{node!r}"


def main():
    """
    Run the lexer, parser, and typechecker on Chimp source code.

    Reads source code either from a `.chimp` file passed as a command-line
    argument or from terminal input. Then tokenizes, parses, prints the AST,
    and runs typechecking.

    Raises
    ------
    SystemExit
        Raised when input is invalid or when parsing/typechecking fails.
    """
    # for reading from a file chimps code
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not filepath.endswith(".chimp"):
            print(f"Error: expected a .chimp file, got '{filepath}'")
            sys.exit(1)
        with open(filepath, 'r') as f:
            source = f.read()
    #for using terminal to input chimps code
    else:
        source = input(">>>")

    tokens = tokenize(source)
    print("--- tokens ---")
    print(tokens)

    parser = Parser(tokens)
    try:
        result = parser.parse_program()
        print("--- AST ---")
        print(format_ast(result))
    except Exception as e:
        print()
        print(f"Parse Error: {e}")
        sys.exit(1)

    try:
        tc = Typechecker(result)
        tc.typecheck()
        print("--- Typecheck ---")
        print("OK")
    except Exception as e:
        print()
        print(f"Typecheck Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()