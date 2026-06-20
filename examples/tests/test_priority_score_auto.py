import pytest

from examples.python_code.priority_score import priority_score


@pytest.mark.parametrize(
    ('age', 'income', 'flags', 'expected'),
    [
        pytest.param(17, 0, 0, 0, id="'age lt 18"),
        pytest.param(18, 5001, 1, 10, id="('age gte 18) and (('income gt 5000) and ('flags gt 0))"),
        pytest.param(18, 5001, 0, 5, id="('age gte 18) and (('income lte 5000) or ('flags lte 0)) and (('income gt 3000) or ('flags gt 2))"),
        pytest.param(18, 0, 1, 1, id="('age gte 18) and (('income lte 5000) or ('flags lte 0)) and (('income lte 3000) and ('flags lte 2))"),
    ],
)
def test_priority_score_returns_expected_result(age, income, flags, expected):
    assert priority_score(age, income, flags) == expected
