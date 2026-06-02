import pytest

from examples.python_code.descending_sum import descending_sum


@pytest.mark.parametrize(
    ('n', 'expected'),
    [
        pytest.param(0, 0, id="'n lte 0"),
        pytest.param(1, 1, id="('n gt 0) and ('n - 1 lte 0)"),
        pytest.param(2, 3, id="('n gt 0) and ('n - 1 gt 0) and ('n - 2 lte 0)"),
        pytest.param(3, 6, id="('n gt 0) and ('n - 1 gt 0) and ('n - 2 gt 0) and ('n - 3 lte 0)"),
    ],
)
def test_descending_sum_returns_expected_result(n, expected):
    assert descending_sum(n) == expected
