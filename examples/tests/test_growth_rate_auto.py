import pytest

from examples.python_code.growth_rate import growth_rate


def test_growth_rate_returns_expected_result():
    assert growth_rate(1, 0) == -100


def test_growth_rate_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        growth_rate(0, 0)
