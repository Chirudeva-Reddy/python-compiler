## GROUP: TARUN, NISHAL 2023A7PS0209U, CHIRU, CALEB

# ============================================================
# slr_parser.py - Naive Shift-Reduce Parser
# Written by request to replace SLR(1) with generic logic.
# ============================================================

from grammar import GRAMMAR, START_SYMBOL, EPSILON, tokens_to_terminals

class ShiftReduceParser:
    def __init__(self):
        self.grammar = GRAMMAR
        # Flatten and sort grammar productions by length of RHS descending
        # so we attempt longest-match reduction first greedily.
        self.productions = []
        for lhs, rhs_list in self.grammar.items():
            for rhs in rhs_list:
                # Epsilon productions are not easily handled by generic shift reduce
                # as it creates infinite reduction loops without lookahead.
                # If they exist, we record them, but they might be skipped.
                if rhs == [EPSILON]:
                    self.productions.append((lhs, []))
                else:
                    self.productions.append((lhs, rhs))
        
        # Sort by RHS length descending to ensure Longest-Match Reduction
        self.productions.sort(key=lambda p: len(p[1]), reverse=True)

    def print_first_follow(self):
        pass

    def print_tables(self):
        pass

    def parse(self, tokens):
        input_syms = tokens_to_terminals(tokens)
        input_ptr = 0
        stack = []
        
        sw, iw, aw = 90, 70, 50
        print("\n" + "=" * 50)
        print("  Shift-Reduce Parsing Trace (Longest-Match Greedy)")
        print("=" * 50)
        print(f"  {'Stack':<{sw}} {'Input':<{iw}} {'Action':<{aw}}")
        print(f"  {'-'*sw} {'-'*iw} {'-'*aw}")

        while True:
            # 1. Check if we accept (Stack has Start Symbol and Input is exhausted)
            if stack == [START_SYMBOL] and input_syms[input_ptr][0] == '$':
                stack_str = ' '.join(stack) + " <- [TOP]"
                input_str = '$'
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {'>> ACCEPT':<{aw}}")
                print("\n>> Result: Parsing Successful")
                return True

            # 2. Try to reduce
            reduced = False
            for lhs, rhs in self.productions:
                n = len(rhs)
                if n > 0:
                    if len(stack) >= n and stack[-n:] == rhs:
                        # Match found! We take the greedy long reduction
                        action = f"Reduce {lhs} -> {' '.join(rhs)}"
                        stack_str = ' '.join(stack) + " <- [TOP]" if len(stack) > 0 else "[TOP]"
                        input_str = ' '.join(v for _, v in input_syms[input_ptr:])
                        print(f"  {stack_str:<{sw}} {input_str:<{iw}} {action:<{aw}}")
                        
                        # Apply reduction
                        stack = stack[:-n] + [lhs]
                        reduced = True
                        break
            
            if reduced:
                continue

            # 3. If we can't reduce and no input left, parsing fails
            curr_term, curr_val = input_syms[input_ptr]
            if curr_term == '$' and not reduced:
                stack_str = ' '.join(stack) + " <- [TOP]" if len(stack) > 0 else "[TOP]"
                input_str = '$'
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {'>> ERROR (Stuck)':<{aw}}")
                print("\n>> Parsing Error: Could not shift or reduce any further.")
                return False
                
            # 4. Shift
            action = f"Shift '{curr_val}'"
            stack_str = ' '.join(stack) + " <- [TOP]" if len(stack) > 0 else "[TOP]"
            input_str = ' '.join(v for _, v in input_syms[input_ptr:])
            print(f"  {stack_str:<{sw}} {input_str:<{iw}} {action:<{aw}}")
            
            stack.append(curr_term)
            input_ptr += 1

