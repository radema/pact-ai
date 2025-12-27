# Implementation Plan: PACT CLI Initialization

**Feature:** `pact init`
**Role:** Architect
**Status:** APPROVED

## 1. Architectural Strategy

We will implement a clean, modular CLI architecture using **Typer**. The user has explicitly added it to the dependencies. This will allow for type-safe, decorative command definitions with minimal boilerplate.

**Design Principles:**

* **Separation of Concerns:** Command logic (`init`) is separated from the main entry point logic.
* **Data as Code:** Default templates for YAMLs will be stored in a dedicated `templates` module.
* **Idempotency/Safety:** The file system operations will explicitly check for existence before writing.
* **Typer Pattern:** We will use `typer.Typer()` app instance in `main.py` and register commands from submodules.

## 2. File Structure Changes

We will introduce the following module structure in `src/pact_cli/`:

```
src/pact_cli/
├── __init__.py          # Version exposure
├── main.py              # Typer entry point
├── commands/            # Command implementations
│   ├── __init__.py
│   └── init.py          # Logic for `pact init` (Typer command)
└── core/
    ├── __init__.py
    └── content.py       # Templates for agents.yaml, models.yaml, Manifesto
```

## 3. Detailed Implementation Steps

### Step 3.1: Define Templates (`src/pact_cli/core/content.py`)

Create constant str variables for:

* `DEFAULT_AGENTS_YAML`: Content mirroring the updated `TECHNICAL_SPECS.md` (Senior Roles).
* `DEFAULT_MODELS_YAML`: Content mirroring `TECHNICAL_SPECS.md`.
* `MANIFESTO_CONTENT`: Summary from `WHITE_PAPER.md`.

### Step 3.2: Implement Init Logic (`src/pact_cli/commands/init.py`)

* Define `init_app = typer.Typer()`? No, easier to just define a function and register it.
* Function: `init()` decorated with `@app.command()` (handled in main or imported).
* Logic:
    1. Check `if os.path.exists(".pacts")`. Raise `typer.Exit(code=1)` with message using `rich` console.
    2. `os.makedirs(".pacts/config")`
    3. `os.makedirs(".pacts/bolts")`
    4. `os.makedirs(".pacts/archive")`
    5. Write `agents.yaml` to `.pacts/config/` (using templates).
    6. Write `models.yaml` to `.pacts/config/` (using templates).
    7. Write `PACT_MANIFESTO.md` to root (using templates).
    8. Use `rich.print` to display success table/message.

### Step 3.3: Wire Entry Point (`src/pact_cli/main.py`)

* Initialize `app = typer.Typer(name="pact", help="Protocol for Agent Control & Trust")`.
* Import the `init` command function.
* `app.command()(init)` to register it.
* `if __name__ == "__main__": app()`

## 4. Verification Plan (QA)

* **Manual Test:** Run `pact --help`.
* **Manual Test:** Run `pact init` in a clean folder -> check structure.
* **Manual Test:** Run `pact init` again -> check error message.
