import pytest

from examples.python_code.unsafe_divide import unsafe_divide


def test_unsafe_divide_returns_expected_result():
    assert unsafe_divide(0, 1) == 0


def test_unsafe_divide_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        unsafe_divide(0, 0)
