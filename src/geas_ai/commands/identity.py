import os
import typer
from rich.console import Console
from rich.table import Table
from geas_ai.schemas.identity import Identity, IdentityRole
from geas_ai.core.identity import IdentityManager
from pathlib import Path
from geas_ai.utils.crypto import generate_keypair

app = typer.Typer(help="Manage cryptographic identities and keys.")
console = Console()


@app.command("add")
def add_identity(
    name: str = typer.Option(..., "--name", "-n", help="Unique name for the identity."),
    role: str = typer.Option(..., "--role", "-r", help="Role: 'human' or 'agent'."),
    persona: str = typer.Option(
        None, "--persona", "-p", help="Persona (required if role is agent)."
    ),
    model: str = typer.Option(
        None, "--model", "-m", help="Model (required if role is agent)."
    ),
) -> None:
    """
    Create a new identity and generate an Ed25519 keypair.
    """
    try:
        # Validate Role
        if role not in [r.value for r in IdentityRole]:
            console.print(
                f"[bold red]Error:[/bold red] Invalid role '{role}'. Must be 'human' or 'agent'."
            )
            raise typer.Exit(code=1)

        role_enum = IdentityRole(role)

        # Generate Keypair
        private_bytes, public_str = generate_keypair()

        # Save Private Key
        keys_dir = Path(os.path.expanduser("~/.geas/keys"))
        keys_dir.mkdir(parents=True, exist_ok=True)
        key_path = keys_dir / f"{name}.key"

        if key_path.exists():
            console.print(
                f"[bold red]Error:[/bold red] Key file already exists: {key_path}"
            )
            raise typer.Exit(code=1)

        # Write private key (mode 0600)
        # Using os.open to ensure permissions from start
        fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(private_bytes)

        # Create Identity Object
        identity = Identity(
            name=name,
            role=role_enum,
            persona=persona,
            model=model,
            active_key=public_str,
        )

        # Add to Identity Store
        manager = IdentityManager()
        manager.add_identity(identity)

        console.print(f"[bold green]Success![/bold green] Identity '{name}' created.")
        console.print(f"Private key saved to: [blue]{key_path}[/blue]")

        if role_enum == IdentityRole.AGENT:
            # We need to print the env var export for the user
            # Convert private key to base64 for env var
            import base64

            b64_key = base64.b64encode(private_bytes).decode("utf-8")
            env_var = f"GEAS_KEY_{name.upper().replace('-', '_')}"
            console.print(
                "\n[yellow]For Agent usage, set this environment variable:[/yellow]"
            )
            console.print(f'export {env_var}="{b64_key}"')

    except ValueError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        # Clean up key file if it was created
        if "key_path" in locals() and key_path.exists():
            os.remove(key_path)
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if "key_path" in locals() and key_path.exists():
            os.remove(key_path)
        raise typer.Exit(code=1)


@app.command("list")
def list_identities() -> None:
    """
    List all registered identities.
    """
    manager = IdentityManager()
    try:
        store = manager.load()
    except Exception as e:
        console.print(f"[bold red]Error loading identities:[/bold red] {e}")
        raise typer.Exit(code=1)

    table = Table(title="GEAS Identities")
    table.add_column("Name", style="cyan")
    table.add_column("Role", style="magenta")
    table.add_column("Persona", style="green")
    table.add_column("Model", style="blue")
    table.add_column("Active Key (Fingerprint)", style="yellow")

    for i in store.identities:
        # Simple truncation for "fingerprint" like display
        key_display = (
            i.active_key.split()[1][:16] + "..."
            if len(i.active_key.split()) > 1
            else "Invalid"
        )
        table.add_row(
            i.name, i.role.value, i.persona or "-", i.model or "-", key_display
        )

    console.print(table)


@app.command("show")
def show_identity(name: str) -> None:
    """
    Show details of a specific identity.
    """
    manager = IdentityManager()
    try:
        store = manager.load()
    except Exception as e:
        console.print(f"[bold red]Error loading identities:[/bold red] {e}")
        raise typer.Exit(code=1)

    identity = store.get_by_name(name)
    if not identity:
        console.print(f"[bold red]Error:[/bold red] Identity '{name}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]Identity: {identity.name}[/bold cyan]")
    console.print(f"  Role: {identity.role.value}")
    if identity.persona:
        console.print(f"  Persona: {identity.persona}")
    if identity.model:
        console.print(f"  Model: {identity.model}")
    console.print(f"  Created At: {identity.created_at}")
    console.print(f"  Active Key: [yellow]{identity.active_key}[/yellow]")
    if identity.revoked_keys:
        console.print(f"  Revoked Keys ({len(identity.revoked_keys)}):")
        for k in identity.revoked_keys:
            console.print(f"    - [red]{k}[/red]")
    else:
        console.print("  Revoked Keys: None")


@app.command("revoke")
def revoke_identity(
    name: str,
    confirm: bool = typer.Option(
        False, "--yes", "-y", help="Skip confirmation prompt."
    ),
) -> None:
    """
    Revoke the current key for an identity and rotate to a new one.
    """
    manager = IdentityManager()
    try:
        store = manager.load()
    except Exception as e:
        console.print(f"[bold red]Error loading identities:[/bold red] {e}")
        raise typer.Exit(code=1)

    identity = store.get_by_name(name)
    if not identity:
        console.print(f"[bold red]Error:[/bold red] Identity '{name}' not found.")
        raise typer.Exit(code=1)

    if not confirm:
        if not typer.confirm(
            f"Are you sure you want to revoke and rotate the key for '{name}'?"
        ):
            raise typer.Abort()

    try:
        # 1. Archive current key
        old_key = identity.active_key
        identity.revoked_keys.append(old_key)

        # 2. Generate new key
        private_bytes, public_str = generate_keypair()
        identity.active_key = public_str

        # 3. Save new private key
        keys_dir = Path(os.path.expanduser("~/.geas/keys"))
        keys_dir.mkdir(parents=True, exist_ok=True)
        key_path = keys_dir / f"{name}.key"

        # Overwrite existing key file (rotation)
        fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(private_bytes)

        # 4. Save Identity Update
        manager.save(store)

        console.print(f"[bold green]Success![/bold green] Key for '{name}' rotated.")
        console.print(f"New private key saved to: [blue]{key_path}[/blue]")

        if identity.role == IdentityRole.AGENT:
            import base64

            b64_key = base64.b64encode(private_bytes).decode("utf-8")
            env_var = f"GEAS_KEY_{name.upper().replace('-', '_')}"
            console.print(
                "\n[yellow]For Agent usage, UPDATE this environment variable:[/yellow]"
            )
            console.print(f'export {env_var}="{b64_key}"')

    except Exception as e:
        console.print(f"[bold red]Error during revocation:[/bold red] {e}")
        raise typer.Exit(code=1)
