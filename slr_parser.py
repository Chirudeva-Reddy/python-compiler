## GROUP: TARUN, NISHAL 2023A7PS0209U, CHIRU, CALEB

# ============================================================
# slr_parser.py - SLR(1) Shift-Reduce Parser
# Builds LR(0) item sets + ACTION/GOTO tables using FOLLOW sets
# ============================================================

from grammar import (
    EPSILON, compute_first_sets, compute_follow_sets,
    tokens_to_terminals,
)

# ----------------------------------------------------------------
# Simplified grammar for SLR (subset so tables stay readable)
# The augmented grammar adds S' -> Program
# ----------------------------------------------------------------
SLR_GRAMMAR = {
    "Program'":     [['Program']],
    'Program':      [['StmtList']],
    'StmtList':     [['Stmt', 'StmtList'],
                     ['Stmt']],
    'Stmt':         [['Decl'],
                     ['PrintStmt'],
                     ['Assign']],
    'Decl':         [['TYPE', 'ID', 'SEMI']],
    'PrintStmt':    [['PRINT', 'LPAREN', 'Expr', 'RPAREN', 'SEMI']],
    'Assign':       [['ID', 'ASSIGN', 'Expr', 'SEMI']],
    'Expr':         [['Expr', 'ADDOP', 'Term'],
                     ['Term']],
    'Term':         [['Term', 'MULOP', 'Factor'],
                     ['Factor']],
    'Factor':       [['ID'], ['INT_CONST'], ['FLOAT_CONST'],
                     ['LPAREN', 'Expr', 'RPAREN']],
}

SLR_START = "Program'"

SLR_TERMINALS = {
    'TYPE', 'ID', 'INT_CONST', 'FLOAT_CONST',
    'ADDOP', 'MULOP', 'ASSIGN', 'SEMI',
    'LPAREN', 'RPAREN', 'PRINT', '$',
}

SLR_NONTERMINALS = set(SLR_GRAMMAR.keys())


# ----------------------------------------------------------------
# LR(0) Item class
# ----------------------------------------------------------------
class Item:
    """An LR(0) item: A -> alpha . beta (dot_pos = position of dot)."""

    def __init__(self, lhs, rhs, dot_pos=0):
        self.lhs = lhs
        self.rhs = tuple(rhs)
        self.dot_pos = dot_pos

    @property
    def next_symbol(self):
        """Symbol right after the dot, or None if dot is at end."""
        return self.rhs[self.dot_pos] if self.dot_pos < len(self.rhs) else None

    def advance(self):
        return Item(self.lhs, self.rhs, self.dot_pos + 1)

    def is_complete(self):
        return self.dot_pos >= len(self.rhs)

    def __eq__(self, other):
        return (self.lhs, self.rhs, self.dot_pos) == (other.lhs, other.rhs, other.dot_pos)

    def __hash__(self):
        return hash((self.lhs, self.rhs, self.dot_pos))

    def __repr__(self):
        before = ' '.join(self.rhs[:self.dot_pos])
        after = ' '.join(self.rhs[self.dot_pos:])
        return f"{self.lhs} -> {before} . {after}".strip()


