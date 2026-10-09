from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_no_typo():
    """Ensure the typo 'resutl' is fixed."""
    import inspect
    source = inspect.getsource(add)
    assert 'resutl' not in source, "Variable 'resutl' should be renamed to 'result'"
