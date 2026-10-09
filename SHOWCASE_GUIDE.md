# LocalPilot - Visual Showcase Guide

## 🎯 For Maximum Impact in 10 Minutes

---

## Pre-Demo Checklist

### Before You Start
```bash
# 1. Ensure Ollama is running
ollama list  # Should show qwen2.5-coder:7b

# 2. Terminal setup
# - Full screen mode
# - Dark theme (better contrast)
# - Large font size (Cmd/Ctrl + Plus)
# - Clear any clutter

# 3. Navigate to project
cd /Users/mohdsahil/Desktop/projects/LocalPilot
git checkout feat/interface
source .venv/bin/activate
```

---

## Option 1: Automated Visual Demo (Recommended) ⭐

**Time: 2-3 minutes**

```bash
./demo_showcase.sh
```

**What judges will see:**
- 🎨 Colorful ASCII art banners
- 📁 Demo project creation with typo
- ❌ Failing tests (shows the problem)
- ⏸️ Pause for effect
- 🤖 LocalPilot fixing the issue with all 4 gates visible
- ✅ Tests passing (shows success)
- 📊 Beautiful summary box

**Pro tip:** This is fully automated and looks professional!

---

## Option 2: Benchmark Showcase

**Time: Choose 10 seconds OR 3-4 minutes**

```bash
./demo_benchmark.sh
```

**Interactive menu:**
1. Quick demo (one task) - 10 seconds
2. Full benchmark (all 10 tasks) - 3-4 minutes

**What judges will see:**
- 🎨 Colorful task list
- ⚡ Real-time progress with checkmarks/crosses
- 📊 Beautiful results table at the end
- 🎯 Key metrics highlighted

---

## Option 3: Manual Demo (More Control)

### Step 1: Show The Problem (30 seconds)

```bash
# Create demo with visible issue
mkdir my_demo && cd my_demo

cat > bug.py << 'EOF'
def calculate(x, y):
    resutl = x + y  # Typo!
    return resutl
EOF

echo "📄 File with typo:"
cat bug.py
```

### Step 2: Run LocalPilot (1 minute)

```bash
cd ..
python -m agent.cli my_demo "Fix the typo: rename 'resutl' to 'result'"
```

**Point out to judges as it runs:**
- 🟦 "Building repo map..." - Shows context gathering
- 🟩 "Step 1/8" - Agent starting
- ✓ Watch each gate pass:
  - Gate 1: Path Guard
  - Gate 2: Fuzzy Patch  
  - Gate 3: Syntax Gate
  - Gate 4: Test/Lint Gate
- 🟢 "✓ Block 1 passed all gates"

### Step 3: Show Success (30 seconds)

```bash
echo "✅ Fixed file:"
cat my_demo/bug.py
```

---

## What Makes It Visually Impressive

### The orchestrator already uses Rich library for:

1. **Color-Coded Output**
   - 🔵 Blue: Info messages
   - 🟢 Green: Success (✓)
   - 🔴 Red: Failures (✗)
   - 🟡 Yellow: Warnings
   - 🟣 Magenta: Steps/progress

2. **Progress Indicators**
   - "Step 1/8", "Step 2/8" shows progress
   - Each gate shows completion: ✓ or ✗

3. **Structured Layout**
   - Clear separation between steps
   - Indented gate checks
   - Clean status messages

4. **Real-Time Streaming**
   - Model responses appear character-by-character
   - Feels interactive and live

---

## Key Visual Moments to Highlight

### 1. Repo Map Building (Shows Intelligence)
```
[bold blue]LocalPilot[/bold blue] starting task in /path/to/project
Model: qwen2.5-coder:7b, best_of: 1
```

### 2. Gate Execution (Shows Safety)
```
[cyan]Processing block 1: calculator.py[/cyan]
  [dim]Gate 1: Path Guard[/dim]
  [dim]Gate 2: Fuzzy Patch[/dim]
  [dim]Gate 3: Syntax Gate[/dim]
  [dim]Gate 4: Test/Lint Gate[/dim]
[green]✓ Block 1 passed all gates[/green]
```

### 3. Success Message (Shows Results)
```
[bold green]✓[/bold green] No edit blocks found. Task complete.
```

---

## Benchmark Visual Highlights

When you run the benchmark, judges see:

