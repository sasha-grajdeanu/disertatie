import re
from typing import Dict, List, Optional


def extract_all_functions(code: str) -> Dict[str, List[str]]:
    funcs: Dict[str, List[str]] = {}
    pattern = r"def\s+'(\w+)\s*\(\s*(.*?)\s*\)\s*\{"
    for match in re.finditer(pattern, code):
        func_name = match.group(1)
        params_str = match.group(2).strip()
        if params_str and params_str != "emptyList":
            params = re.findall(r"'(\w+)", params_str)
        else:
            params = []
        funcs[func_name] = params
    return funcs


def extract_func_body(source_code: str, func_name: str) -> Optional[str]:
    pattern = rf"def\s+'{re.escape(func_name)}\s*\(.*?\)\s*\{{"
    match = re.search(pattern, source_code, re.DOTALL)
    if not match:
        return None

    start = match.start()
    depth = 0
    i = match.end() - 1

    while i < len(source_code):
        if source_code[i] == "{":
            depth += 1
        elif source_code[i] == "}":
            depth -= 1
            if depth == 0:
                return source_code[start : i + 1]
        i += 1

    return None
