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
    Reads .geas/active_context.md to find the current bolt path.
    """
    ctx_file = Path(".geas/active_context.md")
    if not ctx_file.exists():
        console.print("[bold red]Error:[/bold red] No active context found.")
        raise typer.Exit(code=1)

    content = ctx_file.read_text(encoding="utf-8")
    match = re.search(r"\*\*Path:\*\* (.*)", content)
    if not match:
        console.print(
            "[bold red]Error:[/bold red] Could not parse Active Bolt Path from context."
        )
        raise typer.Exit(code=1)

    bolt_path = Path(match.group(1).strip())
    if not bolt_path.exists():
        # Handle the spec requirement 'Active Bolt not found'
        console.print(
            f"[bold red]Error:[/bold red] Active Bolt directory not found: {bolt_path}"
        )
        raise typer.Exit(code=1)

    return bolt_path


def get_active_bolt_name() -> str:
    """Reads .geas/active_context.md to find the current bolt name."""
    ctx_file = Path(".geas/active_context.md")
    if not ctx_file.exists():
        console.print("[bold red]Error:[/bold red] No active context found.")
        raise typer.Exit(code=1)

    content = ctx_file.read_text(encoding="utf-8")
    match = re.search(r"\*\*Current Bolt:\*\* (.*)", content)
    if not match:
        console.print(
            "[bold red]Error:[/bold red] Could not parse Active Bolt Name from context."
        )
        raise typer.Exit(code=1)

    return match.group(1).strip()