```
LocalPilot Benchmark Runner
Model: qwen2.5-coder:7b
Loaded 10 benchmark task(s)
Running mode: harness
  Running add_docstring... ✓
  Running add_type_hints... ✓
  Running fix_import... ✓
  Running add_parameter... ✓
  Running add_default_value... ✓
  Running add_error_handling... ✓
  Running extract_constant... ✓
  Running fix_typo... ✗
  Running remove_unused_import... ✓
  Running rename_function... ✗

                        Benchmark Results                        
┏━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Mode    ┃ Tasks Passed ┃ Syntax Error Rate ┃ Broken Test Rate ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Harness │         8/10 │              0.0% │            20.0% │
└─────────┴──────────────┴───────────────────┴──────────────────┘
```

**Beautiful table formatting** thanks to Rich library!

---

## Tips for Maximum Impact

### 1. Terminal Setup
- **Font size**: Make it BIG (judges need to see from distance)
- **Theme**: Dark background, light text
- **Window size**: Full screen or at least 120 columns wide

### 2. Pacing
- **Pause** between phases to let judges absorb
- **Point out** the 4 gates as they run
- **Emphasize** the 0% syntax error rate

### 3. What to Say

**Opening:** "Watch how LocalPilot runs local AI through 4 safety gates"

**During demo:** 
- "See Gate 1? Path safety check"
- "Gate 2 uses fuzzy matching - 80% similarity"
- "Gate 3 validates syntax before writing"
- "Gate 4 runs tests - only writes if all pass"

**Closing:** "80% success, 0% syntax errors, 100% local"

### 4. Backup Plan
If live demo fails (network, model, etc.):
- Have screenshots ready
- Show the benchmark results table
- Walk through the code structure
- Emphasize the test suite (92 tests passing)

---

## Screen Recording Tips

If recording for async judging:

```bash
# Use asciinema for terminal recording
brew install asciinema

# Record the demo
asciinema rec demo.cast

# Then run your demo
./demo_showcase.sh

# Stop with Ctrl+D

# Play it back
asciinema play demo.cast
```

---

## One-Liner Demos for Quick Impact

```bash
# 1. Single task benchmark (10 seconds)
python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b

# 2. Show test suite (impressive!)
python -m pytest tests/ -v --tb=short

# 3. Quick fix demo
echo 'def hello():\n    print("hi")' > test.py && \
  python -m agent.cli . "Add a docstring to hello function" && \
  cat test.py
```

---

## What Judges Care About

### They want to see:
1. ✅ **It works** - Live demo succeeds
2. ✅ **It's safe** - Gates prevent errors
3. ✅ **It's fast** - 2-3 steps, 10-30 seconds
4. ✅ **It's measurable** - Benchmark results
5. ✅ **It's real** - Actual code changes

### Visual proof points:
- 🎯 **80% success rate** in benchmark table
- ✅ **0% syntax errors** in results
- 🟢 **Green checkmarks** as gates pass
- 📊 **Beautiful Rich tables**
- ⚡ **Real-time streaming** output

---

## Final Checklist Before Demo

```bash
# Verify everything works
cd /Users/mohdsahil/Desktop/projects/LocalPilot
source .venv/bin/activate

# Test 1: Quick benchmark
python bench/run_bench.py --task add_docstring --mode harness --model qwen2.5-coder:7b
# Should see: ✓ and pass

# Test 2: Demo script
./demo_showcase.sh
# Should see: Colorful output, all gates pass

# Test 3: Check model
ollama list
# Should see: qwen2.5-coder:7b

# You're ready! 🚀
```

---

## Emergency Fallbacks

If something breaks during demo:

1. **Model not responding**: Show pre-run benchmark results
2. **Terminal issues**: Show code walkthrough instead
3. **Time running out**: Jump to benchmark summary
4. **Questions interrupt**: Have PRESENTATION_NOTES.md open

Remember: **Confidence matters more than perfection!**

---

## Success Metrics to Emphasize

When showing results, highlight:

```
🎯 80% Success Rate  ← "Most tasks completed correctly"
✅ 0% Syntax Errors  ← "Safety gates work perfectly" 
🔒 100% Local       ← "No cloud, no API keys"
⚡ 2-3 Steps Avg    ← "Fast convergence"
🧪 92 Tests Passing ← "Production quality"
```

---

Good luck with your presentation! The visual elements are all there - just run the scripts and point out the colorful output as it happens. 🌟
