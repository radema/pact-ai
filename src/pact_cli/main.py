
import typer
from pact_cli.commands.init import init
from pact_cli.commands import new

app = typer.Typer(
    name="pact",
    help="Protocol for Agent Control & Trust (PACT) - CLI Tool",
    add_completion=False
)

# Register commands
app.command(name="init")(init)
app.command(name="new")(new.new)

@app.command()
def version():
    """Show the version."""
    print("0.1.0")


def main():
    app()

if __name__ == "__main__":
    # Debug: print commands
    # print("Registered commands:", [c.name for c in app.registered_commands]) 
    app()
