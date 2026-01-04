import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from geas_ai import utils
from geas_ai.core.ledger import LedgerManager

console = Console()

def status(
    bolt: Optional[str] = typer.Option(
        None, "--bolt", "-b", help="Name of the bolt to check status for"
    ),
) -> None:
    """Display the current seal status of a bolt.

    Usage:
        $ geas status
        $ geas status -b feature-login
    """
    utils.ensure_geas_root()

    if bolt:
        bolt_path = utils.get_geas_root() / "bolts" / bolt
        if not bolt_path.exists():
            console.print(f"[bold red]Error:[/bold red] Bolt '{bolt}' not found.")
            raise typer.Exit(code=1)
    else:
        bolt_path = utils.get_active_bolt_path()

    # Load Ledger
    ledger = LedgerManager.load_lock(bolt_path)

    if not ledger or not ledger.events:
        console.print(
            f"[yellow]No ledger (lock.json) found or empty for bolt '{bolt_path.name}'. Not Sealed.[/yellow]"
        )
        return

    # Display Header
    console.print(f"[bold]Bolt:[/bold] {ledger.bolt_id}")
    console.print(f"[bold]Created:[/bold] {ledger.created_at}")

    # Determine State (Last Event)
    last_event = ledger.events[-1]
    state_display = f"[cyan]{last_event.action.value}[/cyan]"
    console.print(f"[bold]Current State:[/bold] {state_display}")
    console.print()

    # Events Table
    table = Table(title=f"Event History: {bolt_path.name}")
    table.add_column("Seq", style="dim", justify="right")
    table.add_column("Timestamp", style="green")
    table.add_column("Action", style="cyan")
    table.add_column("Signer", style="magenta")

    for event in ledger.events:
        signer = "-"
        if event.identity:
            signer = f"{event.identity.signer_id}"

        table.add_row(
            str(event.sequence),
            event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            event.action.value,
            signer
        )

    console.print(table)
