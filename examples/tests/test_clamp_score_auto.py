import pytest

from examples.python_code.clamp_score import clamp_score


@pytest.mark.parametrize(
    ('score', 'expected'),
    [
        pytest.param(-1, 0, id="'score lt 0"),
        pytest.param(101, 100, id="('score gte 0) and ('score gt 100)"),
        pytest.param(4, 4, id="('score gte 0) and ('score lte 100)"),
    ],
)
def test_clamp_score_returns_expected_result(score, expected):
    assert clamp_score(score) == expected
