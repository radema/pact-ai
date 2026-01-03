import os
import shutil
import typer
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from geas_ai import utils
from geas_ai.core import content, ledger
from geas_ai.commands.verify import verify as run_verify

console = Console()


def new(name: str) -> None:
    """Start a new GEAS Unit of Work (Bolt).

    Creates .geas/bolts/<name>/ and updates .geas/active_context.md.

    Args:
        name: The name of the bolt (slugified).

    Usage:
        $ geas new feature-login
    """
    try:
        # 1. Validation
        utils.ensure_geas_root()
        utils.validate_slug(name)

        bolt_dir = os.path.join(".geas", "bolts", name)

        # 2. Check for existence (Idempotencyish warning)
        if os.path.exists(bolt_dir):
            console.print(f"[bold red]Error:[/bold red] Bolt '{name}' already exists.")
            raise typer.Exit(code=1)

        # 3. Create Structure
        os.makedirs(bolt_dir)

        # 4. Initialize Ledger (lock.json)
        genesis = ledger.LedgerManager.create_genesis_ledger(bolt_id=name)
        ledger.LedgerManager.save_lock(Path(bolt_dir), genesis)

        # 5. Create Request File
        req_path = os.path.join(bolt_dir, "01_request.md")
        with open(req_path, "w") as f:
            f.write(content.REQUEST_TEMPLATE.format(bolt_name=name))

        # 6. Update Context
        ctx_path = os.path.join(".geas", "active_context.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ctx_path, "w") as f:
            f.write(
                content.CONTEXT_TEMPLATE.format(bolt_name=name, timestamp=timestamp)
            )

        # 7. Success Output
        console.print(
            Panel(
                f"[bold green]Bolt Started![/bold green]\n\nWorkspace: [blue]{bolt_dir}[/blue]\nContext: [yellow]Updated[/yellow]\nLedger: [yellow]Initialized[/yellow]",
                title=f"Bolt: {name}",
            )
        )

    except Exception as e:
        # If it's a Typer Exit, just re-raise
        if isinstance(e, typer.Exit) or isinstance(e, typer.BadParameter):
            raise e
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def checkout(name: str) -> None:
    """Switch the current active context to a different bolt.

    Usage:
        $ geas checkout feature-login
    """
    utils.ensure_geas_root()
    bolt_dir = utils.get_geas_root() / "bolts" / name

    if not bolt_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)

    # Update active_context.md
    ctx_path = utils.get_geas_root() / "active_context.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(ctx_path, "w") as f:
            f.write(
                content.CONTEXT_TEMPLATE.format(bolt_name=name, timestamp=timestamp)
            )

        console.print(
            Panel(
                f"[bold green]Switched to bolt:[/bold green] [blue]{name}[/blue]",
                title="geas checkout",
            )
        )
    except Exception as e:
        console.print(f"[bold red]Error updating context:[/bold red] {e}")
        raise typer.Exit(code=1)


def delete(
    name: str,
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
) -> None:
    """Delete a bolt. Cannot delete the currently active bolt.

    Usage:
        $ geas delete feature-obsolete
    """
    utils.ensure_geas_root()

    # Safety Check: Do not delete active bolt
    try:
        active_bolt = utils.get_active_bolt_name()
        if name == active_bolt:
            console.print(
                f"[bold red]Error:[/bold red] Cannot delete the active bolt '{name}'. Switch context first."
            )
            raise typer.Exit(code=1)
    except Exception:
        # If no active context, proceed with caution
        pass

    bolt_dir = utils.get_geas_root() / "bolts" / name
    if not bolt_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)

    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete bolt '{name}'?")
        if not confirm:
            raise typer.Abort()

    try:
        shutil.rmtree(bolt_dir)
        console.print(f"[bold green]Success:[/bold green] Bolt '{name}' deleted.")
    except Exception as e:
        console.print(f"[bold red]Error deleting bolt:[/bold red] {e}")
        raise typer.Exit(code=1)


def archive(name: str) -> None:
    """Archive a fully verified bolt.

    A bolt can only be archived if all artifacts (req, specs, plan, mrp) are sealed
    and verified.

    Usage:
        $ geas archive feature-completed
    """
    utils.ensure_geas_root()
    bolt_dir = utils.get_geas_root() / "bolts" / name
    archive_root = utils.get_geas_root() / "archive"

    if not bolt_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
        raise typer.Exit(code=1)

    # 1. Verification
    console.print(f"Verifying bolt '{name}' before archival...")
    try:
        # Run verify logic (will exit 1 if fails)
        run_verify(bolt=name)

        lock_file = bolt_dir / "approved.lock"
        import yaml

        with open(lock_file) as f:
            data = yaml.safe_load(f) or {}

        required = ["req", "specs", "plan", "mrp"]
        missing = [r for r in required if f"{r}_hash" not in data]
        if missing:
            console.print(
                f"[bold red]Archival Rejected:[/bold red] The following artifacts are not sealed: {', '.join(missing)}"
            )
            raise typer.Exit(code=1)

    except (typer.Exit, SystemExit) as e:
        exit_code = getattr(e, "exit_code", getattr(e, "code", 0))
        if exit_code != 0:
            console.print(
                "[bold red]Archival Rejected:[/bold red] Bolt failed verification."
            )
            raise typer.Exit(code=exit_code)
    except Exception as e:
        console.print(f"[bold red]Error during archival check:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 2. Move
    try:
        os.makedirs(archive_root, exist_ok=True)
        target_path = archive_root / name

        if target_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Bolt '{name}' already exists in archive. Rename it or delete the archive version first."
            )
            raise typer.Exit(code=1)

        shutil.move(str(bolt_dir), str(target_path))
        console.print(
            f"[bold green]Success![/bold green] Bolt '{name}' moved to archive."
        )

    except Exception as e:
        console.print(f"[bold red]Error moving bolt to archive:[/bold red] {e}")
        raise typer.Exit(code=1)
