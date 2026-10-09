"""AST repo map: a compact list of classes and functions per file.

Owner: Developer A (task A3).
"""

import os


TOKEN_BUDGET = 1024


def count_tokens(text: str) -> int:
    """Count tokens without requiring torch or a gated model download.

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


def build_repo_map(root_dir: str) -> str:
    """Return a repo map string for all .py files under `root_dir`,
    truncated to fit TOKEN_BUDGET tokens."""
    raise NotImplementedError
