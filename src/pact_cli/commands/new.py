import os
import typer
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from pact_cli import utils
from pact_cli.core import content

console = Console()


def new(name: str) -> None:
    """Start a new PACT Unit of Work (Bolt).

    Creates .pacts/bolts/<name>/ and updates .pacts/active_context.md.

    Args:
        name: The name of the bolt (slugified).

    Usage:
        $ pact new feature-login
    """
    try:
        # 1. Validation
        utils.ensure_pact_root()
        utils.validate_slug(name)

        bolt_dir = os.path.join(".pacts", "bolts", name)

        # 2. Check for existence (Idempotencyish warning)
        if os.path.exists(bolt_dir):
            console.print(f"[bold red]Error:[/bold red] Bolt '{name}' already exists.")
            raise typer.Exit(code=1)

        # 3. Create Structure
        os.makedirs(bolt_dir)

        # 4. Create Request File
        req_path = os.path.join(bolt_dir, "01_request.md")
        with open(req_path, "w") as f:
            f.write(content.REQUEST_TEMPLATE.format(bolt_name=name))

        # 5. Update Context
        ctx_path = os.path.join(".pacts", "active_context.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ctx_path, "w") as f:
            f.write(
                content.CONTEXT_TEMPLATE.format(bolt_name=name, timestamp=timestamp)
            )

        # 6. Success Output
        console.print(
            Panel(
                f"[bold green]Bolt Started![/bold green]\n\nWorkspace: [blue]{bolt_dir}[/blue]\nContext: [yellow]Updated[/yellow]",
                title=f"Bolt: {name}",
            )
        )

    except Exception as e:
        # If it's a Typer Exit, just re-raise
        if isinstance(e, typer.Exit) or isinstance(e, typer.BadParameter):
            raise e
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        raise typer.Exit(code=1)
