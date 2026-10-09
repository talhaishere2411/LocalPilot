#!/usr/bin/env python3
"""Debug fix_typo task to see what the model is doing."""

import shutil
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.orchestrator import Orchestrator

def main():
    # Create temp copy
    task_dir = Path("bench/tasks/fix_typo")
    project_dir = task_dir / "project"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_copy = Path(tmpdir) / "project"
        shutil.copytree(project_dir, project_copy)
        
        print(f"Working in: {project_copy}\n")
        print("=" * 80)
        print("BEFORE:")
        print("=" * 80)
        formatter_path = project_copy / "formatter.py"
        print(formatter_path.read_text())
        print()
        
        # Run orchestrator
        task_desc = "Fix the typo: rename the variable 'mesage' to 'message' in formatter.py."
        orchestrator = Orchestrator(root_dir=str(project_copy))
        
        # Don't suppress output for debugging
        orchestrator.run(task_desc)
        
        print("\n" + "=" * 80)
        print("AFTER:")
        print("=" * 80)
        print(formatter_path.read_text())
        
        # Run test
        print("\n" + "=" * 80)
        print("TEST RESULT:")
        print("=" * 80)
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "-v"],
            cwd=project_copy,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        print(f"Exit code: {result.returncode}")

if __name__ == "__main__":
    main()
