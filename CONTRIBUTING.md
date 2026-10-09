# Contributing: ownership, rules, and git workflow

Two developers work in parallel. The scaffold was built so that **each file has exactly one owner** and nobody needs to edit the same file, which is what prevents merge conflicts.

## Ownership

| Area | Owner | Files |
|---|---|---|
| Engine | Developer A | `src/agent/patch/*`, `src/agent/repomap/builder.py`, `src/agent/parsing.py`, `src/build_parsers.py`, `skills/safe-edit/SKILL.md`, `tests/test_validate.py`, `tests/test_patch.py`, `tests/test_pathguard.py`, `tests/test_checks.py`, `tests/test_repomap.py` |
| Interface | Developer B | `src/agent/llm.py`, `src/agent/prompts.py`, `src/agent/orchestrator.py`, `src/agent/mocks.py`, `src/agent/cli.py`, `bench/*`, `tests/test_llm.py`, `tests/test_orchestrator.py`, `tests/test_cli.py` |
| Shared | Both | `requirements.txt`, `pyproject.toml`, `README.md`, `IMPLEMENTATION.md`, `CONTRIBUTING.md`, `PYTHON_COMPAT.md`, `.gitignore`, `.gitattributes`, `.python-version`, `.github/*`, `tests/test_contract.py`, every `__init__.py` |

## Rules that prevent clashes

1. **Only edit files you own.** If you need a change in the other developer's file, message them. Do not edit it yourself.
2. **Shared files change only through a small pull request to `main`**, reviewed by the other developer and merged quickly. Both then rebase (see below). This includes adding a dependency to `requirements.txt`.
3. **`__init__.py` files stay empty.** Never put code in them.
4. **Never change a signature in the interface contract** (`tests/test_contract.py` enforces it). If one must change, agree first, then change the contract test and both implementations in one shared PR.
5. **New files are fine inside your own area.** Name new test files `tests/test_<your_module>.py`.
6. **Tests that need a running model** must be marked `@pytest.mark.llm`. CI skips them.
7. **The edit-block format is locked** (see `skills/safe-edit/SKILL.md`). Developer A parses it and Developer B prompts the model with it. Changing it requires a shared PR.

## Branches

| Developer | Branch |
|---|---|
| A | `feat/engine` |
| B | `feat/interface` |

`main` only receives merges. Developer A merges `feat/engine` first; Developer B then rebases `feat/interface` onto `main` (Phase 2 in `IMPLEMENTATION.md`).

## Daily workflow (PowerShell)

Start of session:

```powershell
git fetch origin
git rebase origin/main
```

Commit small and often:

```powershell
git add <your files>
git commit -m "feat(patch): implement fuzzy matching"
git push --force-with-lease origin <your-branch>
```

`--force-with-lease` is only for your own feature branch after a rebase. Never force-push `main`.

## One-time setup after cloning

```powershell
git clone <REMOTE_URL> localpilot
cd localpilot
git checkout <your-branch>
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest -q
```

See `PYTHON_COMPAT.md` if your system Python is 3.13 or 3.14.

## Mocks (Developer B)

`src/agent/mocks.py` holds fake versions of Developer A's functions. Developer B builds the orchestrator against them. During integration (Phase 2), B replaces the `mock_*` imports with the real functions.
