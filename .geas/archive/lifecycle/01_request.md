# Request: Lifecycle Management (Phase 5)

**Status:** DRAFT
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 5)
**Prerequisite:** Phase 4 (Verification Engine)

## Context

Lifecycle Management provides commands for Bolt lifecycle: creation, archival, and deletion.

## Goals

Implement Bolt lifecycle management with proper state tracking.

**Primary CLI Commands:**

- `geas new <name>`: Create a new Bolt workspace.
- `geas checkout <name>`: Switch active Bolt context.
- `geas archive <name>`: Archive a completed Bolt.
- `geas delete <name>`: Permanently delete a Bolt.
- `geas list`: List all Bolts with status.

## Requirements

### 1. Bolt State Tracking

**State File (`.geas/state.json`):**

```json
{
  "version": "3.1",
  "active_bolt": "feature-login",
  "last_updated": "2025-01-02T14:30:00Z"
}
```

**Bolt States:** `draft` → `active` → `proved` → `approved` → `archived`

### 2. `geas new <name>`

Create Bolt workspace with template documents and lock.json.

### 3. `geas checkout <name>`

Switch active Bolt context; update state.json.

### 4. `geas archive <name>`

Move completed Bolt to `.geas/archive/`; requires workflow completion.

### 5. `geas delete <name>`

Remove Bolt with confirmation; optional `--backup` flag.

### 6. `geas list`

List all Bolts with status, state, and timestamps.

## Deliverables

1. **State module** (`src/geas_ai/state.py`)
2. **Bolt module** (`src/geas_ai/bolt.py`)
3. **CLI commands** (`src/geas_ai/cli/lifecycle.py`)
4. **Templates** (`src/geas_ai/templates/`)
5. **Unit tests** (`tests/test_lifecycle.py`)

## Acceptance Criteria

- [ ] `geas new` creates Bolt with templates and lock.json.
- [ ] `geas checkout` switches active Bolt.
- [ ] `geas archive` validates and moves to archive.
- [ ] `geas delete` requires confirmation.
- [ ] State.json maintained correctly.
- [ ] Test coverage > 85%.
