"""Benchmark runner: baseline vs harness vs harness + best-of-3.

Owner: Developer B (task B4). Task format: bench/tasks/TASK_FORMAT.md.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

MODES = ("baseline", "harness", "harness_best_of_3")

console = Console()


def load_tasks():
    """Load all benchmark tasks from bench/tasks/."""
    tasks_dir = Path(__file__).parent / "tasks"
    tasks = []
    
    for task_dir in sorted(tasks_dir.iterdir()):
        if not task_dir.is_dir():
            continue
        
        task_json = task_dir / "task.json"
        if not task_json.exists():
            continue
        
        with open(task_json) as f:
            task_data = json.load(f)
        
        project_dir = task_dir / "project"
        if not project_dir.exists():
            console.print(f"[yellow]Warning: No project/ dir in {task_dir.name}[/yellow]")
            continue
        
        tasks.append({
            "id": task_data["id"],
            "description": task_data["description"],
            "success_cmd": task_data["success_cmd"],
            "project_dir": project_dir,
        })
    
    return tasks


def run_baseline(task_desc: str, project_copy: Path) -> dict:
    """Run baseline mode: direct model call with no gates."""
    from agent.llm import LLMClient
    from agent.patch.parse_blocks import parse_edit_blocks
    
    client = LLMClient()
    
    # Simple prompt without repo map
    messages = [
        {"role": "system", "content": "You are a coding assistant. Edit files using SEARCH/REPLACE blocks."},
        {"role": "user", "content": task_desc}
    ]
    
    # Get single response
    response = ""
    for chunk in client.get_completion(messages):
        response += chunk
    
    # Parse blocks using real parser
    blocks = parse_edit_blocks(response)
    
    # Apply with exact string replacement (no fuzzy matching, no gates)
    for block in blocks:
        file_path = project_copy / block.path
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text()
            # Exact string replacement (no fuzzy matching)
            if block.search_block in content:
                new_content = content.replace(block.search_block, block.replace_block, 1)
                file_path.write_text(new_content)
        except Exception:
            # Skip on any error
            continue
    
    return {"blocks_attempted": len(blocks)}


def run_harness(task_desc: str, project_copy: Path, best_of: int = 1) -> dict:
    """Run with full orchestrator."""
    from agent.orchestrator import Orchestrator
    
    try:
        orchestrator = Orchestrator(root_dir=str(project_copy), best_of=best_of)
        
        # Silence console output during benchmark
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        f = io.StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            orchestrator.run(task_desc)
        
        return {}
    except Exception as e:
        # Return error info but don't crash
        return {"error": str(e)}


def check_success(project_dir: Path, success_cmd: str) -> bool:
    """Run the success check command."""
    try:
        result = subprocess.run(
            success_cmd,
            shell=True,
            cwd=project_dir,
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def check_syntax_errors(project_dir: Path) -> int:
    """Count files with syntax errors using tree-sitter."""
    # For now, use Python's ast module
    import ast
    
    error_count = 0
    for py_file in project_dir.glob("**/*.py"):
        try:
            ast.parse(py_file.read_text())
        except SyntaxError:
            error_count += 1
    
    return error_count


def check_broken_tests(project_dir: Path) -> bool:
    """Check if tests that should pass are now broken."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-q"],
            cwd=project_dir,
            capture_output=True,
            timeout=30,
        )
        return result.returncode != 0
    except (subprocess.TimeoutExpired, Exception):
        return True


def run_benchmark_task(task: dict, mode: str) -> dict:
    """Run a single task in a given mode."""
    # Create temp copy of project
    with tempfile.TemporaryDirectory() as tmpdir:
        project_copy = Path(tmpdir) / "project"
        shutil.copytree(task["project_dir"], project_copy)
        
        # Count syntax errors before
        syntax_errors_before = check_syntax_errors(project_copy)
        
        # Run the task based on mode
        try:
            if mode == "baseline":
                run_baseline(task["description"], project_copy)
            elif mode == "harness":
                run_harness(task["description"], project_copy, best_of=1)
            elif mode == "harness_best_of_3":
                run_harness(task["description"], project_copy, best_of=3)
        except Exception as e:
            console.print(f"[red]Error running {task['id']} in {mode}: {e}[/red]")
            return {
                "success": False,
                "syntax_errors": syntax_errors_before,
                "tests_broken": True,
            }
        
        # Check results
        success = check_success(project_copy, task["success_cmd"])
        syntax_errors_after = check_syntax_errors(project_copy)
        new_syntax_errors = max(0, syntax_errors_after - syntax_errors_before)
        tests_broken = check_broken_tests(project_copy)
        
        return {
            "success": success,
            "syntax_errors": new_syntax_errors,
            "tests_broken": tests_broken,
        }


