import os
import subprocess
import re
from collections import defaultdict

def parse_scenario_memory(mry_str):
    if mry_str.strip() == "empty":
        return {}, {}, 'Unknown'
        
    tested_pattern = re.compile(r"tested\('([a-zA-Z0-9_]+)\)")
    tested_match = tested_pattern.search(mry_str)
    tested_func = tested_match.group(1) if tested_match else 'Unknown'

    var_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*->\s*(-?\d+|undefined)")
    variables = {}
    for match in var_pattern.finditer(mry_str):
        variables[match.group(1)] = match.group(2)
        
    func_pattern = re.compile(r"'([a-zA-Z0-9_]+)\s*=>\s*\[")
    functions = set()
    for match in func_pattern.finditer(mry_str):
        functions.add(match.group(1))
        
    return variables, functions, tested_func

def extract_all_functions(code):
    matches = re.finditer(r"def\s+'(\w+)\s*\(\s*(.*?)\s*\)\s*\{", code)
    funcs = {}
    for match in matches:
        func_name = match.group(1)
        params_str = match.group(2).strip()
        params = []
        if params_str != 'emptyList' and params_str:
            params = re.findall(r"'(\w+)", params_str)
        funcs[func_name] = params
    return funcs

def generate_maude_script(code):
    script = "load maude/venus-lang-transition-machine.maude\n"
    script += "load maude/venus-lang-testing.maude\n\n"
    script += "mod TEST-RUNNER is\n"
    script += "    protecting VENUS-TS .\n"
    script += "    protecting VENUS-TESTING .\n\n"
    script += "    op pgm : -> Inst .\n"
    script += f"    eq pgm =\n{code} .\n"
    script += "endm\n\n"
    script += f"search [,500] < pgm # cAutoTest # cNil | sNil | empty > =>! "
    script += "< CTRL:Control | STK:Stack | MRY:Memory > .\n\n"
    script += "quit\n"
    return script

def parse_search_output(output):
    solutions = []
    blocks = re.split(r'Solution\s+\d+', output)

    for block in blocks[1:]:
        ctrl_match = re.search(r"CTRL:Control\s*-->\s*(.*?)$", block, re.MULTILINE)
        mry_match = re.search(r"MRY:Memory\s*-->\s*(.*?)(?:\n\n|\nNo more|\Z)", block, re.DOTALL)

        ctrl = ctrl_match.group(1).strip() if ctrl_match else "cNil"
        mry_str = mry_match.group(1).strip() if mry_match else "empty"

        variables, functions, tested_func = parse_scenario_memory(mry_str)

        solutions.append({
            'variables': variables,
            'functions': functions,
            'tested_func': tested_func,
            'control': ctrl,
            'is_stuck': ctrl != 'cNil'
        })

    return solutions

def detect_loop_vars(code):
    """Detect all variables modified inside loop bodies from Venus source code."""
    loop_vars = set()
    # Match while loop conditions: while ('var lt/lte/gt/gte ...) do
    for m in re.finditer(r"while\s*\(\s*'(\w+)\s+(?:lt|lte|gt|gte|eq|neq)\s", code):
        loop_vars.add(m.group(1))
    # Match for loop iterators: for ( 'var := ...
    for m in re.finditer(r"for\s*\(\s*'(\w+)\s*:=", code):
        loop_vars.add(m.group(1))
    # Match all variables assigned inside while loop bodies
    for m in re.finditer(r"while\s*\(.*?\)\s*do\s*(.*?)\s*od", code, re.DOTALL):
        for assign in re.finditer(r"'(\w+)\s*:=", m.group(1)):
            loop_vars.add(assign.group(1))
    # Match all variables assigned inside for loop bodies
    for m in re.finditer(r"for\s*\(.*?\)\s*do\s*(.*?)\s*od", code, re.DOTALL):
        for assign in re.finditer(r"'(\w+)\s*:=", m.group(1)):
            loop_vars.add(assign.group(1))
    return loop_vars

