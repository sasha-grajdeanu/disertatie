import re
from typing import Any, Dict, List, Optional

LINE_WIDTH = 72


def _flatten_condition(pc: str) -> str:
    pc = pc.replace("'", "")
    pc = re.sub(r"\s+", " ", pc).strip()
    return pc


def _wrap_condition(flat: str, first_width: int, cont_width: int) -> List[str]:
    chunks = re.split(r" (?=and |or )", flat)

    lines = []
    current_line = ""
    available_width = first_width

    for chunk in chunks:
        if current_line:
            candidate = current_line + " " + chunk
        else:
            candidate = chunk

        if not current_line or len(candidate) <= available_width:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = chunk
            available_width = cont_width

    if current_line:
        lines.append(current_line)

    return lines if lines else [flat]


def _print_path_line(prefix: str, flat_condition: str, suffix: str) -> None:
    indent = " " * len(prefix)
    full_line = f"{prefix}{flat_condition}{suffix}"

    if len(full_line) <= LINE_WIDTH:
        print(full_line)
        return

    first_width = LINE_WIDTH - len(prefix)
    cont_width = LINE_WIDTH - len(indent)
    cond_lines = _wrap_condition(flat_condition, first_width, cont_width)

    if len(cond_lines) == 1:
        print(f"{prefix}{cond_lines[0]}{suffix}")
    else:
        print(f"{prefix}{cond_lines[0]}")
        for line in cond_lines[1:-1]:
            print(f"{indent}{line}")
        print(f"{indent}{cond_lines[-1]}{suffix}")


def _get_result_value(variables: Dict[str, str]) -> str:
    val = variables.get("result", "")
    if not val:
        return "(none)"
    return val.replace("'", "")


def format_runner_output(parsed: Dict[str, Any]) -> None:
    variables = parsed["variables"]
    functions = parsed["functions"]
    print("-" * LINE_WIDTH)
    print("VENUS EXECUTION")

    if variables:
        max_name_len = max(len(name) for name in variables)
        for var_name, val in sorted(variables.items()):
            print(f"{var_name:<{max_name_len}} = {val}")

    if functions:
        for func_name, body in sorted(functions.items()):
            print(f"{func_name} => [{body}]")

    if not variables and not functions:
        print("  (memory is empty)")
    print("-" * LINE_WIDTH)



def format_symbolic_results(
    funcs_info: Dict[str, List[str]],
    solutions: List[Dict[str, Any]],
    code: str,
    postcondition: Optional[str] = None,
    pc_results: Optional[List[Dict[str, Any]]] = None,
) -> None:
    pc_map: Dict[int, Dict[str, Any]] = {}
    if pc_results:
        for entry in pc_results:
            pc_map[entry["solution_index"]] = entry

    by_func: Dict[str, List[Dict[str, Any]]] = {}
    for i, sol in enumerate(solutions, start=1):
        func_name = sol.get("tested_func", "Unknown")
        sol_with_index = {**sol, "_solution_index": i}
        by_func.setdefault(func_name, []).append(sol_with_index)

    for func_name, func_solutions in by_func.items():
        safe_paths = [s for s in func_solutions if s["type"] == "safe"]
        bug_paths  = [s for s in func_solutions if s["type"] == "bug"]

        print(f"\n{func_name}  ({len(safe_paths)} safe, {len(bug_paths)} bug)")
        print("-" * LINE_WIDTH)

        for idx, path in enumerate(safe_paths, 1):
            sol_idx = path["_solution_index"]
            flat_cond = _flatten_condition(path["pc"])
            result = _get_result_value(path["variables"])

            post_suffix = ""
            if postcondition is not None and sol_idx in pc_map:
                check = pc_map[sol_idx]
                if check["holds"]:
                    post_suffix = "  HOLDS"
                else:
                    cx = check.get("counterexample") or {}
                    cx_str = ", ".join(f"{k}={v}" for k, v in cx.items())
                    post_suffix = f"  VIOLATED: {cx_str}"

            suffix = f"  =>  result={result}{post_suffix}"
            _print_path_line(f"  path {idx}  if ", flat_cond, suffix)

        for idx, path in enumerate(bug_paths, 1):
            flat_cond = _flatten_condition(path["pc"])
            _print_path_line(f"  threat {idx}  if ", flat_cond, "  =>  division by zero")

    total = len(solutions)
    total_bugs = sum(1 for s in solutions if s["type"] == "bug")
    print(f"\n{total} path(s): {total - total_bugs} safe, {total_bugs} bug")

    if postcondition is not None and pc_results is not None:
        violations = sum(1 for r in pc_results if not r["holds"])
        checked = len(pc_results)
        if violations == 0:
            print(f"post [{postcondition}]: holds on all {checked} path(s)")
        else:
            print(f"post [{postcondition}]: violated on {violations}/{checked} path(s)")

    print()
