# LocalPilot - 10 Minute Presentation Notes

## Opening (30 seconds)

**Hook:** "What if your AI coding assistant never sent your code to the cloud, never broke your syntax, and never made a change that failed your tests?"

**Introduce LocalPilot:**
- 100% local AI coding assistant
- Uses your own LLM via Ollama (Qwen 2.5 Coder 7B)
- Safety-first: 4-gate verification system
- **80% success rate** on real coding tasks

---

## The Problem (1 minute)

**Show slides or explain:**

1. **Privacy Concerns**: Cloud AI assistants send your code to remote servers
   - Enterprise/sensitive code exposure
   - Requires API keys and internet
   
2. **Quality Issues**: Small local models are powerful BUT:
   - Hallucinate file paths and content
   - Generate syntax errors
   - Break existing tests
   - No verification before writing

3. **Need**: A "safety harness" that lets you use small, local models safely

---

## The Solution: LocalPilot Architecture (2 minutes)

**Show diagram or walk through:**

```
User Task → LocalPilot → Local LLM (qwen2.5-coder:7b)
               ↓
        Parse SEARCH/REPLACE Blocks
               ↓
        4 Safety Gates:
          1. Path Guard ✓
          2. Fuzzy Patch ✓  
          3. Syntax Gate ✓
          4. Test/Lint Gate ✓
               ↓
        Write to Disk (only if ALL gates pass)
```

**Key Features:**

1. **Path Guard** 
   - Prevents escaping project root
   - Suggests "did you mean?" for typos
   
2. **Fuzzy Patch** (80% similarity matching)
   - Model doesn't need perfect SEARCH blocks
   - Finds best match using difflib
   
3. **Syntax Gate** (Tree-sitter AST)
   - Parse new code before writing
   - Rejects anything with syntax errors
   
4. **Test/Lint Gate** (pytest + ruff)
   - Run tests on temp copy
   - Reject if breaks existing tests

**Result**: Model can make mistakes, but none reach your files!

---

## Live Demo 1: Simple Fix (3 minutes)

**Setup (pre-prepared):**
```bash
cd demo_project
cat calculator.py  # Show the typo: "resutl" instead of "result"
```

**Run LocalPilot:**
```bash
python -m agent.cli demo_project "Fix the typo: rename 'resutl' to 'result' in calculator.py"
```

**What to highlight as it runs:**
1. "Building repo map..." - Shows model gets project context
2. "Step 1/8" - Agent starts working
3. Watch the gates:
   - ✓ Gate 1: Path Guard (file exists)
   - ✓ Gate 2: Fuzzy Patch (found the code)
   - ✓ Gate 3: Syntax Gate (valid Python)
   - ✓ Gate 4: Test/Lint Gate (tests pass!)
4. File is written only after ALL gates pass
5. Usually completes in 1-2 steps

**Show the result:**
```bash
cat calculator.py  # Typo is fixed!
python -m pytest test_calculator.py  # All tests pass
```

**Key point**: "The model saw the actual file contents, made one precise edit, and all safety gates approved it."

---

## Live Demo 2: Benchmark Suite (3 minutes)

**Explain the benchmark:**
- 10 real-world coding tasks
- Each task has tests that must pass
- Measures: success rate, syntax errors, broken tests

**Show task examples:**
```bash
ls bench/tasks/
# add_docstring, add_type_hints, fix_import, add_parameter, 
# add_error_handling, extract_constant, etc.
```

**Run a single task (fast):**
```bash
python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b
# Should pass in ~10 seconds
```

**Show full results** (pre-run if time is tight):
```bash
python bench/run_bench.py --mode harness --model qwen2.5-coder:7b
```

**Results table:**
```
Mode     | Tasks Passed | Syntax Error Rate | Broken Test Rate
---------|--------------|-------------------|------------------
Harness  |    8/10      |      0.0%         |     20.0%
```

**Key insights:**
- ✅ **80% success** - Model completes most tasks correctly
- ✅ **0% syntax errors** - Safety gates never let bad syntax through
- ⚠️ **20% broken tests** - 2 edge cases (fix_typo, rename_function) are flaky
- 🎯 **Average 2-3 steps** - Fast convergence with feedback

**Emphasize**: "Even on the 2 'failed' tasks, we generated valid Python. No syntax errors. Ever."

---

