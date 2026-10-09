"""Test/Lint Gate: run ruff and pytest on a temporary copy of the project.

Owner: Developer A (task A5).
"""

from dataclasses import dataclass


@dataclass
class CheckResult:
    ok: bool
    stage: str    # "ruff" | "pytest" | "skipped"
    output: str   # tool output to feed back to the model on failure


def run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult:
    """Write `new_content` to `rel_path` inside a temporary copy of `root_dir`
    and run lint and tests there. The real project is never modified."""
    raise NotImplementedError
