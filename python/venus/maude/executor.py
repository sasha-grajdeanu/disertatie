import os
import subprocess
from typing import Tuple


def strip_known_maude_warnings(output: str) -> str:
    lines = output.splitlines()
    clean_lines = []
    skip_next = False

    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if line.startswith("Warning:") and "multiple distinct parses for statement" in line:
            skip_next = True
            continue
        if line.startswith(
            "Warning: sort declarations for operator if_then_else_fi failed preregularity check"
        ):
            continue
        clean_lines.append(line)

    return "\n".join(clean_lines) + ("\n" if output.endswith("\n") else "")


def run_maude(script: str, temp_filename: str = ".temp_runner.maude") -> Tuple[bool, str]:
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
