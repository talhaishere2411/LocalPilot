"""Tests for Path Guard and file walking.

Owner: Developer A (task A4).
"""

import pytest

from agent.patch.pathguard import resolve_safe_path
from agent.repomap.files import EXCLUDE_DIRS, is_excluded_dir, iter_files


def test_resolve_existing_file(tmp_path):
    """Valid existing path returns absolute path and None."""
    test_file = tmp_path / "src" / "utils.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), "src/utils.py")
    assert error is None
    assert result == str(test_file)


def test_resolve_normalized_path(tmp_path):
    """Path with .. normalizes and succeeds."""
    test_file = tmp_path / "src" / "utils.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), "./src/../src/utils.py")
    assert error is None
    assert result == str(test_file)


def test_resolve_outside_root(tmp_path):
    """Path escaping root is rejected."""
    result, error = resolve_safe_path(str(tmp_path), "../../etc/passwd")
    assert result is None
    assert "outside the project root" in error


def test_resolve_absolute_outside(tmp_path):
    """Absolute path outside root is rejected."""
    outside = tmp_path.parent / "other.py"
    outside.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), str(outside))
    assert result is None
    assert "outside the project root" in error


def test_resolve_empty_path(tmp_path):
    """Empty path returns error."""
    result, error = resolve_safe_path(str(tmp_path), "")
    assert result is None
    assert "Empty" in error
    
    result, error = resolve_safe_path(str(tmp_path), "   ")
    assert result is None
    assert "Empty" in error


def test_resolve_directory(tmp_path):
    """Directory path returns error."""
    dir_path = tmp_path / "src"
    dir_path.mkdir()
    
    result, error = resolve_safe_path(str(tmp_path), "src")
    assert result is None
    assert "directory" in error


def test_resolve_missing_with_close_match(tmp_path):
    """Missing file with close match suggests it."""
    real_file = tmp_path / "src" / "utils.py"
    real_file.parent.mkdir(parents=True)
    real_file.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), "src/util.py")
    assert result is None
    assert "not found" in error
    assert "src/utils.py" in error


def test_resolve_missing_basename_match(tmp_path):
    """Missing file with matching basename in another folder."""
    real_file = tmp_path / "other" / "config.py"
    real_file.parent.mkdir(parents=True)
    real_file.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), "src/config.py")
    assert result is None
    assert "not found" in error
    assert "other/config.py" in error


def test_resolve_missing_no_match(tmp_path):
    """Missing file with no similar file."""
    result, error = resolve_safe_path(str(tmp_path), "nonexistent.xyz")
    assert result is None
    assert "not found" in error
    assert "no similar file" in error


def test_resolve_excluded_dir_not_suggested(tmp_path):
    """Files in excluded directories are not suggested."""
    venv_file = tmp_path / ".venv" / "lib" / "test.py"
    venv_file.parent.mkdir(parents=True)
    venv_file.write_text("# test")
    
    result, error = resolve_safe_path(str(tmp_path), "test.py")
    assert result is None
    # Should not suggest .venv/lib/test.py
    assert ".venv" not in error


def test_resolve_symlink_outside(tmp_path):
    """Symlink pointing outside root is rejected."""
    try:
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("external")
        
        link = tmp_path / "link.txt"
        link.symlink_to(outside)
        
        result, error = resolve_safe_path(str(tmp_path), "link.txt")
        assert result is None
        assert "outside the project root" in error
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation not supported on this system")


def test_iter_files_basic(tmp_path):
    """Iterate files in a directory."""
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.txt").write_text("")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "c.py").write_text("")
    
    files = iter_files(str(tmp_path))
    assert sorted(files) == ["a.py", "b.txt", "sub/c.py"]


def test_iter_files_with_suffix(tmp_path):
    """Filter by suffix."""
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.txt").write_text("")
    (tmp_path / "c.py").write_text("")
    
    files = iter_files(str(tmp_path), suffixes=(".py",))
    assert sorted(files) == ["a.py", "c.py"]


def test_iter_files_excludes_dirs(tmp_path):
    """Excluded directories are skipped."""
    (tmp_path / "good.py").write_text("")
    
    for excluded in [".venv", "__pycache__", "node_modules", ".pytest_cache"]:
        exc_dir = tmp_path / excluded
        exc_dir.mkdir()
        (exc_dir / "bad.py").write_text("")
    
    files = iter_files(str(tmp_path), suffixes=(".py",))
    assert files == ["good.py"]


def test_iter_files_excludes_egg_info(tmp_path):
    """Directories ending with .egg-info are excluded."""
    (tmp_path / "good.py").write_text("")
    
    egg_dir = tmp_path / "package.egg-info"
    egg_dir.mkdir()
    (egg_dir / "bad.py").write_text("")
    
    files = iter_files(str(tmp_path), suffixes=(".py",))
    assert files == ["good.py"]


def test_iter_files_max_files(tmp_path):
    """Respects max_files limit."""
    for i in range(10):
        (tmp_path / f"file{i}.txt").write_text("")
    
    files = iter_files(str(tmp_path), max_files=5)
    assert len(files) <= 5


def test_iter_files_sorted(tmp_path):
    """Results are sorted."""
    (tmp_path / "z.py").write_text("")
    (tmp_path / "a.py").write_text("")
    (tmp_path / "m.py").write_text("")
    
    files = iter_files(str(tmp_path))
    assert files == ["a.py", "m.py", "z.py"]


def test_is_excluded_dir():
    """Test excluded directory detection."""
    for name in EXCLUDE_DIRS:
        assert is_excluded_dir(name)
    
    assert is_excluded_dir("package.egg-info")
    assert is_excluded_dir("myproject.egg-info")
    assert not is_excluded_dir("src")
    assert not is_excluded_dir("tests")
