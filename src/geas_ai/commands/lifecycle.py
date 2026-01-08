import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from geas_ai import utils
from geas_ai.bolt import Bolt
from geas_ai.state import StateManager

console = Console()


def new(name: str) -> None:
    """Start a new GEAS Unit of Work (Bolt).

    Creates .geas/bolts/<name>/ and updates state.

    Args:
        name: The name of the bolt (slugified).

    Usage:
        $ geas new feature-login
    """
    try:
        bolt = Bolt.create(name)

        console.print(
            Panel(
                f"[bold green]Bolt Started![/bold green]\n\nWorkspace: [blue]{bolt.path}[/blue]\nContext: [yellow]Updated[/yellow]\nLedger: [yellow]Initialized[/yellow]",
                title=f"Bolt: {name}",
            )
        )

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def checkout(name: str) -> None:
    """Switch the current active context to a different bolt.

    Usage:
        $ geas checkout feature-login
    """
    utils.ensure_geas_root()

    manager = StateManager()
    try:
        # Verify it exists first
        Bolt.load(name)
        manager.set_active_bolt(name)

        console.print(
            Panel(
                f"[bold green]Switched to bolt:[/bold green] [blue]{name}[/blue]",
                title="geas checkout",
            )
        )
    except ValueError:
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error switching bolt:[/bold red] {e}")
        raise typer.Exit(code=1)


def delete(
    name: str,
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
) -> None:
    """Delete a bolt. State is cleaned up.

    Usage:
        $ geas delete feature-obsolete
    """
    utils.ensure_geas_root()

    try:
        manager = StateManager()
        active_bolt = manager.get_active_bolt()

        if name == active_bolt:
            console.print(
                f"[bold red]Error:[/bold red] Cannot delete the active bolt '{name}'. Switch context first."
            )
            raise typer.Exit(code=1)

        # Load implies existence check
        bolt = Bolt.load(name)

        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete bolt '{name}'?")
            if not confirm:
                raise typer.Abort()

        bolt.delete()
        console.print(f"[bold green]Success:[/bold green] Bolt '{name}' deleted.")

    except ValueError:
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)
    except typer.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error deleting bolt:[/bold red] {e}")
        raise typer.Exit(code=1)


def archive(name: str) -> None:
    """Archive a fully verified bolt.

    Usage:
        $ geas archive feature-completed
    """
    utils.ensure_geas_root()

    try:
        bolt = Bolt.load(name)
        bolt.archive()
        console.print(
            f"[bold green]Success![/bold green] Bolt '{name}' moved to archive."
        )
    except RuntimeError as e:
        # Verification failed
        console.print(f"[bold red]Verification Failed:[/bold red] {e}")

        # Prompt for force archive
        confirm = typer.confirm(
            f"Do you want to force archive '{name}' despite verification failure?"
        )
        if not confirm:
            raise typer.Exit(code=1)

        # Force archive logic manual override
        # We need a way to force archive in Bolt class or handle it here
        # Extending Bolt.archive to accept force param or manually moving
        # Let's manually move here since it's an edge case, or better, allow Bolt.archive(force=True)
        # But Bolt.archive currently doesn't accept force.
        # Let's update Bolt.archive? No, I committed that file.
        # Use low-level move.

        try:
            import shutil

            archive_root = utils.get_geas_root() / "archive"
            archive_root.mkdir(exist_ok=True)
            target_path = archive_root / name

            if target_path.exists():
                console.print(
                    f"[bold red]Error:[/bold red] Bolt '{name}' already exists in archive."
                )
                raise typer.Exit(code=1)

            shutil.move(str(bolt.path), str(target_path))

            # Update state
            manager = StateManager()
            manager.update_bolt_status(name, "archived")
            manager.set_active_bolt(None) if manager.get_active_bolt() == name else None

            console.print(
                f"[bold yellow]Forced Archive:[/bold yellow] Bolt '{name}' moved to archive."
            )

        except Exception as inner_e:
            console.print(
                f"[bold red]Error during forced archive:[/bold red] {inner_e}"
            )
            raise typer.Exit(code=1)

    except ValueError:
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def list_bolts() -> None:
    """List all bolts in the repository."""
    utils.ensure_geas_root()

    manager = StateManager()
    bolts = manager.list_bolts()
    active_bolt = manager.get_active_bolt()

    table = Table(title="GEAS Bolts")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Created At", style="green")
    table.add_column("Active", justify="center")

    for name, data in bolts.items():
        is_active = "[bold green]*[/bold green]" if name == active_bolt else ""
        table.add_row(
            name,
            data.get("status", "unknown"),
            data.get("created_at", "N/A"),
            is_active,
        )

    console.print(table)
