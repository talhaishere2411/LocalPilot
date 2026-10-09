"""Parse SEARCH/REPLACE edit blocks out of raw model output.

The block format is locked; see skills/safe-edit/SKILL.md.
Owner: Developer A (task A2).
"""

from dataclasses import dataclass


@dataclass
class EditBlock:
    """One proposed edit: replace `search_block` with `replace_block` in `path`."""

    path: str
    search_block: str
    replace_block: str


def parse_edit_blocks(text: str) -> list[EditBlock]:
    """Find all SEARCH/REPLACE blocks in `text` and return them in order."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    
    blocks = []
    i = 0
    
    while i < len(lines):
        line_stripped = lines[i].rstrip()
        
        # Check for SEARCH marker
        if line_stripped == "<<<<<<< SEARCH":
            # Path is the line immediately before
            if i == 0:
                i += 1
                continue
                
            path_line = lines[i - 1]
            
            # Check if previous line is a markdown fence
            if path_line.lstrip().startswith("```"):
                i += 1
                continue
            
            # Clean the path
            path = path_line.strip()
            # Strip surrounding backticks, quotes, asterisks
            for char in ['`', '"', "'", '*']:
                path = path.strip(char)
            # Strip one trailing colon
            path = path.removesuffix(':')
            path = path.strip()
            
            if not path:
                # Skip this block - no usable path
                i += 1
                continue
            
            # Find separator
            search_lines = []
            i += 1
            separator_found = False
            
            while i < len(lines):
                if lines[i].rstrip() == "=======":
                    separator_found = True
                    break
                if lines[i].rstrip() == "<<<<<<< SEARCH":
                    # New SEARCH marker found - unterminated block
                    break
                search_lines.append(lines[i])
                i += 1
            
            if not separator_found:
                # Unterminated or new block started
                continue
            
            search_text = "\n".join(search_lines)
            
            # Check for empty or whitespace-only search
            if not search_text.strip():
                i += 1
                continue
            
            # Find end marker
            i += 1
            replace_lines = []
            end_found = False
            
            while i < len(lines):
                if lines[i].rstrip() == ">>>>>>> REPLACE":
                    end_found = True
                    break
                if lines[i].rstrip() == "<<<<<<< SEARCH":
                    # New SEARCH marker - unterminated
                    break
                replace_lines.append(lines[i])
                i += 1
            
            if not end_found:
                # Unterminated block
                continue
            
            replace_text = "\n".join(replace_lines)
            
            blocks.append(EditBlock(
                path=path,
                search_block=search_text,
                replace_block=replace_text
            ))
        
        i += 1
    
    return blocks


def count_malformed_blocks(text: str) -> int:
    """Return the number of SEARCH markers that did not produce a valid block.
    
    Useful for determining if a model response is malformed vs. intentionally
    containing no edits (task complete).
    """
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    
    search_count = 0
    valid_count = len(parse_edit_blocks(text))
    
    for line in lines:
        if line.rstrip() == "<<<<<<< SEARCH":
            search_count += 1
    
    return search_count - valid_count
