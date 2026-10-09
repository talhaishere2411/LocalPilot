import inspect
from pricing import calculate_price


def test_calculate_price_basic():
    assert calculate_price(5, 10.0) == 50.0
    assert calculate_price(3, 7.5) == 22.5


def test_calculate_price_with_discount():
    # Should accept discount_rate parameter
    assert calculate_price(10, 100.0, discount_rate=0.1) == 900.0
    assert calculate_price(5, 50.0, discount_rate=0.2) == 200.0


def test_discount_rate_has_default():
    # Check that discount_rate has default value
    sig = inspect.signature(calculate_price)
    assert 'discount_rate' in sig.parameters
    assert sig.parameters['discount_rate'].default == 0.0
