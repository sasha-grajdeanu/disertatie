import pytest

from examples.python_code.risky_running_average import risky_running_average


@pytest.mark.parametrize(
    ('n', 'total', 'count', 'expected'),
    [
        pytest.param(0, 11, 11, 1, id="(0 gte 'n) and ('total gt 10) and ('count - 'n neq 0)"),
        pytest.param(0, 10, 1, 10, id="(0 gte 'n) and ('total lte 10) and ('count neq 0)"),
        pytest.param(1, 11, 11, 1, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 gt 10) and ('count - 'n neq 0)"),
        pytest.param(1, 0, 1, 1, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 lte 10) and ('count neq 0)"),
        pytest.param(2, 11, 11, 1, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 gt 10) and ('count - 'n neq 0)"),
        pytest.param(2, 0, 1, 3, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 lte 10) and ('count neq 0)"),
        pytest.param(3, 11, 11, 2, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 gt 10) and ('count - 'n neq 0)"),
        pytest.param(3, 0, 1, 5, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 lte 10) and ('count neq 0)"),
    ],
)
def test_risky_running_average_returns_expected_result(n, total, count, expected):
    assert risky_running_average(n, total, count) == expected


@pytest.mark.parametrize(
    ('n', 'total', 'count'),
    [
        pytest.param(0, 11, 0, id="(0 gte 'n) and ('total gt 10) and ('count - 'n eq 0)"),
        pytest.param(0, 10, 0, id="(0 gte 'n) and ('total lte 10) and ('count eq 0)"),
        pytest.param(1, 11, 1, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 gt 10) and ('count - 'n eq 0)"),
        pytest.param(1, 0, 0, id="(0 lt 'n) and (1 gte 'n) and ('total + 1 lte 10) and ('count eq 0)"),
        pytest.param(2, 11, 2, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 gt 10) and ('count - 'n eq 0)"),
        pytest.param(2, 0, 0, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n) and ('total + 3 lte 10) and ('count eq 0)"),
        pytest.param(3, 11, 3, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 gt 10) and ('count - 'n eq 0)"),
        pytest.param(3, 0, 0, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n) and ('total + 5 lte 10) and ('count eq 0)"),
    ],
)
def test_risky_running_average_raises_zero_division_error(n, total, count):
    with pytest.raises(ZeroDivisionError):
        risky_running_average(n, total, count)