def extract_condition_constants(source_code, func_name):
    """Extract the integer constants that appear in branching conditions for a function.
    Mirrors what the Maude extractCondConstants does."""
    func_body = extract_func_body(source_code, func_name)
    if not func_body:
        return set()
    
    constants = set()
    # Extract integers from condition expressions (if/while conditions)
    for cond_match in re.finditer(r'(?:if|while)\s*\((.*?)\)\s*(?:then|do)', func_body):
        cond = cond_match.group(1)
        for num in re.finditer(r'(?<!\w)(-?\d+)(?!\w)', cond):
            constants.add(int(num.group(1)))
    return constants

def extract_func_body(source_code, func_name):
    """Extract the source code body of a function, handling nested braces."""
    pattern = rf"def\s+'{re.escape(func_name)}\s*\(.*?\)\s*\{{"
    match = re.search(pattern, source_code, re.DOTALL)
    if not match:
        return None
    start = match.start()
    # Count braces to find the matching closing brace
    depth = 0
    i = match.end() - 1  # position of the opening {
    while i < len(source_code):
        if source_code[i] == '{':
            depth += 1
        elif source_code[i] == '}':
            depth -= 1
            if depth == 0:
                return source_code[start:i+1]
        i += 1
    return None

def get_called_funcs_vars(source_code, func_name, all_funcs):
    """Get variable names that belong to OTHER functions called from func_name.
    These leak into memory but are not meaningful outputs of func_name."""
    func_body = extract_func_body(source_code, func_name)
    if not func_body:
        return set()
    
    leaked_vars = set()
    # Find all call statements in this function's body
    for call_match in re.finditer(r"call\s+'(\w+)\s*\(", func_body):
        called_name = call_match.group(1)
        if called_name == func_name:
            continue  # skip recursive calls
        # Include parameter names of the called function (they get bound in memory)
        called_params = all_funcs.get(called_name, [])
        for p in called_params:
            if p not in all_funcs.get(func_name, []):
                leaked_vars.add(p)
        # Get the body of the called function and extract assigned vars
        called_body = extract_func_body(source_code, called_name)
        if called_body:
            for assign in re.finditer(r"'(\w+)\s*:=", called_body):
                var = assign.group(1)
                # Only leak if it's not also a param of the current function
                if var not in all_funcs.get(func_name, []):
                    leaked_vars.add(var)
            # Also recurse into functions called by the called function
            leaked_vars |= get_called_funcs_vars(source_code, called_name, all_funcs)
    return leaked_vars

def describe_scenario_path(source_code, func_name, key_vars, input_vars_sample, loop_vars):
    """Try to generate a human-readable description of which execution path this scenario represents."""
    func_body = extract_func_body(source_code, func_name)
    if not func_body:
        return None
    
    descriptions = []
    
    # Check if there are loops
    has_loop = bool(re.search(r'(?:while|for)\s*\(', func_body))
    
    # Extract only `if` conditions that compare input params directly to constants
    if_conditions = []
    for cond_match in re.finditer(r'if\s*\((.*?)\)\s*then', func_body):
        if_conditions.append(cond_match.group(1).strip())
    
    # Build a readable description based on the input values
    if input_vars_sample and if_conditions:
        parts = []
        for cond in if_conditions:
            # Parse condition like 'var op val
            m = re.match(r"'(\w+)\s+(lt|gt|eq|lte|gte|neq)\s+(\d+)", cond)
            if m:
                var, op, val = m.group(1), m.group(2), m.group(3)
                if var in input_vars_sample:
                    input_val = int(input_vars_sample[var])
                    op_symbols = {'lt': '<', 'gt': '>', 'eq': '==', 'lte': '<=', 'gte': '>=', 'neq': '!='}
                    op_sym = op_symbols.get(op, op)
                    result = eval(f"{input_val} {op_sym} {val}")
                    cond_readable = f"'{var} {op_sym} {val}"
                    parts.append(f"{cond_readable} is {'TRUE' if result else 'FALSE'}")
        if parts:
            descriptions.append(', '.join(parts))
    
    if has_loop:
        # Check loop iteration info from loop vars
        all_loop_in_output = {k: v for k, v in key_vars.items() if k in loop_vars}
        if all_loop_in_output:
            descriptions.append("loop executed")
    
    return ' → '.join(descriptions) if descriptions else None

