import re
from typing import Any, Dict, List, Union
from .parser import extract_func_body

W = 62


def outer_parens_cover(expr: str) -> bool:
    depth = 0
    for idx, char in enumerate(expr):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and idx != len(expr) - 1:
                return False
    return depth == 0


def strip_outer_parens(expr: str) -> str:
    expr = expr.strip()
    while expr.startswith("(") and expr.endswith(")") and outer_parens_cover(expr):
        expr = expr[1:-1].strip()
    return expr


def split_top_level(expr: str, operator: str) -> List[str]:
    token = f" {operator} "
    depth = 0
    parts = []
    start = 0
    idx = 0

    while idx < len(expr):
        char = expr[idx]
        if char == "(":
            depth += 1
            idx += 1
            continue
        if char == ")":
            depth -= 1
            idx += 1
            continue
        if depth == 0 and expr.startswith(token, idx):
            parts.append(expr[start:idx].strip())
            idx += len(token)
            start = idx
            continue
        idx += 1

    if parts:
        parts.append(expr[start:].strip())

    return parts


def format_condition_lines(condition: str) -> List[str]:
    condition = condition.replace("'", "")
    condition = re.sub(r"\s+", " ", condition).strip()
    return format_condition_expr(condition)


def format_condition_expr(expr: str) -> List[str]:
    stripped = strip_outer_parens(expr)
    if split_top_level(stripped, "or") or split_top_level(stripped, "and"):
        expr = stripped

    for operator in ("or", "and"):
        parts = split_top_level(expr, operator)
        if parts:
            return format_joined_condition(operator, parts)

    return [expr]


def format_joined_condition(operator: str, parts: List[str]) -> List[str]:
    lines = []
    for idx, part in enumerate(parts):
        part_lines = format_condition_expr(part)
        prefix = "" if idx == 0 else f"{operator} "

        if len(part_lines) == 1:
            lines.append(f"{prefix}{part_lines[0]}")
            continue

        lines.append(f"{prefix}(")
        lines.extend(f"  {line}" for line in part_lines)
        lines.append(")")

    return lines


def print_condition(label: str, condition: str) -> None:
    lines = format_condition_lines(condition)
    if len(lines) == 1 and len(lines[0]) <= 40:
        print(f"  │  {label}: {lines[0]}")
        return

    print(f"  │  {label}:")
    for line in lines:
        print(f"  │    {line}")


def print_symbolic_memory(variables: Dict[str, str]) -> None:
    for var, val in sorted(variables.items()):
        if var.startswith("tested"):
            continue
        clean_val = val.replace("'", "")
        print(f"  │    '{var} = {clean_val}")


def format_runner_output(parsed: Dict[str, Any]) -> None:
    variables = parsed["variables"]
    functions = parsed["functions"]
    print("\n" + "=" * 40)
    print(" VENUS PROGRAM EXECUTION SUCCESSFUL")
    print("=" * 40)
    if variables:
        print("\n VARIABLES:")
        print("-" * 20)
        max_len = max((len(v) for v in variables))
        for var, val in sorted(variables.items()):
            print(f" {var:<{max_len}} = {val}")
    if functions:
        print("\n FUNCTIONS:")
        print("-" * 20)
        for func, body in sorted(functions.items()):
            print(f" {func} => [{body}]")
    if not variables and (not functions):
        print("\n Memory is empty.")
    print("\n" + "=" * 40 + "\n")


def format_symbolic_results(
    funcs_info: Dict[str, List[str]], solutions: List[Dict[str, Any]], code: str
) -> None:
    print(f"\n{ '═' * W }")
    print("  VENUS SYMBOLIC TEST SCENARIO DISCOVERY")
    print(f"{ '═' * W }")

    by_func: Dict[str, List[Dict[str, Any]]] = {}
    for sol in solutions:
        func = sol.get("tested_func", "Unknown")
        by_func.setdefault(func, []).append(sol)

    for func_name, func_sols in by_func.items():
        print(f"\n{ '━' * W }")
        print(f"  Function: '{func_name}'")
        print(f"{ '━' * W }")

        func_body_src = extract_func_body(code, func_name)
        if func_body_src:
            print("\n  Source code:")
            for line in func_body_src.strip().split("\n"):
                print(f"    │ {line.strip()}")

        safe_paths = [s for s in func_sols if s["type"] == "safe"]
        bug_paths = [s for s in func_sols if s["type"] == "bug"]

        if safe_paths:
            print(f"\n  { '─' * (W - 2) }")
            print(f"  Safe Symbolic Paths ({len(safe_paths)})")
            print(f"  { '─' * (W - 2) }")
            for idx, path in enumerate(safe_paths, 1):
                print(f"\n  ┌─ Path {idx} (Successful execution)")
                print_condition("Path Condition", path["pc"])
                print("  │  Final State:")
                print_symbolic_memory(path["variables"])
                print(f"  └{ '─' * (W - 3) }")

        if bug_paths:
            print(f"\n  { '─' * (W - 2) }")
            print(f"  Division-by-Zero Threats ({len(bug_paths)})")
            print(f"  { '─' * (W - 2) }")
            for idx, path in enumerate(bug_paths, 1):
                print(f"\n  ┌─ Threat {idx} (Potential runtime crash)")
                print_condition("Trigger Condition", path["pc"])
                print("  │  Memory state at crash:")
                print_symbolic_memory(path["variables"])
                print(f"  └{ '─' * (W - 3) }")

    total_funcs = len(by_func)
    total_paths = len(solutions)
    total_bugs = sum(1 for s in solutions if s["type"] == "bug")
    total_safe = total_paths - total_bugs
    print(f"\n{ '═' * W }")
    print("  SUMMARY")
    print(f"  { '─' * (W - 2) }")
    print(f"  Functions analyzed:   {total_funcs}")
    print(f"  Symbolic paths:       {total_paths}")
    print(f"  Safe execution paths: {total_safe}")
    if total_bugs:
        print(f"  Division-by-zero bug: {total_bugs}")
    print(f"{ '═' * W }\n")
