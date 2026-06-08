import re


def normalize_venus_code_for_maude(code: str) -> str:
    code = re.sub(r"([{}(),;])", r" \1 ", code)
    return re.sub(r"\s+", " ", code).strip()


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
