
import os
import re
import typer
from pathlib import Path
from rich.console import Console

console = Console()

def ensure_pact_root() -> Path:
    """
    Checks if the current directory has a .pacts/ folder.
    Returns the Path to the current directory if true.
    Raises typer.Exit(1) if false.
    """
    if not os.path.exists(".pacts"):
        console.print("[bold red]Error:[/bold red] PACT is not initialized. Run `pact init` first.")
        raise typer.Exit(code=1)
    return Path(".")

def validate_slug(name: str) -> str:
    """
    Validates that the name contains only alphanumeric characters, hyphens, or underscores.
    """
    if not re.match(r"^[a-z0-9-_]+$", name):
        console.print(f"[bold red]Error:[/bold red] Invalid name '{name}'. Use only lowercase letters, numbers, hyphens, and underscores.")
        raise typer.BadParameter("Invalid slug format.")
    return name
