import typer
import json
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from geas_ai import utils
from geas_ai.core import verification, workflow as workflow_core
from geas_ai.core.ledger import LedgerManager
from geas_ai.core.identity import IdentityManager
from geas_ai.schemas.verification import (
    ChainValidationResult,
    SignatureValidationResult,
    WorkflowValidationResult,
    ContentValidationResult,
)

console = Console()


def verify(
    bolt: Optional[str] = typer.Option(
        None, "--bolt", "-b", help="Name of the bolt to verify"
    ),
    check_content: bool = typer.Option(
        False, "--content", help="Also verify sealed file contents match hashes"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
) -> None:
    """Verify the cryptographic integrity and governance compliance of a bolt.

    Usage:
        $ geas verify
        $ geas verify --content
        $ geas verify --json
    """
    utils.ensure_geas_root()

    if bolt:
        bolt_path = utils.get_geas_root() / "bolts" / bolt
        if not bolt_path.exists():
            console.print(f"[bold red]Error:[/bold red] Bolt '{bolt}' not found.")
            raise typer.Exit(code=1)
    else:
        bolt_path = utils.get_active_bolt_path()

    # 1. Load Data
    ledger = LedgerManager.load_lock(bolt_path)
    if not ledger:
        msg = f"No lock.json found for bolt '{bolt_path.name}'."
        if json_output:
            print(json.dumps({"error": msg, "valid": False}))
        else:
            console.print(f"[bold red]Fail:[/bold red] {msg}")
        raise typer.Exit(code=1)

    workflow_config = (
        workflow_core.WorkflowManager.load_workflow()
    )  # Loads default if missing

    id_manager = IdentityManager()
    identities = id_manager.load()

    # 2. Run Validations
    chain_res = verification.validate_chain_integrity(ledger)
    sig_res = verification.validate_signatures(ledger, identities)
    flow_res = verification.validate_workflow_compliance(
        ledger, workflow_config, identities
    )

    content_res = None
    if check_content:
        content_res = verification.validate_content_integrity(ledger, bolt_path)

    # 3. Aggregate Results
    overall_valid = chain_res.valid and sig_res.valid and flow_res.valid
    if content_res:
        overall_valid = overall_valid and content_res.valid

    # 4. Output
    if json_output:
        output = {
            "bolt": bolt_path.name,
            "valid": overall_valid,
            "chain": chain_res.model_dump(mode="json"),
            "signatures": sig_res.model_dump(mode="json"),
            "workflow": flow_res.model_dump(mode="json"),
        }
        if content_res:
            output["content"] = content_res.model_dump(mode="json")
        print(json.dumps(output, indent=2))
    else:
        _print_report(
            bolt_path.name, overall_valid, chain_res, sig_res, flow_res, content_res
        )

    if not overall_valid:
        raise typer.Exit(code=1)


def _print_report(
    bolt_name: str,
    valid: bool,
    chain: ChainValidationResult,
    sig: SignatureValidationResult,
    flow: WorkflowValidationResult,
    content: Optional[ContentValidationResult],
) -> None:
    console.print(Panel(f"[bold]Verification Report:[/bold] {bolt_name}", expand=False))

    # Summary Table
    table = Table(show_header=False, box=None)
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    def status_style(is_valid: bool) -> str:
        return "[green]PASS[/green]" if is_valid else "[red]FAIL[/red]"

    table.add_row(
        "Chain Integrity", status_style(chain.valid), f"{chain.event_count} events"
    )
    table.add_row(
        "Signatures", status_style(sig.valid), f"{sig.verified_count} verified"
    )
    table.add_row(
        "Workflow",
        status_style(flow.valid),
        f"Stages: {', '.join(flow.completed_stages)}",
    )

    if content:
        table.add_row(
            "Content",
            status_style(content.valid),
            f"{content.checked_files} files checked",
        )

    console.print(table)
    console.print()

    # Violations
    all_violations = chain.violations + sig.violations + flow.violations
    if content:
        all_violations += content.violations

    if all_violations:
        console.print("[bold red]Violations:[/bold red]")
        v_table = Table(show_header=True)
        v_table.add_column("Code", style="red")
        v_table.add_column("Seq")
        v_table.add_column("Message")

        for v in all_violations:
            seq = str(v.event_sequence) if v.event_sequence is not None else "-"
            v_table.add_row(v.code.value, seq, v.message)

        console.print(v_table)
    else:
        console.print("[bold green]All checks passed![/bold green]")
