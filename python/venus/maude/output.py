import re
from typing import Any, Dict, List, Optional, Tuple

_RUNNER_RESULT = re.compile(
    r"result State:\s*<\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*)>", re.DOTALL
)
_SOLUTION_SPLIT = re.compile(r"Solution\s+\d+")
_SYMSTATE = re.compile(
    r"S:SymState\s*-->\s*(.*?)(?:\n\n|\nNo more|\Z)", re.DOTALL
)
_SBUG = re.compile(r"sBug\s*\[\s*(.*?)\s*\|\s*(.*?)\s*\]", re.DOTALL)
_SSTATE = re.compile(
    r"sState\s*\[\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\]", re.DOTALL
)


def parse_runner_output(output: str) -> Optional[Dict[str, Any]]:
    match = _RUNNER_RESULT.search(output)
    if not match:
        return None
    _, _, mry = match.groups()
    variables, functions = _parse_memory(mry)
    return {"variables": variables, "functions": functions}


def _parse_memory(mry_str: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    if mry_str.strip() == "empty":
        return ({}, {})
    var_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*->\s*(-?\d+|undefined)")
    variables = {m.group(1): m.group(2) for m in var_pattern.finditer(mry_str)}
    func_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*=>\s*\[(.*?)\]")
    functions = {m.group(1): m.group(2) for m in func_pattern.finditer(mry_str)}
    return (variables, functions)


def parse_symbolic_search_output(output: str) -> List[Dict[str, Any]]:
    solutions = []
    for block in _SOLUTION_SPLIT.split(output)[1:]:
        s_match = _SYMSTATE.search(block)
        if not s_match:
            continue
        state_str = s_match.group(1).strip()

        if state_str.startswith("sBug"):
            match = _SBUG.match(state_str)
            if match:
                pc, mry = match.groups()
                variables, tested_func = _parse_symbolic_memory(mry)
                solutions.append({
                    "type": "bug",
                    "pc": pc.strip(),
                    "variables": variables,
                    "tested_func": tested_func,
                })
        else:
            match = _SSTATE.match(state_str)
            if match:
                _, pc, mry = match.groups()
                variables, tested_func = _parse_symbolic_memory(mry)
                solutions.append({
                    "type": "safe",
                    "pc": pc.strip(),
                    "variables": variables,
                    "tested_func": tested_func,
                })
    return solutions


def _parse_symbolic_memory(mry_str: str) -> Tuple[Dict[str, str], str]:
    tested_match = re.search(r"tested\('([a-zA-Z0-9_]+)\)", mry_str)
    tested_func = tested_match.group(1) if tested_match else "Unknown"

    variables = {}
    for match in re.finditer(r"'([a-zA-Z0-9_]+)\s*->s\s*([^,\]]*)", mry_str):
        val = match.group(2).strip()
        if val.endswith(")") and val.count(")") > val.count("("):
            val = val[:-1].strip()
        variables[match.group(1)] = val

    return variables, tested_func
