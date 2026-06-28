from examples.python_code.fermat import fermat


def test_fermat_returns_expected_result():
    assert fermat(0, 0, 0) == 0
