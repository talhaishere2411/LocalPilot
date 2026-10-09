# LocalPilot Demo Guide (10 Minutes)

## What is LocalPilot?

LocalPilot is an **AI-powered coding assistant** that runs 100% locally using your own LLM (via Ollama). It safely edits Python code through a **4-gate safety system** that prevents breaking changes.

### Key Features
- ✅ **100% Local** - No API keys, no cloud, complete privacy
- ✅ **Safety-First** - 4 gates prevent bad edits: Path Guard, Fuzzy Patch, Syntax Check, Test/Lint
- ✅ **Intelligent Editing** - Uses SEARCH/REPLACE blocks with fuzzy matching
- ✅ **Repository Awareness** - Builds AST-based repo map for context
- ✅ **Benchmark Suite** - 10 real-world coding tasks, 80% success rate

---

## Quick Setup (2 minutes)

### Prerequisites
```bash
# 1. Install Ollama (if not installed)
# Visit: https://ollama.com

# 2. Pull the model
ollama pull qwen2.5-coder:7b

# 3. Clone and setup
git clone https://github.com/talhaishere2411/LocalPilot.git
cd LocalPilot
git checkout feat/interface

# 4. Create virtual environment
uv venv --python 3.12 .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 5. Install dependencies
uv pip install -e .
```

---

## Live Demo 1: Fix a Typo (2 minutes)

Show how LocalPilot safely fixes a simple bug:

```bash
# Create a test file with a typo
mkdir demo_project
cd demo_project

cat > calculator.py << 'EOF'
def add(a, b):
    """Add two numbers."""
    resutl = a + b  # Typo: resutl instead of result
    return resutl

def multiply(a, b):
    return a * b
EOF

cat > test_calculator.py << 'EOF'
from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_no_typo():
    import inspect
    source = inspect.getsource(add)
    assert 'resutl' not in source  # This will fail until fixed
EOF

# Run LocalPilot
cd ..
python -m agent.cli demo_project "Fix the typo: rename 'resutl' to 'result' in calculator.py"

# Watch it work through the 4 gates:
# ✓ Gate 1: Path Guard (file is safe to edit)
# ✓ Gate 2: Fuzzy Patch (found the code to replace)
# ✓ Gate 3: Syntax Gate (new code is valid Python)
# ✓ Gate 4: Test/Lint Gate (tests pass!)
```

**What to highlight:**
- Model sees the actual file contents (no hallucination)
- Uses exact SEARCH/REPLACE blocks with fuzzy matching
- All 4 gates pass before any file is written
- File is safely edited in 1-2 steps

---

## Live Demo 2: Run Benchmarks (3 minutes)

Show the benchmark suite with 10 real coding tasks:

```bash
# Run single task (fast)
python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b

# Run all 10 tasks (takes ~3-4 minutes)
python bench/run_bench.py --mode harness --model qwen2.5-coder:7b

# Expected results:
# ✓ 8/10 tasks passing (80% success rate)
# ✓ 0% syntax errors (safety gates work!)
# ✓ 20% broken tests (edge cases, but code is always valid)
```

**Benchmark tasks include:**
1. ✅ add_docstring - Add docstrings to functions
2. ✅ add_type_hints - Add Python type hints
3. ✅ fix_import - Fix broken imports
4. ✅ add_parameter - Add function parameters
5. ✅ add_default_value - Add default values
6. ✅ add_error_handling - Add try/except blocks
7. ✅ extract_constant - Extract magic numbers
8. ✅ remove_unused_import - Clean up imports
9. ⚠️ fix_typo - Rename variables (flaky)
10. ⚠️ rename_function - Refactor function names (flaky)

---

## Key Technical Achievements (1 minute)

### Architecture
```
User Task → Orchestrator → LLM (Local)
                ↓
         Parse SEARCH/REPLACE Blocks
                ↓
         Run Through 4 Gates:
           1. Path Guard (prevents escaping root)
           2. Fuzzy Patch (80% similarity matching)
           3. Syntax Gate (AST validation)
           4. Test/Lint Gate (pytest + ruff)
                ↓
         Apply Changes (only if all gates pass)
```

### Implementation Highlights
1. **Fuzzy Matching** - Uses difflib.SequenceMatcher for 80% similarity threshold
2. **AST Parsing** - Tree-sitter for Python syntax analysis
3. **Repo Map** - Compact class/function overview within token budget
4. **Best-of-N Sampling** - Optional mode for higher success rates
5. **Streaming LLM** - httpx-based streaming for fast responses

