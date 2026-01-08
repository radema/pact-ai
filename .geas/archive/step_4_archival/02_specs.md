# Technical Specifications: Verification Engine

**Feature:** Verification & Approval
**Bolt:** step_4_archival
**Status:** DRAFT

## 1. Overview

The Verification Engine is the "trust but verify" component of GEAS. It reads the local `lock.json` ledger and validates the cryptographic chain of custody. It ensures that no code is merged unless it strictly adheres to the governance policy defined in `workflow.yaml`.

This phase includes the implementation of the **Workflow Configuration** module (`schemas/workflow.py`) and the `geas verify` command. It also introduces the `geas approve` command, allowing human sign-off on the sealed MRP.

## 2. Architecture

### 2.1 Directory Structure

```
src/geas_ai/
├── core/
│   ├── verification.py      # Core validation logic
│   └── approval.py          # Approval event construction
├── schemas/
│   └── verification.py      # Pydantic models for results
├── commands/
│   ├── verify.py            # CLI: geas verify
│   ├── status.py            # CLI: geas status
│   └── approve.py           # CLI: geas approve
```

### 2.2 Dependencies

- `cryptography`: For signature verification.
- `pydantic`: For schema validation and result models.
- `rich`: For formatting verification reports.
- `typer`: For CLI commands.

## 3. Data Models

### 3.1 Verification Results (`schemas/verification.py`)

(Previous VerificationResult models...)

### 3.2 Workflow Configuration (`schemas/workflow.py`)

We need to define the schema for the governance policy.

```python
from typing import List, Optional
from pydantic import BaseModel

class WorkflowStage(BaseModel):
    id: str
    action: str  # e.g., "SEAL_INTENT", "SEAL_MRP"
    required_role: str  # "human", "agent"
    prerequisite: Optional[str] = None
    description: Optional[str] = None

class IntentConfig(BaseModel):
    required: List[str]
    optional: List[str] = []

class WorkflowConfig(BaseModel):
    name: str
    version: str
    intent_documents: IntentConfig
    stages: List[WorkflowStage]
    test_command: str = "pytest"
    test_timeout: int = 300
```

```python
from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel

class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"

class ViolationCode(str, Enum):
    CHAIN_BROKEN = "CHAIN_BROKEN"
    EVENT_TAMPERED = "EVENT_TAMPERED"
    HEAD_MISMATCH = "HEAD_MISMATCH"
    IDENTITY_NOT_FOUND = "IDENTITY_NOT_FOUND"
    KEY_MISMATCH = "KEY_MISMATCH"
    KEY_REVOKED = "KEY_REVOKED"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    STAGE_MISSING = "STAGE_MISSING"
    ROLE_VIOLATION = "ROLE_VIOLATION"
    PREREQUISITE_MISSING = "PREREQUISITE_MISSING"
    FILE_MODIFIED = "FILE_MODIFIED"
    FILE_MISSING = "FILE_MISSING"

class Violation(BaseModel):
    code: ViolationCode
    message: str
    event_sequence: Optional[int] = None
    details: Optional[dict] = None

class ValidationResult(BaseModel):
    valid: bool
    violations: List[Violation]

class ChainValidationResult(ValidationResult):
    event_count: int

class SignatureValidationResult(ValidationResult):
    verified_count: int

class WorkflowValidationResult(ValidationResult):
    completed_stages: List[str]
    missing_stages: List[str]

class ContentValidationResult(ValidationResult):
    checked_files: int
    modified_files: int
```

## 4. Core Logic (`core/verification.py`)

### 4.1 Chain Integrity

```python
def validate_chain_integrity(ledger: Ledger) -> ChainValidationResult:
    # 1. Iterate events
    # 2. Check prev_hash matches previous event_hash
    # 3. Recalculate event_hash (excluding itself)
    # 4. Check head_hash matches last event
```

### 4.2 Signature Verification

