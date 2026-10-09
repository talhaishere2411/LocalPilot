"""Interface-contract test shared by Developer A and Developer B.

Checks that every contract symbol is importable from its agreed module path
with the agreed parameter names. Stub behavior is intentionally NOT asserted,
so this test keeps passing once real implementations land.
"""

import dataclasses
import inspect

from agent.cli import run
from agent.llm import LLMClient
from agent.orchestrator import Orchestrator
from agent.patch.checks import CheckResult, run_checks
from agent.patch.fuzzy import apply_fuzzy_patch
from agent.patch.parse_blocks import EditBlock, parse_edit_blocks
from agent.patch.pathguard import resolve_safe_path
from agent.patch.validate import is_syntax_valid
from agent.repomap.builder import build_repo_map


def _field_names(cls) -> list[str]:
    return [f.name for f in dataclasses.fields(cls)]


def _params(func) -> list[str]:
    return list(inspect.signature(func).parameters)


def test_edit_block_fields():
    assert _field_names(EditBlock) == ["path", "search_block", "replace_block"]


def test_check_result_fields():
    assert _field_names(CheckResult) == ["ok", "stage", "output"]


def test_engine_function_parameters():
    expected = {
        parse_edit_blocks: ["text"],
        resolve_safe_path: ["root_dir", "path"],
        apply_fuzzy_patch: ["file_content", "block"],
        is_syntax_valid: ["old_content", "new_content"],
        run_checks: ["root_dir", "rel_path", "new_content"],
        build_repo_map: ["root_dir"],
    }
    for func, params in expected.items():
        assert _params(func) == params, func.__name__


def test_llm_client_signature():
    assert _params(LLMClient.__init__) == ["self", "model", "base_url", "timeout"]
    assert _params(LLMClient.get_completion) == ["self", "messages", "temperature", "model"]


def test_orchestrator_signature():
    assert _params(Orchestrator.__init__) == ["self", "root_dir", "model", "best_of"]
    assert _params(Orchestrator.run) == ["self", "task"]


def test_cli_run_signature():
    assert _params(run) == ["task", "dir", "model", "best_of"]
