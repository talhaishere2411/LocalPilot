"""Agent loop: prompt the model, run each proposed edit through the gates, give feedback.

Owner: Developer B (tasks B2 and B3).

Gate order for every edit block:
  resolve_safe_path -> apply_fuzzy_patch -> is_syntax_valid -> run_checks
Develop against the functions in `.mocks`; in Phase 2 replace them with the
real functions from `.patch` and `.repomap`.
"""

from .llm import DEFAULT_MODEL

MAX_STEPS = 8


class Orchestrator:
    def __init__(
        self,
        root_dir: str,
        model: str = DEFAULT_MODEL,
        best_of: int = 1,
    ) -> None:
        raise NotImplementedError

    def run(self, task: str) -> None:
        raise NotImplementedError
