"""Mock versions of Developer A's functions so Developer B can work independently.

Owner: Developer B. Imports here match the interface contract exactly.
Replace usages with the real functions during Phase 2 integration.
"""

from .patch.checks import CheckResult
from .patch.parse_blocks import EditBlock


def mock_build_repo_map(root_dir: str) -> str:
    return "mock/path.py\n  - def mock_function:L5"


def mock_parse_edit_blocks(text: str) -> list[EditBlock]:
    # Returns a sample block if the model's response contains 'SEARCH'
    if "SEARCH" in text:
        return [EditBlock(path="mock/path.py", search_block="old", replace_block="new")]
    return []


def mock_resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]:
    return (f"{root_dir}/{path}", None)


def mock_apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None:
    return "This is the new, patched file content."


def mock_is_syntax_valid(old_content: str, new_content: str) -> bool:
    return True


def mock_run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult:
    return CheckResult(ok=True, stage="skipped", output="")
