import typer
from typing import Optional
from datetime import datetime, timezone
from rich.console import Console

from geas_ai import utils
from geas_ai.core import ledger, identity
from geas_ai.schemas import ledger as ledger_schemas
from geas_ai.schemas.identity import IdentityRole
from geas_ai.utils import crypto
from cryptography.hazmat.primitives.asymmetric import ed25519

console = Console()


def approve(
    identity_name: str = typer.Option(
        ..., "--identity", "-i", help="Identity to sign approval (must be human)"
    ),
    comment: Optional[str] = typer.Option(
        None, "--comment", "-c", help="Optional approval comment"
    ),
) -> None:
    """Approve the sealed MRP for merge.

    Usage:
        $ geas approve --identity tech-lead
        $ geas approve -i tech-lead -c "LGTM"
    """
    utils.ensure_geas_root()
    bolt_path = utils.get_active_bolt_path()

    # 1. Load Ledger
    ledger_obj = ledger.LedgerManager.load_lock(bolt_path)
    if not ledger_obj:
        console.print("[bold red]Error:[/bold red] No lock.json found.")
        raise typer.Exit(code=1)

    # 2. Verify State (Must have SEAL_MRP)
    # Check if SEAL_MRP exists
    mrp_event = None
    for event in reversed(ledger_obj.events):
        if event.action == ledger_schemas.LedgerAction.SEAL_MRP:
            mrp_event = event
            break

    if not mrp_event:
        console.print(
            "[bold red]Error:[/bold red] Cannot approve: MRP is not yet sealed."
        )
        raise typer.Exit(code=1)

    # Check if already approved? (Optional, but good UX)
    # The spec doesn't strictly forbid double approval, but let's warn.
    for event in ledger_obj.events:
        if event.action == ledger_schemas.LedgerAction.APPROVE:
            console.print(
                "[yellow]Warning: This bolt already has an approval.[/yellow]"
            )

    # 3. Validate Identity
    id_manager = identity.IdentityManager()
    id_store = id_manager.load()
    signer = id_store.get_by_name(identity_name)

    if not signer:
        console.print(
            f"[bold red]Error:[/bold red] Identity '{identity_name}' not found."
        )
        raise typer.Exit(code=1)

    if signer.role != IdentityRole.HUMAN:
        console.print(
            f"[bold red]Error:[/bold red] Only HUMAN identities can approve. '{identity_name}' is {signer.role.value}."
        )
        raise typer.Exit(code=1)

    # 4. Create Approval Event
    # Payload references the MRP hash (head of chain at that time, or the MRP event hash?)
    # Spec says: "Reference the sealed MRP."
    # Let's reference the `mrp_event.event_hash` specifically to be precise.

    payload = {"mrp_event_hash": mrp_event.event_hash, "comment": comment or ""}

    # 5. Sign
    try:
        # Load Private Key
        private_key_obj = identity.KeyManager.load_private_key(identity_name)
        if not isinstance(private_key_obj, ed25519.Ed25519PrivateKey):
            raise ValueError("Loaded key is not an Ed25519 private key")

        # Canonicalize and Sign
        canonical_bytes = crypto.canonicalize_json(payload)
        signature = crypto.sign(private_key_obj, canonical_bytes)

        event_identity = ledger_schemas.EventIdentity(
            signer_id=identity_name,
            public_key=signer.active_key,
            signature=signature,
        )

        # 6. Append
        event = ledger_schemas.LedgerEvent(
            sequence=0,  # Set by append
            timestamp=datetime.now(timezone.utc),
            action=ledger_schemas.LedgerAction.APPROVE,
            payload=payload,
            identity=event_identity,
            event_hash="",  # Set by append
        )

        ledger.LedgerManager.append_event(ledger_obj, event)
        ledger.LedgerManager.save_lock(bolt_path, ledger_obj)

        console.print(
            f"[bold green]Approved![/bold green] Bolt '{ledger_obj.bolt_id}' is approved by '{identity_name}'."
        )

    except identity.KeyNotFoundError:
        console.print(
            f"[bold red]Error:[/bold red] Private key for '{identity_name}' not found."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Approval failed: {e}")
        raise typer.Exit(code=1)
