import pytest

from examples.python_code.risky_running_average import risky_running_average


@pytest.mark.parametrize(
    ('n', 'total', 'count', 'expected'),
    [
        pytest.param(0, 11, 1, 11, id="(0 gte 'n) and ('total gt 10) and ('count - 'n neq 0)"),
        pytest.param(0, 10, 1, 10, id="(0 gte 'n) and ('total lte 10) and ('count neq 0)"),
        pytest.param(1, 10, 2, 11, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 gt 10) and ('count - 'n neq 0)"),
        pytest.param(1, 9, 1, 10, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 lte 10) and ('count neq 0)"),
        pytest.param(2, 8, 3, 11, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 gt 10) and ('count - 'n neq 0)"),
        pytest.param(2, 7, 1, 10, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 lte 10) and ('count neq 0)"),
        pytest.param(3, 6, 4, 11, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 gt 10) and ('count - 'n neq 0)"),
        pytest.param(3, 5, 1, 10, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 lte 10) and ('count neq 0)"),
    ],
)
def test_risky_running_average_returns_expected_result(n, total, count, expected):
    assert risky_running_average(n, total, count) == expected


@pytest.mark.parametrize(
    ('n', 'total', 'count'),
    [
        pytest.param(0, 11, 0, id="(0 gte 'n) and ('total gt 10) and ('count - 'n eq 0)"),
        pytest.param(0, 10, 0, id="(0 gte 'n) and ('total lte 10) and ('count eq 0)"),
        pytest.param(1, 10, 1, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 gt 10) and ('count - 'n eq 0)"),
        pytest.param(1, 9, 0, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 lte 10) and ('count eq 0)"),
        pytest.param(2, 8, 2, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 gt 10) and ('count - 'n eq 0)"),
        pytest.param(2, 7, 0, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 lte 10) and ('count eq 0)"),
        pytest.param(3, 6, 3, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 gt 10) and ('count - 'n eq 0)"),
        pytest.param(3, 5, 0, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 lte 10) and ('count eq 0)"),
    ],
)
def test_risky_running_average_raises_zero_division_error(n, total, count):
    with pytest.raises(ZeroDivisionError):
        risky_running_average(n, total, count)
