#basic imports
from lexer import Lexer, LexerError
from parser import Parser, SyntaxErrors

lexer = Lexer()

#syntax error handling function
# what we are essentially doing is tracking the line and column number of the error 
# and then printing the error message without showing 
# the line and column number while tokenizing the code.
def print_error(filename, src, line, col, message):
    lines = src.splitlines()
    source_line = lines[line - 1] if 1 <= line <= len(lines) else ""
    print(f"{filename}:line->{line} col->{col}: error: {message}")
    print(source_line)
    print(" " * (max(col, 1) - 1) + "^") 

with open('code.tarun', 'r') as file:
    code = file.read()
    try:
        tokens = lexer.tokenize(code)
        print("Tokens:", [(kind, value) for kind, value, _, _ in tokens]) #hiding line and col number while printing.
    except LexerError as e:
        print_error(
            "code.tarun",
            code,
            getattr(e, "line", 1),
            getattr(e, "col", 1),
            getattr(e, "message_only", str(e)),
        )
        exit(1)


try:
    parser = Parser(tokens, show_tree=True, show_left=True, show_right=True, show_gui_tree=True)
    root = parser.parse_program()
except SyntaxErrors as errors:
    for error in errors.errors:
        print_error(
            "code.tarun",
            code,
            getattr(error, "line", 1),
            getattr(error, "col", 1),
            getattr(error, "message_only", str(error)),
        )
except SyntaxError as e:
    print_error(
        "code.tarun",
        code,
        getattr(e, "line", 1),
        getattr(e, "col", 1),
        getattr(e, "message_only", str(e)),
    )
