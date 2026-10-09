"""AST repo map: a compact list of classes and functions per file.

Owner: Developer A (task A3).
"""

import os
from pathlib import Path

from agent.parsing import get_python_parser
from agent.repomap.files import iter_files

TOKEN_BUDGET = 1024


def count_tokens(text: str) -> int:
    """Count tokens without requiring PyTorch or a gated model download.

    If the environment variable LOCALPILOT_TOKENIZER points to a local
    tokenizer.json file, use it (via the `tokenizers` package). Otherwise,
    or if loading fails for any reason, approximate with len(text) // 4.
    """
    path = os.environ.get("LOCALPILOT_TOKENIZER")
    if path:
        try:
            from tokenizers import Tokenizer

            return len(Tokenizer.from_file(path).encode(text).ids)
        except Exception:
            pass
    return max(1, len(text) // 4)


def _extract_definitions(node, depth=0):
    """Extract class and function definitions from a syntax tree node.
    
    Returns list of (name, line, depth) tuples.
    """
    definitions = []
    
    # Check current node type
    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        if name_node:
            name = name_node.text.decode("utf-8", errors="replace")
            line = node.start_point[0] + 1  # 1-based
            definitions.append((f"class {name}", line, depth))
            
            # Descend into class body to find methods
            for child in node.children:
                definitions.extend(_extract_definitions(child, depth + 1))
            return definitions
    
    elif node.type == "function_definition":
        # Check if async
        is_async = any(child.type == "async" for child in node.children)
        prefix = "async def" if is_async else "def"
        
        name_node = node.child_by_field_name("name")
        if name_node:
            name = name_node.text.decode("utf-8", errors="replace")
            line = node.start_point[0] + 1
            definitions.append((f"{prefix} {name}", line, depth))
        # Do NOT descend into function bodies
        return definitions
    
    elif node.type == "decorated_definition":
        # Walk through the decorated definition to find the actual definition
        for child in node.children:
            definitions.extend(_extract_definitions(child, depth))
        return definitions
    
    # For other nodes, descend into children
    for child in node.children:
        definitions.extend(_extract_definitions(child, depth))
    
    return definitions


def build_repo_map(root_dir: str) -> str:
    """Return a repo map string for all .py files under `root_dir`,
    truncated to fit TOKEN_BUDGET tokens (use count_tokens)."""
    # Read TOKEN_BUDGET at call time
    budget = globals()["TOKEN_BUDGET"]
    
    files = iter_files(root_dir, suffixes=(".py",))
    
    if not files:
        return "(no Python files found)"
    
    lines = []
    parser = get_python_parser()
    
    for file_path in files:
        full_path = Path(root_dir) / file_path
        
        # Read file
        try:
            content = full_path.read_bytes()
        except OSError:
            continue
        
        # Parse
        tree = parser.parse(content)
        root = tree.root_node
        
        # Extract definitions
        definitions = _extract_definitions(root)
        
        # Add file path line
        lines.append(file_path)
        
        # Add definitions with proper indentation
        for def_name, def_line, depth in definitions:
            indent = "  " * depth
            lines.append(f"{indent}- {def_name}:L{def_line}")
    
    # Join all lines
    full_text = "\n".join(lines)
    
    # Estimate smallest possible truncation marker to check if budget is too tiny
    min_marker = f"... (truncated, {len(lines)} more lines)"
    if count_tokens(min_marker) > budget:
        # Budget is so small that even a minimal marker doesn't fit
        # Return omitted message regardless of whether content fits
        return "(repo map omitted: exceeds token budget)"
    
    # Check if within budget
    if count_tokens(full_text) <= budget:
        return full_text
    
    # Need truncation - binary search for best fit
    left, right = 0, len(lines)
    result_k = 0
    
    while left <= right:
        mid = (left + right) // 2
        truncated_marker = f"... (truncated, {len(lines) - mid} more lines)"
        test_text = "\n".join(lines[:mid] + [truncated_marker])
        
        if count_tokens(test_text) <= budget:
            result_k = mid
            left = mid + 1
        else:
            right = mid - 1
    
    truncated_marker = f"... (truncated, {len(lines) - result_k} more lines)"
    return "\n".join(lines[:result_k] + [truncated_marker])
