import pytest

from examples.python_code.classify import classify


@pytest.mark.parametrize(
    ('x', 'y', 'expected'),
    [
        pytest.param(10, 0, 0, id="'x + 'y lte 10"),
        pytest.param(11, 0, 1, id="('x + 'y gt 10) and ('x + 'y gte 5)"),
    ],
)
def test_classify_returns_expected_result(x, y, expected):
    assert classify(x, y) == expected
