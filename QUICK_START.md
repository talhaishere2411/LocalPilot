# LocalPilot - Quick Start Guide (5 Minutes)

Get LocalPilot running in 5 minutes and see the safety gates in action.

---

## Step 1: Install Ollama & Pull Model (2 minutes)

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.com
# Or use: brew install ollama  (macOS)

# Pull the recommended model (7B, ~4GB download)
ollama pull qwen2.5-coder:7b

# Verify it's running
ollama list
```

---

## Step 2: Setup LocalPilot (1 minute)

```bash
# Clone and checkout the working branch
git clone https://github.com/talhaishere2411/LocalPilot.git
cd LocalPilot
git checkout feat/interface

# Create virtual environment (Python 3.12 recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build tree-sitter parsers
python src/build_parsers.py
```

---

## Step 3: Run a Simple Demo (2 minutes)

### Option A: Quick Test with Existing Benchmark

```bash
# Run one benchmark task (fast, ~10 seconds)
python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b

# Expected output:
# ✓ Task passes
# See the 4 gates in action!
```

### Option B: Create Your Own Test

```bash
# Create a demo project
mkdir my_demo
cd my_demo

# Create a file with a typo
cat > calculator.py << 'EOF'
def add(a, b):
    """Add two numbers."""
    resutl = a + b  # Typo: resutl instead of result
    return resutl

def multiply(a, b):
    return a * b
EOF

# Create a test
cat > test_calculator.py << 'EOF'
from calculator import add

def test_add():
    assert add(2, 3) == 5

def test_no_typo():
    import inspect
    source = inspect.getsource(add)
    assert 'resutl' not in source  # This should pass after fix
EOF

# Run LocalPilot
cd ..
python -m agent.cli my_demo "Fix the typo: rename 'resutl' to 'result' in calculator.py"

# Watch the gates:
# ✓ Gate 1: Path Guard
# ✓ Gate 2: Fuzzy Patch
# ✓ Gate 3: Syntax Gate
# ✓ Gate 4: Test/Lint Gate

# Verify it worked
cat my_demo/calculator.py  # Typo is fixed!
cd my_demo && python -m pytest test_calculator.py  # Tests pass!
```

---

## What Just Happened?

LocalPilot:
1. ✅ Read your file contents (no hallucination)
2. ✅ Sent task to local LLM (qwen2.5-coder:7b)
3. ✅ Model proposed a SEARCH/REPLACE block
4. ✅ Ran through 4 safety gates:
   - Path Guard: File exists and is safe
   - Fuzzy Patch: Found the code to change
   - Syntax Gate: New code is valid Python
   - Test/Lint Gate: Tests still pass
5. ✅ Wrote the file ONLY after all gates passed

**Result**: Safe, verified code edit. No syntax errors. No broken tests.

---

## Run the Full Benchmark

```bash
# Run all 10 tasks (takes 3-4 minutes)
python bench/run_bench.py --mode harness --model qwen2.5-coder:7b

# Expected results:
# ✅ 8/10 tasks passing (80% success rate)
# ✅ 0% syntax errors
# ✅ 20% broken tests (2 edge cases, but still valid syntax)
```

---

## CLI Reference

```bash
# Basic usage
python -m agent.cli <project_dir> "<task description>"

# With custom model
python -m agent.cli <project_dir> "<task>" --model codellama:7b

# Best-of-3 mode (higher quality, slower)
python -m agent.cli <project_dir> "<task>" --best-of 3

# Run specific benchmark task
python bench/run_bench.py --task <task_id> --mode harness

# Run all benchmarks
python bench/run_bench.py --mode harness

# Run tests
python -m pytest tests/ -v
```

---

## Available Benchmark Tasks

1. `add_docstring` - Add docstrings to functions ✅
2. `add_type_hints` - Add Python type hints ✅
3. `fix_import` - Fix broken imports ✅
4. `add_parameter` - Add function parameters ✅
5. `add_default_value` - Add default parameter values ✅
6. `add_error_handling` - Add try/except blocks ✅
7. `extract_constant` - Extract magic numbers to constants ✅
8. `remove_unused_import` - Clean up unused imports ✅
9. `fix_typo` - Rename variables (edge case) ⚠️
10. `rename_function` - Refactor function names (edge case) ⚠️

---

## Troubleshooting

### "ollama: command not found"
Install Ollama from https://ollama.com

### "Model not found"
Pull the model: `ollama pull qwen2.5-coder:7b`

### "Module not found" errors
Activate venv: `source .venv/bin/activate`
Install deps: `pip install -r requirements.txt`

### "No module named 'tree_sitter_languages'"
Run: `python src/build_parsers.py`

### Model is slow
- Smaller model: `ollama pull gemma3:4b` (faster but less accurate)
- Larger model: `ollama pull qwen2.5-coder:14b` (more accurate but slower)
- Check your hardware (7B model needs ~8GB RAM)

---

## What's Next?

1. **Read DEMO.md** - Full 10-minute presentation guide
2. **Read PRESENTATION_NOTES.md** - Talking points for judges
3. **Read IMPLEMENTATION.md** - Technical deep dive
4. **Explore the code**:
   - `src/agent/orchestrator.py` - Main agent loop
   - `src/agent/patch/fuzzy.py` - Fuzzy matching logic
   - `src/agent/patch/checks.py` - Test/lint gate
   - `bench/run_bench.py` - Benchmark runner

---

## Key Metrics

- **Success Rate**: 80% (8/10 tasks)
- **Syntax Error Rate**: 0% (safety gates work!)
- **Broken Test Rate**: 20% (2 edge cases)
- **Average Steps**: 2-3 per task
- **Model**: qwen2.5-coder:7b (local, 7B params)

---

## Support

- **Repository**: https://github.com/talhaishere2411/LocalPilot
- **Branch**: feat/interface
- **License**: MIT

**Questions?** Check DEMO.md or PRESENTATION_NOTES.md for more details!
