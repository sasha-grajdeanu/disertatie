from dead_constant import check


def test_check_returns_expected_result():
    assert check(0) == 1
