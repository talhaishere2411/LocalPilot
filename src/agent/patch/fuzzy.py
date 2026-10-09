"""Fuzzy patching of SEARCH blocks using difflib.

Owner: Developer A (task A2).
"""

from .parse_blocks import EditBlock


def apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None:
    """Apply `block` to `file_content` using a fuzzy line-window match.

    Returns the new file content on a single, unambiguous match above the
    similarity threshold, or None if there is no match or the match is ambiguous.
    """
    raise NotImplementedError
