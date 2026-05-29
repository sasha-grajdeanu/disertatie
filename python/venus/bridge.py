import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

RUNNER_RESULT_PATTERN = re.compile(
    r"result State:\s*<\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*)>", re.DOTALL
)
SOLUTION_SPLIT_PATTERN = re.compile(r"Solution\s+\d+")
S_SYMSTATE_PATTERN = re.compile(
    r"S:SymState\s*-->\s*(.*?)(?:\n\n|\nNo more|\Z)", re.DOTALL
)
SBUG_PATTERN = re.compile(r"sBug\s*\[\s*(.*?)\s*\|\s*(.*?)\s*\]", re.DOTALL)
SSTATE_PATTERN = re.compile(
    r"sState\s*\[\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\]", re.DOTALL
)


def normalize_venus_code_for_maude(code: str) -> str:
    code = re.sub(r"([{}(),;])", r" \1 ", code)
    return re.sub(r"\s+", " ", code).strip()


def strip_known_maude_warnings(output: str) -> str:
    lines = output.splitlines()
    clean_lines = []
    skip_next_statement = False

    for line in lines:
        if skip_next_statement:
            skip_next_statement = False
            continue

        if (
            line.startswith("Warning:")
            and "multiple distinct parses for statement" in line
        ):
            skip_next_statement = True
            continue

        if line.startswith(
            "Warning: sort declarations for operator if_then_else_fi failed preregularity check"
        ):
            continue

        clean_lines.append(line)

    return "\n".join(clean_lines) + ("\n" if output.endswith("\n") else "")


def generate_run_script(code: str) -> str:
    code = normalize_venus_code_for_maude(code)
    return f"""load maude/venus-lang-transition-machine.maude
mod RUNNER is
    protecting VENUS-TS .
    op checkedProgram : Inst -> Inst .
    var I : Inst .
    eq checkedProgram(I) = I .
    op pgm : -> Inst .
    eq pgm = checkedProgram(
{code}) .
endm
rew < pgm # cNil | sNil | empty > .
quit
"""


def generate_symbolic_test_script(code: str, depth: int = 3) -> str:
    code = normalize_venus_code_for_maude(code)
    return f"""load maude/venus-lang-testing.maude

mod TEST-RUNNER is
    protecting VENUS-TS .
    protecting VENUS-SYMBOLIC .

    op checkedProgram : Inst -> Inst .
    var I : Inst .
    eq checkedProgram(I) = I .

    op pgm : -> Inst .
    eq pgm = checkedProgram(
{code}) .
    eq loopDepth = {depth} .
endm

red pgm .

search [1000, 100000] in TEST-RUNNER : sState [ pgm # cSymTest # cNil | true | empty ] =>! S:SymState .

quit
"""


def run_maude(
    script: str, temp_filename: str = ".temp_runner.maude"
) -> Tuple[bool, str]:
    with open(temp_filename, "w") as f:
        f.write(script)
    try:
        result = subprocess.run(
            ["maude", "-no-advise", "-no-wrap", "-no-banner", temp_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        raw_output = result.stdout
        output = strip_known_maude_warnings(raw_output)
        has_error = (
            "no parse" in raw_output
            or "checkedProgram(" in raw_output
            or "result [" in raw_output
        )
        return (not has_error, output)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def parse_runner_output(output: str) -> Optional[Dict[str, Any]]:
    match = RUNNER_RESULT_PATTERN.search(output)
    if not match:
        return None
    ctrl, stk, mry = match.groups()
    variables, functions = _parse_memory(mry)
    return {"variables": variables, "functions": functions}


def _parse_memory(mry_str: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    if mry_str.strip() == "empty":
        return ({}, {})
    var_pattern = re.compile("'([a-zA-Z0-9_]+)\\s*->\\s*(-?\\d+|undefined)")
    variables = {}
    for match in var_pattern.finditer(mry_str):
        variables[match.group(1)] = match.group(2)
    func_pattern = re.compile("'([a-zA-Z0-9_]+)\\s*=>\\s*\\[(.*?)\\]")
    functions = {}
    for match in func_pattern.finditer(mry_str):
        functions[match.group(1)] = match.group(2)
    return (variables, functions)


def parse_symbolic_search_output(output: str) -> List[Dict[str, Any]]:
    solutions = []
    blocks = SOLUTION_SPLIT_PATTERN.split(output)
    for block in blocks[1:]:
        s_match = S_SYMSTATE_PATTERN.search(block)
        if not s_match:
            continue
        state_str = s_match.group(1).strip()

        is_bug = state_str.startswith("sBug")
        if is_bug:
            match = SBUG_PATTERN.match(state_str)
            if match:
                pc, mry = match.groups()
                variables, tested_func = _parse_symbolic_memory(mry)
                solutions.append(
                    {
                        "type": "bug",
                        "pc": pc.strip(),
                        "variables": variables,
                        "tested_func": tested_func,
                    }
                )
        else:
            match = SSTATE_PATTERN.match(state_str)
            if match:
                ctrl, pc, mry = match.groups()
                variables, tested_func = _parse_symbolic_memory(mry)
                solutions.append(
                    {
                        "type": "safe",
                        "pc": pc.strip(),
                        "variables": variables,
                        "tested_func": tested_func,
                    }
                )
    return solutions


def _parse_symbolic_memory(mry_str: str) -> Tuple[Dict[str, str], str]:
    tested_pattern = re.compile(r"tested\('([a-zA-Z0-9_]+)\)")
    tested_match = tested_pattern.search(mry_str)
    tested_func = tested_match.group(1) if tested_match else "Unknown"

    var_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*->s\s*([^,\]]*)")
    variables = {}
    for match in var_pattern.finditer(mry_str):
        val = match.group(2).strip()
        if val.endswith(")"):
            if val.count(")") > val.count("("):
                val = val[:-1].strip()
        variables[match.group(1)] = val

    return variables, tested_func
