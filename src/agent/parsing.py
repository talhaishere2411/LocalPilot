"""Shared tree-sitter helpers used by the syntax gate and the repo map.

Owner: Developer A. Not part of the cross-developer contract.
"""


def get_python_parser():
    """Return a tree-sitter Parser configured for Python."""
    raise NotImplementedError


def count_error_nodes(source: str) -> int:
    """Return the number of ERROR or MISSING nodes in the parse tree of `source`."""
    raise NotImplementedError
