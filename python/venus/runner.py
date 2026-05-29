import re
from .bridge import generate_run_script, run_maude, parse_runner_output
from .formatter import format_runner_output


def run_venus(file_path: str) -> None:
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
