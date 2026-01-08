# Implementation Plan: Lifecycle Management (Phase 5)

**Status:** DRAFT
**Source:** [02_specs.md](./02_specs.md)

## 1. Architecture Refactoring

We will move from a utility-function based approach to a domain-model approach with strict state management.

### 1.1. New Modules

* `src/geas_ai/state.py`: Handles `state.json` persistence and locking.
* `src/geas_ai/bolt.py`: Domain model for a Bolt (encapsulates path, ledger access, status).

### 1.2. State Schema

The `state.json` will be the single source of truth.

* Location: `.geas/state.json`
* Replaces: `.geas/active_context.md`

## 2. Implementation Steps

### Step 1: State Management (`state.py`)

* Implement `StateManager` class.
* Methods: `load()`, `save()`, `get_active()`, `set_active()`, `list_bolts()`.
* Unit Tests: `tests/test_state.py`.

### Step 2: Bolt Domain Model (`bolt.py`)

* Implement `Bolt` class.
* Methods: `create()`, `load()`, `verify()`, `archive()`, `delete()`.
* Integrate `LedgerManager` for internal bolt operations.
* Unit Tests: `tests/test_bolt.py`.

### Step 3: Refactor Utils (`utils.py`)

* Modify `get_active_bolt_path` to read from `StateManager` instead of `active_context.md`.
* Ensure backward compatibility where possible, or clearly break if `active_context.md` is gone. (Decision: We will generate `active_context.md` *inside* `StateManager` for now to keep other agents happy, but read from `state.json`).

### Step 4: CLI Refactoring (`lifecycle.py`)

* Refactor `new` to use `Bolt.create()` and `StateManager`.
* Refactor `checkout` to use `StateManager.set_active()`.
* Refactor `delete` to use `Bolt.delete()`.
* Refactor `archive` to use `Bolt.archive()` and `Bolt.verify()`.
* Implement `list` command using `StateManager.list_bolts()`.

### Step 5: Integration Testing

* Update `tests/test_lifecycle.py` to reflect new architecture.
* Verify `geas list` output format.
* Verify `geas archive` prompts on failure.

## 3. Verification Plan

### 3.1. Manual Verification

* Current `geas verify` logic handles cryptographic sealing. Active `geas archive` needs to call this logic programmatically.

### 3.2. Automated Tests

* `test_state_persistence`: Ensure state survives restarts.
* `test_lifecycle_flow`: New -> Checkout -> Seal -> Archive -> Delete.

## 4. Dependencies

* Existing logic in `commands/verify.py` needs to be accessible as a library function (it is already `run_verify` in `lifecycle.py`, but might need cleanup).
