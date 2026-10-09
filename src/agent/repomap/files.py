"""Shared file-walking utilities for repo map and path guard.

Owner: Developer A.
"""

import os
from pathlib import Path

EXCLUDE_DIRS = frozenset({
    ".venv", "venv", ".git", "__pycache__", "node_modules",
    ".pytest_cache", ".ruff_cache", ".mypy_cache",
    "build", "dist", ".idea", ".vscode",
})


def is_excluded_dir(name: str) -> bool:
    """Check if a directory name should be excluded from walks."""
    return name in EXCLUDE_DIRS or name.endswith(".egg-info")


def iter_files(
    root_dir: str,
    suffixes: tuple[str, ...] | None = None,
    max_files: int = 5000
) -> list[str]:
    """Walk root_dir and return relative paths to files.
    
    Args:
        root_dir: Root directory to walk
        suffixes: If provided, only include files ending with these suffixes
        max_files: Maximum number of files to return
        
    Returns:
        Sorted list of relative paths (with forward slashes), truncated to max_files
    """
    root = Path(root_dir)
    files = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in place
        dirnames[:] = [d for d in dirnames if not is_excluded_dir(d)]
        
        for filename in filenames:
            # Check suffix filter
            if suffixes is not None and not any(filename.endswith(s) for s in suffixes):
                continue
            
            # Get relative path with forward slashes
            file_path = Path(dirpath) / filename
            try:
                rel_path = file_path.relative_to(root)
                files.append(rel_path.as_posix())
            except ValueError:
                # Skip files outside root (shouldn't happen but be defensive)
                continue
            
            if len(files) >= max_files:
                break
        
        if len(files) >= max_files:
            break
    
    return sorted(files)
