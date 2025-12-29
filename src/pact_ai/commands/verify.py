import yaml
import typer
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from pact_ai import utils

console = Console()


def verify(
    bolt: Optional[str] = typer.Option(
        None, "--bolt", "-b", help="Name of the bolt to verify"
    ),
) -> None:
    """Verify the cryptographic integrity and temporal sequence of a bolt.

    Usage:
        $ pact verify
        $ pact verify -b feature-login
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
            f"[bold red]Fail:[/bold red] No lock file found for bolt '{bolt_path.name}'."
        )
        raise typer.Exit(code=1)

    try:
        with open(lock_file) as f:
            data = yaml.safe_load(f) or {}

        table = Table(title=f"Verification: {bolt_path.name}")
        table.add_column("Artifact", style="cyan")
        table.add_column("Status", style="bold")

        artifacts_map = {
            "req": "01_request.md",
            "specs": "02_specs.md",
            "plan": "03_plan.md",
            "mrp": "mrp/summary.md",
        }

        all_passed = True
        seal_times: list[datetime | None] = []

        # 1. Integrity Check
        for key, filename in artifacts_map.items():
            stored_hash = data.get(f"{key}_hash")
            sealed_at = data.get(f"{key}_sealed_at")

            if not stored_hash:
                table.add_row(key, "[dim]Not Sealed[/dim]")
                seal_times.append(None)
                continue

            # Track timestamp for sequence check
            try:
                dt = datetime.fromisoformat(str(sealed_at))
                seal_times.append(dt)
            except (ValueError, TypeError):
                seal_times.append(None)

            file_path = bolt_path / filename
            if not file_path.exists():
                table.add_row(key, "[red]Missing File[/red]")
                all_passed = False
                continue

            current_hash = utils.compute_sha256(file_path)
            if current_hash == stored_hash:
                table.add_row(key, "[green]PASS[/green]")
            else:
                table.add_row(key, "[red]FAIL (Drift Detected)[/red]")
                all_passed = False

        console.print(table)

        # 2. Sequence Verification
        valid_sequence = True
        # Filter out None values for comparison
        active_times = [
            (artifacts_map[list(artifacts_map.keys())[i]], t)
            for i, t in enumerate(seal_times)
            if t is not None
        ]

        for i in range(len(active_times) - 1):
            if active_times[i][1] > active_times[i + 1][1]:
                console.print(
                    f"[bold red]Sequence Error:[/bold red] {active_times[i][0]} was sealed AFTER {active_times[i + 1][0]}."
                )
                valid_sequence = False

        if not valid_sequence:
            all_passed = False

        if not all_passed:
            raise typer.Exit(code=1)
        else:
            console.print(
                "[bold green]Success:[/bold green] All artifacts verified and sequence is correct."
            )

    except Exception as e:
        if isinstance(e, typer.Exit):
            raise e
        console.print(f"[bold red]Error during verification:[/bold red] {e}")
        raise typer.Exit(code=1)