def format_results(funcs_info, solutions, source_code=''):
    W = 62  # output width
    
    print(f"\n{'═' * W}")
    print(f"  🔍 VENUS AUTOMATED TEST SCENARIO DISCOVERY")
    print(f"{'═' * W}")
    print(f"  Method: Boundary Value Analysis + Exhaustive Path Exploration")
    print(f"  Engine: Maude rewriting-based state-space search")
    
    loop_vars = detect_loop_vars(source_code) if source_code else set()
    
    solutions_by_func = defaultdict(list)
    for s in solutions:
        solutions_by_func[s['tested_func']].append(s)
        
    if not solutions_by_func:
        print(f"\n  ❌ No solutions found. The program may have infinite loops.")
        print(f"\n{'═' * W}\n")
        return

    for func_name, func_solutions in solutions_by_func.items():
        if func_name == 'Unknown' and not func_solutions:
            continue
            
        params = funcs_info.get(func_name, [])
        successful = [s for s in func_solutions if not s['is_stuck']]
        stuck = [s for s in func_solutions if s['is_stuck']]
        
        # --- Function header ---
        print(f"\n{'━' * W}")
        print(f"  📦 Function: '{func_name}({', '.join(params) if params else ''})'")
        print(f"{'━' * W}")
        
        # --- Show source code ---
        func_body_src = extract_func_body(source_code, func_name)
        if func_body_src:
            print(f"\n  Source code:")
            for line in func_body_src.strip().split('\n'):
                print(f"    │ {line.strip()}")

        # --- Show test values used ---
        cond_constants = extract_condition_constants(source_code, func_name)
        all_test_values = {0, 1}  # always included
        for c in cond_constants:
            all_test_values.update([c - 1, c, c + 1])
        
        # Detect if function has loops (for invariant info display)
        has_loop = bool(re.search(r'(?:while|for)\s*\(', func_body_src or ''))
        
        if cond_constants:
            print(f"\n  Test value generation (BVA):")
            print(f"    Constants in conditions: {{{', '.join(str(c) for c in sorted(cond_constants))}}}")
            print(f"    Boundary values (N±1):   {{{', '.join(str(v) for v in sorted(all_test_values))}}}")
            if len(params) == 1:
                print(f"    Applied to parameter:    '{params[0]}'")
            elif len(params) > 1:
                print(f"    Combinations across:     {', '.join(params)}")
        else:
            print(f"\n  Test values: {{0, 1}} (no condition constants found)")
        
        if has_loop and len(params) == 1:
            print(f"\n  Loop invariant analysis:")
            print(f"    Equational evaluator scanned inputs n=0..200")
            print(f"    Looking for values where post-loop branch outcome changes")
            print(f"    (Boundary values automatically merged into test set)")
        
        # --- Identify cross-function leaked vars ---
        leaked_vars = get_called_funcs_vars(source_code, func_name, funcs_info)
        
        # --- Build scenarios ---
        scenarios = defaultdict(list)
        for s in successful:
            output_vars = {k: v for k, v in s['variables'].items()
                           if k not in params and k not in s['functions']
                           and k not in leaked_vars}
            result_vars = {k: v for k, v in output_vars.items() if k not in loop_vars}
            iter_vars = {k: v for k, v in output_vars.items() if k in loop_vars}
            
            # Group by non-loop output vars when available, else by all vars
            if result_vars:
                key = tuple(sorted(result_vars.items()))
            else:
                key = tuple(sorted(output_vars.items()))
            
            input_vars = {k: v for k, v in s['variables'].items() if k in params}
            scenarios[key].append((input_vars, iter_vars))
            
        if scenarios:
            total_inputs = sum(len(entries) for entries in scenarios.values())
            print(f"\n  {'─' * (W - 2)}")
            print(f"  📊 Results: {len(scenarios)} distinct execution path(s) "
                  f"from {total_inputs} test case(s)")
            print(f"  {'─' * (W - 2)}")
            
            for i, (key, entries) in enumerate(scenarios.items(), 1):
                key_vars = dict(key)
                has_non_loop_output = any(k not in loop_vars for k in key_vars)
                
                # Try to describe the path
                sample_input = entries[0][0] if entries else {}
                path_desc = describe_scenario_path(source_code, func_name, key_vars, sample_input, loop_vars)
                
                print(f"\n  ┌─ Scenario {i}" + (f": {path_desc}" if path_desc else ""))
                print(f"  │")
                
                # Inputs
                print(f"  │  Inputs ({len(entries)} case{'s' if len(entries) != 1 else ''} "
                      f"produce this outcome):")
                for inp, _ in entries:
                    inp_str = ', '.join(f"'{k} = {v}" for k, v in sorted(inp.items()))
                    if not inp_str: inp_str = "(no inputs)"
                    print(f"  │    → {inp_str}")
                
                # Output
                print(f"  │")
                output_label = "Output variables" if has_non_loop_output else "Final state"
                print(f"  │  {output_label}:")
                for var, val in sorted(key_vars.items()):
                    label = ""
                    if var in loop_vars:
                        label = "  (loop iterator)"
                    print(f"  │    '{var} = {val}{label}")
                
                # Loop state
                all_loop_states = [lv for _, lv in entries if lv]
                if all_loop_states and has_non_loop_output:
                    unique_states = set(tuple(sorted(lv.items())) for lv in all_loop_states)
                    if len(unique_states) == 1:
                        loop_state = dict(list(unique_states)[0])
                        print(f"  │")
                        print(f"  │  Loop variables after execution:")
                        for k, v in sorted(loop_state.items()):
                            print(f"  │    '{k} = {v}")
                    elif len(unique_states) > 1:
                        print(f"  │")
                        print(f"  │  Loop variables (vary per input):")
                        for inp, lv in entries:
                            if lv:
                                inp_str = ', '.join(f"'{k}={v}" for k, v in sorted(inp.items()))
                                lv_str = ', '.join(f"'{k}={v}" for k, v in sorted(lv.items()))
                                print(f"  │    {inp_str} → {lv_str}")
                
                print(f"  └{'─' * (W - 3)}")
        else:
            print(f"\n  No successful scenarios found.")
            
        # --- Stuck states (errors) ---
        if stuck:
            print(f"\n  ⚠️  RUNTIME ERRORS DETECTED: {len(stuck)} stuck state(s)")
            print(f"  {'─' * (W - 2)}")
            for i, s in enumerate(stuck, 1):
                input_vars = {k: v for k, v in s['variables'].items() if k in params}
                inp_str = ', '.join(f"'{k} = {v}" for k, v in sorted(input_vars.items()))
                if not inp_str: inp_str = "(no inputs)"
                
                # Determine cause
                if 'cDiv' in s['control']:
                    cause = "Division by zero"
                    explanation = "The divisor evaluates to 0 for this input."
                elif 'cMod' in s['control']:
                    cause = "Modulo by zero"
                    explanation = "The modulo operand evaluates to 0 for this input."
                else:
                    cause = "Unknown runtime error"
                    explanation = f"Execution stuck at control: {s['control']}"
                
                print(f"\n  ┌─ Error {i}: {cause}")
                print(f"  │  Input: {inp_str}")
                print(f"  │  Why:   {explanation}")
                print(f"  └{'─' * (W - 3)}")

    # --- Summary ---
    total_funcs = len(solutions_by_func)
    total_solutions = len(solutions)
    total_errors = sum(1 for s in solutions if s['is_stuck'])
    total_ok = total_solutions - total_errors
    
    print(f"\n{'═' * W}")
    print(f"  📋 SUMMARY")
    print(f"  {'─' * (W - 2)}")
    print(f"  Functions tested:    {total_funcs}")
    print(f"  Total test cases:    {total_solutions}")
    print(f"  Successful:          {total_ok}")
    if total_errors:
        print(f"  Runtime errors:      {total_errors}")
    print(f"{'═' * W}\n")

def run_test_generator(file_path):
    with open(file_path, 'r') as f:
        code = f.read().strip()
        while code.endswith('.'):
            code = code[:-1].strip()
            
    code = re.sub(r'\}\s*def', '} ; def', code)
    funcs_info = extract_all_functions(code)
    script = generate_maude_script(code)

    temp_file = ".temp_test.maude"
    with open(temp_file, 'w') as f:
        f.write(script)

    try:
        result = subprocess.run(
            ["maude", "-no-advise", "-no-wrap", "-no-banner", temp_file],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, stdin=subprocess.DEVNULL
        )
        output = result.stdout

        if 'no parse' in output:
            print("--- Maude Error ---")
            print(output)
            return

        solutions = parse_search_output(output)
        format_results(funcs_info, solutions, code)

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
