import pytest

from examples.python_code.multiple_branches import multiple_branches


@pytest.mark.parametrize(
    ('x', 'expected'),
    [
        pytest.param(1, 1, id="'x gt 0"),
        pytest.param(-1, -1, id="('x lte 0) and ('x lt 0)"),
        pytest.param(0, 0, id="('x lte 0) and ('x gte 0)"),
    ],
)
def test_multiple_branches_returns_expected_result(x, expected):
    assert multiple_branches(x) == expected
