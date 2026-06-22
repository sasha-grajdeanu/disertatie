import pytest

from examples.python_code.average_speed import average_speed


def test_average_speed_returns_expected_result():
    assert average_speed(0, 0, 1) == 0


def test_average_speed_raises_zero_division_error():
    with pytest.raises(ZeroDivisionError):
        average_speed(0, 0, 0)
