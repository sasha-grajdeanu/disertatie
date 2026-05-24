---
marp: true
theme: default
paginate: true
---

# Venus
### Automated Test Generation via Rewriting Logic

*Sasha Grajdeanu* — Dissertation Project

---

## Motivation & Approach

**Problem:** Writing unit tests is manual — developers must guess inputs, edge cases are missed, runtime errors slip through.

**Solution:** Build a language whose formal semantics can **automatically test itself**.

Venus is an imperative language executed entirely in **Maude** (Rewriting Logic).
Because execution = term rewriting, Maude can:
- **Execute** programs normally (deterministic rewriting)
- **Explore all paths** simultaneously (nondeterministic search)

```
 .venus file ──► Python CLI ──► Maude Engine ──► Human-readable results
                                 ├─ VENUS-TS    (execution)
                                 └─ VENUS-TEST  (automated testing)
```

---

## The Formal Machine

State = `< Control | Stack | Memory >`, transformed by rewrite rules.

**AC Memory** — variables are found via pattern matching, no explicit lookup:
```maude
op _,_ : Memory Memory -> Memory [assoc comm id: empty] .
eq get(((X -> N) , M), X) = N .
```

**Desugaring** — complex syntax reduced to minimal core:
```maude
eq for (Init, Cond, Step) do Body od =
    Init ; while Cond do Body ; Step od .
eq if Cond then Body fi = if Cond then Body else skip fi .
```

The engine only needs `while` and binary `if` — everything else is sugar.

---

## The Testing Engine — cAutoTest

Given a function, the engine automatically:

**1. Extracts constants** from the AST (e.g., `if ('score gte 50)` → extracts `50`)

**2. Generates boundaries:** each constant `N` → `{N-1, N, N+1}` plus `0, 1`

**3. Removes duplicates** via an AC IntSet with idempotency:
```maude
eq N ;; N = N .     --- algebraic dedup, no filtering code needed
```

**4. Nondeterministically executes** — one rule forks all possibilities:
```maude
rl [pickValue] : testValues(N ;; SSet) => N .
```
Maude's `search` explores **every combination simultaneously**.

---

## Demo 1: Branching — checkStatus

```
def 'checkStatus ('score) {
    'passed := 0 ;
    if ('score gte 50) then 'passed := 1 fi ;
    'checked := 1
}
```

```
  SCENARIOS FOUND: 2 execution paths
  ───────────────────────────────────
  Scenario 1:                       Scenario 2:
    Inputs: 'score = 0, 1, 49         Inputs: 'score = 50, 51
    Output: 'passed = 0               Output: 'passed = 1
            'checked = 1                      'checked = 1
```

**Zero manual tests** — boundary at 50 discovered automatically.

---

## Demo 2: Loops — classify

```
def 'classify ('n) {
    'sum := 0 ; 'i := 1 ;
    while ('i lte 'n) do 'sum := 'sum + 'i ; 'i := 'i + 1 od ;
    if ('sum gt 10) then 'category := 2
    else if ('sum gt 0) then 'category := 1
         else 'category := 0 fi fi
}
```

Constants extracted: `0, 1, 2, 10` → boundaries: `-1, 0, 1, 2, 3, 9, 10, 11`

| Scenario | Input `'n` | Loop iterations | `'sum` | `'category` |
|----------|-----------|-----------------|--------|-------------|
| 1 | 0, -1 | 0 | 0 | 0 |
| 2 | 1 | 1 | 1 | 1 |
| 3 | 9 | 9 | 45 | 2 |
| 4 | 10 | 10 | 55 | 2 |
| 5 | 11 | 11 | 66 | 2 |

**5 paths through loop + conditionals** — all discovered automatically.

---

## Demo 3: Runtime Error Detection

```
def 'divide ('x , 'y) { 'result := 'x / 'y }
```

Division has a **guard**: `if (N2 =/= 0)`. When `'y = 0`, the state gets **stuck**.

```
  ⚠  STUCK STATES (Runtime Errors)
  ───────────────────────────────────
  Error 1:
    Input: 'x = 0, 'y = 0
    Stuck at: cDiv # cAssign
    Cause: Division by zero
```

No crash — Maude safely **isolates the error branch** and reports it.

---

## Future Directions

| Area | Direction |
|------|-----------|
| **More constructs** | Handle arrays, return values, nested function calls |
| **Smarter boundaries** | Extract values from arithmetic expressions, not just comparisons |
| **Optimization** | Reduce redundant search paths, prune equivalent states |
| **Better output** | Show execution trace per scenario |
| **Edge cases** | Handle negative numbers, overflow, deeply nested loops |

---

## Key Takeaways

1. **Rewriting Logic** is a practical execution engine, not just theory
2. **Nondeterminism** gives exhaustive path exploration for free
3. **AC matching** eliminates boilerplate (memory lookup, deduplication)
4. The testing framework requires **zero manual test definitions**
5. Works on **branching, loops, and error detection** — all automatically

> The same formal semantics that **define** the language
> also **test** it — automatically and exhaustively.

**Thank you! Questions?**
