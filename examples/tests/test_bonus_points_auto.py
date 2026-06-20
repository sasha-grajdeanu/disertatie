import pytest

from examples.python_code.bonus_points import bonus_points


@pytest.mark.parametrize(
    ('score', 'streak', 'expected'),
    [
        pytest.param(90, 4, 100, id="('score gte 90) and ('streak gt 3)"),
        pytest.param(0, 6, 5, id="(('score lt 90) or ('streak lte 3)) and (('score gte 70) or ('streak gt 5))"),
        pytest.param(0, 4, 0, id="(('score lt 90) or ('streak lte 3)) and (('score lt 70) and ('streak lte 5))"),
    ],
)
def test_bonus_points_returns_expected_result(score, streak, expected):
    assert bonus_points(score, streak) == expected
