import pytest

from examples.python_code.countdown import countdown


@pytest.mark.parametrize(
    ('n', 'start', 'expected'),
    [
        pytest.param(0, 0, 0, id="'n lte 0"),
        pytest.param(1, 0, -1, id="('n gt 0) and ('n - 1 lte 0)"),
        pytest.param(2, 0, -3, id="('n gt 0) and ('n - 1 gt 0) and ('n - 2 lte 0)"),
        pytest.param(3, 0, -6, id="('n gt 0) and ('n - 1 gt 0) and ('n - 2 gt 0) and ('n - 3 lte 0)"),
    ],
)
def test_countdown_returns_expected_result(n, start, expected):
    assert countdown(n, start) == expected
