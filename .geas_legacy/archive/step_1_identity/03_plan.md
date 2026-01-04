# Implementation Plan: Identity & Keyring (Phase 1)

**Status:** PROPOSED
**Source:** [02_specs.md](./02_specs.md)

## 1. Project Setup & Dependencies

Establish the project structure and install necessary dependencies.

- [x] **Initialize Project Dictionary**
  - Ensure `src/geas_ai` and `tests` directories exist.
  - Create `src/geas_ai/__init__.py`.
- [x] **Install Dependencies**
  - Add `cryptography`, `pydantic`, `typer`, `ruamel.yaml`, `rich` to `pyproject.toml` or `requirements.txt`.
  - Install dependencies in the environment.

## 2. Core Implementation

Implement the foundational logic and data structures.

- [ ] **Schemas (`src/geas_ai/schemas/identity.py`)**
  - Define `IdentityRole` enum (`human`, `agent`).
  - Define `Identity` model with validation for `persona`/`model`.
  - Define `IdentityStore` model for managing the collection of identities.
- [ ] **Crypto Utilities (`src/geas_ai/utils/crypto.py`)**
  - Implement `generate_keypair()` -> (private_bytes, public_str).
  - Implement `sign(private_key, payload_bytes)`.
  - Implement `verify(public_key, signature, payload_bytes)`.
  - Implement `load_private_key_from_bytes(bytes)`.
  - Implement `canonicalize_json(dict)`.
- [ ] **Identity Core Logic (`src/geas/core/identity.py`)**
  - Implement `KeyManager` class (or functions) to handle:
    - Key resolution: Env Var (`GEAS_KEY_X`) vs Local File (`~/.geas/keys/X.key`).
    - Loading `identities.yaml`.
    - Saving `identities.yaml`.

## 3. CLI Command Implementation

Build the user interface for interacting with the identity system.

- [ ] **Refactor Init Command (`src/geas_ai/commands/init.py`)**
  - Update `init()` to also create `config/identities.yaml` (empty file).
  - Ensure it preserves existing `agents.yaml`/`models.yaml` logic.
- [ ] **Identity Commands (`src/geas_ai/commands/identity.py`)**
  - Implement `add_identity`:
    - Validate inputs (unique name, role, references).
    - Generate keys using `utils.crypto`.
    - Save private key to `~/.geas/keys`.
    - Update `identities.yaml`.
  - Implement `list_identities`:
    - Read `identities.yaml`.
    - Display table using `rich`.
  - Implement `show_identity`:
    - Find by name.
    - Display details.
  - Implement `revoke_identity` (Basic implementation: mark key as revoked in yaml).
- [ ] **Main CLI Entry Point (`src/geas_ai/main.py`)**
  - Register `identity` command group.

## 4. Testing & Verification

Ensure correctness and reliability.

- [ ] **Unit Tests (`tests/core/test_identity.py`)**
  - Test `crypto` functions (gen, sign, verify, canonicalize).
  - Test `Identity` schema validation.
  - Test `KeyManager` resolution logic (mocking env vars and files).
- [ ] **Integration Tests (`tests/commands/test_cli_identity.py`)**
  - Test `geas init` creates files.
  - Test `geas identity add` flow (file creation + yaml update).
  - Test `geas identity list` output.
  - Test `geas identity show` output.
- [ ] **Manual Verification**
  - Run the commands manually to verify UX.
