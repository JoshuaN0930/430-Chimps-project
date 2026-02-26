from src.lexer.tokenizer import tokenize

source = input("enter source: ")
tokens = tokenize(source)
print(tokens)