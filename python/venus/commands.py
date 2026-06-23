import json
import os
import re
from typing import Any, Dict, List, Optional

from .source import extract_all_functions
from .maude import (
    generate_run_script,
    generate_symbolic_test_script,
    run_maude,
    parse_runner_output,
    parse_symbolic_search_output,
)
from .display import format_runner_output, format_symbolic_results
from .pytest_writer import generate_pytest_suite, generated_tests_dir
from .solver import check_postcondition_on_path, solve_path_condition


def run_venus(file_path: str) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        return

    with open(file_path, "r") as f:
        code = f.read().strip()
        while code.endswith("."):
            code = code[:-1].strip()

    code = re.sub(r"\}\s*def", "} def", code)
    script = generate_run_script(code)
    success, output = run_maude(script, ".temp_runner.maude")

    if not success:
        if "checkedProgram(" in output or "result [" in output:
            print("Invalid Venus program: return outside function.")
            return
        print("--- Maude Error / Warning ---")
        print(output)
        return

    parsed = parse_runner_output(output)
    if not parsed:
        print("Failed to parse Maude output. Raw output:")
        print(output)
        return

    format_runner_output(parsed)


def _symbolic_json_path(file_path: str) -> str:
    results_dir = os.path.join(generated_tests_dir(file_path), "symbolic_results")
    os.makedirs(results_dir, exist_ok=True)
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.join(results_dir, f"{module_name}_symbolic.json")


def _write_symbolic_json_report(
    file_path: str,
    depth: int,
    funcs_info: Dict[str, List[str]],
    code: str,
    maude_output: str,
    solutions: List[Dict[str, Any]],
    status: str = "ok",
    postcondition: Optional[str] = None,
    pc_results: Optional[List[Dict[str, Any]]] = None,
) -> str:
    json_path = _symbolic_json_path(file_path)

    safe_count = sum(1 for sol in solutions if sol.get("type") == "safe" and sol.get("feasible") is True)
    bug_count  = sum(1 for sol in solutions if sol.get("type") == "bug" and sol.get("feasible") is True)
    unreachable_count = sum(1 for sol in solutions if sol.get("feasible") is False)
    unknown_count = sum(1 for sol in solutions if sol.get("feasible") == "unknown")

    pc_map: Dict[int, Dict[str, Any]] = {}
    if pc_results:
        for entry in pc_results:
            pc_map[entry["solution_index"]] = entry

    paths_json = []
    for i, sol in enumerate(solutions, start=1):
        path_entry: Dict[str, Any] = {
            "index": i,
            "type": sol.get("type"),
            "tested_func": sol.get("tested_func"),
            "path_condition": sol.get("pc"),
            "variables": sol.get("variables", {}),
        }
        if sol.get("feasible") is False:
            path_entry["feasible"] = False
        elif sol.get("feasible") == "unknown":
            path_entry["feasible"] = "unknown"
        if i in pc_map:
            check = pc_map[i]
            if "error" in check:
                path_entry["postcondition_error"] = check["error"]
                path_entry["postcondition_holds"] = False
            else:
                path_entry["postcondition_holds"] = check["holds"]
                path_entry["counterexample"] = check.get("counterexample")
        paths_json.append(path_entry)

    report: Dict[str, Any] = {
        "status": status,
        "source_file": file_path,
        "loop_depth": depth,
        "functions": funcs_info,
        "summary": {
            "functions": len(funcs_info),
            "symbolic_paths": len(solutions),
            "safe_paths": safe_count,
            "bug_paths": bug_count,
            "unreachable_paths": unreachable_count,
            "unknown_paths": unknown_count,
        },
        "source_code": code,
        "paths": paths_json,
        "maude_output": maude_output,
    }

    if postcondition is not None:
        all_checks = pc_results or []
        errors = [check["error"] for check in all_checks if "error" in check]
        if errors:
            report["postcondition_summary"] = {
                "error": errors[0],
                "checked_paths": 0,
                "passing": 0,
                "violations": 0,
            }
        else:
            checked_checks = [
                check for check in all_checks
                if not check.get("unreachable") and not check.get("inconclusive")
            ]
            inconclusive_checks = [check for check in all_checks if check.get("inconclusive")]
            violations = sum(1 for check in checked_checks if check["holds"] is False)
            checked = len(checked_checks)
            report["postcondition"] = postcondition
            report["postcondition_summary"] = {
                "checked_paths": checked,
                "passing": checked - violations,
                "violations": violations,
                "inconclusive": len(inconclusive_checks),
            }

    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    return json_path


def run_test_generator(
    file_path: str,
    depth: int = 3,
    postcondition: Optional[str] = None,
) -> None:
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        return

    with open(file_path, "r") as f:
        code = f.read().strip()
        while code.endswith("."):
            code = code[:-1].strip()

    code = re.sub(r"\}\s*def", "} def", code)
    funcs_info = extract_all_functions(code)
    script = generate_symbolic_test_script(code, depth)
    success, output = run_maude(script, ".temp_test.maude")

    if not success:
        _write_symbolic_json_report(
            file_path, depth, funcs_info, code, output, [], status="maude-error"
        )
        if "checkedProgram(" in output or "result [" in output:
            print("Invalid Venus program: return outside function.")
            return
        print("--- Maude Error ---")
        print(output)
        return

    solutions = parse_symbolic_search_output(output)


    params: List[str] = next(iter(funcs_info.values())) if funcs_info else []
    dead_code_paths: List[Dict[str, Any]] = []

    for sol in solutions:
        result = solve_path_condition(sol["pc"], params)
        if result["status"] == "sat":
            sol["_concrete_inputs"] = result["values"]
            sol["feasible"] = True
        elif result["status"] == "unsat":
            sol["feasible"] = False
            dead_code_paths.append(sol)
        else:
            sol["feasible"] = "unknown"




    pc_results: Optional[List[Dict[str, Any]]] = None
    if postcondition and funcs_info:
        pc_results = []
        for i, sol in enumerate(solutions, start=1):
            if sol.get("type") != "safe":
                continue
            if sol.get("feasible") is False:
                pc_results.append({
                    "solution_index": i,
                    "holds": True,
                    "counterexample": None,
                    "substituted_post": postcondition,
                    "unreachable": True,
                })
                continue
            if sol.get("feasible") == "unknown":
                pc_results.append({
                    "solution_index": i,
                    "holds": None,
                    "inconclusive": True,
                    "counterexample": None,
                    "substituted_post": postcondition,
                })
                continue
            check_result = check_postcondition_on_path(
                sol["pc"],
                sol["variables"],
                params,
                postcondition,
            )
            pc_results.append({"solution_index": i, **check_result})


    format_symbolic_results(funcs_info, solutions, code, postcondition, pc_results)

    if funcs_info:
        func_name = next(iter(funcs_info))
        generate_pytest_suite(
            file_path,
            {"name": func_name, "params": funcs_info[func_name]},
            solutions,
            postcondition=postcondition,
            pc_results=pc_results,
        )

    json_path = _write_symbolic_json_report(
        file_path, depth, funcs_info, code, output, solutions,
        postcondition=postcondition, pc_results=pc_results,
    )
    print(f"  Symbolic JSON:  {json_path}")