def main() -> None:
    """Run the full benchmark across all modes."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LocalPilot benchmark")
    parser.add_argument("--model", default="gemma3:4b", help="Model to use (default: gemma3:4b)")
    parser.add_argument("--mode", choices=MODES, help="Run only this mode (default: all)")
    parser.add_argument("--task", help="Run only this task ID (default: all)")
    args = parser.parse_args()
    
    console.print("[bold blue]LocalPilot Benchmark Runner[/bold blue]\n")
    console.print(f"Model: {args.model}\n")
    
    # Set model for LLM client
    import os
    os.environ["LOCALPILOT_MODEL"] = args.model
    
    # Load tasks
    tasks = load_tasks()
    
    # Filter tasks if specified
    if args.task:
        tasks = [t for t in tasks if t["id"] == args.task]
        if not tasks:
            console.print(f"[red]Task '{args.task}' not found![/red]")
            sys.exit(1)
    
    console.print(f"Loaded {len(tasks)} benchmark task(s)\n")
    
    if not tasks:
        console.print("[red]No tasks found![/red]")
        sys.exit(1)
    
    # Determine which modes to run
    modes_to_run = [args.mode] if args.mode else MODES
    
    # Run benchmark for each mode
    results = {mode: [] for mode in modes_to_run}
    
    for mode in modes_to_run:
        console.print(f"[cyan]Running mode: {mode}[/cyan]")
        
        for task in tasks:
            console.print(f"  Running {task['id']}... ", end="")
            result = run_benchmark_task(task, mode)
            results[mode].append(result)
            
            status = "✓" if result["success"] else "✗"
            console.print(status)
        
        console.print()
    
    # Compute statistics
    stats = {}
    for mode in modes_to_run:
        mode_results = results[mode]
        total = len(mode_results)
        
        stats[mode] = {
            "passed": sum(1 for r in mode_results if r["success"]),
            "total": total,
            "syntax_error_rate": sum(1 for r in mode_results if r["syntax_errors"] > 0) / total * 100 if total > 0 else 0,
            "broken_test_rate": sum(1 for r in mode_results if r["tests_broken"]) / total * 100 if total > 0 else 0,
        }
    
    # Display results table
    table = Table(title="Benchmark Results")
    table.add_column("Mode", style="cyan")
    table.add_column("Tasks Passed", justify="right")
    table.add_column("Syntax Error Rate", justify="right")
    table.add_column("Broken Test Rate", justify="right")
    
    for mode in modes_to_run:
        s = stats[mode]
        table.add_row(
            mode.replace("_", " ").title(),
            f"{s['passed']}/{s['total']}",
            f"{s['syntax_error_rate']:.1f}%",
            f"{s['broken_test_rate']:.1f}%",
        )
    
    console.print()
    console.print(table)
    
    # Write results to file
    results_file = Path(__file__).parent / "results.md"
    with open(results_file, "w") as f:
        f.write("# Benchmark Results\n\n")
        f.write(f"Model: {args.model}\n\n")
        f.write("| Mode | Tasks Passed | Syntax Error Rate | Broken Test Rate |\n")
        f.write("|------|--------------|-------------------|------------------|\n")
        
        for mode in modes_to_run:
            s = stats[mode]
            f.write(f"| {mode.replace('_', ' ').title()} | {s['passed']}/{s['total']} | {s['syntax_error_rate']:.1f}% | {s['broken_test_rate']:.1f}% |\n")
    
    console.print(f"\n[green]Results written to {results_file}[/green]")


if __name__ == "__main__":
    main()
