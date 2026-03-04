## GROUP: TARUN, NISHAL 2023A7PS0209U, CHIRU, CALEB

# Question 1: Lexical Specification and Tokenization (5 Marks)
# Date of Evaluation: 02/03/2026 - 05/03/2026
# Using the given language specification (int, float, control constructs, operators, etc.), formally 
# define the lexical structure of the language.
# You are required to:
# • Identify and classify all token categories relevant to the prescribed constructs.
# • Specify the regular expressions corresponding to each token class.
# • Implement a lexical analyzer that reads a source program and generates a token stream.
# • Demonstrate the token stream generated for the prescribed evaluation program.
# • Clearly report lexical errors, if any.
# Your lexical analyzer must correctly tokenize the entire evaluation program provided.

import re

class Lexer:
    rules = [
    ('keyword',           r'\b(int|float|if|else|while|print)\b'),
    ('float_constant',    r'\d+\.\d+'),
    ('integer_constant',  r'\d+'),
    ('identifier',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('boolean_operator',  r'(&&|\|\||!)'),
    ('relational_operator', r'(<=|>=|==|!=|<|>)'),
    ('arithmetic_operator', r'(\+|-|\*|/|%)'),
    ('assignment',        r'='),
    ('semicolon',         r';'),
    ('left_parenthesis',  r'\('),
    ('right_parenthesis', r'\)'),
    ('left_brace',        r'\{'),
    ('right_brace',       r'\}'),
    ('skip',              r'[ \t\n]+'),     
    ('mismatch',          r'.'),                
    ]

    re_rules = '|'.join('(?P<%s>%s)' % pair for pair in rules)

    def __init__(self):
        pass

    def tokenize(self, code):
        tokens = []
        for mo in re.finditer(self.re_rules, code):
            kind = mo.lastgroup
            value = mo.group()
            # print(f"Matched {kind}: '{value}'")  
            if kind == 'skip':
                continue
            elif kind == 'mismatch':
                raise RuntimeError(f'Unexpected character: {value}')
            else:
                tokens.append((kind, value))
        return tokens

lexer = Lexer()

with open('code.tarun', 'r') as file:
    code = file.read()
    try:
        tokens = lexer.tokenize(code)
        print("Tokens:", tokens)
    except RuntimeError as e:
        print("Lexical Error:", e)