### Code Quality
- ✅ Full test suite (92 tests, all passing)
- ✅ Type hints throughout
- ✅ Clean separation of concerns (Developer A: engine, Developer B: interface)
- ✅ Comprehensive documentation (README, IMPLEMENTATION, PYTHON_COMPAT)

---

## Why LocalPilot Matters (1 minute)

### Problem
- Cloud-based AI coding assistants send your code to remote servers
- Privacy concerns for enterprise/sensitive code
- Requires API keys and internet connection
- No control over model behavior

### Solution
- **100% Local** - Your code never leaves your machine
- **Open Source** - Inspect, modify, extend
- **Safety-First** - 4 gates prevent accidental damage
- **Model Agnostic** - Works with any OpenAI-compatible local server (Ollama, mlx-lm)

### Use Cases
1. **Enterprise Development** - Keep proprietary code private
2. **Learning/Education** - Understand how AI coding works
3. **Offline Development** - No internet required
4. **Research** - Benchmark different local models

---

## Quick CLI Reference

```bash
# Basic usage
python -m agent.cli <project_dir> "<task description>"

# With custom model
python -m agent.cli <project_dir> "<task>" --model codellama:7b

# Best-of-3 mode (slower but higher quality)
python -m agent.cli <project_dir> "<task>" --best-of 3

# Run benchmarks
python bench/run_bench.py --mode harness
python bench/run_bench.py --task <task_id> --mode harness
python bench/run_bench.py --mode harness_best_of_3

# Run tests
python -m pytest tests/ -v
python -m pytest tests/test_contract.py -v -k fuzzy
```

---

## Project Structure

```
LocalPilot/
├── src/agent/
│   ├── llm.py              # LLM client (Developer B)
│   ├── cli.py              # CLI interface (Developer B)
│   ├── orchestrator.py     # Main agent loop (Developer B)
│   ├── prompts.py          # System prompts (Developer B)
│   ├── patch/              # Safety gates (Developer A)
│   │   ├── fuzzy.py        # Fuzzy matching
│   │   ├── pathguard.py    # Path safety
│   │   ├── validate.py     # Syntax checking
│   │   ├── checks.py       # Test/lint runner
│   │   └── parse_blocks.py # SEARCH/REPLACE parser
│   └── repomap/            # Repo map builder (Developer A)
│       └── builder.py
├── bench/                  # Benchmark suite (Developer B)
│   ├── run_bench.py
│   └── tasks/              # 10 benchmark tasks
└── tests/                  # Test suite (Developer A)
    └── test_contract.py    # 92 tests
```

---

## Results Summary

### Metrics
- **Success Rate**: 80% (8/10 tasks)
- **Syntax Error Rate**: 0% (safety gates work!)
- **Broken Test Rate**: 20% (edge cases)
- **Model**: qwen2.5-coder:7b (local, 7B parameters)
- **Average Steps**: 2-3 per task
- **Token Budget**: 1024 tokens for repo map

### Comparison to Requirements
- ✅ Local LLM integration via Ollama
- ✅ 4-gate safety system implemented
- ✅ Fuzzy matching with 80% threshold
- ✅ AST-based repo map
- ✅ SEARCH/REPLACE block format
- ✅ Comprehensive test suite
- ✅ Benchmark harness with 10 tasks
- ✅ Best-of-N sampling mode
- ✅ Python 3.12+ compatibility

---

## Questions for Judges

**Q: Why only 80% success rate?**
A: The 2 failing tasks (fix_typo, rename_function) are edge cases where the model needs more context or steps. The important metric is 0% syntax errors - we never break code.

**Q: How does fuzzy matching work?**
A: We use Python's difflib.SequenceMatcher to find the best match with ≥80% similarity. This allows the model to be slightly off while still finding the right code.

**Q: Can I use a different model?**
A: Yes! Works with any OpenAI-compatible API. Just pass `--model <name>` or modify DEFAULT_MODEL in llm.py.

**Q: What's the token budget strategy?**
A: Repo map is capped at 1024 tokens (configurable). We include file contents in the initial prompt, then stream responses from the model.

**Q: Production ready?**
A: This is a research prototype demonstrating local AI safety gates. For production, you'd want: more gates, better error recovery, user confirmation UI, and broader language support.

---

## Contact & Links

- **Repository**: https://github.com/talhaishere2411/LocalPilot
- **Branch**: feat/interface
- **Model**: qwen2.5-coder:7b (via Ollama)
- **License**: MIT

**Built for**: Local LLM Safety & Privacy Research
**Built by**: Developer A (safety gates) + Developer B (interface)
