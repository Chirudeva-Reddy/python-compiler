from lexer import Lexer
from parser import Parser

lexer = Lexer()

with open('small.tarun', 'r') as file:
    code = file.read()
    try:
        tokens = lexer.tokenize(code)
        print("Tokens:", tokens)
    except RuntimeError as e:
        print("Lexical Error:", e)
        exit(1)


try:
    parser = Parser(tokens, show_tree=True, show_left=True, show_right=True, show_gui_tree=True)
    root = parser.parse_program()
except SyntaxError as e:
    print("Syntax Error:", e)

