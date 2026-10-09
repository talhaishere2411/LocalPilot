"""Agent loop: prompt the model, run each proposed edit through the gates, give feedback.

Owner: Developer B (tasks B2 and B3).

Gate order for every edit block:
  resolve_safe_path -> apply_fuzzy_patch -> is_syntax_valid -> run_checks
Develop against the functions in `.mocks`; in Phase 2 replace them with the
real functions from `.patch` and `.repomap`.
"""

from pathlib import Path

from rich.console import Console

from .llm import LLMClient, DEFAULT_MODEL
from .patch.parse_blocks import EditBlock
from .patch.checks import CheckResult

# --- MOCK IMPLEMENTATIONS FOR DEV B ---

def mock_build_repo_map(root_dir: str) -> str:
    """Mock repo map for testing."""
    return "mock/path.py\n  - def mock_function:L5"


def mock_parse_edit_blocks(text: str) -> list[EditBlock]:
    """Mock parser - returns a sample block if the model's response contains 'SEARCH'."""
    if "SEARCH" in text:
        return [EditBlock(path="mock/path.py", search_block="old", replace_block="new")]
    return []


def mock_resolve_safe_path(root_dir: str, path: str) -> tuple[str | None, str | None]:
    """Mock path guard - always succeeds."""
    return (f"{root_dir}/{path}", None)


def mock_apply_fuzzy_patch(file_content: str, block: EditBlock) -> str | None:
    """Mock fuzzy patcher - always succeeds."""
    return "This is the new, patched file content."


def mock_is_syntax_valid(old_content: str, new_content: str) -> bool:
    """Mock syntax validator - always passes."""
    return True


def mock_run_checks(root_dir: str, rel_path: str, new_content: str) -> CheckResult:
    """Mock check runner - always passes."""
    return CheckResult(ok=True, stage="skipped", output="")

# --- END MOCKS ---


MAX_STEPS = 8

SYSTEM_PROMPT = """You are a coding assistant that edits files safely using SEARCH/REPLACE blocks.

When the user asks you to change code, respond with one or more edit blocks in this exact format:

path/to/file.py
<<<<<<< SEARCH
exact lines to find
=======
replacement lines
>>>>>>> REPLACE

Rules:
1. The SEARCH block must match the existing file content EXACTLY (including whitespace)
2. You can have multiple edit blocks in one response
3. Only output edit blocks when making changes, otherwise just respond normally
4. Keep SEARCH blocks small and focused (3-10 lines typically)

Repository overview:
{repo_map}
"""


