class Node:
    def __init__(self, name, children=None, is_terminal=False):
        self.name = name
        self.children = children if children else []
        self.is_terminal = is_terminal

class Parser:
    def __init__(self, tokens, show_left=False, show_right=False, show_tree=False, show_gui_tree=False):
        self.tokens = tokens
        self.pos = 0
        self.show_left = show_left
        self.show_right = show_right
        self.show_tree = show_tree
        self.show_gui_tree = show_gui_tree

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def eat(self, expected_kind):
        kind, value = self.current_token()
        if kind == expected_kind:
            self.pos += 1
            return Node(value, is_terminal=True)
        else:
            print(self.current_token())
            raise SyntaxError(f"Expected {expected_kind}, got {kind} at position {self.pos}")
        
    def print_tree(self, node, level=0):
        if self.show_tree:
            print("  " * level + "|-- " + str(node.name))
            for child in node.children:
                self.print_tree(child, level + 1)

    def get_derivation(self, root, mode="left"):
        steps = []
        current_sentential_form = [root]

        def is_complete(form):
            return all(n.is_terminal for n in form)

        def get_labels(form):
            return " ".join([n.name for n in form])

        steps.append(get_labels(current_sentential_form))

        while not is_complete(current_sentential_form):
            new_form = []
            expanded = False

            iterator = range(len(current_sentential_form))
            if mode == "right":
                iterator = reversed(iterator)

            target_idx = -1
            for i in iterator:
                if not current_sentential_form[i].is_terminal:
                    target_idx = i
                    break
            
            for i in range(len(current_sentential_form)):
                if i == target_idx and not expanded:
                    new_form.extend(current_sentential_form[i].children)
                    expanded = True
                else:
                    new_form.append(current_sentential_form[i])
            
            current_sentential_form = new_form
            steps.append(get_labels(current_sentential_form))
        
        return steps

    def display_derivation(self, node, mode="left"):
        print(f"\n--- {mode.capitalize()}most Derivation ---")
        steps = self.get_derivation(node, mode=mode)
        for i, step in enumerate(steps):
            arrow = "=>" if i > 0 else "  "
            print(f" {arrow} {step}")


    def parse_program(self):
        root = Node("Program")  
        while self.pos < len(self.tokens):
            root.children.append(self.parse_statement())
        print("Syntactic Validation Successful.")
        if self.show_gui_tree:
            from tree_view import draw_with_nltk
            draw_with_nltk(root, hide_terminals=True)
        if self.show_tree:
            print("\nParse Tree:")
            self.print_tree(root)
        if self.show_left:
            self.display_derivation(root, mode="left")
        if self.show_right:
            self.display_derivation(root, mode="right")
        return root

    def parse_statement(self):
        kind, value = self.current_token()
        node = Node("Statement")
        if kind == 'keyword':
            if value in ['int', 'float']: node.children.append(self.parse_declaration())
            elif value == 'if': node.children.append(self.parse_if())
            elif value == 'while': node.children.append(self.parse_while())
            elif value == 'print': node.children.append(self.parse_print())
        elif kind == 'left_brace': node.children.append(self.parse_block())
        elif kind == 'identifier': node.children.append(self.parse_assignment())
        else: raise SyntaxError(f"Unexpected start of statement: {kind}")
        return node

    def parse_declaration(self):
        node = Node("Declaration")
        node.children.append(self.eat('keyword')) # type
        node.children.append(self.eat('identifier'))
        node.children.append(self.eat('semicolon'))
        return node

    def parse_assignment(self):
        node = Node("Assignment")
        node.children.append(self.eat('identifier'))
        node.children.append(self.eat('assignment'))
        node.children.append(self.parse_expr())
        node.children.append(self.eat('semicolon'))
        return node

    def parse_expr(self):
        node = Node("Expression")
        node.children.append(self.parse_term())
        while self.current_token()[0] in ['arithmetic_operator']:
            op = self.current_token()[1]
            if op in ['+', '-']:
                node.children.append(self.eat('arithmetic_operator'))
                node.children.append(self.parse_term())
            else: break
        return node

    def parse_term(self):
        node = Node("Term")
        node.children.append(self.parse_factor())
        while self.current_token()[0] in ['arithmetic_operator']:
            op = self.current_token()[1]
            if op in ['*', '/', '%']:
                node.children.append(self.eat('arithmetic_operator'))
                node.children.append(self.parse_factor())
            else: break
        return node

    def parse_factor(self):
        node = Node("Factor")
        kind, value = self.current_token()
        if kind == 'integer_constant' or kind == 'float_constant': node.children.append(self.eat(kind))
        elif kind == 'identifier': node.children.append(self.eat('identifier'))
        elif kind == 'left_parenthesis':
            node.children.append(self.eat('left_parenthesis'))
            node.children.append(self.parse_expr())
            node.children.append(self.eat('right_parenthesis'))
        else:
            raise SyntaxError(f"Expected factor, got {kind} at position {self.pos}")
        return node

    def parse_if(self):
        node = Node("IfStatement")
        node.children.append(self.eat('keyword')) # if
        node.children.append(self.eat('left_parenthesis'))
        node.children.append(self.parse_bool_expr())
        node.children.append(self.eat('right_parenthesis'))
        node.children.append(self.parse_statement())
        if self.current_token()[1] == 'else':
            node.children.append(self.eat('keyword'))
            node.children.append(self.parse_statement())
        return node

    def parse_while(self):
        node = Node("WhileStatement")
        node.children.append(self.eat('keyword')) # while
        node.children.append(self.eat('left_parenthesis'))
        node.children.append(self.parse_bool_expr())
        node.children.append(self.eat('right_parenthesis'))
        node.children.append(self.parse_statement())
        return node

    def parse_bool_expr(self):
        node = Node("BooleanExpression")
        node.children.append(self.parse_bool_term())
        while self.current_token()[1] == '||':
            node.children.append(self.eat('boolean_operator'))
            node.children.append(self.parse_bool_term())
        return node

    def parse_bool_term(self):
        node = Node("BooleanTerm")
        node.children.append(self.parse_bool_factor())
        while self.current_token()[1] == '&&':
            node.children.append(self.eat('boolean_operator'))
            node.children.append(self.parse_bool_factor())
        return node

    def parse_bool_factor(self):
        node = Node("BooleanFactor")
        kind, value = self.current_token()
        
        if value == '!':
            node.children.append(self.eat('boolean_operator'))
            node.children.append(self.parse_bool_factor())
        elif value == '(':
            node.children.append(self.eat('left_parenthesis'))
            node.children.append(self.parse_bool_expr())
            node.children.append(self.eat('right_parenthesis'))
        else:
            node.children.append(self.parse_expr())
            if self.current_token()[0] == 'relational_operator':
                node.children.append(self.eat('relational_operator'))
                node.children.append(self.parse_expr())
        return node

    def parse_block(self):
        node = Node("Block")
        node.children.append(self.eat('left_brace'))
        while self.current_token()[0] != 'right_brace':
            node.children.append(self.parse_statement())
        node.children.append(self.eat('right_brace'))
        return node

    def parse_print(self):
        node = Node("PrintStatement")
        node.children.append(self.eat('keyword')) # print
        node.children.append(self.eat('left_parenthesis'))
        node.children.append(self.parse_expr())
        node.children.append(self.eat('right_parenthesis'))
        node.children.append(self.eat('semicolon'))
        return node


# Usage:
# p = Parser(tokens, show_gui_tree=True)
# root = p.parse_program()

