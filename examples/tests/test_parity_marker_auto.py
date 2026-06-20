import pytest

from examples.python_code.parity_marker import parity_marker


@pytest.mark.parametrize(
    ('n', 'expected'),
    [
        pytest.param(0, 0, id="'n % 2 eq 0"),
        pytest.param(1, 1, id="'n % 2 neq 0"),
    ],
)
def test_parity_marker_returns_expected_result(n, expected):
    assert parity_marker(n) == expected
