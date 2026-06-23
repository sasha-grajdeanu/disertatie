import keyword
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from .solver import eval_symbolic_expr, solve_path_condition


def python_identifier(name: str) -> str:
    identifier = re.sub(r"\W", "_", name)
    if not identifier or identifier[0].isdigit():
        identifier = f"_{identifier}"
    if keyword.iskeyword(identifier):
        identifier = f"{identifier}_"
    return identifier


def generated_tests_dir(file_path: str) -> str:
    source_dir = os.path.dirname(file_path) or "."
    if os.path.basename(source_dir) == "venus_code":
        project_dir = os.path.dirname(source_dir)
    else:
        project_dir = source_dir
    return os.path.join(project_dir, "tests")


def is_valid_module_part(value: str) -> bool:
    is_valid_identifier = bool(re.match(r"^[A-Za-z_]\w*$", value))
    return is_valid_identifier and not keyword.iskeyword(value)


def dotted_module_path(file_path: str) -> Optional[str]:
    module_path = os.path.splitext(os.path.relpath(file_path))[0]
    parts = module_path.split(os.sep)
    if not all(is_valid_module_part(part) for part in parts):
        return None
    return ".".join(parts)


def implementation_module_name(
    file_path: str, module_name: str, fallback_module_name: str
) -> str:
    source_dir = os.path.dirname(file_path) or "."

    if os.path.basename(source_dir) == "venus_code":
        python_impl = os.path.join(
            os.path.dirname(source_dir),
            "python_code",
            f"{fallback_module_name}.py",
        )
        module_path = dotted_module_path(python_impl)
        if os.path.exists(python_impl) and module_path:
            return module_path

    local_impl = os.path.join(source_dir, f"{fallback_module_name}.py")
    module_path = dotted_module_path(local_impl)
    if os.path.exists(local_impl) and module_path:
        return module_path

    return fallback_module_name or module_name


def expected_return_value(expected: Dict[str, Any]) -> Any:
    if "result" in expected:
        return expected["result"]
    if expected:
        first_key = next(iter(expected))
        return expected[first_key]
    return None


def argument_names(params: List[str]) -> List[str]:
    names = []
    used_names = {"expected"}
    for param in params:
        name = python_identifier(param)
        base_name = name
        suffix = 2
        while name in used_names:
            name = f"{base_name}_{suffix}"
            suffix += 1
        used_names.add(name)
        names.append(name)
    return names


def format_function_call(func_name: str, arguments: List[str]) -> str:
    if not arguments:
        return f"{func_name}()"
    args_joined = ", ".join(arguments)
    return f"{func_name}({args_joined})"


def format_parametrize_names(names: List[str]) -> str:
    if len(names) == 1:
        return repr(names[0])
    quoted = ", ".join(repr(name) for name in names)
    return "(" + quoted + ")"


def format_pytest_param(values: List[Any], case_id: str) -> str:
    value_list = ", ".join(repr(value) for value in values)
    if value_list:
        return f"        pytest.param({value_list}, id={case_id!r}),"
    return f"        pytest.param(id={case_id!r}),"


def format_safe_tests(
    test_name: str,
    func_name: str,
    params: List[str],
    safe_cases: List[Tuple[int, List[int], Any, str]],
) -> str:
    if not safe_cases:
        return ""

    if len(safe_cases) == 1:
        _, inputs, expected, _ = safe_cases[0]
        call = format_function_call(func_name, [repr(v) for v in inputs])
        return f"""

def test_{test_name}_returns_expected_result():
    assert {call} == {expected!r}
"""

    arg_names = argument_names(params)
    parametrize_names = arg_names + ["expected"]
    call = format_function_call(func_name, arg_names)
    param_lines = "\n".join(
        format_pytest_param(inputs + [expected], pc)
        for _, inputs, expected, pc in safe_cases
    )

    return f"""

@pytest.mark.parametrize(
    {format_parametrize_names(parametrize_names)},
    [
{param_lines}
    ],
)
def test_{test_name}_returns_expected_result({', '.join(parametrize_names)}):
    assert {call} == expected
"""


def format_bug_tests(
    test_name: str,
    func_name: str,
    params: List[str],
    bug_cases: List[Tuple[int, List[int], str]],
) -> str:
    if not bug_cases:
        return ""

    if len(bug_cases) == 1 or not params:
        _, inputs, _ = bug_cases[0]
        call = format_function_call(func_name, [repr(v) for v in inputs])
        return f"""

def test_{test_name}_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        {call}
"""

    arg_names = argument_names(params)
    call = format_function_call(func_name, arg_names)
    param_lines = "\n".join(
        format_pytest_param(inputs, pc)
        for _, inputs, pc in bug_cases
    )

    return f"""

@pytest.mark.parametrize(
    {format_parametrize_names(arg_names)},
    [
{param_lines}
    ],
)
def test_{test_name}_raises_zero_division_error({', '.join(arg_names)}):
    with pytest.raises(ZeroDivisionError):
        {call}
"""


