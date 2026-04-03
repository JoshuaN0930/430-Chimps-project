import sys
from dataclasses import fields, is_dataclass
from src.lexer.tokenizer import tokenize
from src.parser.parser import Parser

def format_ast(node, indent=0):
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

# for reading from a file chimps code 
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
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
    print(f"Parse Error: {e}")
    exit(1)