```python
def validate_signatures(ledger: Ledger, identity_store: IdentityStore) -> SignatureValidationResult:
    # 1. Iterate events
    # 2. Get signer_id
    # 3. Load public key from store (check history + active)
    # 4. Check revocation list
    # 5. Verify Ed25519 signature on canonical payload
```

### 4.3 Workflow Compliance

```python
def validate_workflow_compliance(ledger: Ledger, workflow: WorkflowConfig, identity_store: IdentityStore) -> WorkflowValidationResult:
    # 1. Extract completed actions from ledger
    # 2. Map actions to workflow stages
    # 3. Check prerequisites
    # 4. Check signer role (human vs agent)
```

### 4.4 Refactoring of Existing Functions

The implementation of Phase 4 requires modifications to existing modules to support the new features.

#### 4.4.1 `src/geas_ai/schemas/ledger.py`

- **Update `LedgerAction` Enum**: Add `APPROVE` member.
- **Update `LedgerEvent`**: Ensure `payload` can support the approval structure (it is currently generic Dict, which is fine, but we might want specific TypedDict for ApprovalPayload).

#### 4.4.2 `src/geas_ai/core/ledger.py`

- **No major refactor expected**, but `LedgerManager` should ensure it strictly validates the schema when loading, to support the new `APPROVE` events.

#### 4.4.3 `src/geas_ai/commands/*.py`

- **Refactor `verify.py`**: Completely rewrite to use `LedgerManager` and `lock.json`. The current implementation supports the legacy `approved.lock` YAML format which is now deprecated.
- **Refactor `status.py`**: Rewrite to read from `lock.json` and display the new Ledger event history.
- **Future Integration**: Future iterations of `seal` and `prove` should ideally use the `workflow` module to determine required files/steps instead of hardcoded lists.

## 5. CLI Commands

### 5.1 `geas verify` (`commands/verify.py`)

**Usage:**

```bash
geas verify [--json] [--content] [--strict]
```

**Logic:**

1. Loads `lock.json`.
2. Runs all validation functions.
3. Aggregates results.
4. Prints rich report (or JSON).
5. Exits with 0 (Pass) or 1 (Fail).

### 5.2 `geas status` (`commands/status.py`)

**Usage:**

```bash
geas status
```

**Logic:**

1. Loads `lock.json`.
2. Prints summary:
   - Bolt Name / Created
   - Status (e.g., "Pending Approval")
   - Event Log (Table: Seq | Time | Action | Actor)
   - Next Steps (based on workflow gap)

### 5.3 `geas approve` (`commands/approve.py`)

**Usage:**

```bash
geas approve --identity <name> [--comment <msg>]
```

**Logic:**

1. Checks if `SEAL_MRP` exists.
2. Checks if already approved (prevents double approval? No, technically allowed but redundant).
3. Verifies `--identity` is a HUMAN.
4. Creates `APPROVE` event.
   - Payload: `{"mrp_hash": <current_head>, "comment": <msg>}`
5. Appends to ledger.

## 6. Testing Strategy

### 6.1 Unit Tests (`tests/core/test_verification.py`)

- **Chain**:
  - `test_valid_chain`: Generated chain passes.
  - `test_broken_link`: Manually modify `prev_hash` -> Detects `CHAIN_BROKEN`.
  - `test_tampered_event`: Modify payload without hash update -> Detects `EVENT_TAMPERED`.
- **Signatures**:
  - `test_valid_sigs`: Signed events pass.
  - `test_invalid_sig`: Bitflip signature -> Detects `INVALID_SIGNATURE`.
  - `test_revoked_key`: Sign with key in `revoked_keys` -> Detects `KEY_REVOKED`.
- **Workflow**:
  - `test_compliance`: Full flow passes.
  - `test_missing_stage`: Intent only -> Reports missing proofs.
  - `test_role_violation`: Agent signs intent -> Detects `ROLE_VIOLATION`.

### 6.2 Integration Tests (`tests/commands/test_verify.py`)

- `test_verify_cli_pass`: Run against a fully valid bolt.
- `test_verify_cli_fail`: Run against corrupted bolt.
- `test_verify_json`: Verify JSON output structure.
