"""Parse SEARCH/REPLACE edit blocks out of raw model output.

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
    raise NotImplementedError