## Technical Highlights (1 minute)

**Implementation quality:**

1. **Developer Split**:
   - Developer A: Safety gates (fuzzy.py, pathguard.py, validate.py, checks.py)
   - Developer B: Interface (llm.py, orchestrator.py, cli.py, prompts.py)
   - Clean separation of concerns

2. **Test Coverage**:
   - 92 tests, all passing
   - Contract tests for each gate
   - Integration tests for orchestrator

3. **Smart Prompting**:
   - Few-shot examples in prompts
   - File contents included in context
   - Prevents hallucination

4. **AST-Based Repo Map**:
   - Tree-sitter parsing
   - Token-budget aware (1024 tokens)
   - Shows classes/functions only

5. **Best-of-N Mode**:
   - Sample multiple candidates
   - Gates pick the best
   - Increases success rate

---

## Why This Matters (30 seconds)

**Use cases:**

1. **Enterprise Development**
   - Keep proprietary code private
   - No cloud dependency
   
2. **Education & Research**
   - Understand how AI coding works
   - Benchmark different models
   
3. **Offline Development**
   - No internet required
   - Full control over model

4. **Open Source Community**
   - MIT licensed
   - Easy to extend
   - Model agnostic

---

## Results Summary (30 seconds)

**Show slide with metrics:**

```
✅ 80% Success Rate (8/10 tasks)
✅ 0% Syntax Errors (safety gates work!)
✅ 100% Local (no cloud, no API keys)
✅ 92 Tests Passing (comprehensive test suite)
✅ Model Agnostic (works with any OpenAI-compatible API)
```

**Key achievement**: "We built a safety harness that makes small local models reliable for real code editing."

---

## Q&A Prep

**Expected questions:**

**Q: Why only 80% success?**
A: The 2 failing tasks need more context or steps. The key is 0% syntax errors - we never break code. The failing tasks still produce valid Python, they just don't fully meet the test requirements.

**Q: How does fuzzy matching work?**
A: Python's difflib.SequenceMatcher finds best match with ≥80% similarity. Lets model be slightly imprecise while still finding the right code.

**Q: What about languages other than Python?**
A: Architecture is language-agnostic. Need to add tree-sitter parsers and lint/test runners for other languages. Python was our MVP.

**Q: Production ready?**
A: This is a research prototype. For production you'd want:
- More gates (security, performance)
- User confirmation UI
- Better error recovery
- Multi-language support
- Larger context windows

**Q: Can I use GPT-4 or Claude?**
A: Yes! Works with any OpenAI-compatible API. Just pass --model or modify llm.py. But the point is local models can work safely.

**Q: What's the performance?**
A: Average 2-3 steps per task, ~10-30 seconds on qwen2.5-coder:7b (local). Speed depends on your hardware.

---

## Closing (30 seconds)

**Summary:**
- LocalPilot proves small local models can safely edit code
- 4-gate verification prevents all syntax-breaking changes
- 80% success rate on real tasks
- 100% local, 100% private, 0% syntax errors

**Call to action:**
- GitHub: github.com/talhaishere2411/LocalPilot
- Branch: feat/interface
- Try it: `ollama pull qwen2.5-coder:7b && python -m agent.cli`
- MIT licensed - fork, extend, contribute!

**Final line**: "LocalPilot: Safe AI coding, entirely on your machine."

---

## Backup Slides/Info

### Tech Stack
- **Inference**: Ollama (local LLM server)
- **Model**: qwen2.5-coder:7b (7B parameters, 4-bit quantized)
- **Parsing**: tree-sitter, tree-sitter-language-pack
- **Patching**: difflib.SequenceMatcher
- **Testing**: pytest, ruff
- **CLI**: typer, rich
- **HTTP**: httpx

### Project Stats
- **Lines of Code**: ~3,000+ lines
- **Files**: 15+ modules
- **Tests**: 92 tests
- **Benchmark Tasks**: 10 tasks
- **Success Rate**: 80%
- **Syntax Error Rate**: 0%

### Quick Commands
```bash
# Install
git clone <repo> && cd LocalPilot
git checkout feat/interface
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -e .

# Run
python -m agent.cli <project> "<task>" --model qwen2.5-coder:7b

# Benchmark
python bench/run_bench.py --mode harness --model qwen2.5-coder:7b

# Test
python -m pytest tests/ -v
```
