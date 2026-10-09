"""Fuzzy patching of SEARCH blocks using difflib.

Owner: Developer A (task A2).
"""

import difflib
from dataclasses import dataclass

from .parse_blocks import EditBlock

# Matching thresholds
THRESHOLD = 0.85
INDENT_THRESHOLD = 0.90
AMBIGUITY_MARGIN = 0.03


@dataclass
class _Match:
    """Result of finding a match in a file."""
    status: str  # "ok" | "empty" | "none" | "ambiguous"
    index: int  # Start line index of match (-1 if not found)
    score: float  # Similarity score
    other_index: int  # Index of ambiguous second match (-1 if not applicable)
    indent_insensitive: bool = False  # True if match was found via indent-insensitive pass


def _find_match(file_lines: list[str], search_lines: list[str]) -> _Match:
    """Find the best match for search_lines in file_lines.
    
    Returns a _Match with status and location info.
    """
    # Drop leading and trailing blank lines from search
    while search_lines and not search_lines[0].strip():
        search_lines = search_lines[1:]
    while search_lines and not search_lines[-1].strip():
        search_lines = search_lines[:-1]
    
    if not search_lines:
        return _Match("empty", -1, 0.0, -1)
    
    n = len(search_lines)
    if n > len(file_lines):
        return _Match("none", -1, 0.0, -1)
    
    # Pass 1: Exact match (after rstrip)
    search_stripped = [line.rstrip() for line in search_lines]
    exact_matches = []
    
    for i in range(len(file_lines) - n + 1):
        window = [file_lines[i + j].rstrip() for j in range(n)]
        if window == search_stripped:
            exact_matches.append(i)
    
    if len(exact_matches) == 1:
        return _Match("ok", exact_matches[0], 1.0, -1)
    elif len(exact_matches) > 1:
        return _Match("ambiguous", exact_matches[0], 1.0, exact_matches[1])
    
    # Pass 2: Fuzzy match
    search_text = "\n".join(search_stripped)
    scores = []
    
    for i in range(len(file_lines) - n + 1):
        window = [file_lines[i + j].rstrip() for j in range(n)]
        window_text = "\n".join(window)
        ratio = difflib.SequenceMatcher(None, window_text, search_text, autojunk=False).ratio()
        scores.append((i, ratio))
    
    if not scores:
        return _Match("none", -1, 0.0, -1)
    
    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    best_idx, best_score = scores[0]
    
    if best_score < THRESHOLD:
        # Try indent-insensitive pass
        search_super_stripped = [line.strip() for line in search_lines if line.strip()]
        if not search_super_stripped:
            return _Match("empty", -1, 0.0, -1)
        
        search_text_stripped = "\n".join(search_super_stripped)
        indent_scores = []
        
        for i in range(len(file_lines) - n + 1):
            window = [file_lines[i + j].strip() for j in range(n) if file_lines[i + j].strip()]
            window_text = "\n".join(window)
            ratio = difflib.SequenceMatcher(None, window_text, search_text_stripped, autojunk=False).ratio()
            indent_scores.append((i, ratio))
        
        if indent_scores:
            indent_scores.sort(key=lambda x: x[1], reverse=True)
            best_idx, best_score = indent_scores[0]
            
            if best_score >= INDENT_THRESHOLD:
                # Check for ambiguity
                for j, score in indent_scores[1:]:
                    if abs(j - best_idx) >= n and score >= INDENT_THRESHOLD and score >= best_score - AMBIGUITY_MARGIN:
                        return _Match("ambiguous", best_idx, best_score, j, True)
                return _Match("ok", best_idx, best_score, -1, True)
        
        return _Match("none", best_idx, best_score, -1)
    
    # Check for ambiguity in fuzzy pass
    for j, score in scores[1:]:
        if abs(j - best_idx) >= n and score >= THRESHOLD and score >= best_score - AMBIGUITY_MARGIN:
            return _Match("ambiguous", best_idx, best_score, j)
    
    return _Match("ok", best_idx, best_score, -1)


def apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None:
    """Apply `block` to `file_content` using a fuzzy line-window match.

    Returns the new file content on a single, unambiguous match above the
    similarity threshold, or None if there is no match or the match is ambiguous.
    """
    # Detect and preserve line endings
    uses_crlf = "\r\n" in file_content
    content = file_content.replace("\r\n", "\n").replace("\r", "\n")
    
    file_lines = content.split("\n")
    search_block = block.search_block.replace("\r\n", "\n").replace("\r", "\n")
    replace_block = block.replace_block.replace("\r\n", "\n").replace("\r", "\n")
    
    search_lines = search_block.split("\n")
    replace_lines = replace_block.split("\n")
    
    # Find match
    match = _find_match(file_lines, search_lines)
    
    if match.status != "ok":
        return None
    
    i = match.index
    n = len(search_lines)
    
    # Handle indent-insensitive match re-indentation
    if match.indent_insensitive:  # Match found via indent-insensitive pass needs re-indentation
        # Find leading whitespace of first non-blank search and file lines
        search_indent = ""
        file_indent = ""
        
        for line in search_lines:
            if line.strip():
                search_indent = line[:len(line) - len(line.lstrip())]
                break
        
        for j in range(n):
            if file_lines[i + j].strip():
                file_indent = file_lines[i + j][:len(file_lines[i + j]) - len(file_lines[i + j].lstrip())]
                break
        
        # Re-indent replace lines
        new_replace_lines = []
        for line in replace_lines:
            if not line.strip():
                new_replace_lines.append("")
            else:
                # Strip the search indent (if present) from the line
                if search_indent and line.startswith(search_indent):
                    # Line has the same base indent as search - remove it and add file indent
                    content_part = line[len(search_indent):]
                    new_replace_lines.append(file_indent + content_part)
                elif not search_indent:
                    # Search has no indent - preserve the replace line's own indent structure
                    # but add the file's base indent
                    new_replace_lines.append(file_indent + line)
                else:
                    # Line doesn't match search indent - keep as-is (shouldn't happen normally)
                    new_replace_lines.append(file_indent + line.lstrip())
        replace_lines = new_replace_lines
    
    # Apply patch
    result_lines = file_lines[:i] + replace_lines + file_lines[i + n:]
    result = "\n".join(result_lines)
    
    # Convert back to CRLF if needed
    if uses_crlf:
        result = result.replace("\n", "\r\n")
    
    # Return None if content unchanged (not an error, just no-op)
    if result == file_content:
        return result
    
    return result


def describe_match_failure(file_content: str, block: EditBlock) -> str:
    """Describe why a SEARCH block failed to match.
    
    Returns a human-readable message for feedback to the model.
    """
    content = file_content.replace("\r\n", "\n").replace("\r", "\n")
    file_lines = content.split("\n")
    search_block = block.search_block.replace("\r\n", "\n").replace("\r", "\n")
    search_lines = search_block.split("\n")
    
    match = _find_match(file_lines, search_lines)
    
    if match.status == "empty":
        return "The SEARCH block is empty."
    elif match.status == "ambiguous":
        # Convert to 1-based line numbers
        a = match.index + 1
        b = match.other_index + 1
        return f"The SEARCH block matches more than one place in the file (around lines {a} and {b}). Include more surrounding lines so it matches exactly one place."
    elif match.status == "none":
        if match.index >= 0:
            # Show closest match
            n = match.index + 1  # 1-based
            score = match.score
            return f"No close match for the SEARCH block. The closest text starts at line {n} (similarity {score:.2f}). Copy the lines from the file exactly, including indentation."
        else:
            return "No close match for the SEARCH block."
    else:  # "ok"
        return "The SEARCH block matches."