class Orchestrator:
    def __init__(
        self,
        root_dir: str,
        model: str = DEFAULT_MODEL,
        best_of: int = 1,
    ) -> None:
        self.root_dir = Path(root_dir).resolve()
        self.model = model
        self.best_of = best_of
        self.console = Console()
        self.client = LLMClient(model=model)
        self.messages: list[dict] = []

    def run(self, task: str) -> None:
        """Main agent loop."""
        self.console.print(f"\n[bold blue]LocalPilot[/bold blue] starting task in {self.root_dir}")
        self.console.print(f"Model: {self.model}, best_of: {self.best_of}\n")
        
        # Build repo map and create system prompt
        repo_map = mock_build_repo_map(str(self.root_dir))
        system_prompt = SYSTEM_PROMPT.format(repo_map=repo_map)
        
        # Initialize message history
        self.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # Agent loop
        for step in range(MAX_STEPS):
            self.console.print(f"[bold cyan]Step {step + 1}/{MAX_STEPS}[/bold cyan]")
            
            if self.best_of == 1:
                # Standard mode: single candidate
                response = self._get_model_response()
                self.console.print(f"[bold green]Assistant:[/bold green]\n{response}\n")
                
                # Add to history
                self.messages.append({"role": "assistant", "content": response})
                
                # Parse and verify blocks
                blocks = mock_parse_edit_blocks(response)
                
                if not blocks:
                    self.console.print("[bold green]✓[/bold green] No edit blocks found. Task complete.")
                    break
                
                self.console.print(f"[bold yellow]Found {len(blocks)} edit block(s)[/bold yellow]")
                feedback_messages = self._verify_all_blocks(blocks)
                
            else:
                # Best-of-N mode: sample multiple candidates
                self.console.print(f"[dim]Sampling {self.best_of} candidates with temperature=0.7...[/dim]\n")
                
                best_response = None
                best_feedback = None
                best_blocks_passed = 0
                
                for candidate_num in range(self.best_of):
                    self.console.print(f"[cyan]Candidate {candidate_num + 1}/{self.best_of}[/cyan]")
                    
                    # Sample with higher temperature for variety
                    response = self._get_model_response(temperature=0.7)
                    blocks = mock_parse_edit_blocks(response)
                    
                    if not blocks:
                        self.console.print("  [dim]No edit blocks found[/dim]")
                        # If this is the first candidate with no blocks, use it
                        if best_response is None:
                            best_response = response
                            best_feedback = []
                        continue
                    
                    # Verify all blocks for this candidate
                    self.console.print(f"  [dim]Found {len(blocks)} block(s), verifying...[/dim]")
                    feedback_messages = self._verify_all_blocks(blocks, quiet=True)
                    
                    # Count how many blocks passed
                    blocks_passed = sum(1 for msg in feedback_messages if "Successfully applied" in msg)
                    
                    self.console.print(f"  [dim]{blocks_passed}/{len(blocks)} blocks passed gates[/dim]")
                    
                    # If all blocks passed, use this candidate
                    if blocks_passed == len(blocks):
                        self.console.print(f"[bold green]✓ Candidate {candidate_num + 1} passed all gates![/bold green]\n")
                        best_response = response
                        best_feedback = feedback_messages
                        break
                    
                    # Track the best candidate so far
                    if blocks_passed > best_blocks_passed:
                        best_blocks_passed = blocks_passed
                        best_response = response
                        best_feedback = feedback_messages
                
                # Use the best candidate found
                if best_response is None:
                    self.console.print("[yellow]⚠ No valid candidates found[/yellow]")
                    break
                
                self.console.print(f"[bold green]Assistant (best candidate):[/bold green]\n{best_response}\n")
                self.messages.append({"role": "assistant", "content": best_response})
                
                blocks = mock_parse_edit_blocks(best_response)
                if not blocks:
                    self.console.print("[bold green]✓[/bold green] No edit blocks found. Task complete.")
                    break
                
                feedback_messages = best_feedback
            
            # Send feedback back to model
            combined_feedback = "\n\n".join(feedback_messages)
            self.messages.append({"role": "user", "content": f"Gate results:\n{combined_feedback}"})
            
            self.console.print()
        
        if step == MAX_STEPS - 1:
            self.console.print("[yellow]⚠[/yellow] Reached maximum steps")
    
    def _get_model_response(self, temperature: float = 0.2) -> str:
        """Get a single response from the model."""
        response = ""
        for chunk in self.client.get_completion(self.messages, temperature=temperature):
            response += chunk
        return response
    
    def _verify_all_blocks(self, blocks: list[EditBlock], quiet: bool = False) -> list[str]:
        """Verify all blocks and return feedback messages.
        
        Args:
            blocks: List of edit blocks to verify
            quiet: If True, suppress per-block console output
        """
        feedback_messages = []
        
        for i, block in enumerate(blocks, 1):
            if not quiet:
                self.console.print(f"\n[cyan]Processing block {i}: {block.path}[/cyan]")
            
            success, feedback, _ = self._verify_block(block, quiet=quiet)
            feedback_messages.append(feedback)
            
            if not quiet:
                if not success:
                    self.console.print(f"[red]✗ Block {i} failed a gate[/red]")
                else:
                    self.console.print(f"[green]✓ Block {i} passed all gates[/green]")
        
        return feedback_messages
    
    def _verify_block(self, block: EditBlock, quiet: bool = False) -> tuple[bool, str, str | None]:
        """Run one edit block through all gates in order.
        
        Returns (passed, feedback_message, new_content).
        """
        # Gate 1: Path Guard
        if not quiet:
            self.console.print("  [dim]Gate 1: Path Guard[/dim]")
        resolved_path, error = mock_resolve_safe_path(str(self.root_dir), block.path)
        if error:
            return False, f"Path Guard failed for {block.path}: {error}", None
        
        # In real implementation, would read file here
        # For now, use mock content
        old_content = "mock old file content"
        
        # Gate 2: Fuzzy Patch
        if not quiet:
            self.console.print("  [dim]Gate 2: Fuzzy Patch[/dim]")
        new_content = mock_apply_fuzzy_patch(old_content, block)
        if new_content is None:
            return False, f"Fuzzy Patch failed for {block.path}: Could not find a unique match for SEARCH block", None
        
        # Gate 3: Syntax Gate
        if not quiet:
            self.console.print("  [dim]Gate 3: Syntax Gate[/dim]")
        if not mock_is_syntax_valid(old_content, new_content):
            return False, f"Syntax Gate failed for {block.path}: New code has syntax errors", None
        
        # Gate 4: Test/Lint Gate
        if not quiet:
            self.console.print("  [dim]Gate 4: Test/Lint Gate[/dim]")
        check_result = mock_run_checks(str(self.root_dir), block.path, new_content)
        if not check_result.ok:
            return False, f"Test/Lint Gate failed for {block.path} at {check_result.stage}:\n{check_result.output}", None
        
        # All gates passed - in real implementation would write file here
        return True, f"Successfully applied patch to {block.path}", new_content
