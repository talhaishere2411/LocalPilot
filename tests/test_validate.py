"""Tests for syntax validation using tree-sitter.

Owner: Developer A (task A1).
"""

from agent.parsing import count_error_nodes, get_python_parser
from agent.patch.validate import is_syntax_valid


def test_count_error_nodes_valid_code():
    """Valid Python code should have zero errors."""
    assert count_error_nodes("x = 1\n") == 0
    assert count_error_nodes("def foo():\n    pass\n") == 0
    assert count_error_nodes("class A:\n    def m(self):\n        return 42\n") == 0


def test_count_error_nodes_syntax_error():
    """Code with syntax errors should have at least one error."""
    # Missing closing parenthesis in function signature
    assert count_error_nodes("def f(:\n    pass\n") >= 1
    # Invalid syntax
    assert count_error_nodes("if\n") >= 1


def test_count_error_nodes_empty():
    """Empty string should return 0."""
    assert count_error_nodes("") == 0


def test_count_error_nodes_multiple_errors():
    """File with multiple errors should count more than one error."""
    one_error = "def f(:\n    pass\n"
    two_errors = "def f(:\n    if\n"
    assert count_error_nodes(two_errors) > count_error_nodes(one_error)


def test_is_syntax_valid_both_valid():
    """Valid to valid should return True."""
    old = "x = 1\n"
    new = "x = 2\n"
    assert is_syntax_valid(old, new) is True


def test_is_syntax_valid_valid_to_broken():
    """Valid to broken should return False."""
    old = "x = 1\n"
    new = "def f(:\n    pass\n"
    assert is_syntax_valid(old, new) is False


def test_is_syntax_valid_broken_to_same():
    """Broken to same broken should return True."""
    broken = "def f(:\n    pass\n"
    assert is_syntax_valid(broken, broken) is True


def test_is_syntax_valid_broken_to_fixed():
    """Broken to fixed should return True."""
    broken = "def f(:\n    pass\n"
    fixed = "def f():\n    pass\n"
    assert is_syntax_valid(broken, fixed) is True


def test_is_syntax_valid_broken_to_more_broken():
    """Adding more errors should return False."""
    one_error = "def f(:\n    pass\n"
    two_errors = "def f(:\n    if\n"
    assert is_syntax_valid(one_error, two_errors) is False


def test_is_syntax_valid_empty_to_valid():
    """Empty old and valid new should return True."""
    assert is_syntax_valid("", "x = 1\n") is True


def test_is_syntax_valid_unicode():
    """Unicode content should be handled correctly."""
    old = "# Тест\nx = 1\n"
    new = "# Тест κόσμε\nx = 2\n"
    assert is_syntax_valid(old, new) is True
    
    # Unicode in string literal
    valid_unicode = 'msg = "Hello 世界"\n'
    assert count_error_nodes(valid_unicode) == 0


def test_parser_caching():
    """Parser should be cached."""
    p1 = get_python_parser()
    p2 = get_python_parser()
    assert p1 is p2
