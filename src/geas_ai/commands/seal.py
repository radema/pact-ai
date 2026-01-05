import typer
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from typing import Optional, Dict, Any

from pathlib import Path
from geas_ai import utils
from geas_ai.core import ledger, hashing, identity
from geas_ai.schemas import ledger as ledger_schemas
from geas_ai.utils import crypto
from cryptography.hazmat.primitives.asymmetric import ed25519

console = Console()


def seal(
    target: str = typer.Argument(
        ..., help="Target to seal [req, specs, plan, mrp, intent]"
    ),
    identity_name: Optional[str] = typer.Option(
        None, "--identity", "-i", help="Identity to sign with (required for intent)"
    ),
    context: Optional[str] = typer.Option(
        None, "--context", "-c", help="Context message for the event"
    ),
) -> None:
    """Cryptographically seal the current Bolt's artifacts.

    Args:
        target: The artifact to seal.
        identity_name: The identity to sign with.
        context: Context message.

    Usage:
        $ geas seal req
        $ geas seal intent --identity arch-lead
    """
    utils.ensure_geas_root()
    bolt_path = utils.get_active_bolt_path()

    # Load Ledger
    ledger_obj = ledger.LedgerManager.load_lock(bolt_path)
    if not ledger_obj:
        console.print(
            "[bold red]Error:[/bold red] lock.json not found. Is this a valid bolt?"
        )
        raise typer.Exit(code=1)

    # Verify Chain Integrity before appending
    if not ledger.LedgerManager.verify_chain_integrity(ledger_obj):
        console.print(
            "[bold red]CRITICAL:[/bold red] Ledger integrity check failed! The chain is broken."
        )
        raise typer.Exit(code=1)

    # Dispatch Logic
    if target == "intent":
        _seal_intent(bolt_path, ledger_obj, identity_name, context)
    else:
        _seal_artifact(bolt_path, ledger_obj, target, identity_name, context)

    # Save Ledger
    ledger.LedgerManager.save_lock(bolt_path, ledger_obj)

    # ledger_obj.head_hash is Optional[str], but after seal it should be str.
    head_hash_display = ledger_obj.head_hash[:12] if ledger_obj.head_hash else "None"

    console.print(
        Panel(
            f"[bold green]Sealed {target}![/bold green]\nHead Hash: {head_hash_display}...",
            title="GEAS Seal",
        )
    )


def _seal_artifact(
    bolt_path: Path,
    ledger_obj: ledger_schemas.Ledger,
    target: str,
    identity_name: Optional[str],
    context: Optional[str],
) -> None:
    # 1. Map Target to File and Action
    mapping = {
        "req": ("01_request.md", ledger_schemas.LedgerAction.SEAL_REQ),
        "specs": ("02_specs.md", ledger_schemas.LedgerAction.SEAL_SPECS),
        "plan": ("03_plan.md", ledger_schemas.LedgerAction.SEAL_PLAN),
        "mrp": ("mrp/summary.md", ledger_schemas.LedgerAction.SEAL_MRP),
    }

    if target not in mapping:
        console.print(
            f"[bold red]Error:[/bold red] Invalid target '{target}'. Use: req, specs, plan, mrp, intent"
        )
        raise typer.Exit(code=1)

    # Mypy doesn't infer tuple unpacking from dict union safely enough here?
    target_info = mapping[target]
    filename, action = target_info
    file_path = bolt_path / filename

    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {filename}")
        raise typer.Exit(code=1)

    # 2. Hash Content
    file_hash = hashing.file_sha256(file_path)

    # 3. Handle Identity (Optional)
    event_identity = None
    if identity_name:
        event_identity = _create_event_signature(identity_name, action, file_hash)

    # 4. Create Event
    payload = {
        "target": target,
        "file": filename,
        "hash": file_hash,
        "context": context or "",
    }

    event = ledger_schemas.LedgerEvent(
        sequence=0,  # Will be set by append_event
        timestamp=datetime.utcnow(),
        action=action,
        payload=payload,
        identity=event_identity,
        event_hash="",  # Will be set by append_event
    )

    ledger.LedgerManager.append_event(ledger_obj, event)


def _seal_intent(
    bolt_path: Path,
    ledger_obj: ledger_schemas.Ledger,
    identity_name: Optional[str],
    context: Optional[str],
) -> None:
    # 1. Validation: Identity Required
    if not identity_name:
        console.print(
            "[bold red]Error:[/bold red] --identity is required for sealing intent."
        )
        raise typer.Exit(code=1)

    # 2. Validation: Files Exist
    # TODO(Phase 5): Read required files from workflow configuration (workflow.yaml)
    required_files = ["01_request.md", "02_specs.md", "03_plan.md"]
    file_hashes = {}

    for filename in required_files:
        path = bolt_path / filename
        if not path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Required document '{filename}' not found."
            )
            raise typer.Exit(code=1)
        file_hashes[filename] = hashing.file_sha256(path)

    # 3. Create Payload for Signing
    # We sign the hashes of the documents
    payload = {"action": "SEAL_INTENT", "hashes": file_hashes, "context": context or ""}

    # 4. Sign
    event_identity = _create_event_signature_from_payload(identity_name, payload)

    # 5. Create Event
    event = ledger_schemas.LedgerEvent(
        sequence=0,
        timestamp=datetime.utcnow(),
        action=ledger_schemas.LedgerAction.SEAL_INTENT,
        payload=payload,
        identity=event_identity,
        event_hash="",
    )

    ledger.LedgerManager.append_event(ledger_obj, event)


def _create_event_signature(
    identity_name: str, action: str, content_hash: str
) -> ledger_schemas.EventIdentity:
    # Simple signature on action + hash
    data_to_sign = {"action": action, "hash": content_hash}
    return _create_event_signature_from_payload(identity_name, data_to_sign)


def _create_event_signature_from_payload(
    identity_name: str, payload: Dict[str, Any]
) -> ledger_schemas.EventIdentity:
    try:
        # Load Private Key
        # KeyManager.load_private_key returns `object`, but we know it's Ed25519PrivateKey
        private_key_obj = identity.KeyManager.load_private_key(identity_name)
        if not isinstance(private_key_obj, ed25519.Ed25519PrivateKey):
            raise TypeError("Loaded key is not an Ed25519PrivateKey")

        private_key: ed25519.Ed25519PrivateKey = private_key_obj

        # Load Public Key from Identity Store (to ensure it matches name)
        # Actually, KeyManager.load_private_key gives us the keypair object.
        # But we also need the public key string for the EventIdentity model.
        # We should look up the identity in identities.yaml to get the stored pub key
        # to ensure consistency.

        id_manager = identity.IdentityManager()
        id_store = id_manager.load()
        stored_identity = id_store.get_by_name(identity_name)

        if not stored_identity:
            console.print(
                f"[bold red]Error:[/bold red] Identity '{identity_name}' not found in registry."
            )
            raise typer.Exit(code=1)

        # Canonicalize and Sign
        canonical_bytes = crypto.canonicalize_json(payload)
        signature = crypto.sign(private_key, canonical_bytes)

        return ledger_schemas.EventIdentity(
            signer_id=identity_name,
            public_key=stored_identity.active_key,
            signature=signature,
        )

    except identity.KeyNotFoundError:
        console.print(
            f"[bold red]Error:[/bold red] Private key for '{identity_name}' not found."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Signing failed: {e}")
        raise typer.Exit(code=1)
