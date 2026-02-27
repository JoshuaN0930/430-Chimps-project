import sys
from src.lexer.tokenizer import tokenize

# for reading from a file chimps code 
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        source = f.read()
#for using terminal to input chimps code 
else: 
    source = input(">>>")


tokens = tokenize(source)
print(tokens)