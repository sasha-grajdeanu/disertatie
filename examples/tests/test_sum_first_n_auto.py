import pytest

from examples.python_code.sum_first_n import sum_first_n


@pytest.mark.parametrize(
    ('n', 'expected'),
    [
        pytest.param(0, 0, id="0 gte 'n"),
        pytest.param(1, 0, id="(0 lt 'n) and (1 gte 'n)"),
        pytest.param(2, 1, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n)"),
        pytest.param(3, 3, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n)"),
    ],
)
def test_sum_first_n_returns_expected_result(n, expected):
    assert sum_first_n(n) == expected
