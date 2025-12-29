import yaml
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from pact_cli import utils

console = Console()


def status(
    bolt: Optional[str] = typer.Option(
        None, "--bolt", "-b", help="Name of the bolt to check status for"
    ),
) -> None:
    """Display the current seal status of a bolt.

    Usage:
        $ pact status
        $ pact status -b feature-login
    """
    utils.ensure_pact_root()

    if bolt:
        bolt_path = utils.get_pact_root() / "bolts" / bolt
        if not bolt_path.exists():
            console.print(f"[bold red]Error:[/bold red] Bolt '{bolt}' not found.")
            raise typer.Exit(code=1)
    else:
        bolt_path = utils.get_active_bolt_path()

    lock_file = bolt_path / "approved.lock"

    if not lock_file.exists():
        console.print(
            f"[yellow]No approved.lock found for bolt '{bolt_path.name}'.[/yellow]"
        )
        return

    try:
        with open(lock_file) as f:
            data = yaml.safe_load(f) or {}

        table = Table(title=f"Seal Status: {bolt_path.name}")
        table.add_column("Artifact", style="cyan")
        table.add_column("Sealed At", style="green")
        table.add_column("Hash (Prefix)", style="dim")

        for key in ["req", "specs", "plan", "mrp"]:
            ts = data.get(f"{key}_sealed_at", "-")
            h = data.get(f"{key}_hash", "")
            table.add_row(key, ts, h[:8] if h else "-")

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error reading lock file:[/bold red] {e}")
        raise typer.Exit(code=1)
