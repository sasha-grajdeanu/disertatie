import pytest

from examples.python_code.safe_ratio import safe_ratio


@pytest.mark.parametrize(
    ('x', 'y', 'expected'),
    [
        pytest.param(0, 0, 0, id="'y eq 0"),
        pytest.param(0, 1, 0, id="'y neq 0"),
    ],
)
def test_safe_ratio_returns_expected_result(x, y, expected):
    assert safe_ratio(x, y) == expected
