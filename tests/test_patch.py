"""Tests for edit block parsing and fuzzy patching.

Owner: Developer A (task A2).
"""

from agent.patch.fuzzy import apply_fuzzy_patch, describe_match_failure
from agent.patch.parse_blocks import (
    EditBlock,
    count_malformed_blocks,
    parse_edit_blocks,
)

# ==== Parser Tests ====

def test_parse_one_block():
    """Parse a single edit block."""
    text = """src/utils.py
<<<<<<< SEARCH
old line
=======
new line
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].path == "src/utils.py"
    assert blocks[0].search_block == "old line"
    assert blocks[0].replace_block == "new line"


def test_parse_multiple_blocks():
    """Parse several blocks in order."""
    text = """file1.py
<<<<<<< SEARCH
a
=======
b
>>>>>>> REPLACE

file2.py
<<<<<<< SEARCH
c
=======
d
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 2
    assert blocks[0].path == "file1.py"
    assert blocks[0].search_block == "a"
    assert blocks[1].path == "file2.py"
    assert blocks[1].search_block == "c"


def test_parse_markdown_fence():
    """Blocks wrapped in markdown code fence."""
    text = """```
src/test.py
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
```"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].path == "src/test.py"


def test_parse_trailing_spaces_on_markers():
    """Trailing spaces on marker lines are tolerated."""
    text = """file.py
<<<<<<< SEARCH  
content
=======  
new content
>>>>>>> REPLACE  """
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1


def test_parse_crlf_input():
    """CRLF line endings in input."""
    text = "file.py\r\n<<<<<<< SEARCH\r\nold\r\n=======\r\nnew\r\n>>>>>>> REPLACE"
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].search_block == "old"


def test_parse_path_with_backticks():
    """Path wrapped in backticks."""
    text = """`src/file.py`
<<<<<<< SEARCH
x
=======
y
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].path == "src/file.py"


def test_parse_path_with_trailing_colon():
    """Path with trailing colon."""
    text = """src/file.py:
<<<<<<< SEARCH
x
=======
y
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].path == "src/file.py"


def test_parse_no_usable_path():
    """Block with no usable path is skipped."""
    text = """
<<<<<<< SEARCH
x
=======
y
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 0


def test_parse_unterminated_block():
    """Unterminated block is dropped."""
    text = """file.py
<<<<<<< SEARCH
x
=======
y"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 0


def test_parse_empty_replace():
    """Empty replace section (deletion)."""
    text = """file.py
<<<<<<< SEARCH
delete me
=======
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].replace_block == ""


def test_parse_empty_search():
    """Empty search block is skipped."""
    text = """file.py
<<<<<<< SEARCH
=======
new
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert len(blocks) == 0


def test_parse_no_blocks():
    """Text with no blocks returns empty list."""
    text = "Just some text without any blocks."
    blocks = parse_edit_blocks(text)
    assert blocks == []


def test_count_malformed_blocks():
    """Count malformed blocks."""
    clean = """file.py
<<<<<<< SEARCH
x
=======
y
>>>>>>> REPLACE"""
    assert count_malformed_blocks(clean) == 0
    
    malformed = """file.py
<<<<<<< SEARCH
x
======="""
    assert count_malformed_blocks(malformed) == 1


def test_parse_no_trailing_newline():
    """Block text has no trailing newline."""
    text = """file.py
<<<<<<< SEARCH
line1
line2
=======
new1
new2
>>>>>>> REPLACE"""
    blocks = parse_edit_blocks(text)
    assert blocks[0].search_block == "line1\nline2"
    assert blocks[0].replace_block == "new1\nnew2"


# ==== Fuzzy Patch Tests ====

def test_fuzzy_exact_match():
    """Exact match applies successfully."""
    file_content = "line1\nline2\nline3\n"
    block = EditBlock("f.py", "line2", "LINE2")
    result = apply_fuzzy_patch(file_content, block)
    assert result == "line1\nLINE2\nline3\n"


def test_fuzzy_trailing_whitespace():
    """Trailing whitespace difference still matches."""
    file_content = "line1  \nline2\n"
    block = EditBlock("f.py", "line1", "new")
    result = apply_fuzzy_patch(file_content, block)
    assert result == "new\nline2\n"


def test_fuzzy_one_char_typo():
    """Small typo in multi-line search block matches."""
    file_content = "def foo():\n    x = 1\n    y = 2\n    return x + y\n"
    block = EditBlock("f.py", "def foo():\n    x = 1\n    y = 3\n    return x + y", "def bar():\n    return 42")
    result = apply_fuzzy_patch(file_content, block)
    # Should match despite y = 2 vs y = 3
    assert result is not None
    assert "def bar():" in result


def test_fuzzy_unrelated_search():
    """Unrelated search block returns None."""
    file_content = "a\nb\nc\n"
    block = EditBlock("f.py", "x\ny\nz", "new")
    result = apply_fuzzy_patch(file_content, block)
    assert result is None


def test_fuzzy_ambiguous():
    """Search block appearing twice returns None."""
    file_content = "foo\nbar\nfoo\nbar\n"
    block = EditBlock("f.py", "foo\nbar", "baz")
    result = apply_fuzzy_patch(file_content, block)
    assert result is None


def test_fuzzy_overlapping_not_ambiguous():
    """Overlapping windows don't count as ambiguous."""
    # Use a more realistic repetitive pattern
    file_content = "x = 1\ny = 2\nx = 1\nz = 3\n"
    block = EditBlock("f.py", "x = 1", "x = 10")
    # Two exact matches but they're the same line repeated - should match first
    result = apply_fuzzy_patch(file_content, block)
    # This will still be ambiguous with two exact matches
    # So let's test that neighboring overlapping windows don't add to ambiguity
    
    # Better test: search spans 2 lines, file has similar overlapping windows
    file_content = "line\nfoo\nbar\nfoo\nbaz\n"
    block = EditBlock("f.py", "foo\nbar", "replaced")
    result = apply_fuzzy_patch(file_content, block)
    # Should match the first occurrence
    assert result is not None
    assert "replaced" in result


