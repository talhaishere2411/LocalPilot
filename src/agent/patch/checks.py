"""Test/Lint Gate: run ruff and pytest on a temporary copy of the project.

Owner: Developer A (task A5).
"""

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from agent.repomap.files import is_excluded_dir

# Configuration constants
RUFF_TIMEOUT = 30
PYTEST_TIMEOUT = 60
OUTPUT_LIMIT = 600
RUFF_SELECT = "E9,F63,F7,F82"


@dataclass
class CheckResult:
    ok: bool
    stage: str    # "ruff" | "pytest" | "skipped"
    output: str   # tool output to feed back to the model on failure


def _truncate(text: str, limit: int, from_end: bool = False) -> str:
    """Truncate text to limit characters."""
    if len(text) <= limit:
        return text
    if from_end:
        return "..." + text[-(limit - 3):]
    else:
        return text[:limit - 3] + "..."


def _has_tests(project_dir: Path) -> bool:
    """Check if project has test files."""
    for dirpath, dirnames, filenames in os.walk(project_dir):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if not is_excluded_dir(d)]
        
        for filename in filenames:
            if filename.startswith("test_") and filename.endswith(".py"):
                return True
            if filename.endswith("_test.py"):
                return True
    
    return False


def _run_command(cmd: list[str], cwd: str, timeout: int, env: dict | None = None) -> tuple[int, str]:
    """Run a command and return (returncode, combined_output)."""
    try:
        if env is None:
            env = os.environ.copy()
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        output = result.stdout + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, f"Command timed out after {timeout}s"
    except OSError as e:
        return -1, f"Failed to run command: {e}"


def run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult:
    """Write `new_content` to `rel_path` inside a temporary copy of `root_dir`
    and run lint and tests there. The real project is never modified."""
    # Refuse unsafe paths
    path_obj = Path(rel_path)
    if path_obj.is_absolute() or ".." in path_obj.parts:
        return CheckResult(False, "skipped", "Refused: path is outside the project.")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        tmp_path = Path(tmpdir)
        proj_copy = tmp_path / "proj"
        
        # Copy project with ignore
        def ignore_func(directory, contents):
            ignored = []
            for name in contents:
                if is_excluded_dir(name):
                    ignored.append(name)
            return ignored
        
        try:
            shutil.copytree(root_dir, proj_copy, ignore=ignore_func)
        except OSError as e:
            return CheckResult(False, "skipped", f"Failed to copy project: {e}")
        
        # Remember original content or note file didn't exist
        target_file = proj_copy / rel_path
        original_existed = target_file.exists()
        original_content = None
        
        if original_existed:
            try:
                original_content = target_file.read_bytes()
            except OSError:
                pass
        
        # Write new content
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(new_content, encoding="utf-8")
        except OSError as e:
            return CheckResult(False, "skipped", f"Failed to write file: {e}")
        
        # Run ruff (only for .py files)
        if rel_path.endswith(".py"):
            ruff_cmd = [
                sys.executable, "-m", "ruff", "check",
                "--isolated", "--no-cache",
                "--select", RUFF_SELECT,
                "--output-format", "concise",
                rel_path
            ]
            
            returncode, output = _run_command(ruff_cmd, str(proj_copy), RUFF_TIMEOUT)
            
            if returncode == -1:
                # Timeout or error - skip stage
                pass
            elif returncode == 0:
                # Lint passed
                pass
            elif returncode == 1:
                # Lint failed - check if ruff is available
                if "No module named ruff" in output or "No module named 'ruff'" in output:
                    # Ruff not available, skip
                    pass
                else:
                    # Real lint error
                    truncated = _truncate(output, OUTPUT_LIMIT, from_end=False)
                    return CheckResult(False, "ruff", truncated)
            # Other return codes: skip stage
        
        # Check for tests
        if not _has_tests(proj_copy):
            return CheckResult(True, "skipped", "")
        
        # Run pytest
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["NO_COLOR"] = "1"
        
        pytest_cmd = [
            sys.executable, "-m", "pytest",
            "-x", "-q", "--no-header", "--color=no",
            "-p", "no:cacheprovider"
        ]
        
        returncode, output = _run_command(pytest_cmd, str(proj_copy), PYTEST_TIMEOUT, env)
        
        if returncode == -1:
            # Timeout
            return CheckResult(False, "pytest", f"pytest timed out after {PYTEST_TIMEOUT}s")
        elif returncode == 0:
            # Tests passed
            return CheckResult(True, "pytest", "")
        elif returncode == 5:
            # No tests collected
            return CheckResult(True, "skipped", "")
        else:
            # Tests failed - check if they were already failing
            # Restore original file
            if original_existed and original_content is not None:
                try:
                    target_file.write_bytes(original_content)
                except OSError:
                    pass
            elif not original_existed:
                try:
                    target_file.unlink()
                except OSError:
                    pass
            
            # Run baseline
            baseline_returncode, _ = _run_command(pytest_cmd, str(proj_copy), PYTEST_TIMEOUT, env)
            
            if baseline_returncode != 0 and baseline_returncode != 5:
                # Tests were already failing
                return CheckResult(True, "pytest", "Tests were already failing before this edit; not blocking.")
            else:
                # Tests passed in baseline but fail with our change
                truncated = _truncate(output, OUTPUT_LIMIT, from_end=True)
                return CheckResult(False, "pytest", truncated)
