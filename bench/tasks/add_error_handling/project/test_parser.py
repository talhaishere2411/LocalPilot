from parser import parse_number, safe_divide


def test_parse_number():
    assert parse_number("42") == 42
    assert parse_number("100") == 100


def test_safe_divide_normal():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(9, 3) == 3.0


def test_safe_divide_by_zero():
    # Should return None instead of raising exception
    result = safe_divide(10, 0)
    assert result is None