def format_postcondition_violation_tests(
    test_name: str,
    func_name: str,
    params: List[str],
    postcondition: str,
    pc_results: List[Dict[str, Any]],
) -> str:
    violations = [
        check for check in pc_results
        if check["holds"] is False and check.get("counterexample")
    ]
    if not violations:
        return ""

    arg_names = argument_names(params)
    safe_post = postcondition.replace('"', "'")

    if len(violations) == 1:
        check = violations[0]
        counterexample: Dict[str, int] = check["counterexample"]
        arg_names = argument_names(params)
        param_assigns = "\n".join(
            f"    {name} = {counterexample.get(p, 0)}"
            for name, p in zip(arg_names, params)
        )
        call = format_function_call(func_name, arg_names)
        docstring = f'    """Counterexample violating postcondition: {safe_post}"""'
        return (
            f"\n\ndef test_{test_name}_postcondition_violation():\n"
            f"{docstring}\n"
            f"{param_assigns}\n"
            f"    result = {call}\n"
            f"    assert {postcondition}\n"
        )

    param_lines = "\n".join(
        format_pytest_param(
            [check["counterexample"].get(p, 0) for p in params],
            f"violation_{i + 1}",
        )
        for i, check in enumerate(violations)
    )
    call = format_function_call(func_name, arg_names)
    docstring = f'    """Counterexample violating postcondition: {safe_post}"""'
    args_joined = ", ".join(arg_names)
    return (
        f"\n\n@pytest.mark.parametrize(\n"
        f"    {format_parametrize_names(arg_names)},\n"
        f"    [\n"
        f"{param_lines}\n"
        f"    ],\n"
        f")\n"
        f"def test_{test_name}_postcondition_violation({args_joined}):\n"
        f"{docstring}\n"
        f"    result = {call}\n"
        f"    assert {postcondition}\n"
    )


def generate_pytest_suite(
    file_path: str,
    func_info: Dict[str, Any],
    solutions: List[Dict[str, Any]],
    postcondition: Optional[str] = None,
    pc_results: Optional[List[Dict[str, Any]]] = None,
) -> None:
    func_name = func_info["name"]
    test_name = python_identifier(func_name)
    params = func_info["params"]

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    tests_dir = generated_tests_dir(file_path)
    os.makedirs(tests_dir, exist_ok=True)

    if module_name.startswith("test_"):
        pytest_path = os.path.join(tests_dir, f"{module_name}_auto.py")
        fallback_module_name = module_name[5:]
    else:
        pytest_path = os.path.join(tests_dir, f"test_{module_name}_auto.py")
        fallback_module_name = module_name

    implementation_module = implementation_module_name(file_path, module_name, fallback_module_name)

    safe_cases: List[Tuple[int, List[int], Any, str]] = []
    bug_cases: List[Tuple[int, List[int], str]] = []
    omitted_paths = 0

    func_solutions = [sol for sol in solutions if sol.get("tested_func") == func_name]
    if not func_solutions:
        func_solutions = solutions

    for idx, sol in enumerate(func_solutions, start=1):
        pc = sol["pc"]
        concrete_inputs = sol.get("_concrete_inputs")
        if concrete_inputs is None:
            result = solve_path_condition(pc, params)
            if result["status"] == "sat":
                concrete_inputs = result["values"]

        if concrete_inputs is None:
            omitted_paths += 1
            continue

        if sol["type"] == "bug":
            bug_cases.append((idx, concrete_inputs, pc))
            continue

        concrete_outputs = {
            var: eval_symbolic_expr(expr, concrete_inputs, params)
            for var, expr in sol["variables"].items()
        }
        expected = expected_return_value(concrete_outputs)
        safe_cases.append((idx, concrete_inputs, expected, pc))

    needs_pytest = len(safe_cases) > 1 or bool(bug_cases) or not (safe_cases or bug_cases)

    imports = []
    if needs_pytest:
        imports.append("import pytest")
    imports.append(f"from {implementation_module} import {func_name}")
    code = "\n\n".join(imports) + "\n"

    code += format_safe_tests(test_name, func_name, params, safe_cases)
    code += format_bug_tests(test_name, func_name, params, bug_cases)

    if not safe_cases and not bug_cases:
        code += f"""

def test_{test_name}_has_concrete_scenarios():
    pytest.skip("No concrete symbolic scenarios generated.")
"""

    with open(pytest_path, "w") as f:
        f.write(code)

    parts = f"{len(safe_cases)} safe, {len(bug_cases)} bug, {omitted_paths} omitted"
    print(f"  Pytest suite:   {pytest_path} ({parts})")