# ----------------------------------------------------------------
# SLR Parser Class
# ----------------------------------------------------------------
class SLRParser:
    """
    SLR(1) parser - builds canonical LR(0) item sets,
    constructs ACTION/GOTO tables, and runs shift-reduce parsing.
    """

    def __init__(self):
        self.grammar = SLR_GRAMMAR
        self.start = SLR_START
        self.first = self._compute_first()
        self.follow = self._compute_follow()
        self.item_sets = []
        self.action = {}    # (state, terminal) -> ('shift',s) | ('reduce',lhs,rhs) | ('accept',)
        self.goto = {}      # (state, nonterminal) -> state
        self._transitions = {}
        self._build_item_sets()
        self._build_tables()

    # ---- FIRST/FOLLOW for the SLR grammar ----
    def _compute_first(self):
        first = {nt: set() for nt in self.grammar}
        changed = True
        while changed:
            changed = False
            for nt, prods in self.grammar.items():
                for rhs in prods:
                    for sym in rhs:
                        if sym in SLR_TERMINALS:
                            if sym not in first[nt]:
                                first[nt].add(sym); changed = True
                            break
                        elif sym in self.grammar:
                            added = first[sym] - {EPSILON}
                            if not added.issubset(first[nt]):
                                first[nt] |= added; changed = True
                            if EPSILON not in first[sym]:
                                break
                    else:
                        if EPSILON not in first[nt]:
                            first[nt].add(EPSILON); changed = True
        return first

    def _compute_follow(self):
        follow = {nt: set() for nt in self.grammar}
        follow[self.start].add('$')
        follow['Program'].add('$')
        changed = True
        while changed:
            changed = False
            for nt, prods in self.grammar.items():
                for rhs in prods:
                    for i, sym in enumerate(rhs):
                        if sym not in self.grammar:
                            continue
                        rest = rhs[i + 1:]
                        first_rest = self._first_of_seq(rest)
                        added = first_rest - {EPSILON}
                        if not added.issubset(follow[sym]):
                            follow[sym] |= added; changed = True
                        if EPSILON in first_rest or len(rest) == 0:
                            if not follow[nt].issubset(follow[sym]):
                                follow[sym] |= follow[nt]; changed = True
        return follow

    def _first_of_seq(self, symbols):
        result = set()
        for sym in symbols:
            if sym in SLR_TERMINALS:
                result.add(sym); break
            elif sym in self.grammar:
                result |= (self.first[sym] - {EPSILON})
                if EPSILON not in self.first[sym]:
                    break
        else:
            result.add(EPSILON)
        return result

    # ---- Closure and GOTO operations ----
    def _closure(self, items):
        closure = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for item in closure:
                sym = item.next_symbol
                if sym and sym in self.grammar:
                    for rhs in self.grammar[sym]:
                        new_item = Item(sym, rhs, 0)
                        if new_item not in closure:
                            new_items.add(new_item)
                            added = True
            closure |= new_items
        return frozenset(closure)

    def _goto_set(self, items, symbol):
        moved = set()
        for item in items:
            if item.next_symbol == symbol:
                moved.add(item.advance())
        return self._closure(moved) if moved else frozenset()

    # ---- Build canonical collection of LR(0) item sets ----
    def _build_item_sets(self):
        start_item = Item(self.start, self.grammar[self.start][0], 0)
        start_set = self._closure({start_item})
        self.item_sets = [start_set]
        set_map = {start_set: 0}
        queue = [start_set]

        while queue:
            current = queue.pop(0)
            current_idx = set_map[current]
            # All symbols that appear after dots in this set
            symbols = set(item.next_symbol for item in current if item.next_symbol)
            for sym in symbols:
                next_set = self._goto_set(current, sym)
                if not next_set:
                    continue
                if next_set not in set_map:
                    set_map[next_set] = len(self.item_sets)
                    self.item_sets.append(next_set)
                    queue.append(next_set)
                self._transitions[(current_idx, sym)] = set_map[next_set]

    # ---- Build ACTION and GOTO tables ----
    def _build_tables(self):
        self.action = {}
        self.goto = {}
        for i, iset in enumerate(self.item_sets):
            for item in iset:
                sym = item.next_symbol
                if sym and sym in SLR_TERMINALS and sym != '$':
                    # Shift action
                    target = self._transitions.get((i, sym))
                    if target is not None:
                        self.action[(i, sym)] = ('shift', target)
                elif item.is_complete():
                    if item.lhs == self.start:
                        self.action[(i, '$')] = ('accept',)
                    else:
                        # Reduce for each terminal in FOLLOW(lhs)
                        for t in self.follow.get(item.lhs, set()):
                            if (i, t) not in self.action:
                                self.action[(i, t)] = ('reduce', item.lhs, list(item.rhs))
            # GOTO entries for non-terminals
            for nt in SLR_NONTERMINALS:
                target = self._transitions.get((i, nt))
                if target is not None:
                    self.goto[(i, nt)] = target

    # ---- Print FIRST/FOLLOW sets ----
    def print_first_follow(self):
        print("\n" + "=" * 50)
        print("  FIRST Sets (SLR Grammar)")
        print("=" * 50)
        for nt in self.grammar:
            items = ', '.join(sorted(self.first.get(nt, set())))
            print(f"  FIRST({nt}) = {{ {items} }}")
        print("\n" + "=" * 50)
        print("  FOLLOW Sets (SLR Grammar)")
        print("=" * 50)
        for nt in self.grammar:
            items = ', '.join(sorted(self.follow.get(nt, set())))
            print(f"  FOLLOW({nt}) = {{ {items} }}")

    # ---- Pretty-print ACTION/GOTO tables ----
    def print_tables(self):
        num_states = len(self.item_sets)
        terminals = sorted(SLR_TERMINALS - {'$'}) + ['$']
        nonterminals = sorted(SLR_NONTERMINALS - {self.start})
        from tabulate import tabulate
        
        print("\n" + "=" * 50)
        print("  SLR ACTION Table")
        print("=" * 50)
        
        headers_action = ["State \\ Terminal"] + terminals
        action_data = []
        for i in range(num_states):
            row = [i]
            for t in terminals:
                entry = self.action.get((i, t))
                cell = ""
                if entry:
                    if entry[0] == 'shift': cell = f"s{entry[1]}"
                    elif entry[0] == 'reduce': cell = f"r:{entry[1]}"
                    elif entry[0] == 'accept': cell = "ACC"
                row.append(cell)
            action_data.append(row)

        print(tabulate(action_data, headers=headers_action, tablefmt="grid"))

        print("\n" + "=" * 50)
        print("  SLR GOTO Table")
        print("=" * 50)
        
        headers_goto = ["State \\ NonTerminal"] + nonterminals
        goto_data = []
        for i in range(num_states):
            row = [i]
            for nt in nonterminals:
                target = self.goto.get((i, nt))
                cell = str(target) if target is not None else ""
                row.append(cell)
            goto_data.append(row)
            
        print(tabulate(goto_data, headers=headers_goto, tablefmt="grid"))

    # ---- Shift-reduce parsing with step-by-step trace ----
    def parse(self, tokens):
        input_syms = tokens_to_terminals(tokens)
        # Keep only terminals that our SLR grammar knows about
        filtered = [(t, v) for t, v in input_syms if t in SLR_TERMINALS]
        if not filtered or filtered[-1][0] != '$':
            filtered.append(('$', '$'))

        stack = [0]   # state stack starts with state 0
        ip = 0

        print("\n" + "=" * 50)
        print("  SLR Parsing Trace")
        print("=" * 50)
        sw, iw, aw = 40, 35, 45
        print(f"  {'Stack':<{sw}} {'Input':<{iw}} {'Action':<{aw}}")
        print(f"  {'-'*sw} {'-'*iw} {'-'*aw}")

        max_steps = 500
        for step in range(max_steps):
            state = stack[-1]
            curr_term, curr_val = filtered[ip]

            stack_str = ' '.join(str(s) for s in stack)
            if len(stack_str) > sw - 2: stack_str = "..." + stack_str[-(sw - 5):]
            input_str = ' '.join(v for _, v in filtered[ip:])
            if len(input_str) > iw - 2: input_str = input_str[:iw - 5] + "..."

            entry = self.action.get((state, curr_term))

            if entry is None:
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {'>> ERROR':<{aw}}")
                expected = [t for (s, t) in self.action if s == state]
                print(f"\n>> Parsing Error: unexpected '{curr_term}' ('{curr_val}') in state {state}")
                if expected:
                    print(f"   Expected one of: {', '.join(sorted(set(expected)))}")
                return False

            if entry[0] == 'shift':
                target = entry[1]
                action_str = f"Shift '{curr_val}', go to state {target}"
                if len(action_str) > aw - 2: action_str = action_str[:aw - 5] + "..."
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {action_str:<{aw}}")
                stack.append(curr_term)
                stack.append(target)
                ip += 1

            elif entry[0] == 'reduce':
                lhs, rhs = entry[1], entry[2]
                prod_str = f"{lhs} -> {' '.join(rhs)}"
                action_str = f"Reduce by {prod_str}"
                if len(action_str) > aw - 2: action_str = action_str[:aw - 5] + "..."
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {action_str:<{aw}}")
                # Pop 2 * len(rhs) items (symbol + state pairs)
                for _ in range(len(rhs)):
                    stack.pop()
                    stack.pop()
                top_state = stack[-1]
                goto_state = self.goto.get((top_state, lhs))
                if goto_state is None:
                    print(f"\n>> Parsing Error: no GOTO for state {top_state}, '{lhs}'")
                    return False
                stack.append(lhs)
                stack.append(goto_state)

            elif entry[0] == 'accept':
                print(f"  {stack_str:<{sw}} {input_str:<{iw}} {'>> ACCEPT':<{aw}}")
                print("\n>> Result: Parsing Successful")
                return True

        print("\n>> Parsing Error: exceeded maximum steps")
        return False
