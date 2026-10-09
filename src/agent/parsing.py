"""Shared tree-sitter helpers used by the syntax gate and the repo map.

Owner: Developer A. Not part of the cross-developer contract.
"""

import functools

from tree_sitter_language_pack import get_parser as get_ts_parser


def _flag(node, name: str):
    """Get a node flag, handling both property and method APIs."""
    attr = getattr(node, name)
    return attr() if callable(attr) else attr


@functools.lru_cache(maxsize=1)
def get_python_parser():
    """Return a tree-sitter Parser configured for Python."""
    return get_ts_parser("python")


def count_error_nodes(source: str) -> int:
    """Return the number of ERROR or MISSING nodes in the parse tree of `source`."""
    if not source:
        return 0
    
    parser = get_python_parser()
    tree = parser.parse(source.encode("utf-8"))
    root = tree.root_node
    
    if not root.has_error:
        return 0
    
    # Iterative traversal to avoid recursion limits
    count = 0
    stack = [root]
    
    while stack:
        node = stack.pop()
        
        if node.type == "ERROR" or _flag(node, "is_missing"):
            count += 1
        
        # Add children to stack in reverse order to maintain tree order
        for child in reversed(node.children):
            stack.append(child)
    
    return count
