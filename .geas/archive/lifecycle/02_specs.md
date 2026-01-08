# Specifications: Lifecycle Management (Phase 5)

**Status:** APPROVED
**Source:** [01_request.md](./01_request.md)
**Prerequisites:** Phase 4 (Verification Engine)

## 1. Overview

The Lifecycle Management bolt (Phase 5) professionalizes how GEAS manages "Bolts" (units of work). It transitions the system from a loose collection of folders + a markdown file (`active_context.md`) to a structured, state-managed system driven by a machine-readable ledger (`state.json`).

It also introduces the `Bolt` class abstraction to encapsulate bolt logic, moving away from scattered procedural utility functions.

## 2. Goals

1. **Strict State Management**: Replace `active_context.md` with `.geas/state.json`.
2. **Object-Oriented Core**: encapsulated `Bolt` logic in `src/geas_ai/bolt.py`.
3. **Enhanced Lifecycle Commands**:
    * `geas new`: Creates bolt + updates state.
    * `geas checkout`: Switches state.
    * `geas list`: Lists bolts with fast status lookup.
    * `geas archive`: Verifies integrity before moving to archive.
    * `geas delete`: Safe deletion with state cleanup.
4. **Backward Compatibility**: Deprecate `active_context.md` but ensure agents can still function (likely by relying on standard paths or implicit context).

## 3. Data Structures

### 3.1. State File (`.geas/state.json`)

This file replaces `.geas/active_context.md` as the single source of truth for the repository's active state.

```json
{
  "version": "1.0",
  "active_bolt": "feature-login",
  "last_updated": "2026-01-05T10:00:00Z",
  "bolts": {
    "feature-login": {
      "status": "active",
      "created_at": "2026-01-01T09:00:00Z",
      "path": "bolts/feature-login"
    },
    "bugfix-auth": {
      "status": "draft",
      "created_at": "2026-01-02T14:00:00Z",
      "path": "bolts/bugfix-auth"
    }
  }
}
```

* **active_bolt**: Name of the currently active bolt (or null).
* **bolts**: Dictionary of known bolts for fast lookup/listing.

### 3.2. Bolt Statuses

* `draft`: Created, no intent sealed yet.
* `active`: Intent sealed, work in progress.
* `proved`: MRP sealed.
* `verified`: `geas verify` passed.
* `archived`: Moved to `.geas/archive/`.

## 4. Architecture & Components

### 4.1. The `Bolt` Class (`src/geas_ai/bolt.py`)

A new core abstraction to handle efficient bolt operations.

```python
class Bolt:
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    @classmethod
    def load(cls, name: str) -> "Bolt": ...

    @classmethod
    def current(cls) -> "Bolt": ...  # Reads state.json

    def exists(self) -> bool: ...
    def create(self) -> None: ...
    def archive(self) -> None: ...
    def delete(self) -> None: ...
    def verify_integrity(self) -> bool: ...
```

### 4.2. State Manager (`src/geas_ai/state.py`)

Handles reading/writing `state.json`.

```python
class StateManager:
    def get_state(self) -> dict: ...
    def set_active_bolt(self, name: str) -> None: ...
    def register_bolt(self, name: str, status: str = "draft") -> None: ...
    def update_bolt_status(self, name: str, status: str) -> None: ...
    def remove_bolt(self, name: str) -> None: ...
```

## 5. Command Specifications

### 5.1. `geas new <name>`

* **Pre-conditions**: Name matches slug regex.
* **Action**:
    1. Create `.geas/bolts/<name>/`.
    2. Init `lock.json` (genesis).
    3. Create key files (`01_request.md`).
    4. Update `state.json`: set as `active_bolt`, add to `bolts` list with status `draft`.
* **Output**: Success message with path.

### 5.2. `geas checkout <name>`

* **Pre-conditions**: Bolt must exist in `bolts` folder.
* **Action**: Update `active_bolt` in `state.json`.
* **Output**: "Switched context to <name>".

### 5.3. `geas list`

* **Action**: Read `state.json`.
* **Output**: Table with columns:
  * Name
  * Status (e.g., active, draft)
  * Created At
  * Last Updated

### 5.4. `geas archive <name>`

* **Pre-conditions**: Bolt exists.
* **Verification**:
  * Run `Bolt.verify_integrity()`.
  * If valid: Proceed.
  * If invalid/warning: **Prompt User** ("Verification failed/warned. Force archive? [y/N]").
* **Action**:
    1. Move folder to `.geas/archive/<name>`.
    2. Update `state.json`: remove from `bolts` list or mark as `archived` (if we want to list archived bolts, usually we just remove from active list or have a separate section. Decision: **Remove from main active list**, maybe strictly file-system move implies archival).
    3. *Refinement*: Let's keep it simple. `state.json` tracks *active* bolts. Archived ones are removed from `state.json` or marked `archived`.
  * *Decision*: Mark as `archived` in `state.json` so `geas list --all` can find it, OR remove it.
  * *System Rule*: Archive folder is separate. Let's **update status to 'archived'** in state.json so we verify it doesn't reappear as a ghost.
* **Output**: Success message.

### 5.5. `geas delete <name>`

* **Pre-conditions**: Bolt exists.
* **Action**:
    1. Prompt confirmation (unless `--force`).
    2. Delete directory.
    3. Remove from `state.json`.
    4. If it was `active_bolt`, set `active_bolt` to null.

### 5.6. Deprecations

* **`active_context.md`**: The system will no longer read/write this file.
* The `get_active_bolt_path()` utility in `utils.py` must be updated to read `state.json`.

## 6. Implementation Plan

See `03_plan.md` (to be created).
