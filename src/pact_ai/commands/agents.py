import yaml
import typer
from rich.table import Table
from pact_ai import utils


def agents() -> None:
    """List the currently active agents configuration."""
    utils.ensure_pact_root()

    # Read from global .pacts/config/agents.yaml
    config_path = utils.get_pact_root() / "config/agents.yaml"

    if not config_path.exists():
        utils.console.print(
            f"[bold red]Error:[/bold red] Agent configuration not found at {config_path}"
        )
        raise typer.Exit(code=1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        utils.console.print(
            f"[bold red]Error:[/bold red] Failed to parse agents.yaml: {e}"
        )
        raise typer.Exit(code=1)

    if not data or "agents" not in data:
        utils.console.print(
            "[bold yellow]Warning:[/bold yellow] No agents defined in agents.yaml"
        )
        return

    table = Table(title="PACT Agents Roster (Global)")
    table.add_column("Agent Name", style="cyan", no_wrap=True)
    table.add_column("Role", style="magenta")
    table.add_column("Goal", style="green")

    # Sort agents for consistent display
    for agent_name, agent_info in sorted(data["agents"].items()):
        role = agent_info.get("role", "N/A")
        goal = agent_info.get("goal", "N/A")
        table.add_row(agent_name, role, goal)

    utils.console.print(table)
