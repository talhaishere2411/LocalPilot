"""Syntax Gate: reject edits that introduce new tree-sitter errors.

Owner: Developer A (task A1).
"""

from agent.parsing import count_error_nodes


def is_syntax_valid(old_content: str, new_content: str) -> bool:
    """Return True only if `new_content` has no more ERROR/MISSING nodes
    than `old_content`."""
    return count_error_nodes(new_content) <= count_error_nodes(old_content)
