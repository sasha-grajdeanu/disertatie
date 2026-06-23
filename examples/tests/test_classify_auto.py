import pytest

from examples.python_code.classify import classify


@pytest.mark.parametrize(
    ('score', 'expected'),
    [
        pytest.param(60, 1, id="'score gte 60"),
        pytest.param(0, 0, id="('score lt 60) and ('score lt 80)"),
    ],
)
def test_classify_returns_expected_result(score, expected):
    assert classify(score) == expected
