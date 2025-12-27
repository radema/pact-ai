import yaml
import typer
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from pact_cli import utils

console = Console()


def seal(
    target: str = typer.Argument(..., help="Target to seal [req, specs, plan, mrp]"),
) -> None:
    """Cryptographically seal the current Bolt's artifacts.

    Args:
        target: The artifact to seal.

    Usage:
        $ pact seal req
        $ pact seal specs
    """
    utils.ensure_pact_root()
    bolt_path = utils.get_active_bolt_path()
    lock_file = bolt_path / "approved.lock"

    # --- Main Logic: Sealing ---
    valid_targets = {
        "req": "01_request.md",
        "specs": "02_specs.md",
        "plan": "03_plan.md",
        "mrp": "mrp/summary.md",
    }

    if target not in valid_targets:
        console.print(
            f"[bold red]Error:[/bold red] Invalid target '{target}'. Use: req, specs, plan, mrp"
        )
        raise typer.Exit(code=1)

    target_file = bolt_path / valid_targets[target]

    if not target_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {target_file}")
        raise typer.Exit(code=1)

    # Calculate Hash
    new_hash = utils.compute_sha256(target_file)
    timestamp = datetime.now().isoformat()

    # Update Lock
    lock_data: dict[str, str] = {}
    if lock_file.exists():
        with open(lock_file) as f:
            lock_data = yaml.safe_load(f) or {}

    lock_data[f"{target}_hash"] = new_hash
    lock_data[f"{target}_sealed_at"] = timestamp

    with open(lock_file, "w") as f:
        yaml.safe_dump(lock_data, f)

    console.print(
        Panel(
            f"[bold green]Sealed {target}![/bold green]\nHash: {new_hash[:12]}...",
            title="PACT Seal",
        )
    )
