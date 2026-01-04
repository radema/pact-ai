# Implementation Plan: Proof Engine (Phase 3)

**Status:** PROPOSED
**Source:** [02_specs.md](./02_specs.md)
**Prerequisites:** Phase 2 (Intent Engine)

## 1. Project Setup & Dependencies

Add necessary tools for file system traversal.

- [ ] **Dependencies**
  - Add `pathspec` to `pyproject.toml` (via `uv add pathspec`).
  - Verify installation.

## 2. Core Implementation

Implement the components required to generate the MRP.

- [ ] **Test Runner (`src/geas_ai/core/testing.py`)**
  - Implement `run_tests(command, timeout)`.
  - Define `TestResult` class/model.
  - Ensure output capturing works reliably.

- [ ] **File System Walker (`src/geas_ai/core/walker.py`)**
  - Implement `walk_source_files(root, scope)`.
  - Integrate `pathspec` for `.gitignore` support.

- [ ] **Manifest Logic (`src/geas_ai/core/manifest.py`)**
  - Define `Manifest` model.
  - Implement `calculate_merkle_root(file_hashes)`.
  - Implement `generate_manifest(bolt_id, scope, test_result)`.

- [ ] **MRP Generator (`src/geas_ai/core/mrp.py`)**
  - Logic to orchestrate: Walk -> Hash -> Manifest -> Summary -> Write Files.

## 3. CLI Command Implementation

Bind the core logic to the user interface.

- [ ] **Prove Command (`src/geas_ai/commands/prove.py`)**
  - **Logic Flow:**
        1. Validate Pre-conditions.
        2. Run Tests.
        3. Generate `mrp/manifest.json` and `mrp/tests.log`.
        4. Print instruction for next steps (Write Summary -> Seal).
  - Register command in `main.py`.

## 4. Testing & Verification

Ensure the proof engine is robust.

- [ ] **Unit Tests (`tests/core/test_proof_engine.py`)**
  - `test_merkle_root`: Test with known (A, B) pairs.
  - `test_walker`: Mock file system and gitignore to verify filtering.
  - `test_runner`: Mock `subprocess.run` output/error codes.

- [ ] **Integration Tests (`tests/commands/test_prove.py`)**
  - `test_prove_success`: Full flow with passing dummy tests.
  - `test_prove_failure`: Full flow with failing tests (ensure no seal).
  - `test_prove_unsealed_intent`: Ensure early reject.
