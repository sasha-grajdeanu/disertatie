# Venus

**Automated Test Generation via Rewriting Logic**

Venus is a simple imperative language whose semantics are formally defined as rewriting rules in Maude. The same formal semantics that execute programs also power an automated test scenario discovery engine, executing symbolic verification and generating concrete Python test suites.

---

## How It Works

```
.venus file  ──►  Python CLI  ──►  Maude Engine  ──►  Results  ──►  Pytest Suites
                                    ├─ VENUS-TS    (normal execution)
                                    └─ VENUS-TEST  (test discovery)
```

The Maude engine uses **nondeterministic rewriting** and **state-space search** to explore all possible execution paths through a program. Combined with Floyd's Strongest Postcondition Calculus and a hybrid constraint solver, it automatically generates parameterized unit tests for Python implementation files.

---

## Project Structure

```
├── python/                         # Python CLI & Core Package
│   ├── main.py                     # Argument parser & entrypoint wrapper
│   └── venus/                      # Core Venus Package
│       ├── __init__.py             # Exposes package API
│       ├── parser.py               # Venus source code syntax parser
│       ├── bridge.py               # Maude execution and output parsing
│       ├── formatter.py            # Clean terminal report pretty-printing
│       ├── pytest_generator.py     # Constraint solver and pytest builder
│       ├── runner.py               # Concrete program execution runner
│       └── test_generator.py       # Symbolic test generator orchestration
│
├── maude/                          # Maude Formal Semantics
│   ├── core/                       # Operational Semantics definition
│   │   ├── venus-lang-syntax.maude
│   │   ├── venus-lang-configuration.maude
│   │   ├── venus-lang-arithmetic.maude
│   │   ├── venus-lang-boolean.maude
│   │   ├── venus-lang-instructions.maude
│   │   ├── venus-lang-functions.maude
│   │   ├── venus-lang-desugaring.maude
│   │   └── venus-lang-transition-machine.maude
│   ├── testing/                    # Test-Generation Rules
│   │   └── venus-lang-symbolic-assignments.maude
│   └── main.maude                  # Harness test script
│
├── examples/                       # Venus & Python Examples
│   ├── venus_code/                 # Imp-syntax program source files
│   │   ├── safe_ratio.venus
│   │   ├── countdown.venus
│   │   ├── bonus_points.venus
│   │   ├── clamp_score.venus
│   │   └── risky_running_average.venus
│   ├── python_code/                # Concrete Python implementations
│   │   ├── safe_ratio.py
│   │   ├── countdown.py
│   │   ├── bonus_points.py
│   │   └── ...
│   └── tests/                      # Automatically generated pytest suites
│       ├── test_safe_ratio_auto.py
│       ├── test_countdown_auto.py
│       └── ...

---

## Usage

### 1. Execute a Venus program concretely
To execute a program concretely using the Venus interpreter:
```bash
python python/main.py examples/venus_code/countdown.venus
```

### 2. Run symbolic scenario discovery and generate tests
To run symbolic execution path discovery and generate a parameterized `pytest` unit test suite:
```bash
python python/main.py examples/venus_code/countdown.venus -s
```

This will automatically:
1. Parse the function signature and variables from the Venus file.
2. Formulate a Maude script to search the program's abstract state configuration.
3. Query Maude to discover all safe execution branches and potential runtime crash threats.
4. Solve the symbolic path constraints mathematically (using the pre-compiled constraint solver).
5. Generate a parameterized Python test suite under `examples/tests/` where each parameter is assigned a unique test `id` representing its abstract path condition.

### 3. Run the generated tests
To run all generated test suites:
```bash
PYTHONPATH=. pytest examples/tests
```

---

## Requirements

- **Python 3.8+**
- **Maude** — must be installed and globally available on `PATH`
- **Pytest** — for running generated unit tests (`pip install pytest`)

---

## Venus Language Syntax

Venus supports:
- Variables (`'name := expression | value`)
- Arithmetic (`+`, `-`, `*`, `/`, `%`)
- Comparisons (`lt`, `gt`, `eq`, `lte`, `gte`, `neq`)
- Boolean operators (`and`, `not`)
- Conditionals (`if ... then ... else ... fi`)
- Loops (`while ... do ... od`, `for 'i in range (start, stop) do ... od`)
- Functions (`def 'name (...) { ... }`, `call 'name (...)`)
- Returns inside functions (`return expression`)

### Example:
```
def 'bonus_points ('score, 'streak) {
    if (('score gte 90) and ('streak gt 3)) then
        return 'score + 10
    else
        if (('score gte 70) or ('streak gt 5)) then
            return 'score + 5
        else
            return 'score
        fi
    fi
}
```
