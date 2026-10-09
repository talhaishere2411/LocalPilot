import inspect
from math_ops import add, multiply


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-2, 5) == -10


def test_add_has_type_hints():
    # Check that add function has type hints
    sig = inspect.signature(add)
    
    # Check parameter annotations
    assert sig.parameters['a'].annotation == int
    assert sig.parameters['b'].annotation == int
    
    # Check return annotation
    assert sig.return_annotation == int
