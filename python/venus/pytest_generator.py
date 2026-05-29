import keyword
import os
import re
from itertools import product
from typing import Any, Dict, List, Optional, Tuple, Set

_TRUE_RE = re.compile(r"\btrue\b")
_FALSE_RE = re.compile(r"\bfalse\b")
_LTE_RE = re.compile(r"\blte\b")
_GTE_RE = re.compile(r"\bgte\b")
_NEQ_RE = re.compile(r"\bneq\b|\bne\b")
_EQ_RE = re.compile(r"\beq\b")
_LT_RE = re.compile(r"\blt\b")
_GT_RE = re.compile(r"\bgt\b")
_DIV_RE = re.compile(r"(?<!/)/(?!/)")

_RANGE_LTE_RE = re.compile(r"([a-zA-Z0-9_]+)\s*-\s*(\d+)\s*lte\s*(\d+)")
_RANGE_GT_RE = re.compile(r"([a-zA-Z0-9_]+)\s*-\s*(\d+)\s*gt\s*(\d+)")


def pc_to_python_expr(pc_str: str) -> str:
    expr = pc_str.replace("'", "")
    expr = _TRUE_RE.sub("True", expr)
    expr = _FALSE_RE.sub("False", expr)
    expr = _LTE_RE.sub("<=", expr)
    expr = _GTE_RE.sub(">=", expr)
    expr = _NEQ_RE.sub("!=", expr)
    expr = _EQ_RE.sub("==", expr)
    expr = _LT_RE.sub("<", expr)
    expr = _GT_RE.sub(">", expr)
    expr = _DIV_RE.sub("//", expr)
    return expr


def path_condition_holds(pc_str: str, params: List[str], inputs: List[int]) -> bool:
    if pc_str.strip() == "true":
        return True

    env = dict(zip(params, inputs))
    expr = pc_to_python_expr(pc_str)

    try:
        return bool(eval(expr, {"__builtins__": {}}, env))
    except Exception:
        return False


def brute_force_inputs(pc_str: str, params: List[str]) -> Optional[List[int]]:
    constants = {int(match) for match in re.findall(r"-?\d+", pc_str)}
    domain = {-3, -2, -1, 0, 1, 2, 3, 4, 5}

    for value in constants:
        domain.update({value - 1, value, value + 1})

    expr_str = pc_to_python_expr(pc_str)
    try:
        compiled_code = compile(expr_str, "<string>", "eval")
    except Exception:
        return None

    used_params = [p for p in params if re.search(r"\b" + re.escape(p) + r"\b", pc_str)]
    if not used_params:
        env = {p: 0 for p in params}
        try:
            if bool(eval(compiled_code, {"__builtins__": {}}, env)):
                return [0] * len(params)
        except Exception:
            pass
        return None

    for inputs in product(sorted(domain), repeat=len(used_params)):
        input_map = dict(zip(used_params, inputs))
        env = {p: input_map.get(p, 0) for p in params}
        try:
            if bool(eval(compiled_code, {"__builtins__": {}}, env)):
                return [env[p] for p in params]
        except Exception:
            pass

    return None


def solve_constraints(pc_str: str, params: List[str]) -> Optional[List[int]]:
    original_pc = pc_str
    values = {p: 0 for p in params}
    pc_str = pc_str.replace("(", " ").replace(")", " ").replace("'", "")
    clauses = [c.strip() for c in pc_str.split(" and ") if c.strip()]

    op_reflect = {"lt": "gt", "gt": "lt", "lte": "gte", "gte": "lte", "eq": "eq", "neq": "neq", "ne": "neq"}

    for clause in clauses:
        parts = clause.split()
        if len(parts) == 3:
            left, op, right = parts
            var = None
            if left in params and right not in params:
                var, val_str = left, right
            elif right in params and left not in params:
                var, val_str, op = right, left, op_reflect.get(op, op)

            if var:
                try:
                    val = int(val_str)
                    if op == "lt":
                        values[var] = val - 1
                    elif op == "gt":
                        values[var] = val + 1
                    elif op in ("lte", "gte", "eq"):
                        values[var] = val
                    elif op in ("neq", "ne"):
                        values[var] = val + 1 if val == 0 else 0
                except ValueError:
                    pass

        match = _RANGE_LTE_RE.search(clause)
        if match:
            var, c1, c2 = match.groups()
            if var in params:
                values[var] = int(c1) + int(c2)

        match_gt = _RANGE_GT_RE.search(clause)
        if match_gt:
            var, c1, c2 = match_gt.groups()
            if var in params:
                values[var] = int(c1) + int(c2) + 1

    heuristic_inputs = [values[p] for p in params]
    if path_condition_holds(original_pc, params, heuristic_inputs):
        return heuristic_inputs

    return brute_force_inputs(original_pc, params)


