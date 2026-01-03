# Implementation Plan: Intent Engine (Phase 2)

**Status:** PROPOSED
**Source:** [02_specs.md](./02_specs.md)
**Prerequisites:** Phase 1 (Identity & Keyring)

## 1. Project Setup & Dependencies

Prepare the environment for the new modules.

- [ ] **Dependencies**
  - Ensure `pydantic` and `ruamel.yaml` are available (should be from Phase 1).
  - No new external packages required as per specs.

## 2. Core Implementation

Implement the foundational logic for the cryptographic ledger and workflow engine.

- [ ] **Hashing Logic (`src/geas_ai/core/hashing.py`)**
  - Implement `file_sha256(path)`.
  - Import `canonicalize_json` from `src.geas_ai.utils.crypto` (Do not re-implement).
  - Implement `calculate_event_hash(event_dict)`.
  - *Note: Refactor any file-hashing implementation from `utils.py` to this new module.*

- [ ] **Ledger Models (`src/geas_ai/schemas/ledger.py`)**
  - Define `EventIdentity` model.
  - Define `LedgerEvent` model (using Enums for actions).
  - Define `Ledger` model (Events list, head hash).

- [ ] **Workflow Models (`src/geas_ai/schemas/workflow.py`)**
  - Define `WorkflowStage` and `WorkflowConfig` models.

- [ ] **Ledger Manager (`src/geas_ai/core/ledger.py`)**
  - Implement `load_lock(bolt_path)`.
  - Implement `save_lock(bolt_path, ledger_obj)`.
  - Implement `create_genesis_ledger(bolt_id)`.
  - Implement `append_event(ledger, event)`.

- [ ] **Workflow Manager (`src/geas_ai/core/workflow.py`)**
  - Implement `load_workflow(config_path)`.
  - Implement `validate_workflow(workflow_obj)`.

## 3. CLI Command Implementation

Update and extend the CLI to support the new Intent Engine.

- [ ] **Update `geas new` (`src/geas_ai/commands/lifecycle.py`)**
  - Modify the `new` command to initialize `lock.json` using `ledger.create_genesis_ledger`.

- [ ] **Refactor `geas seal` (`src/geas_ai/commands/seal.py`)**
  - Implement `seal_intent` subcommand (or logic branch).
  - **Logic Flow:**
        1. Validate active bolt & workflow.
        2. Identify required docs from workflow.
        3. Check all docs exist.
        4. Hash all docs.
        5. Verify Identity exists (using Phase 1 IdentityManager).
        6. Construct `SEAL_INTENT` event.
        7. Sign event (IdManager.sign).
        8. Append to Ledger.
        9. Save `lock.json`.
        10. Output success table.

## 4. Testing & Verification

Ensure integrity and correctness.

- [ ] **Unit Tests (`tests/core/test_intent_engine.py`)**
  - Test Canonicalization (strict ordering).
  - Test Hash Chain linking (prev_hash integrity).
  - Test Ledger serialization/deserialization.
  - Test Workflow parsing.

- [ ] **Integration Tests (`tests/commands/test_seal_intent.py`)**
  - `test_seal_intent_happy_path`: Full flow (new -> seal intent).
  - `test_seal_intent_missing_doc`: Ensure failure.
  - `test_seal_intent_double_seal`: Ensure failure.
  - `test_seal_intent_verify_signature`: Manually verify the signature produced in lock.json matches the public key.
