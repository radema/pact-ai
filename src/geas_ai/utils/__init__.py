import os
import re
import typer
from pathlib import Path
from rich.console import Console

console = Console()


def get_geas_root() -> Path:
    """Returns the Path to the .geas directory."""
    return Path(".geas")


def ensure_geas_root() -> Path:
    """Checks if the current directory has a .geas/ folder.

    Returns the Path to the current directory if true.
    Raises typer.Exit(1) if false.
    """
    if not os.path.exists(".geas"):
        console.print(
            "[bold red]Error:[/bold red] GEAS is not initialized. Run `geas init` first."
        )
        raise typer.Exit(code=1)
    return Path(".")


def validate_slug(name: str) -> str:
    """
    Validates that the name contains only alphanumeric characters, hyphens, or underscores.
    """
    if not re.match(r"^[a-z0-9-_]+$", name):
        console.print(
            f"[bold red]Error:[/bold red] Invalid name '{name}'. Use only lowercase letters, numbers, hyphens, and underscores."
        )
        raise typer.BadParameter("Invalid slug format.")
    return name


def compute_sha256(file_path: Path) -> str:
    """
    Computes SHA256 hash of the file content (normalized).
    Strips trailing whitespace to avoid CRLF/LF issues.
    """
    import hashlib

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    # Normalize: strip and universal newlines are handled by python read_text usually,
    # but we explicitly strip to be safe against editor added newlines at EOF.
    normalized = content.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def get_active_bolt_path() -> Path:
    """
    Returns the Path to the current active bolt directory.
    Uses StateManager (state.json) as source of truth.
    """
    from geas_ai.state import StateManager

    manager = StateManager()
    active = manager.get_active_bolt()

    if not active:
        console.print("[bold red]Error:[/bold red] No active bolt selected.")
        raise typer.Exit(code=1)

    bolt_path = get_geas_root() / "bolts" / active
    if not bolt_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Active Bolt directory not found: {bolt_path}"
        )
        raise typer.Exit(code=1)

    return bolt_path


def get_active_bolt_name() -> str:
    """Returns the name of the current active bolt."""
    from geas_ai.state import StateManager

    manager = StateManager()
    active = manager.get_active_bolt()

    if not active:
        console.print("[bold red]Error:[/bold red] No active bolt selected.")
        raise typer.Exit(code=1)

    return active
