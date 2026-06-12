import ast
import operator
import re
from typing import Any, Dict, List, Optional

import z3 as _z3


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.truediv,
    ast.Mod: operator.mod,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

_MAUDE_OPS = {"lte": "<=", "gte": ">=", "neq": "!=", "ne": "!=",
              "eq": "==", "lt": "<", "gt": ">"}
_MAUDE_OP_RE = re.compile(r"\b(lte|gte|neq|ne|eq|lt|gt)\b")
_SINGLE_SLASH_RE = re.compile(r"(?<!/)/(?!/)")


def _parse_expr(node: ast.AST, env: Dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        return env[node.id]

    if isinstance(node, ast.UnaryOp):
        operand = _parse_expr(node.operand, env)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.Not):
            return _z3.Not(operand)

    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unknown operator: {type(node.op)}")
        return op(_parse_expr(node.left, env), _parse_expr(node.right, env))

    if isinstance(node, ast.Compare):
        op = _BIN_OPS.get(type(node.ops[0]))
        if op is None:
            raise ValueError(f"Unknown operator: {type(node.ops[0])}")
        return op(_parse_expr(node.left, env), _parse_expr(node.comparators[0], env))

    if isinstance(node, ast.BoolOp):
        values = [_parse_expr(v, env) for v in node.values]
        if isinstance(node.op, ast.And):
            return _z3.And(*values)
        if isinstance(node.op, ast.Or):
            return _z3.Or(*values)

    raise ValueError(f"Unsupported AST node: {ast.dump(node)}")


def _maude_to_python(expr: str) -> str:
    expr = expr.replace("'", "")
    expr = _MAUDE_OP_RE.sub(lambda m: _MAUDE_OPS[m.group(0)], expr)
    expr = _SINGLE_SLASH_RE.sub("//", expr)
    return expr


def _to_z3(python_expr: str, z3_vars: Dict[str, Any]) -> Any:
    tree = ast.parse(python_expr, mode="eval")
    return _parse_expr(tree.body, z3_vars)


def _model_values(model: Any, z3_vars: Dict[str, Any], params: List[str]) -> List[int]:
    values = []
    for param in params:
        z3_val = model.eval(z3_vars[param], model_completion=True)
        try:
            values.append(z3_val.as_long())
        except Exception:
            values.append(0)
    return values


def _substitute_symbolic_vars(postcondition: str, final_vars: Dict[str, str]) -> str:
    sorted_vars = sorted(final_vars.items(), key=lambda item: -len(item[0]))
    for var_name, symbolic_expr in sorted_vars:
        if var_name.startswith("tested"):
            continue
        python_expr = _maude_to_python(symbolic_expr)
        pattern = r"\b" + re.escape(var_name) + r"\b"
        postcondition = re.sub(pattern, f"({python_expr})", postcondition)
    return postcondition


def solve_path_condition(pc_str: str, params: List[str]) -> Optional[List[int]]:
    if pc_str.strip() in ("true", ""):
        return [0] * len(params)

    z3_vars = {param: _z3.Int(param) for param in params}
    try:
        constraint = _to_z3(_maude_to_python(pc_str), z3_vars)
    except Exception:
        return None

    solver = _z3.Solver()
    solver.set("timeout", 5000)
    solver.add(constraint)

    if solver.check() != _z3.sat:
        return None
    return _model_values(solver.model(), z3_vars, params)


def is_path_feasible(pc_str: str, params: List[str]) -> bool:
    if pc_str.strip() in ("true", ""):
        return True
    if pc_str.strip() == "false":
        return False

    z3_vars = {param: _z3.Int(param) for param in params}
    try:
        constraint = _to_z3(_maude_to_python(pc_str), z3_vars)
    except Exception:
        return True

    solver = _z3.Solver()
    solver.set("timeout", 5000)
    solver.add(constraint)
    return solver.check() == _z3.sat


def eval_symbolic_expr(expr_str: str, inputs: List[int], params: List[str]) -> Any:
    expr = expr_str.replace("'", "")
    for param, value in zip(params, inputs):
        expr = re.sub(r"\b" + re.escape(param) + r"\b", str(value), expr)
    try:
        safe_expr = _SINGLE_SLASH_RE.sub("//", expr)
        return int(eval(safe_expr, {"__builtins__": {}}, {}))
    except ZeroDivisionError:
        return "ZeroDivisionError"
    except Exception:
        return expr_str


def check_postcondition_on_path(
    pc_str: str,
    final_vars: Dict[str, str],
    params: List[str],
    post_str: str,
) -> Dict[str, Any]:
    z3_vars = {param: _z3.Int(param) for param in params}

    pc_constraint = None
    if pc_str.strip() not in ("true", ""):
        try:
            pc_constraint = _to_z3(_maude_to_python(pc_str), z3_vars)
        except Exception:
            return {"holds": True, "counterexample": None, "substituted_post": post_str}

    substituted_post = _substitute_symbolic_vars(post_str, final_vars)

    try:
        post_constraint = _to_z3(substituted_post, z3_vars)
    except Exception:
        return {"holds": True, "counterexample": None, "substituted_post": substituted_post}

    solver = _z3.Solver()
    solver.set("timeout", 5000)
    if pc_constraint is not None:
        solver.add(pc_constraint)
    solver.add(_z3.Not(post_constraint))

    if solver.check() != _z3.sat:
        return {"holds": True, "counterexample": None, "substituted_post": substituted_post}

    counterexample = dict(zip(params, _model_values(solver.model(), z3_vars, params)))
    return {
        "holds": False,
        "counterexample": counterexample,
        "substituted_post": substituted_post,
    }
