# Implementation Plan - Agent Configuration & Testing

**Status:** PROPOSED
**Bolt:** `feature-agents`
**Specs:** `02_specs.md` (Sealed)

## Architecture Overview

This bolt focuses on enhancing the PACT CLI with agent inspection capabilities and enforcing a strict testing culture through updated default personas. We will introduce a new `pact agents` command and establish a `pytest` foundation.

### Domains Affected

1. **Core Content (`src/pact_cli/core/`)**: Updating the source of truth for agent personas.
2. **CLI Commands (`src/pact_cli/commands/`)**: Adding the read-only `agents` command.
3. **Entry Point (`src/pact_cli/main.py`)**: Registering the new command.
4. **Testing (`tests/`)**: Creating the test suite directory and initial tests.

## Step-by-Step Implementation

### Step 1: Update Default Agent Personas

**User Story:** US 2
**File:** `src/pact_cli/core/content.py`
**Action:**

- Update `DEFAULT_AGENTS_YAML` string constant.
- Replace existing agent definitions with the sealed Reference Configuration from `02_specs.md`.
- Verify that YAML formatting is valid.

### Step 2: Implement `pact agents` Command Logic

**User Story:** US 1
**File:** `src/pact_cli/commands/agents.py` (New File)
**Action:**

- Create a new Typer command function `agents`.
- Logic:
    1. Read from global `.pacts/config/agents.yaml`.
    2. Parse YAML.
    3. Use `rich.table.Table` to display formatted output (Name, Role, Goal).

### Step 3: Register Command in Main CLI

**User Story:** US 1
**File:** `src/pact_cli/main.py`
**Action:**

- Import `agents` command from `src.pact_cli.commands.agents`.
- Add `app.command()(agents.agents)` (or appropriate registration).

### Step 4: Initialize Test Suite

**User Story:** US 3
**File:** `tests/test_agents.py` (New File)
**Action:**

- Create `tests/` directory.
- Create `tests/conftest.py` for shared fixtures (e.g., setting up a dummy `.pacts` folder).
- Implement `test_agents_command`:
  - Test default global config reading.
  - Test active bolt config reading (mocking active context).
  - Test formatting (checking output string).

### Step 5: Verify CI Integration

**User Story:** US 3
**File:** `.github/workflows/ci.yml`
**Action:**

- Review existing `ci.yml`.
- Confirm `uv run pytest` step exists and passes with the new tests.

## Verification Plan

### Automated Tests

- Run `uv run pytest` locally.
- Ensure 100% pass rate for new tests.

### Manual Verification

1. Run `pact agents` in a clean state -> Should show global agents (updated versions).
2. Create a new bolt `pact new test-bolt`.
3. Run `pact checkout test-bolt`.
4. Run `pact agents` -> Should show agents from the new bolt (which copied the defaults).
5. Inspect `src/pact_cli/core/content.py` to ensure typos are gone.
