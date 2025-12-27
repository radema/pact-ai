import os
import typer
from rich.console import Console
from rich.panel import Panel
from pact_cli.core import content

console = Console()


def init() -> None:
    """Initialize the PACT governance layer in the current directory.

    Creates the .pacts/ directory structure and default configuration files.
    This includes config/agents.yaml, config/models.yaml, and PACT_MANIFESTO.md.

    Usage:
        $ pact init
    """
    base_dir = ".pacts"

    # 1. Check Pre-condition
    if os.path.exists(base_dir):
        console.print(
            Panel(
                "[bold red]Error:[/bold red] PACT is already initialized in this directory.",
                title="Initialization Failed",
            )
        )
        raise typer.Exit(code=1)

    try:
        # 2. Create Directory Structure
        os.makedirs(os.path.join(base_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "bolts"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "archive"), exist_ok=True)

        # 3. Create Configuration Files
        with open(os.path.join(base_dir, "config", "agents.yaml"), "w") as f:
            f.write(content.DEFAULT_AGENTS_YAML)

        with open(os.path.join(base_dir, "config", "models.yaml"), "w") as f:
            f.write(content.DEFAULT_MODELS_YAML)

        # 4. Create Manifesto
        with open("PACT_MANIFESTO.md", "w") as f:
            f.write(content.MANIFESTO_CONTENT)

        # 5. Success Message
        console.print(
            Panel(
                f"[bold green]Success![/bold green] PACT initialized at [blue]{os.path.abspath(base_dir)}[/blue]\n\nCreated:\n- .pacts/config/agents.yaml\n- .pacts/config/models.yaml\n- PACT_MANIFESTO.md",
                title="PACT Protocol",
            )
        )

    except Exception as e:
        console.print(
            f"[bold red]An error occurred during initialization:[/bold red] {e}"
        )
        raise typer.Exit(code=1)
