from calculator import calculate_sum, calculate_product


def test_calculate_sum():
    assert calculate_sum(2, 3) == 5
    assert calculate_sum(-1, 1) == 0
    # Check docstring exists
    assert calculate_sum.__doc__ is not None
    assert len(calculate_sum.__doc__.strip()) > 0


def test_calculate_product():
    assert calculate_product(2, 3) == 6
    assert calculate_product(-1, 5) == -5
