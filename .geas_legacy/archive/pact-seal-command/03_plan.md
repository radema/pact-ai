# Implementation Plan: PACT Seal Command

**Feature:** `pact seal`
**Role:** Architect
**Status:** APPROVED

## 1. Architectural Strategy

We will add a new command module `src/pact_cli/commands/seal.py`.
This module will handle hashing, file I/O for `approved.lock`, and the subcommand structure (`seal` as a command group or just a single command with arguments).
Since `status` and `verify` are requested as sub-commands of `seal` (or related), it's best to structure `seal` as a Typer callback/group, or keep it flat if simple.
**Decision:** Flat structure `pact seal <target>` is simplest for the main action. `pact seal status` and `pact seal verify` can be separate commands or subcommands. Typer supports nesting:
`pact seal [specs|plan|mrp]`
`pact seal status` -> Conflict with target argument?
**Better Design:** `pact seal` is the main command group. `pact seal lock <target>` (default)?
Actually, `pact seal` (verb) is the main action.
Let's make `seal` a Typer App.

* `pact seal specs`
* `pact seal plan`
* `pact seal mrp`
* `pact seal status`
* `pact seal verify`

**Wait**, the Spec said: `pact seal <target>`.
Typer doesn't easily mix "positional argument" with "subcommands" on the same level.
**Plan B:**
`pact seal <target>` where target is an Enum [specs, plan, mrp].
`pact status`? No, specific to seal.
Let's stick to the spec: `pact seal <target>` is the command.
But then `pact seal status` would mean `target="status"`. We can handle this in the logic or explicit subcommands.
**Refined Strategy:** Implement `seal` as a subcommand group.

* `pact seal <target>` (via a callback? No, that's complex).
Let's use Typer's explicit subcommands:

1. `pact seal <artifact_name>` (Main command? No).
Let's implement `pact seal` as a **Typer Application**.

* Command `hash <artifact>` (internal logic)
* Command `specs` alias?

**Pragmatic Approach:**
One command `seal(target: str)`.
If `target` is "status", run status logic.
If `target` is "verify", run verify logic.
Else if target in [specs, plan, mrp], run lock logic.
Else fail.

This keeps the CLI flat: `pact seal specs`, `pact seal status`.

## 2. File Structure Changes

```
src/pact_cli/
├── commands/
│   └── seal.py          # Logic for hashing and locking
├── utils.py             # Add hashing helper
```

## 3. Detailed Implementation Steps

### Step 3.1: Hashing Utility (`src/pact_cli/utils.py`)

* Add function `compute_sha256(file_path: Path) -> str`.
  * Read binary? Yes, to be safe. But specs mentioned "normalization" for CRLF.
  * **Decision:** Read as text, `.strip()`, encode to 'utf-8'. This avoids trailing newline differences between editors.

### Step 3.2: Context Utility (`src/pact_cli/utils.py`)

* Add function `get_active_bolt_path() -> Path`.
  * Reads `.pacts/active_context.md`.
  * Parses "**Path:** (.*)".
  * Validates path exists. Returns Path object.

### Step 3.3: Seal Logic (`src/pact_cli/commands/seal.py`)

* **Function**: `seal(target: str)`
* **Target handling**:
    1. **If `status`**: Read `approved.lock` (YAML) and print Table (Artifact, Hash, Sealed At).
    2. **If `verify`**: Iterate known keys in `approved.lock`. Re-hash files. Print PASS/FAIL in a table.
    3. **If `specs`|`plan`|`mrp`**:
        * Map target to filename (`02_specs.md`, etc).
        * `utils.compute_sha256(file)`.
        * Load `approved.lock` (if exists) else empty dict.
        * Update dict with `hash` and `timestamp`.
        * Write `approved.lock` (YAML).
        * Print "Sealed {target}".

### Step 3.4: Wire Main (`src/pact_cli/main.py`)

* Import `seal.seal`.
* `app.command()(seal)`

## 4. Verification Plan (QA)

1. **Seal Specs**: `pact seal specs` -> `approved.lock` created.
2. **Seal Plan**: `pact seal plan` -> `approved.lock` updated.
3. **Status**: `pact seal status` -> Shows both.
4. **Verify Pass**: `pact seal verify` -> All Green.
5. **Verify Fail**: Modify `02_specs.md`. `pact seal verify` -> Fail Red.
 Change
