import pytest

from examples.python_code.complex_while_path import complex_while_path


@pytest.mark.parametrize(
    ('n', 'limit', 'expected'),
    [
        pytest.param(0, 0, 0, id="(0 gte 'n) or (0 gt 'limit)"),
        pytest.param(1, 0, 0, id="(0 lt 'n) and (0 lte 'limit) and (1 gt 'limit) and ((1 gte 'n) or (1 gt 'limit))"),
        pytest.param(1, 1, 1, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 gte 'n) or (1 gt 'limit))"),
        pytest.param(2, 1, 1, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 lt 'n) and (1 lte 'limit)) and (4 gt 'limit) and ((2 gte 'n) or (4 gt 'limit))"),
        pytest.param(2, 4, 4, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 lt 'n) and (1 lte 'limit)) and (4 lte 'limit) and ((2 gte 'n) or (4 gt 'limit))"),
        pytest.param(3, 4, 4, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 lt 'n) and (1 lte 'limit)) and (4 lte 'limit) and ((2 lt 'n) and (4 lte 'limit)) and (7 gt 'limit) and (5 gt 'limit) and ((3 gte 'n) or (5 gt 'limit))"),
        pytest.param(3, 5, 5, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 lt 'n) and (1 lte 'limit)) and (4 lte 'limit) and ((2 lt 'n) and (4 lte 'limit)) and (7 gt 'limit) and (5 lte 'limit) and ((3 gte 'n) or (5 gt 'limit))"),
        pytest.param(3, 7, 7, id="(0 lt 'n) and (0 lte 'limit) and (1 lte 'limit) and ((1 lt 'n) and (1 lte 'limit)) and (4 lte 'limit) and ((2 lt 'n) and (4 lte 'limit)) and (7 lte 'limit) and (7 lte 'limit) and ((3 gte 'n) or (7 gt 'limit))"),
    ],
)
def test_complex_while_path_returns_expected_result(n, limit, expected):
    assert complex_while_path(n, limit) == expected
