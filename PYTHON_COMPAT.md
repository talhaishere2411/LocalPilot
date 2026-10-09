# Python Version Guide

**Standard version for this project: Python 3.12.** The code supports 3.10 to 3.14, but dependency wheels (especially PyTorch-related ones) are not always available for the newest Python. Use 3.12 unless you have a reason not to.

## If your system Python is 3.13 or 3.14

Do not change your system Python. Create the project environment with 3.12 instead.

### Option A: uv (recommended)

```bash
# install uv once: https://docs.astral.sh/uv/
uv venv --python 3.12 .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
uv pip install -e .
```

`uv` downloads Python 3.12 automatically if it is not installed.

### Option B: pyenv

```bash
pyenv install 3.12
pyenv local 3.12                   # reads/writes .python-version
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Check an install before you run it

```bash
pip install --dry-run -r requirements.txt
```

If a package has no wheel for your Python version, this reports it without changing anything. Fix it by switching to 3.12, not by patching the code.

## Verify your environment

```bash
python --version                   # expect 3.12.x (or the version you chose)
python -m pytest -q                # expect: all tests pass
ruff check .                       # expect: All checks passed!
```

## Token counting

The repo map uses `count_tokens()` in `src/agent/repomap/builder.py`. It needs no torch and no model download:

- Default: approximates tokens as `len(text) // 4`.
- Optional exact counts: set `LOCALPILOT_TOKENIZER` to the path of a local `tokenizer.json` file.

## Supported versions

| Python | Status |
|---|---|
| 3.12 | Standard, always tested |
| 3.10 | Tested in CI |
| 3.13 | Tested in CI |
| 3.14 | Tested in CI, failures do not block merges |

Update this table to match the CI results before submission.
