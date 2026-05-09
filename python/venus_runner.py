import sys
import os
import subprocess
import re

def parse_memory(mry_str):
    if mry_str.strip() == "empty":
        return {}, {}
    
    # Extract integer variables: 'name -> value
    # value can be negative, so -?\d+, or 'undefined'
    var_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*->\s*(-?\d+|undefined)")
    variables = {}
    for match in var_pattern.finditer(mry_str):
        variables[match.group(1)] = match.group(2)

    # Extract functions: 'name => [args, body]
    func_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*=>\s*\[(.*?)\]")
    functions = {}
    for match in func_pattern.finditer(mry_str):
        functions[match.group(1)] = match.group(2)

    return variables, functions

def run_venus(file_path):
    with open(file_path, 'r') as f:
        code = f.read().strip()
        while code.endswith('.'):
            code = code[:-1].strip()
        
    maude_script = f"""
load maude/venus-lang-transition-machine.maude

mod RUNNER is
    protecting VENUS-TS .
    op pgm : -> Inst .
    eq pgm = 
{code} .
endm

rew < pgm # cNil | sNil | empty > .
quit
"""
    temp_file = ".temp_runner.maude"
    with open(temp_file, 'w') as f:
        f.write(maude_script)

    try:
        # Run maude
        result = subprocess.run(["maude", "-no-advise", "-no-wrap", "-no-banner", temp_file], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, stdin=subprocess.DEVNULL)
        
        output = result.stdout
        
        # Check for parsing or rewrite errors
        if "Warning:" in output or "ERROR" in output or "no parse" in output:
            print("--- Maude Error / Warning ---")
            print(output)
            return

        # Find result state (no re.DOTALL so we stay on one line, greedy on the last part to capture the final >)
        match = re.search(r"result State:\s*<\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*)>", output)
        if not match:
            print("Failed to parse Maude output. Raw output:")
            print(output)
            return
            
        ctrl, stk, mry = match.groups()
        
        variables, functions = parse_memory(mry)

        print("\n" + "="*40)
        print(" VENUS PROGRAM EXECUTION SUCCESSFUL")
        print("="*40)
        
        if variables:
            print("\n VARIABLES:")
            print("-" * 20)
            max_len = max(len(v) for v in variables)
            for var, val in sorted(variables.items()):
                print(f" {var:<{max_len}} = {val}")
        
        if functions:
            print("\n FUNCTIONS:")
            print("-" * 20)
            for func, body in sorted(functions.items()):
                print(f" {func} => [{body}]")
                
        if not variables and not functions:
            print("\n Memory is empty.")
            
        print("\n" + "="*40 + "\n")

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python venus_runner.py <file.venus>")
        sys.exit(1)
        
    run_venus(sys.argv[1])
