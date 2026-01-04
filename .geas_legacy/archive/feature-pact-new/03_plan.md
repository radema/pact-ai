# Implementation Plan: PACT CLI `new` Command

**Feature:** `pact new`
**Role:** Architect
**Status:** APPROVED

## 1. Architectural Strategy

We will extend the existing `pact_cli` Typer application.

* **Command Module:** Create `src/pact_cli/commands/new.py`.
* **Utilities:** Introduce `src/pact_cli/utils.py` for shared logic (checking PACT existence, validation).
* **Templates:** Update `src/pact_cli/core/content.py` to include the `01_request.md` and `active_context.md` templates.

**Design Principles:**

* **Validation First:** Validate input (slug format) and state (bolt existence) before side effects.
* **Atomic-ish Operations:** Although file system ops aren't transactional, we will check all pre-conditions first to minimize partial failures.

## 2. File Structure Changes

```
src/pact_cli/
├── commands/
│   └── new.py           # Logic for `pact new`
├── core/
│   └── content.py       # Add REQUEST_TEMPLATE and CONTEXT_TEMPLATE
└── utils.py             # New file for helpers
```

## 3. Detailed Implementation Steps

### Step 3.1: Define Templates (`src/pact_cli/core/content.py`)

Add:

* `REQUEST_TEMPLATE`: A markdown string starting with `# Request: {bolt_name}`.
* `CONTEXT_TEMPLATE`: A markdown template for the active context file.

### Step 3.2: Create Utilities (`src/pact_cli/utils.py`)

Implement:

* `ensure_pact_root() -> Path`: Checks if `.pacts` exists. Raises `typer.Exit(1)` if not. Returns the root path.
* `validate_slug(name: str) -> str`: Checks if the string matches regex `^[a-z0-9-_]+$`. Raises `typer.BadParameter` if invalid.

### Step 3.3: Implement New Logic (`src/pact_cli/commands/new.py`)

* Function: `new(name: str)`
* Logic:
    1. `ensure_pact_root()`
    2. `validate_slug(name)`
    3. Define `bolt_dir = .pacts/bolts/{name}`.
    4. Check `if bolt_dir.exists()`. Raise `typer.Exit(1)` with "Bolt exists".
    5. `os.makedirs(bolt_dir)`
    6. Write `01_request.md` using formatted `REQUEST_TEMPLATE`.
    7. Write `.pacts/active_context.md` using formatted `CONTEXT_TEMPLATE` (with timestamp).
    8. `rich.print` success with the path to the new bolt.

### Step 3.4: Wire Entry Point (`src/pact_cli/main.py`)

* Import `new.new`.
* Register: `app.command(name="new")(new)`.

## 4. Verification Plan (QA)

* **Manual Test:** `pact new my-feature` -> Verify files.
* **Manual Test:** `pact new Invalid Name` -> Verify failure.
* **Manual Test:** `pact new my-feature` (Duplicate) -> Verify error.