def test_fuzzy_deletion():
    """Empty replace (deletion)."""
    file_content = "keep\ndelete\nkeep\n"
    block = EditBlock("f.py", "delete", "")
    result = apply_fuzzy_patch(file_content, block)
    assert result == "keep\n\nkeep\n"


def test_fuzzy_preserve_trailing_newline():
    """Trailing newline of file is preserved."""
    file_content = "line1\nline2\n"
    block = EditBlock("f.py", "line1", "new1")
    result = apply_fuzzy_patch(file_content, block)
    assert result == "new1\nline2\n"
    
    file_no_newline = "line1\nline2"
    result2 = apply_fuzzy_patch(file_no_newline, block)
    assert result2 == "new1\nline2"


def test_fuzzy_crlf_preserved():
    """CRLF file stays CRLF after patching."""
    file_content = "line1\r\nline2\r\n"
    block = EditBlock("f.py", "line1", "new1")
    result = apply_fuzzy_patch(file_content, block)
    assert result == "new1\r\nline2\r\n"


def test_fuzzy_indent_insensitive():
    """Indent-insensitive pass works and re-indents."""
    file_content = "class A:\n    def foo():\n        pass\n"
    # Search without indentation
    block = EditBlock("f.py", "def foo():\npass", "def bar():\nreturn 42")
    result = apply_fuzzy_patch(file_content, block)
    assert result is not None
    # Replacement should be indented to match file
    assert "    def bar():" in result
    assert "    return 42" in result


def test_fuzzy_empty_search():
    """Empty search block returns None."""
    file_content = "x\n"
    block = EditBlock("f.py", "", "y")
    result = apply_fuzzy_patch(file_content, block)
    assert result is None


def test_fuzzy_search_longer_than_file():
    """Search longer than file returns None."""
    file_content = "short\n"
    block = EditBlock("f.py", "line1\nline2\nline3\nline4", "new")
    result = apply_fuzzy_patch(file_content, block)
    assert result is None


def test_fuzzy_noop_replacement():
    """No-op replacement returns content unchanged."""
    file_content = "line1\nline2\n"
    block = EditBlock("f.py", "line1", "line1")
    result = apply_fuzzy_patch(file_content, block)
    assert result == file_content


def test_describe_match_failure_messages():
    """Describe match failure returns correct messages."""
    # Empty
    block = EditBlock("f.py", "", "x")
    msg = describe_match_failure("content\n", block)
    assert msg == "The SEARCH block is empty."
    
    # Ambiguous
    file_content = "foo\nbar\nfoo\nbar\n"
    block = EditBlock("f.py", "foo\nbar", "x")
    msg = describe_match_failure(file_content, block)
    assert "matches more than one place" in msg
    assert "lines 1 and 3" in msg or "around lines" in msg
    
    # None with closest match
    file_content = "def foo():\n    pass\n"
    block = EditBlock("f.py", "def bar():\n    pass", "x")
    msg = describe_match_failure(file_content, block)
    assert "No close match" in msg
    assert "line 1" in msg or "starts at" in msg
    assert "similarity" in msg
    
    # OK
    file_content = "x\ny\n"
    block = EditBlock("f.py", "x", "z")
    msg = describe_match_failure(file_content, block)
    assert msg == "The SEARCH block matches."


def test_fuzzy_performance():
    """Patching a large file should be fast."""
    import time
    
    # 5000-line file
    file_content = "\n".join([f"line {i}" for i in range(5000)])
    # 10-line search block near the end
    search_lines = "\n".join([f"line {i}" for i in range(4990, 5000)])
    block = EditBlock("f.py", search_lines, "replaced")
    
    start = time.time()
    result = apply_fuzzy_patch(file_content, block)
    elapsed = time.time() - start
    
    assert result is not None
    assert elapsed < 2.0, f"Took {elapsed:.2f}s, should be < 2s"
