"""Tests for AST repo map generation.

Owner: Developer A (task A3).
"""

import agent.repomap.builder
from agent.repomap.builder import build_repo_map, count_tokens


def test_build_repo_map_small_project(tmp_path):
    """Generate map for small project with various definitions."""
    # File with class, method, function, async function, decorated function, nested function
    code = '''class MyClass:
    def method(self):
        pass

def top_function():
    def nested():  # Should be skipped
        pass
    return 42

async def async_func():
    pass

@decorator
def decorated_func():
    pass
'''
    file1 = tmp_path / "module.py"
    file1.write_text(code)
    
    result = build_repo_map(str(tmp_path))
    
    assert "module.py" in result
    assert "class MyClass" in result
    assert "def method" in result
    assert "def top_function" in result
    assert "async def async_func" in result
    assert "def decorated_func" in result
    # Nested function should NOT appear
    assert "nested" not in result


def test_build_repo_map_line_numbers(tmp_path):
    """Line numbers are 1-based."""
    code = '''# Comment on line 1
class A:  # Line 2
    pass

def foo():  # Line 5
    pass
'''
    (tmp_path / "test.py").write_text(code)
    
    result = build_repo_map(str(tmp_path))
    
    assert "class A:L2" in result
    assert "def foo:L5" in result


def test_build_repo_map_indentation(tmp_path):
    """Format and indentation are correct."""
    code = '''class Outer:
    def method1(self):
        pass
    
    def method2(self):
        pass

def standalone():
    pass
'''
    (tmp_path / "test.py").write_text(code)
    
    result = build_repo_map(str(tmp_path))
    lines = result.split("\n")
    
    # Find the class line
    class_idx = next(i for i, line in enumerate(lines) if "class Outer" in line)
    # Methods should be indented with 2 spaces
    assert lines[class_idx + 1].startswith("  - def method1")
    assert lines[class_idx + 2].startswith("  - def method2")
    # Standalone function should not be indented
    standalone_idx = next(i for i, line in enumerate(lines) if "def standalone" in line)
    assert lines[standalone_idx].startswith("- def standalone")


def test_build_repo_map_excludes_directories(tmp_path):
    """Files in excluded directories are not included."""
    # Good file
    (tmp_path / "good.py").write_text("def foo(): pass")
    
    # Bad files in excluded dirs
    for excluded in [".venv", "__pycache__", "node_modules"]:
        exc_dir = tmp_path / excluded
        exc_dir.mkdir()
        (exc_dir / "bad.py").write_text("def bad(): pass")
    
    # Egg-info directory
    egg_dir = tmp_path / "pkg.egg-info"
    egg_dir.mkdir()
    (egg_dir / "bad.py").write_text("def bad(): pass")
    
    result = build_repo_map(str(tmp_path))
    
    assert "good.py" in result
    assert "def foo" in result
    assert "bad.py" not in result
    assert "def bad" not in result


def test_build_repo_map_no_definitions(tmp_path):
    """File with no definitions still has path line."""
    (tmp_path / "empty.py").write_text("# Just a comment\nx = 1\n")
    
    result = build_repo_map(str(tmp_path))
    
    assert "empty.py" in result
    # Should have path line but no definition lines


def test_build_repo_map_syntax_error(tmp_path):
    """File with syntax error does not crash."""
    (tmp_path / "broken.py").write_text("def foo(:\n    pass")
    (tmp_path / "good.py").write_text("def bar(): pass")
    
    result = build_repo_map(str(tmp_path))
    
    # Good file should be present
    assert "good.py" in result
    assert "def bar" in result


def test_build_repo_map_empty_project(tmp_path):
    """Empty project returns special message."""
    result = build_repo_map(str(tmp_path))
    assert result == "(no Python files found)"


def test_build_repo_map_deterministic(tmp_path):
    """Output is deterministic across multiple calls."""
    (tmp_path / "a.py").write_text("def a(): pass")
    (tmp_path / "b.py").write_text("def b(): pass")
    
    result1 = build_repo_map(str(tmp_path))
    result2 = build_repo_map(str(tmp_path))
    
    assert result1 == result2


def test_build_repo_map_truncation(tmp_path, monkeypatch):
    """Map is truncated to fit token budget."""
    # Create many files
    for i in range(50):
        code = f"def func{i}(): pass\n"
        (tmp_path / f"file{i:02d}.py").write_text(code)
    
    # Set a small budget
    monkeypatch.setattr(agent.repomap.builder, "TOKEN_BUDGET", 100)
    
    result = build_repo_map(str(tmp_path))
    
    # Should be truncated
    assert "truncated" in result
    # Should fit budget
    assert count_tokens(result) <= 100
    # Should end with truncation marker
    assert result.endswith("more lines)")


def test_build_repo_map_omitted_tiny_budget(tmp_path, monkeypatch):
    """Tiny budget returns omitted message."""
    (tmp_path / "test.py").write_text("def foo(): pass")
    
    # Set budget so small even marker doesn't fit
    monkeypatch.setattr(agent.repomap.builder, "TOKEN_BUDGET", 5)
    
    result = build_repo_map(str(tmp_path))
    
    assert result == "(repo map omitted: exceeds token budget)"


def test_count_tokens_default():
    """count_tokens approximates with len // 4."""
    text = "hello world"
    result = count_tokens(text)
    # len("hello world") = 11, 11 // 4 = 2, max(1, 2) = 2
    assert result == 2


def test_count_tokens_empty():
    """Empty string returns 1."""
    assert count_tokens("") == 1


def test_count_tokens_bogus_env(monkeypatch):
    """Bogus LOCALPILOT_TOKENIZER falls back to approximation."""
    monkeypatch.setenv("LOCALPILOT_TOKENIZER", "/nonexistent/tokenizer.json")
    
    text = "hello world"
    result = count_tokens(text)
    # Should fall back to len // 4
    assert result == 2


def test_count_tokens_no_env(monkeypatch):
    """No env var uses approximation."""
    monkeypatch.delenv("LOCALPILOT_TOKENIZER", raising=False)
    
    text = "test string here"
    result = count_tokens(text)
    expected = max(1, len(text) // 4)
    assert result == expected
