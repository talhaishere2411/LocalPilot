# LocalPilot: 6-Hour Hackathon Implementation Plan

This document outlines a parallelized development plan for two developers to build the LocalPilot MVP in 6 hours.

**Primary Goal:** A working demo where a user can issue a coding task, and the agent successfully (and safely) edits a Python file.

**Differentiators (added on top of the MVP):** a Path Guard, a Test/Lint Gate, Best-of-N verified sampling, and a benchmark harness that shows the lift the gates give a small model.

**Team Roles:**

- **Developer A: The Engine.** Focuses on the core, offline tooling: the patch pipeline, the path guard, the check gate and the repo map generator. These are pure, testable functions.
- **Developer B: The Interface.** Focuses on the live components: the CLI, the LLM client, the main orchestrator loop (including best-of-N) and the benchmark harness.

## Timeline Overview

| Phase | Duration | Who |
|---|---|---|
| Phase 0: Shared Setup | 15 minutes | Both |
| Phase 1: Parallel Development | 3.5 hours | A and B separately |
| Phase 2: Integration | 1.5 hours | Both (pair programming) |
| Phase 3: Final Touches & Submission | 45 minutes | Both |

## Priority and Cut Line

If time runs short, cut from the bottom of this list. Do not cut above the line.

1. Syntax Gate, Fuzzy Patch, Repo Map, Orchestrator, CLI (the MVP)
2. Path Guard (A4)
3. Benchmark harness (B4), because the demo needs real numbers
4. Test/Lint Gate (A5)
5. Best-of-N sampling (B3)
6. Stretch goals (see the end of this document)

## Table of Contents

