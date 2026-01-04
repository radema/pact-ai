# Specs: Intent Engine (Phase 2)

**Status:** APPROVED
**Source:** [01_request.md](./01_request.md)
**Prerequisites:** Phase 1 (Identity & Keyring)

## 1. Architecture & Modules

The Intent Engine introduces the cryptographic ledger and workflow enforcement.

### 1.1 Module Organization

* `src/geas_ai/core/ledger.py`: Handles `lock.json` operations (load, save, append event).
* `src/geas_ai/core/workflow.py`: Handles `workflow.yaml` parsing and validation.
* `src/geas_ai/core/hashing.py`: Dedicated module for SHA-256 and Event hashing (refactoring `utils.py`).
* `src/geas_ai/commands/seal.py`: Updates existing `seal` command to support signatures and ledger updates.
* `src/geas_ai/commands/lifecycle.py`: Updates `new` command to initialize `lock.json`.

## 2. Data Structures

### 2.1 Ledger Models (`src/geas_ai/schemas/ledger.py`)

```python
class EventIdentity(BaseModel):
    signer_id: str
    public_key: str
    signature: str

class LedgerEvent(BaseModel):
    sequence: int
    timestamp: datetime
    action: str  # Enum: SEAL_INTENT, SEAL_MRP, APPROVE
    payload: Dict[str, Any]
    prev_hash: Optional[str]
    identity: EventIdentity
    event_hash: str

class Ledger(BaseModel):
    version: str = "3.1"
    bolt_id: str
    created_at: datetime
    head_hash: Optional[str]
    events: List[LedgerEvent]
```

### 2.2 Workflow Models (`src/geas_ai/schemas/workflow.py`)

```python
class WorkflowStage(BaseModel):
    id: str
    action: str
    required_role: str  # human/agent
    prerequisite: Optional[str] = None
    description: str

class WorkflowConfig(BaseModel):
    name: str
    version: str
    intent_documents: Dict[str, List[str]] # required: [], optional: []
    stages: List[WorkflowStage]
```

## 3. Core Logic & Algorithms

### 3.1 Hash Chain (`calculate_event_hash`)

1. **Input**: Event dictionary/model *excluding* `event_hash`.
2. **Canonicalization**:
    * Sort keys.
    * Remove whitespace (separators `(',', ':')`).
    * Ensure strict UTF-8.
3. **Hashing**: `SHA-256(canonical_bytes)`.
4. **Output**: `sha256:{hexdigest}`.

### 3.2 Event Signing

1. **Input**: Event payload + Identity.
2. **Canonicalization**: Same as above.
3. **Key Lookup**: Use `IdentityManager` (Phase 1) to get private key.
4. **Signing**: `Ed25519(canonical_bytes)`.
5. **Format**: Base64 encoded signature.

### 3.3 Workflow Validation

* `load_workflow()`: Reads `.geas/config/workflow.yaml`.
* Validation: Ensure references to documents exist.

## 4. CLI Specifications

### 4.1 `geas seal intent`

* **Arguments**:
  * `--identity`: (Optional) Name of signer. Defaults to current user or prompts.
  * `--context`: (Optional) Message string.
* **Logic**:
    1. **Pre-check**: active bolt exists? `workflow.yaml` valid?
    2. **Requirement Check**: Are `01_request.md`, `02_specs.md` present?
    3. **Hashing**: Compute SHA-256 for all required + optional docs found.
    4. **Ledger Load**: Read `lock.json`.
    5. **Chain Check**: Verify existing chain integrity (light check).
    6. **Event Construction**: Build `SEAL_INTENT` event.
    7. **Signing**: Interactive sign (if password protected key) or auto-sign.
    8. **Commit**: Append to `lock.json`, update `head_hash`, save.

### 4.2 `geas new` (Update)

* **Logic**:
  * Existing folder creation.
  * **NEW**: Initialize `lock.json` with empty events list and `created_at` timestamp.

## 5. Dependencies

* `pydantic` (Schemas)
* `cryptography` (Signing)
* `ruamel.yaml` (Workflow config)

## 6. Testing Strategy

### 6.1 Unit Tests

* `test_ledger_models`: Validate schema constraints.
* `test_hash_chain`: Verify `prev_hash` linking calculation.
* `test_signature`: Verify event signature validation.

### 6.2 Integration Tests

* `test_seal_intent_flow`:
    1. `geas new test-bolt`
    2. Create dummy `01_request.md`, `02_specs.md`.
    3. `geas seal intent --identity test-user`
    4. Verify `lock.json` content (signatures, hashes).
    5. Verify `head_hash` update.

## 7. Behavioral Specifications (Gherkin)

**Feature:** Seal Intent Documents
  As a Product Owner
  I want to seal the requirement documents
  So that the development scope is fixed and non-repudiable

  **Scenario:** Successful Intent Seal
    Given I have a GEAS bolt named "feature-login"
    And the file "01_request.md" exists
    And the file "02_specs.md" exists
    And I have a valid identity "arch-lead" with a loaded private key
    When I run "geas seal intent --identity arch-lead"
    Then the command should exit with code 0
    And the "approved.lock" file should contain a new event "SEAL_INTENT"
    And the event payload should contain SHA-256 hashes of "01_request.md" and "02_specs.md"
    And the event should be signed by "arch-lead"

  **Scenario:** Prevent Double Sealing
    Given "01_request.md" and "02_specs.md" are already sealed
    When I run "geas seal intent"
    Then the command should fail with "Intent already sealed"

  **Scenario:** Missing Required Document
    Given the file "02_specs.md" is missing
    When I run "geas seal intent"
    Then the command should fail with "Required document '02_specs.md' not found"
