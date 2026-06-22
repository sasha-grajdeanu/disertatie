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



def _format_variables(variables: Dict[str, str], params: List[str]) -> str:
    skip = {"result"} | {p.replace("'", "") for p in params}
    items = []
    for var, val in sorted(variables.items()):
        if var in skip:
            continue
        clean_val = val.replace("'", "")
        items.append(f"{var}={clean_val}")
    if not items:
        return ""
    return "  [" + ", ".join(items) + "]"


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

    # ── Global summary counts ──
    total = len(solutions)
    total_safe = sum(1 for s in solutions if s["type"] == "safe" and s.get("feasible", True))
    total_bugs = sum(1 for s in solutions if s["type"] == "bug" and s.get("feasible", True))
    total_unreachable = sum(1 for s in solutions if not s.get("feasible", True))

    # ── Header ──
    print()
    print("=" * LINE_WIDTH)
    print("  SYMBOLIC ANALYSIS RESULTS")
    print("=" * LINE_WIDTH)

    # Collect param names for variable display
    all_params: List[str] = []
    if funcs_info:
        all_params = next(iter(funcs_info.values()), [])

    for func_name, func_solutions in by_func.items():
        safe_paths = [s for s in func_solutions if s["type"] == "safe"]
        bug_paths  = [s for s in func_solutions if s["type"] == "bug"]

        safe_feasible = [s for s in safe_paths if s.get("feasible", True)]
        bug_feasible = [s for s in bug_paths if s.get("feasible", True)]

        safe_unreachable = [s for s in safe_paths if not s.get("feasible", True)]
        bug_unreachable = [s for s in bug_paths if not s.get("feasible", True)]

        # ── Function sub-header ──
        print(f"\n  Function: {func_name}")
        print("  " + "-" * (LINE_WIDTH - 2))

        # Map original indices
        safe_indices = {id(s): idx for idx, s in enumerate(safe_paths, 1)}
        bug_indices = {id(s): idx for idx, s in enumerate(bug_paths, 1)}

        # ── Safe paths ──
        if safe_feasible:
            print()
            for path in safe_feasible:
                idx = safe_indices[id(path)]
                sol_idx = path["_solution_index"]
                flat_cond = _flatten_condition(path["pc"])
                result = _get_result_value(path["variables"])

                post_suffix = ""
                if postcondition is not None and sol_idx in pc_map:
                    check = pc_map[sol_idx]
                    if "error" in check:
                        post_suffix = f"  ERROR: {check['error']}"
                    elif check["holds"]:
                        post_suffix = "  HOLDS"
                    else:
                        cx = check.get("counterexample") or {}
                        cx_str = ", ".join(f"{k}={v}" for k, v in cx.items())
                        post_suffix = f"  VIOLATED: {cx_str}"

                var_info = _format_variables(path["variables"], all_params)
                suffix = f"  =>  result={result}{post_suffix}"
                _print_path_line(f"    path {idx}  if ", flat_cond, suffix)
                if var_info:
                    print(f"            {var_info}")

        # ── Bug paths ──
        if bug_feasible:
            print()
            for path in bug_feasible:
                idx = bug_indices[id(path)]
                flat_cond = _flatten_condition(path["pc"])
                _print_path_line(f"    threat {idx}  if ", flat_cond, "  =>  division by zero")

        # ── Unreachable (dead code) paths ──
        if safe_unreachable or bug_unreachable:
            print()
            print("    unreachable (dead code):")
            for path in safe_unreachable:
                idx = safe_indices[id(path)]
                flat_cond = _flatten_condition(path["pc"])
                result = _get_result_value(path["variables"])
                var_info = _format_variables(path["variables"], all_params)
                _print_path_line(f"      path {idx}  if ", flat_cond, f"  =>  result={result}")
                if var_info:
                    print(f"              {var_info}")
            for path in bug_unreachable:
                idx = bug_indices[id(path)]
                flat_cond = _flatten_condition(path["pc"])
                _print_path_line(f"      threat {idx}  if ", flat_cond, "  =>  division by zero")

    # ── Summary ──
    print()
    print("-" * LINE_WIDTH)

    parts = [f"{total_safe} safe", f"{total_bugs} bug"]
    if total_unreachable:
        parts.append(f"{total_unreachable} unreachable")
    print(f"  {total} path(s): {', '.join(parts)}")

    # ── Postcondition ──
    if postcondition is not None and pc_results is not None:
        errors = [r["error"] for r in pc_results if "error" in r]
        if errors:
            print(f"  postcondition [{postcondition}]: ERROR - {errors[0]}")
        else:
            checked_results = [r for r in pc_results if not r.get("unreachable")]
            violations = sum(1 for r in checked_results if not r["holds"])
            checked = len(checked_results)
            if checked == 0:
                print(f"  postcondition [{postcondition}]: holds vacuously (all paths unreachable)")
            elif violations == 0:
                print(f"  postcondition [{postcondition}]: holds on all {checked} path(s)")
            else:
                print(f"  postcondition [{postcondition}]: violated on {violations}/{checked} path(s)")

    if total > 0 and total_safe == 0 and total_bugs == 0:
        print()
        print("  hint: all paths are unreachable — try increasing loop")
        print("        depth with -d (e.g. -d 5, -d 10)")

    print("=" * LINE_WIDTH)
    print()
