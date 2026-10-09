from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_add_has_docstring():
    assert add.__doc__ is not None, "add function should have a docstring"
    assert "add" in add.__doc__.lower() or "sum" in add.__doc__.lower()
