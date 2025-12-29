import typer
from pact_ai.commands.init import init
from pact_ai.commands import seal
from pact_ai.commands import status
from pact_ai.commands import verify
from pact_ai.commands import lifecycle
from pact_ai.commands import agents

app = typer.Typer(
    name="pact",
    help="Protocol for Agent Control & Trust (PACT) - CLI Tool",
    add_completion=False,
)

# Register commands
app.command(name="init")(init)
app.command(name="new")(lifecycle.new)
app.command(name="seal")(seal.seal)
app.command(name="status")(status.status)
app.command(name="verify")(verify.verify)
app.command(name="checkout")(lifecycle.checkout)
app.command(name="delete")(lifecycle.delete)
app.command(name="archive")(lifecycle.archive)
app.command(name="agents")(agents.agents)


@app.command()  # type: ignore[misc]
def version() -> None:
    """Show the currently installed PACT version.

    Usage:
        $ pact version
    """
    print("0.1.0")


def main() -> None:
    """Entry point for the PACT CLI application."""
    app()


if __name__ == "__main__":
    # Debug: print commands
    # print("Registered commands:", [c.name for c in app.registered_commands])
    app()
