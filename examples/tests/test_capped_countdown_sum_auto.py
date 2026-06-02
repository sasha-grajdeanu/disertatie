import pytest

from examples.python_code.capped_countdown_sum import capped_countdown_sum


@pytest.mark.parametrize(
    ('n', 'limit', 'expected'),
    [
        pytest.param(0, 0, 0, id="0 gte 'n"),
        pytest.param(1, -1, -1, id="(0 lt 'n) and (0 gt 'limit) and (1 gte 'n)"),
        pytest.param(1, 0, 0, id="(0 lt 'n) and (0 lte 'limit) and (1 gte 'n)"),
        pytest.param(2, -1, -1, id="(0 lt 'n) and (0 gt 'limit) and (1 lt 'n) and (2 gte 'n)"),
        pytest.param(2, 0, 0, id="(0 lt 'n) and (0 lte 'limit) and (1 lt 'n) and (1 gt 'limit) and (2 gte 'n)"),
        pytest.param(2, 1, 1, id="(0 lt 'n) and (0 lte 'limit) and (1 lt 'n) and (1 lte 'limit) and (2 gte 'n)"),
        pytest.param(3, -1, -1, id="(0 lt 'n) and (0 gt 'limit) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n)"),
        pytest.param(3, 0, 0, id="(0 lt 'n) and (0 lte 'limit) and (1 lt 'n) and (1 gt 'limit) and (2 lt 'n) and (3 gte 'n)"),
        pytest.param(3, 2, 2, id="(0 lt 'n) and (0 lte 'limit) and (1 lt 'n) and (1 lte 'limit) and (2 lt 'n) and (3 gt 'limit) and (3 gte 'n)"),
        pytest.param(3, 3, 3, id="(0 lt 'n) and (0 lte 'limit) and (1 lt 'n) and (1 lte 'limit) and (2 lt 'n) and (3 lte 'limit) and (3 gte 'n)"),
    ],
)
def test_capped_countdown_sum_returns_expected_result(n, limit, expected):
    assert capped_countdown_sum(n, limit) == expected