def evaluate_symbolic_expr(expr_str: str, inputs: List[int], params: List[str]) -> Any:
    env = dict(zip(params, inputs))
    expr_str = expr_str.replace("**", "**")
    expr_str = re.sub(
        r"([a-zA-Z0-9_]+)",
        lambda m: f"({env[m.group(1)]})" if m.group(1) in env else m.group(1),
        expr_str,
    )
    try:
        clean_expr = re.sub(r"[^0-9+\-*/% ()]", "", expr_str)
        return int(eval(clean_expr))
    except Exception:
        return expr_str


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
    return bool(re.match(r"^[A-Za-z_]\w*$", value)) and not keyword.iskeyword(value)


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
        return expected[next(iter(expected))]
    return None


def argument_names(params: List[str]) -> List[str]:
    names = []
    used = {"expected"}

    for param in params:
        name = python_identifier(param)
        base_name = name
        suffix = 2

        while name in used:
            name = f"{base_name}_{suffix}"
            suffix += 1

        used.add(name)
        names.append(name)

    return names


def format_function_call(func_name: str, arguments: List[str]) -> str:
    if not arguments:
        return f"{func_name}()"
    return f"{func_name}({', '.join(arguments)})"


def format_parametrize_names(names: List[str]) -> str:
    if len(names) == 1:
        return repr(names[0])
    return "(" + ", ".join(repr(name) for name in names) + ")"


def format_input_id(params: List[str], inputs: List[int]) -> str:
    if not params:
        return "no arguments"
    return ", ".join(f"{param}={value!r}" for param, value in zip(params, inputs))


def format_safe_case_id(params: List[str], inputs: List[int], expected: Any) -> str:
    return f"{format_input_id(params, inputs)} returns {expected!r}"


def format_pytest_param(values: List[Any], case_id: str) -> str:
    value_list = ", ".join(repr(value) for value in values)
    if value_list:
        return f"        pytest.param({value_list}, id={case_id!r}),"
    return f"        pytest.param(id={case_id!r}),"


def format_safe_tests(
    test_name: str, func_name: str, params: List[str], safe_cases: List[Tuple[int, List[int], Any, str]]
) -> str:
    if not safe_cases:
        return ""

    if len(safe_cases) == 1:
        _, inputs, expected, pc = safe_cases[0]
        call = format_function_call(func_name, [repr(value) for value in inputs])
        return f"""

def test_{test_name}_returns_expected_result():
    assert {call} == {expected!r}
"""

    arg_names = argument_names(params)
    parametrize_names = arg_names + ["expected"]
    call = format_function_call(func_name, arg_names)
    param_lines = "\n".join(
        format_pytest_param(
            inputs + [expected],
            pc,
        )
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
    test_name: str, func_name: str, params: List[str], bug_cases: List[Tuple[int, List[int], str]]
) -> str:
    if not bug_cases:
        return ""

    if len(bug_cases) == 1 or not params:
        _, inputs, pc = bug_cases[0]
        call = format_function_call(func_name, [repr(value) for value in inputs])
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


def generate_pytest_suite(
    file_path: str, func_info: Dict[str, Any], solutions: List[Dict[str, Any]]
) -> None:
    func_name = func_info["name"]
    test_name = python_identifier(func_name)
    params = func_info["params"]

    file_basename = os.path.basename(file_path)
    module_name = os.path.splitext(file_basename)[0]
    tests_dir = generated_tests_dir(file_path)
    os.makedirs(tests_dir, exist_ok=True)

    if module_name.startswith("test_"):
        pytest_path = os.path.join(tests_dir, f"{module_name}_auto.py")
    else:
        pytest_path = os.path.join(tests_dir, f"test_{module_name}_auto.py")
    fallback_module_name = (
        module_name[5:] if module_name.startswith("test_") else module_name
    )
    implementation_module = implementation_module_name(
        file_path,
        module_name,
        fallback_module_name,
    )

    safe_cases = []
    bug_cases = []
    omitted_paths = 0

    func_solutions = [
        sol for sol in solutions if sol.get("tested_func") == func_name
    ]
    if not func_solutions:
        func_solutions = solutions

    for idx, sol in enumerate(func_solutions, start=1):
        pc = sol["pc"]
        expected_sym = sol["variables"]
        sol_type = sol["type"]
        concrete_inputs = solve_constraints(pc, params)

        if concrete_inputs is None:
            omitted_paths += 1
            continue

        if sol_type == "bug":
            bug_cases.append((idx, concrete_inputs, pc))
            continue

        concrete_outputs = {}
        for var_name, expr in expected_sym.items():
            concrete_outputs[var_name] = evaluate_symbolic_expr(
                expr, concrete_inputs, params
            )
        safe_cases.append(
            (
                idx,
                concrete_inputs,
                expected_return_value(concrete_outputs),
                pc,
            )
        )

    needs_pytest = (
        len(safe_cases) > 1 or bool(bug_cases) or not (safe_cases or bug_cases)
    )
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

    print(
        f"  Generated Pytest suite: {pytest_path} "
        f"({len(safe_cases)} safe, {len(bug_cases)} bug, {omitted_paths} omitted)"
    )
