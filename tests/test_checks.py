"""Tests for Test/Lint Gate.

Owner: Developer A (task A5).
"""

import agent.patch.checks
from agent.patch.checks import run_checks


def test_checks_passing_change_with_tests(tmp_path):
    """Passing change with tests gives ok=True, stage='pytest'."""
    # Create a simple project with a test
    code_file = tmp_path / "module.py"
    code_file.write_text("def add(a, b):\n    return a + b\n")
    
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""from module import add

def test_add():
    assert add(1, 2) == 3
""")
    
    # Make a valid change
    new_content = "def add(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is True
    assert result.stage == "pytest"
    assert result.output == ""


def test_checks_breaks_test(tmp_path):
    """Change that breaks a test gives ok=False, stage='pytest'."""
    code_file = tmp_path / "module.py"
    code_file.write_text("def add(a, b):\n    return a + b\n")
    
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""from module import add

def test_add():
    assert add(1, 2) == 3
""")
    
    # Break the function
    new_content = "def add(a, b):\n    return a - b\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is False
    assert result.stage == "pytest"
    assert "assert" in result.output or "FAILED" in result.output or "AssertionError" in result.output


def test_checks_lint_error(tmp_path):
    """Change with lint error gives ok=False, stage='ruff'."""
    code_file = tmp_path / "module.py"
    code_file.write_text("x = 1\n")
    
    # No tests, but should catch lint error
    new_content = "def foo():\n    bar  # F821: undefined name\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    # Should fail on ruff before checking for tests
    assert result.ok is False
    assert result.stage == "ruff"
    assert "bar" in result.output or "F821" in result.output


def test_checks_no_tests(tmp_path):
    """Project with no tests and clean change gives ok=True, stage='skipped'."""
    code_file = tmp_path / "module.py"
    code_file.write_text("x = 1\n")
    
    new_content = "x = 2\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is True
    assert result.stage == "skipped"


def test_checks_non_python_file(tmp_path):
    """Non-.py target skips ruff and passes."""
    readme = tmp_path / "README.md"
    readme.write_text("# Test\n")
    
    new_content = "# Updated\n"
    
    result = run_checks(str(tmp_path), "README.md", new_content)
    
    assert result.ok is True
    assert result.stage == "skipped"


def test_checks_already_failing_tests(tmp_path):
    """Tests already failing before edit give ok=True with message."""
    code_file = tmp_path / "module.py"
    code_file.write_text("def add(a, b):\n    return a - b  # Already broken\n")
    
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""from module import add

def test_add():
    assert add(1, 2) == 3
""")
    
    # Make an unrelated change
    new_content = "def add(a, b):\n    # Comment\n    return a - b\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is True
    assert "already failing" in result.output


def test_checks_output_truncation(tmp_path):
    """Output longer than OUTPUT_LIMIT is truncated."""
    code_file = tmp_path / "module.py"
    code_file.write_text("def foo(): return 42\n")  # Start with passing test
    
    test_file = tmp_path / "test_module.py"
    # Create a test with very long output that will fail ONLY with our change
    test_content = '''def test_depends_on_foo():
    """Test that depends on foo returning specific value."""
    from module import foo
    result = foo()
    msg = "x" * 1000
    assert result == 42, msg  # Will pass initially, fail after change
'''
    test_file.write_text(test_content)
    
    # Change foo to return something different (triggers the test failure)
    new_content = "def foo(): return 1\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is False
    assert len(result.output) <= agent.patch.checks.OUTPUT_LIMIT


def test_checks_unsafe_path_double_dot(tmp_path):
    """Path with .. is refused."""
    (tmp_path / "file.py").write_text("x = 1\n")
    
    result = run_checks(str(tmp_path), "../etc/passwd", "evil")
    
    assert result.ok is False
    assert result.stage == "skipped"
    assert "Refused" in result.output


def test_checks_unsafe_path_absolute(tmp_path):
    """Absolute path is refused."""
    (tmp_path / "file.py").write_text("x = 1\n")
    
    # Use a Windows absolute path
    result = run_checks(str(tmp_path), "C:\\Windows\\system32\\evil.py", "evil")
    
    assert result.ok is False
    assert result.stage == "skipped"
    assert "Refused" in result.output


def test_checks_timeout(tmp_path, monkeypatch):
    """Test timeout gives ok=False, stage='pytest'."""
    monkeypatch.setattr(agent.patch.checks, "PYTEST_TIMEOUT", 1)
    
    code_file = tmp_path / "module.py"
    code_file.write_text("import time\ndef slow(): time.sleep(10)\n")
    
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""import time

def test_slow():
    time.sleep(5)
    assert True
""")
    
    new_content = "import time\ndef slow():\n    time.sleep(10)\n"
    
    result = run_checks(str(tmp_path), "module.py", new_content)
    
    assert result.ok is False
    assert result.stage == "pytest"
    assert "timed out" in result.output


def test_checks_real_project_untouched(tmp_path):
    """Real project is never modified."""
    # Create test project
    code_file = tmp_path / "module.py"
    original_content = "def foo():\n    return 1\n"
    code_file.write_text(original_content)
    
    test_file = tmp_path / "test_module.py"
    test_content = "def test_foo():\n    assert True\n"
    test_file.write_text(test_content)
    
    # Capture file state before
    files_before = {p.name for p in tmp_path.iterdir()}
    code_bytes_before = code_file.read_bytes()
    test_bytes_before = test_file.read_bytes()
    
    # Run checks with a change
    new_content = "def foo():\n    return 2\n"
    _ = run_checks(str(tmp_path), "module.py", new_content)
    
    # Verify nothing changed in real project
    files_after = {p.name for p in tmp_path.iterdir()}
    code_bytes_after = code_file.read_bytes()
    test_bytes_after = test_file.read_bytes()
    
    assert files_before == files_after
    assert code_bytes_before == code_bytes_after
    assert test_bytes_before == test_bytes_after


def test_checks_real_project_untouched_on_failure(tmp_path):
    """Real project untouched even when check fails."""
    code_file = tmp_path / "module.py"
    original_content = "def add(a, b):\n    return a + b\n"
    code_file.write_text(original_content)
    
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""from module import add

def test_add():
    assert add(1, 2) == 3
""")
    
    # Capture state
    files_before = list(tmp_path.iterdir())
    code_bytes_before = code_file.read_bytes()
    
    # Run with breaking change
    new_content = "def add(a, b):\n    return a - b\n"
    _ = run_checks(str(tmp_path), "module.py", new_content)
    
    # Verify unchanged
    files_after = list(tmp_path.iterdir())
    code_bytes_after = code_file.read_bytes()
    
    assert len(files_before) == len(files_after)
    assert code_bytes_before == code_bytes_after


def test_checks_creates_new_file(tmp_path):
    """Can check a file that doesn't exist yet."""
    # Project with just a test
    test_file = tmp_path / "test_new.py"
    test_file.write_text("def test_placeholder():\n    assert True\n")
    
    # Create new file
    new_content = "def new_function():\n    return 42\n"
    
    result = run_checks(str(tmp_path), "new_module.py", new_content)
    
    # Should succeed
    assert result.ok is True
    
    # Original project should not have the new file
    assert not (tmp_path / "new_module.py").exists()
