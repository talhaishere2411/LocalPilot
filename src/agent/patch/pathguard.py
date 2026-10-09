"""Path Guard: confine edits to the project root and suggest real paths.

Owner: Developer A (task A4).
"""


def resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]:
    """Resolve `path` against `root_dir`.

    Returns (resolved_absolute_path, None) if the path is inside `root_dir`
    and the file exists, or (None, error_message_with_suggestion) otherwise.
    """
    raise NotImplementedError
