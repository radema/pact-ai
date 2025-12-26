
import os
import yaml
import typer
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pact_cli import utils

console = Console()

def seal(target: str = typer.Argument(..., help="Target to seal [specs, plan, mrp] or command [status, verify]")):
    """
    Cryptographically seal the current Bolt's artifacts.
    Also provides 'status' and 'verify' capabilities.
    """
    utils.ensure_pact_root()
    bolt_path = utils.get_active_bolt_path()
    lock_file = bolt_path / "approved.lock"

    # --- Sub-command: Status ---
    if target == "status":
        if not lock_file.exists():
            console.print("[yellow]No approved.lock found for this bolt.[/yellow]")
            return
        
        with open(lock_file) as f:
            data = yaml.safe_load(f) or {}
            
        table = Table(title=f"Seal Status: {bolt_path.name}")
        table.add_column("Artifact", style="cyan")
        table.add_column("Sealed At", style="green")
        table.add_column("Hash (Prefix)", style="dim")
        
        for key in ["specs", "plan", "mrp"]:
            ts = data.get(f"{key}_sealed_at", "-")
            h = data.get(f"{key}_hash", "")
            table.add_row(key, ts, h[:8] if h else "-")
            
        console.print(table)
        return

    # --- Sub-command: Verify ---
    if target == "verify":
        if not lock_file.exists():
            console.print("[bold red]Fail:[/bold red] No lock file to verify against.")
            raise typer.Exit(code=1)
            
        with open(lock_file) as f:
            data = yaml.safe_load(f) or {}

        table = Table(title=f"Verification: {bolt_path.name}")
        table.add_column("Artifact", style="cyan")
        table.add_column("Status", style="bold")
        
        artifacts_map = {
            "specs": "02_specs.md",
            "plan": "03_plan.md",
            "mrp": "mrp/summary.md"
        }
        
        all_passed = True
        for key, filename in artifacts_map.items():
            stored_hash = data.get(f"{key}_hash")
            if not stored_hash:
                table.add_row(key, "[dim]Not Sealed[/dim]")
                continue
                
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
        if not all_passed:
            raise typer.Exit(code=1)
        return

    # --- Main Logic: Sealing ---
    valid_targets = {
        "specs": "02_specs.md",
        "plan": "03_plan.md",
        "mrp": "mrp/summary.md"
    }
    
    if target not in valid_targets:
        console.print(f"[bold red]Error:[/bold red] Invalid target '{target}'. Use: specs, plan, mrp, status, verify")
        raise typer.Exit(code=1)
        
    target_file = bolt_path / valid_targets[target]
    
    if not target_file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {target_file}")
        raise typer.Exit(code=1)
        
    # Calculate Hash
    new_hash = utils.compute_sha256(target_file)
    timestamp = datetime.now().isoformat()
    
    # Update Lock
    lock_data = {}
    if lock_file.exists():
        with open(lock_file) as f:
            lock_data = yaml.safe_load(f) or {}
            
    lock_data[f"{target}_hash"] = new_hash
    lock_data[f"{target}_sealed_at"] = timestamp
    
    with open(lock_file, "w") as f:
        yaml.safe_dump(lock_data, f)
        
    console.print(Panel(f"[bold green]Sealed {target}![/bold green]\nHash: {new_hash[:12]}...", title="PACT Seal"))
