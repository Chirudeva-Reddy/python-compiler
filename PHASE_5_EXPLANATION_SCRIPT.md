# Phase 5 Explanation Script: Optimization and Target Code Generation

## 1. One-line overview

For Phase 5, we take the TAC generated in Phase 7, optimize it in `pipeline/phase08_optimizer.py`, and then translate the optimized TAC into pseudo assembly in `pipeline/phase09_target_code.py`.

## 2. Flow to explain

| Step | File | What it does |
|---|---|---|
| Input | `pipeline/phase07_tac.py` | Produces TAC quadruples like `(op, arg1, arg2, result)`. |
| Optimization | `pipeline/phase08_optimizer.py` | Reduces unnecessary TAC while preserving meaning. |
| Target code | `pipeline/phase09_target_code.py` | Converts optimized TAC into pseudo assembly instructions. |
| Driver | `pipeline/test.py` | Prints raw TAC, optimized TAC, and pseudo assembly. |

## 3. Phase 8: Optimization

The optimizer receives TAC as a list of quadruples:

```text
(op, arg1, arg2, result)
```

Example:

```text
("*", "3", "4", "t0")
("+", "2", "t0", "t1")
("=", "t1", "", "x")
```

The optimizer applies three simple optimizations:

| Optimization | Example | Result |
|---|---|---|
| Constant folding | `3 * 4` | `12` |
| Algebraic simplification | `x + 0` | `x` |
| Single-use temporary propagation | `t1 = a + b; x = t1` | `x = a + b` |

The important safety point:

```text
When the optimizer sees label, goto, or if_false_goto, it clears known constants.
```

This prevents wrong optimization across branches and loops.

## 4. Phase 9: Target code generation

The target-code generator takes optimized TAC and maps each TAC operation to pseudo assembly.

| TAC operation | Pseudo assembly |
|---|---|
| `=` | `MOV` |
| `+` | `ADD` |
| `-` | `SUB` |
| `*` | `MUL` |
| `/` | `DIV` |
| `%` | `MOD` |
| `<` | `LT` |
| `>` | `GT` |
| `&&` | `AND` |
| `||` | `OR` |
| `!` | `NOT` |
| `if_false_goto` | `JZ` |
| `goto` | `JMP` |
| `label` | `L0:` |
| `print` | `PRINT` |

Example:

```text
("+", "a", "b", "x")
```

becomes:

```text
ADD x, a, b
```

## 5. Example to say in viva

Raw TAC:

```text
t0 = 3 * 4
t1 = 2 + t0
x = t1
t2 = x + 0
y = t2
print y
```

Optimized TAC:

```text
x = 14
y = 14
print 14
```

Pseudo assembly:

```text
MOV x, 14
MOV y, 14
PRINT 14
```

## 6. Short spoken explanation

In Phase 8, I do not change the parser or semantic analyzer. I only optimize the generated TAC. The optimizer works on quadruples and returns a new optimized list, so the original TAC is preserved for comparison.

The main optimization is constant folding. If both operands are numbers, the expression is computed at compile time. For example, `3 * 4` becomes `12`. I also handle simple identities like `x + 0 = x` and remove unnecessary temporary copies when the temporary is used only once.

In Phase 9, I translate each optimized TAC instruction into pseudo assembly. Arithmetic TAC becomes instructions like `ADD`, `SUB`, and `MUL`. Control flow TAC becomes labels and jumps, for example `if_false_goto` becomes `JZ` and `goto` becomes `JMP`.

This preserves program semantics because optimization only replaces expressions with equivalent forms, and control-flow boundaries reset constant tracking.

## 7. Command to demonstrate

```bash
python3 pipeline/test.py examples/q5_constant_folding.tarun
```

Then point to these sections in the output:

```text
Three-Address Code Generation
Question 5: Optimization and Target Code Generation
Optimized Readable TAC
Pseudo Assembly Target Code
```
