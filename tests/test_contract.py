"""Interface-contract smoke test.

Checks that every contract symbol is importable from its agreed module path
and that the dataclasses have the agreed fields. Stub behavior (raising
NotImplementedError) is intentionally NOT asserted, so this test keeps passing
once real implementations land.
"""

import dataclasses
import inspect

from agent.patch.checks import CheckResult, run_checks
from agent.patch.fuzzy import apply_fuzzy_patch
from agent.patch.parse_blocks import EditBlock, parse_edit_blocks
from agent.patch.pathguard import resolve_safe_path
from agent.patch.validate import is_syntax_valid
from agent.repomap.builder import build_repo_map


def _field_names(cls) -> list[str]:
    return [f.name for f in dataclasses.fields(cls)]


def test_edit_block_fields():
    assert _field_names(EditBlock) == ["path", "search_block", "replace_block"]


def test_check_result_fields():
    assert _field_names(CheckResult) == ["ok", "stage", "output"]


def test_function_parameters():
    expected = {
        parse_edit_blocks: ["text"],
        resolve_safe_path: ["root_dir", "path"],
        apply_fuzzy_patch: ["file_content", "block"],
        is_syntax_valid: ["old_content", "new_content"],
        run_checks: ["root_dir", "rel_path", "new_content"],
        build_repo_map: ["root_dir"],
    }
    for func, params in expected.items():
        assert list(inspect.signature(func).parameters) == params, func.__name__
