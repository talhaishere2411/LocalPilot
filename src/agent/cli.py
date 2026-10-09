"""Command-line interface.

Owner: Developer B (task B1).
"""

import typer
from rich.console import Console

from .llm import DEFAULT_MODEL
from .orchestrator import Orchestrator

app = typer.Typer(
    help="LocalPilot: a verification-first coding harness for small local LLMs."
)

console = Console()


@app.callback()
def main() -> None:
    """LocalPilot command line interface."""


@app.command()
def run(
    task: str = typer.Argument(..., help="What the agent should do."),
    dir: str = typer.Option(".", help="Project directory to work in."),
    model: str = typer.Option(DEFAULT_MODEL, help="Model name served by the local server."),
    best_of: int = typer.Option(1, help="Candidate edits to sample per step."),
) -> None:
    """Run the agent on a task inside a project directory."""
    try:
        orchestrator = Orchestrator(root_dir=dir, model=model, best_of=best_of)
        orchestrator.run(task)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
