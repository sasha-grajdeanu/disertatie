import pytest

from examples.python_code.guarded_ratio import guarded_ratio


@pytest.mark.parametrize(
    ('total', 'count', 'limit', 'expected'),
    [
        pytest.param(0, 0, 0, 0, id="'count lte 0"),
        pytest.param(-1, 5, -1, -1, id="('count gt 0) and ('total lt 0) and ('count neq 0) and (0 / 'count gt 'limit)"),
        pytest.param(-1, 1, 0, 0, id="('count gt 0) and ('total lt 0) and ('count neq 0) and (0 / 'count lte 'limit)"),
        pytest.param(5, 5, 0, 0, id="('count gt 0) and ('total gte 0) and ('count neq 0) and ('total / 'count gt 'limit)"),
        pytest.param(0, 1, 0, 0, id="('count gt 0) and ('total gte 0) and ('count neq 0) and ('total / 'count lte 'limit)"),
    ],
)
def test_guarded_ratio_returns_expected_result(total, count, limit, expected):
    assert guarded_ratio(total, count, limit) == expected
