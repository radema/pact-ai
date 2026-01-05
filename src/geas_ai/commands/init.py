import os
import typer
from rich.console import Console
from rich.panel import Panel
from ruamel.yaml import YAML
from geas_ai.core import content
from geas_ai.core.workflow import WorkflowManager

console = Console()


def init() -> None:
    """Initialize the GEAS governance layer in the current directory.

    Creates the .geas/ directory structure and default configuration files.
    This includes config/agents.yaml, config/models.yaml, and GEAS_MANIFESTO.md.

    Usage:
        $ geas init
    """
    base_dir = ".geas"

    # 1. Check Pre-condition
    if os.path.exists(base_dir):
        console.print(
            Panel(
                "[bold red]Error:[/bold red] GEAS is already initialized in this directory.",
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

        with open(os.path.join(base_dir, "config", "identities.yaml"), "w") as f:
            f.write(content.DEFAULT_IDENTITIES_YAML)

        # 4. Create Default Workflow
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        workflow_path = os.path.join(base_dir, "config", "workflow.yaml")

        # Convert Pydantic model to dict, handling enums if necessary (mode='json')
        # However, we want clean YAML.
        workflow_data = WorkflowManager.DEFAULT_WORKFLOW.model_dump(
            mode="json", exclude_none=True
        )

        with open(workflow_path, "w") as f:
            yaml.dump(workflow_data, f)

        # 5. Create Manifesto
        with open("GEAS_MANIFESTO.md", "w") as f:
            f.write(content.MANIFESTO_CONTENT)

        # 6. Success Message
        console.print(
            Panel(
                f"[bold green]Success![/bold green] GEAS initialized at [blue]{os.path.abspath(base_dir)}[/blue]\n\nCreated:\n- .geas/config/agents.yaml\n- .geas/config/models.yaml\n- .geas/config/identities.yaml\n- .geas/config/workflow.yaml\n- GEAS_MANIFESTO.md",
                title="GEAS Protocol",
            )
        )

    except Exception as e:
        console.print(
            f"[bold red]An error occurred during initialization:[/bold red] {e}"
        )
        raise typer.Exit(code=1)
