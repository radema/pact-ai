import typer
from geas_ai.commands.init import init
from geas_ai.commands import seal
from geas_ai.commands import status
from geas_ai.commands import verify
from geas_ai.commands import approve
from geas_ai.commands import lifecycle
from geas_ai.commands import agents
from geas_ai.commands import identity
from geas_ai.commands import prove

app = typer.Typer(
    name="geas",
    help="Governance Enforcement for Agentic Systems (GEAS) - CLI Tool",
    add_completion=False,
)


def version() -> None:
    """Show the currently installed GEAS version.

    Usage:
        $ geas version
    """
    print("0.1.3")


# Register commands
app.command(name="init")(init)
app.command(name="new")(lifecycle.new)
app.command(name="seal")(seal.seal)
app.command(name="status")(status.status)
app.command(name="verify")(verify.verify)
app.command(name="approve")(approve.approve)
app.command(name="prove")(prove.prove)
app.command(name="checkout")(lifecycle.checkout)
app.command(name="delete")(lifecycle.delete)
app.command(name="archive")(lifecycle.archive)
app.command(name="list")(lifecycle.list_bolts)
app.command(name="agents")(agents.agents)
app.command(name="version")(version)
app.add_typer(identity.app, name="identity")


def main() -> None:
    """Entry point for the PACT CLI application."""
    app()


if __name__ == "__main__":
    app()
