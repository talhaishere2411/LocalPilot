"""Path Guard: confine edits to the project root and suggest real paths.

Owner: Developer A (task A4).
"""

import difflib
from pathlib import Path

from agent.repomap.files import iter_files


def resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]:
    """Resolve `path` against `root_dir`.

    Returns (resolved_absolute_path, None) if the path is inside `root_dir`
    and the file exists, or (None, error_message_with_suggestion) otherwise.
    """
    # Clean the path
    path = path.strip()
    for char in ['"', "'", '`']:
        path = path.strip(char)
    path = path.strip()
    
    if not path:
        return (None, "Empty file path.")
    
    root = Path(root_dir).resolve()
    candidate = Path(path)
    
    # Make relative to root if not absolute
    if not candidate.is_absolute():
        candidate = root / candidate
    
    # Resolve (follows symlinks)
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError):
        return (None, f"Path '{path}' could not be resolved.")
    
    # Check if inside root
    try:
        is_inside = resolved.is_relative_to(root)
    except ValueError:
        is_inside = False
    
    if not is_inside:
        return (None, f"Path '{path}' is outside the project root and was rejected.")
    
    # Check if it's a directory
    if resolved.exists() and resolved.is_dir():
        try:
            rel = resolved.relative_to(root).as_posix()
        except ValueError:
            rel = path
        return (None, f"'{rel}' is a directory, not a file.")
    
    # Check if file exists
    if resolved.exists() and resolved.is_file():
        return (str(resolved), None)
    
    # File doesn't exist - suggest alternatives
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError:
        rel = path
    
    # Gather all files
    all_files = iter_files(str(root))
    
    # Build suggestions
    suggestions = []
    
    # First: files with matching basename (case-insensitive)
    target_basename = Path(rel).name.lower()
    for f in all_files:
        if Path(f).name.lower() == target_basename:
            suggestions.append(f)
    
    # Then: close matches by full path
    close = difflib.get_close_matches(rel, all_files, n=3, cutoff=0.6)
    for c in close:
        if c not in suggestions:
            suggestions.append(c)
    
    # Limit to 3
    suggestions = suggestions[:3]
    
    if len(suggestions) == 1:
        msg = f"File '{rel}' not found. Did you mean '{suggestions[0]}'?"
    elif len(suggestions) > 1:
        quoted = "', '".join(suggestions)
        msg = f"File '{rel}' not found. Did you mean one of: '{quoted}'?"
    else:
        msg = f"File '{rel}' not found, and no similar file exists in the project."
    
    return (None, msg)
