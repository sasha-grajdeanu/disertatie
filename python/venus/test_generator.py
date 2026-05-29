import json
import os
import re
from typing import Any, Dict, List

from .parser import extract_all_functions
from .bridge import (
    generate_symbolic_test_script,
    parse_symbolic_search_output,
    run_maude,
)
from .formatter import format_symbolic_results
from .pytest_generator import generate_pytest_suite, generated_tests_dir


def symbolic_json_path(file_path: str) -> str:
    tests_dir = generated_tests_dir(file_path)
    results_dir = os.path.join(tests_dir, "symbolic_results")
    os.makedirs(results_dir, exist_ok=True)

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.join(results_dir, f"{module_name}_symbolic.json")


def normalize_solution(solution: Dict[str, Any], index: int) -> Dict[str, Any]:
    return {
        "index": index,
        "type": solution.get("type"),
        "tested_func": solution.get("tested_func"),
        "path_condition": solution.get("pc"),
        "variables": solution.get("variables", {}),
    }


def write_symbolic_json_report(
    file_path: str,
    depth: int,
    funcs_info: Dict[str, List[str]],
    code: str,
    maude_output: str,
    solutions: List[Dict[str, Any]],
    status: str = "ok",
) -> str:
    safe_paths = sum(1 for sol in solutions if sol.get("type") == "safe")
    bug_paths = sum(1 for sol in solutions if sol.get("type") == "bug")
    json_path = symbolic_json_path(file_path)

    report = {
        "status": status,
        "source_file": file_path,
        "loop_depth": depth,
        "functions": funcs_info,
        "summary": {
            "functions": len(funcs_info),
            "symbolic_paths": len(solutions),
            "safe_paths": safe_paths,
            "bug_paths": bug_paths,
        },
        "source_code": code,
        "paths": [
            normalize_solution(solution, index)
            for index, solution in enumerate(solutions, start=1)
        ],
        "maude_output": maude_output,
    }

    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(f"  Stored Maude JSON result: {json_path}")
    return json_path


def run_test_generator(file_path: str, depth: int = 3) -> None:
    with open(file_path, "r") as f:
        code = f.read().strip()
        while code.endswith("."):
            code = code[:-1].strip()

    code = re.sub(r"\}\s*def", "} def", code)
    funcs_info = extract_all_functions(code)
    script = generate_symbolic_test_script(code, depth)

    success, output = run_maude(script, ".temp_test.maude")

    if not success:
        write_symbolic_json_report(
            file_path,
            depth,
            funcs_info,
            code,
            output,
            [],
            status="maude-error",
        )
        if "checkedProgram(" in output or "result [" in output:
            print("Invalid Venus program: return outside function.")
            return
        print("--- Maude Error ---")
        print(output)
        return

    solutions = parse_symbolic_search_output(output)
    format_symbolic_results(funcs_info, solutions, code)

    if funcs_info:
        func_name = list(funcs_info.keys())[0]
        func_obj = {"name": func_name, "params": funcs_info[func_name]}
        generate_pytest_suite(file_path, func_obj, solutions)

    write_symbolic_json_report(
        file_path,
        depth,
        funcs_info,
        code,
        output,
        solutions,
    )
