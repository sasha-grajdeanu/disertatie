import pytest

from examples.python_code.condition_error import condition_error


@pytest.mark.parametrize(
    ('x', 'y', 'expected'),
    [
        pytest.param(11, 11, 1, id="('y neq 0) and ('x gt 10 / 'y)"),
        pytest.param(0, 1, 0, id="('y neq 0) and ('x lte 10 / 'y)"),
    ],
)
def test_condition_error_returns_expected_result(x, y, expected):
    assert condition_error(x, y) == expected


def test_condition_error_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        condition_error(0, 0)
