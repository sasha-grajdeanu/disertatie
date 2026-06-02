import pytest

from examples.python_code.countdown_sum import countdown_sum


@pytest.mark.parametrize(
    ('n', 'expected'),
    [
        pytest.param(0, 0, id="0 gte 'n"),
        pytest.param(1, 0, id="(0 lt 'n) and (1 gte 'n)"),
        pytest.param(2, 1, id="(0 lt 'n) and (1 lt 'n) and (2 gte 'n)"),
        pytest.param(3, 3, id="(0 lt 'n) and (1 lt 'n) and (2 lt 'n) and (3 gte 'n)"),
    ],
)
def test_countdown_sum_returns_expected_result(n, expected):
    assert countdown_sum(n) == expected