- [Phase 0: Shared Setup](#phase-0-shared-setup-15-minutes)
- [Phase 1: Parallel Development](#phase-1-parallel-development-35-hours)
  - [Agreed-Upon Interface Contract](#agreed-upon-interface-contract)
  - [Track A: The Engine](#track-a-the-engine-developer-a)
  - [Track B: The Interface](#track-b-the-interface-developer-b)
- [Phase 2: Integration](#phase-2-integration-15-hours)
- [Phase 3: Final Touches & Submission](#phase-3-final-touches--submission-45-minutes)
- [Stretch Goals](#stretch-goals)

---

## Phase 0: Shared Setup (15 Minutes)

*Both developers do this together.*

1. `git clone` the repository and `cd` into it.
2. Create the project directory structure:

   ```
   localpilot/
   ├── src/
   │   ├── agent/
   │   │   ├── patch/
   │   │   ├── repomap/
   │   │   └── __init__.py
   │   └── build_parsers.py
   ├── bench/
   │   ├── tasks/
   │   └── run_bench.py
   ├── tests/
   ├── skills/
   │   └── safe-edit/
   └── requirements.txt
   ```

3. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Python version:** use Python 3.12 (see `.python-version` and `PYTHON_COMPAT.md`). If your system Python is 3.13 or 3.14, create the venv with `uv venv --python 3.12 .venv` instead of `python3 -m venv .venv`.

4. Create `requirements.txt` and install initial dependencies:

   ```
   # requirements.txt
   typer[all]
   rich
   httpx
   tree-sitter
   tree-sitter-language-pack
   tokenizers
   ruff
   pytest
   ```

   Then run `pip install -r requirements.txt`.

   Tree-sitter packages are pinned to exact versions. Token counting uses count_tokens() in repomap/builder.py and does not require torch.

5. Install Ollama from [ollama.com](https://ollama.com/) and pull the model:

   ```bash
   ollama pull gemma3:4b-instruct
   ```

6. **Verify the LLM is running.** Run this `curl` command. If it returns a JSON response, you are good to go.

   ```bash
   curl http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "gemma3:4b-instruct", "messages":[{"role":"user","content":"Who are you?"}], "stream": false}'
   ```

7. Developer A creates a branch `feat/engine`; Developer B creates a branch `feat/interface`.

---

## Phase 1: Parallel Development (3.5 Hours)

Developers work on their separate branches. **Crucially, agree on the function signatures below before starting.**

### Agreed-Upon Interface Contract

This is the "API" between the two developers. Developer A promises to build functions with these signatures; Developer B promises to use them.

```python
# From Developer A's modules
from dataclasses import dataclass

@dataclass
class EditBlock:
    path: str
    search_block: str
    replace_block: str

@dataclass
class CheckResult:
    ok: bool
    stage: str    # "ruff" | "pytest" | "skipped"
    output: str   # tool output to feed back to the model on failure

# In src/agent/patch/parse_blocks.py
def parse_edit_blocks(text: str) -> list[EditBlock]: ...

# In src/agent/patch/pathguard.py
def resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]:
    """Returns (resolved_absolute_path, None) if the path is safe and exists,
    or (None, error_message_with_suggestion) otherwise."""

# In src/agent/patch/fuzzy.py
def apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None: ...

# In src/agent/patch/validate.py
def is_syntax_valid(old_content: str, new_content: str) -> bool: ...

# In src/agent/patch/checks.py
def run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult: ...

# In src/agent/repomap/builder.py
def build_repo_map(root_dir: str) -> str: ...
```

---

### Track A: The Engine (Developer A)

Your goal is to create a set of pure, testable functions. You will work primarily in `src/agent/patch/` and `src/agent/repomap/`.

#### Task A1: The Syntax Gate (`src/agent/patch/validate.py`)

1. Implement `src/build_parsers.py` to download and compile tree-sitter grammars for Python into a `build/my-languages.so` file. Run this script once.
2. Implement `is_syntax_valid(old_content: str, new_content: str) -> bool`.
   - Load the Python grammar from the `.so` file.
   - Create a `tree_sitter.Parser`.
   - Parse `old_content` and count `ERROR` or `MISSING` nodes.
   - Parse `new_content` and count its errors.
   - Return `True` only if `new_errors <= old_errors`. This prevents the edit from introducing *new* errors into a possibly-already-broken file.
3. **Write unit tests** in `tests/test_validate.py` using sample valid and invalid Python code strings.

#### Task A2: The Patch Pipeline (`src/agent/patch/parse_blocks.py` & `fuzzy.py`)

1. In `parse_blocks.py`, implement `parse_edit_blocks(text: str) -> list[EditBlock]`.
   - Use a regular expression to find all `SEARCH/REPLACE` blocks in the model's text output.
   - Return a list of `EditBlock` dataclasses.
2. In `fuzzy.py`, implement `apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None`.
   - Implement the sliding window algorithm using `difflib.SequenceMatcher`.
   - The window size should be the number of lines in the `search_block`.
   - Score each window position against the `search_block`.
   - Return the new, patched file content on a successful, unambiguous match above the threshold (e.g., 0.85).
   - Return `None` if the best match is below the threshold or if the top two matches are too close in score (ambiguous).
3. **Write unit tests** in `tests/test_patch.py` for both functions.

#### Task A3: The Repo Map (`src/agent/repomap/builder.py`)

1. Implement `build_repo_map(root_dir: str) -> str`.
2. Use `glob` to find all `*.py` files, respecting a simple `exclude` list (e.g., `.venv`, `.git`, `__pycache__`).
3. For each file, use the `tree-sitter` parser to parse its content.
4. Write a recursive function to walk the AST and find `function_definition` and `class_definition` nodes. Extract their names and starting line numbers.
5. Format this into a single, clean string like:

   ```
   path/to/file.py
   - class MyClass:L10
   - def my_function:L25
   ```

6. Use the `transformers` tokenizer (for `gemma3-4b`) to count tokens and truncate the final string until it fits the `TOKEN_BUDGET` (1024).

#### Task A4: The Path Guard (`src/agent/patch/pathguard.py`) — about 30 minutes

1. Implement `resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]`.
   - Resolve `path` against `root_dir` with `pathlib.Path.resolve()`.
   - Reject any resolved path that is not inside `root_dir` (this blocks `../` escapes and absolute paths elsewhere on disk).
   - If the file exists, return `(resolved_path, None)`.
   - If it does not exist, collect all project file paths (reuse the repo map's exclude list) and use `difflib.get_close_matches` to build a message such as `File 'src/util.py' not found. Did you mean 'src/utils.py'?`. Return `(None, message)`.
2. **Write unit tests** in `tests/test_pathguard.py` covering: valid path, `../../etc/passwd`, an absolute path outside the root, a missing file with a close match, and a missing file with no close match.

#### Task A5: The Test/Lint Gate (`src/agent/patch/checks.py`) — about 60 minutes

1. Implement `run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult`.
   - Copy the project to a temporary directory with `shutil.copytree`, ignoring `.venv`, `.git`, `__pycache__` and `node_modules`.
   - Write `new_content` to `rel_path` inside the temporary copy. The real project is never touched.
   - Run `ruff check --select E9,F63,F7,F82 <file>` (errors that indicate real bugs, not style) with `subprocess.run`, a timeout and captured output. If it fails, return `CheckResult(False, "ruff", output)`.
   - If the project contains a `tests/` directory or `test_*.py` files, run `python -m pytest -x -q` in the temporary copy with a timeout (e.g., 60 seconds). If it fails, return `CheckResult(False, "pytest", output)`.
   - If there are no tests, return `CheckResult(True, "skipped", "")` for that stage.
   - Always clean up the temporary directory (`try/finally` or `tempfile.TemporaryDirectory`).
   - Truncate the tool output to a few hundred characters before returning it, so it fits in the small model's context.
2. **Write unit tests** in `tests/test_checks.py`: a change that passes, a change that breaks a test, a change with a lint error, and a project with no tests.

---

### Track B: The Interface (Developer B)

Your goal is to build the user-facing parts and the main agent loop. You will use **mock functions** for the engine parts until integration time. This allows you to work completely independently of Developer A.

#### Task B1: The LLM Client & CLI (`src/agent/llm.py` & `src/agent/cli.py`)

1. In `llm.py`, implement the `LLMClient` class with a `get_completion` streaming method that uses `httpx` to talk to the Ollama endpoint (`http://localhost:11434/v1`). Accept optional `temperature` and `model` parameters (needed for best-of-N and the benchmark).
2. In `cli.py`, create a `typer` app with a `run(task: str, dir: str = ".", model: str = "gemma3:4b-instruct", best_of: int = 1)` command.
3. As a first step, have the `run` command simply instantiate the `LLMClient`, send the task, and stream the response to the console using `rich.console.Console`. This verifies the end-to-end connection to the LLM.

#### Task B2: The Orchestrator with Mocks (`src/agent/orchestrator.py`)

1. Create the `Orchestrator` class. Its `__init__` should take the `root_dir`.
2. **Create mock functions** at the top of `orchestrator.py`. These must match the signatures from the "Interface Contract" above.

   ```python
   # --- MOCK IMPLEMENTATIONS FOR DEV B ---
   from .patch.parse_blocks import EditBlock # Can import the dataclass
   from .patch.checks import CheckResult     # Can import the dataclass

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
   # --- END MOCKS ---
   ```

3. Implement the main `run(task: str)` method, which contains the agent loop (`for i in range(MAX_STEPS)`).
   - Assemble the system prompt using `mock_build_repo_map()`.
   - Append the user's task to the message history.
   - Call the `LLMClient` to get the model's response.
   - Parse the response with `mock_parse_edit_blocks()`.
   - If no blocks, print "Task complete" and break the loop.
   - For each block, run it through the gates in order: `mock_resolve_safe_path()`, then `mock_apply_fuzzy_patch()`, then `mock_is_syntax_valid()`, then `mock_run_checks()`. Stop at the first gate that fails.
   - Print the actions being taken to the console using `rich`, including which gate passed or failed.
   - Assemble a "tool feedback" message (e.g., "Successfully applied patch to X", or the failing gate's message such as the path suggestion or the test output) and append it to the message history for the next loop iteration.
4. Connect the `cli.py`'s `run` command to invoke `Orchestrator(dir).run(task)`.

#### Task B3: Best-of-N Verified Sampling (in `orchestrator.py`) — about 45 minutes

1. Refactor the per-block gate sequence from B2 into a single helper, `verify_block(block) -> tuple[bool, str, str | None]` returning `(passed, feedback_message, new_content)`.
2. Add a `best_of` parameter to `Orchestrator`. When `best_of > 1`, sample that many responses for the same step (use `temperature` of about 0.7 for variety), and verify each one with `verify_block`.
3. Keep the first candidate in which every block passes all gates, and discard the others. If none pass, send the failure feedback of the best-scoring candidate (the one that got furthest through the gates) back to the model for the next step.
4. Print a short summary with `rich`, e.g. `Candidate 2/3 passed all gates`.

#### Task B4: The Benchmark Harness (`bench/run_bench.py`) — about 60 minutes

1. Create 10-15 small tasks in `bench/tasks/`. Each task is a folder (or a JSON file plus fixture folder) with:
   - A tiny sample Python project (2-3 files, ideally with a few `pytest` tests).
   - A task description (e.g., "add a docstring to `main`", "rename `calc` to `calculate_total`", "add a `discount_rate` argument").
   - A success check: a command that must pass after the edit (e.g., `pytest -q`, or a small assertion script that checks the intended change).
2. Implement `run_bench.py` with three modes:
   - **Baseline:** call the model, parse its edit blocks, and apply them with plain exact string replacement and no gates.
   - **Harness:** run the full `Orchestrator` pipeline.
   - **Harness + best-of-3:** same, with `best_of=3`.
3. For each task and mode, work in a fresh temporary copy of the fixture project, then record:
   - Task success (success check passes).
   - Syntax-error rate (file has new tree-sitter errors after the run).
   - Broken-test rate (tests that passed before now fail).
4. Print a results table with `rich` and write it to `bench/results.md` so you can paste it into the README.

---

## Phase 2: Integration (1.5 Hours)

*This is a team effort. Pair program this phase.*

1. **Code Merge:**
   - Developer A merges `feat/engine` into `main`.
   - Developer B rebases `feat/interface` onto the updated `main`.
2. **Replace Mocks:** In `orchestrator.py`, Developer B replaces all `mock_*` function calls with the actual functions imported from Developer A's modules.

   ```python
   # Before: from .mocks import mock_build_repo_map
   # After:  from .repomap.builder import build_repo_map
   ```

   Do the same for `mock_resolve_safe_path` (from `pathguard`) and `mock_run_checks` (from `checks`).
3. **End-to-End Testing:**
   - Create a small, sample Python project in `/tmp/sample_project/`. Give it 2-3 simple files and at least one passing test.
   - Run the `localpilot run "add a docstring to the main function in main.py" --dir /tmp/sample_project/` command.
   - Try a few failure cases on purpose to confirm each gate fires: ask the model to edit a file that doesn't exist (Path Guard), a task likely to produce a bad `SEARCH` block (Fuzzy Patch), and one that breaks a test (Test/Lint Gate).
   - **Debug together.** This is where you'll find signature mismatches, unexpected return values, and subtle logical errors in the agent loop. Expect this to take time.
4. **Add Final Polish:**
   - Implement `git stash` logic at the start of the `run` command (using `subprocess.run`) to make all changes reversible.
   - Implement a final diff display at the end of the loop using `rich.syntax.Syntax` or `difflib.unified_diff`.
5. **Run the Benchmark:** Run `python bench/run_bench.py` across all three modes. Keep the results; they go in the README. If the harness numbers are not better than the baseline, look at which gate is rejecting valid edits (for example, a Fuzzy Patch threshold that is too strict) and tune it.

---

## Phase 3: Final Touches & Submission (45 Minutes)

1. **Documentation:**
   - Create the `skills/safe-edit/SKILL.md` file. Define the skill's name, description, and the format of the `SEARCH/REPLACE` block it uses. Check the current Agent Skill specification for the exact required frontmatter fields (at minimum `name` and `description`).
   - Finalize the `README.md` with the correct usage instructions and fill in the Benchmark table with the real numbers from `bench/results.md`.
2. **Demo Prep:**
   - Clean up your sample project.
   - Record a short GIF or video (`asciinema` or QuickTime) of the agent successfully completing a task from start to finish. If possible, also show a gate catching a bad edit (for example, the Test/Lint Gate rejecting a change that breaks a test). **This is your most important deliverable.**
3. **Final Review:**
   - Read through the code one last time, remove dead code, and add comments where logic is complex.
   - Ensure `requirements.txt` is up to date (`pip freeze > requirements.txt`).
   - Make sure the GitHub repo is public and has the correct `LICENSE` file.
4. **SUBMIT!**

---

## Stretch Goals

Only attempt these if everything above is done and working.

- **Session log:** write every prompt, edit block and gate result to a JSONL file so a run can be replayed and debugged.
- **Structured output:** use Ollama's JSON-schema constrained output (or llama.cpp grammars) to reduce malformed edit blocks from small models.
- **Task-aware repo map:** rank files and symbols by relevance to the task (keyword/BM25 match) instead of listing everything, so the 1024-token budget is used better.
- **More languages:** add JavaScript/TypeScript and Go grammars for the Syntax Gate and repo map, since `tree-sitter-language-pack` is already a dependency.
- **Dry-run / approval mode:** show the unified diff and ask `y/n` before writing.
- **More agent skills:** split the workflow into separate skills, such as `safe-edit`, `repo-map` and `verify-changes`.
