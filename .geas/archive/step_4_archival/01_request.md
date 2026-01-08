# Request: (Phase 4)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 4)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Phase 4)
**Prerequisite:** Phase 3 (Proof Engine)

## Context

The Verification Engine validates a Bolt against the configured workflow policy. It ensures that all governance requirements have been met before code can be merged, providing the final gate in the GEAS governance chain.

Verification checks three aspects of the Trinity Lock:

1. **Chain Integrity**: Each event's `prev_hash` correctly references the previous event.
2. **Signature Validity**: All signatures are valid and made by authorized, non-revoked keys.
3. **Workflow Compliance**: All required stages are present with correct role assignments.

## Goals

Implement the verification engine that validates Bolts against governance policies.

**Primary CLI Commands:**

- `geas verify`: Validate Bolt against configured workflow.
- `geas status`: Display current Bolt state and seal status.

## Requirements

### 1. Chain Integrity Validation

Verify the hash chain of the ledger is intact.

**Algorithm:**

1. Load `lock.json` from the Bolt.
2. For each event in sequence order:
   - If first event: verify `prev_hash` is `null`.
   - Otherwise: verify `prev_hash` equals previous event's `event_hash`.
3. Recalculate each event's `event_hash` and verify it matches stored value.
4. Verify `head_hash` equals the last event's `event_hash`.

**Function Signature:**

```python
def validate_chain_integrity(lock: Lock) -> ChainValidationResult:
    """
    Validate the hash chain integrity of the ledger.

    Args:
        lock: Parsed Lock object from lock.json.

    Returns:
        ChainValidationResult with valid flag and any violations.

    Example:
        >>> result = validate_chain_integrity(lock)
        >>> result.valid
        True
        >>> result.violations
        []
    """
```

**Violation Types:**

| Code | Description |
|------|-------------|
| `CHAIN_BROKEN` | `prev_hash` does not match previous event's hash. |
| `EVENT_TAMPERED` | Recalculated `event_hash` does not match stored value. |
| `HEAD_MISMATCH` | `head_hash` does not match last event's hash. |
| `SEQUENCE_GAP` | Event sequence numbers are not contiguous. |

### 2. Signature Verification

Verify all event signatures are valid.

**Algorithm:**

1. For each event in the ledger:
   - Extract `identity.signer_id` and `identity.public_key`.
   - Look up identity in `identities.yaml`.
   - Verify public key matches the stored `active_key` or is in history.
   - Check public key is NOT in `revoked_keys`.
   - Reconstruct the canonical payload.
   - Verify Ed25519 signature against public key.

**Function Signature:**

```python
def validate_signatures(
    lock: Lock,
    identities: IdentityStore
) -> SignatureValidationResult:
    """
    Validate all event signatures in the ledger.

    Args:
        lock: Parsed Lock object.
        identities: Parsed identity store.

    Returns:
        SignatureValidationResult with valid flag and any violations.

    Example:
        >>> result = validate_signatures(lock, identities)
        >>> result.valid
        True
    """
```

**Violation Types:**

| Code | Description |
|------|-------------|
| `IDENTITY_NOT_FOUND` | Signer ID not found in identities.yaml. |
| `KEY_MISMATCH` | Public key in event does not match identity record. |
| `KEY_REVOKED` | Signing key has been revoked. |
| `INVALID_SIGNATURE` | Ed25519 signature verification failed. |

### 3. Workflow Compliance Validation

Verify the Bolt meets all workflow requirements.

**Algorithm:**

1. Load `workflow.yaml` configuration.
2. Parse the ledger to identify completed stages.
3. For each required stage in workflow:
   - Check a matching event exists (e.g., `SEAL_INTENT` for "intent" stage).
   - Verify the signer has the correct role (human vs agent).
   - Verify prerequisites are satisfied (e.g., "proof" requires "intent").
4. Report missing stages and role violations.

**Function Signature:**

```python
def validate_workflow_compliance(
    lock: Lock,
    workflow: WorkflowConfig,
    identities: IdentityStore
) -> WorkflowValidationResult:
    """
    Validate Bolt against workflow requirements.

    Args:
        lock: Parsed Lock object.
        workflow: Workflow configuration.
        identities: Identity store for role lookup.

    Returns:
        WorkflowValidationResult with valid flag, completed stages, missing stages.

    Example:
        >>> result = validate_workflow_compliance(lock, workflow, identities)
        >>> result.completed_stages
        ["intent", "proof"]
        >>> result.missing_stages
        ["approval"]
    """
```

**Violation Types:**

| Code | Description |
|------|-------------|
| `STAGE_MISSING` | Required stage not found in ledger. |
| `ROLE_VIOLATION` | Stage signed by wrong role (e.g., agent signed intent). |
| `PREREQUISITE_MISSING` | Stage completed before its prerequisite. |

### 4. Content Integrity Verification (Optional)

Re-hash sealed files and compare against stored hashes.

**Algorithm:**

1. For each sealed event (SEAL_INTENT, SEAL_MRP):
   - Extract the file list from `payload.files`.
   - Re-hash each file that still exists.
   - Compare against stored hash.
2. Report any mismatches (file modified after sealing).

**Function Signature:**

```python
def validate_content_integrity(
    lock: Lock,
    bolt_path: Path
) -> ContentValidationResult:
    """
    Verify sealed files have not been modified.

    Args:
        lock: Parsed Lock object.
        bolt_path: Path to the Bolt folder.

    Returns:
        ContentValidationResult with valid flag and any violations.

    Example:
        >>> result = validate_content_integrity(lock, Path(".geas/bolts/feature-login"))
        >>> result.valid
        True
    """
```

**Violation Types:**

| Code | Description |
|------|-------------|
| `FILE_MODIFIED` | File hash differs from sealed value. |
| `FILE_MISSING` | Sealed file no longer exists. |

### 5. CLI Command: `geas verify`

Validate Bolt against the configured workflow.

**Behavior:**

1. **Load Configuration**: Parse workflow.yaml and identities.yaml.
2. **Load Ledger**: Parse the Bolt's lock.json.
3. **Run Validations**:
   - Chain integrity
   - Signature verification
   - Workflow compliance
   - Content integrity (optional, with `--content` flag)
4. **Report Result**: PASS with summary, or FAIL with specific violations.

**Options:**

- `--content`: Also verify sealed file contents still match hashes.
- `--json`: Output results as JSON for CI integration.
- `--strict`: Fail on any warnings (not just errors).

**Example (Pass):**

```bash
$ geas verify
Verifying Bolt: feature-login

Chain Integrity:    ✅ PASS (3 events, chain intact)
Signatures:         ✅ PASS (3 signatures verified)
Workflow:           ✅ PASS (all stages complete)

══════════════════════════════════════════════════════
VERIFICATION PASSED ✅
══════════════════════════════════════════════════════

Completed Stages:
  1. intent   - sealed by 'arch-lead' (human)
  2. proof    - sealed by 'claude-developer' (agent)
  3. approval - signed by 'tech-lead' (human)

This Bolt is ready for merge.
```

**Example (Fail):**

```bash
$ geas verify
Verifying Bolt: feature-login

Chain Integrity:    ✅ PASS (2 events, chain intact)
Signatures:         ❌ FAIL
Workflow:           ⚠️  INCOMPLETE

══════════════════════════════════════════════════════
VERIFICATION FAILED ❌
══════════════════════════════════════════════════════

Errors:
  • [INVALID_SIGNATURE] Event #2: Signature verification failed for 'claude-developer'

Warnings:
  • [STAGE_MISSING] Stage 'approval' not yet completed

This Bolt cannot be merged.
```

**Example (JSON Output for CI):**

```bash
$ geas verify --json
{
  "bolt_id": "feature-login",
  "result": "FAIL",
  "chain_integrity": {"valid": true, "event_count": 2},
  "signatures": {"valid": false, "violations": [...]},
  "workflow": {"valid": false, "completed": ["intent", "proof"], "missing": ["approval"]},
  "errors": [...],
  "warnings": [...]
}
```

### 6. CLI Command: `geas status`

Display current Bolt state and seal status.

**Behavior:**

1. Load the active Bolt's `lock.json`.
2. Display Bolt metadata (name, created, current state).
3. List all events with timestamps and actors.
4. Show next required action based on workflow.

**Example:**

```bash
$ geas status
Bolt: feature-login
Created: 2025-01-02T10:00:00Z
State: PROOF_SEALED

Event History:
  #1  SEAL_INTENT  2025-01-02T12:05:00Z  arch-lead (human)
  #2  SEAL_MRP     2025-01-02T14:30:00Z  claude-developer (agent)

Next Action: Awaiting human approval ('geas approve')
```

### 7. CLI Command: `geas approve` (APPROVE Event)

Human approval of sealed MRP for merge.

**Behavior:**

1. **Validate State**: Ensure MRP is sealed, not yet approved.
2. **Resolve Identity**: Must be a human identity.
3. **Construct APPROVE Event**: Reference the sealed MRP.
4. **Sign and Append**: Add to ledger with human signature.

**Options:**

- `--identity <name>`: Approver identity (required).
- `--comment <string>`: Optional approval comment.

**Example:**

```bash
$ geas approve --identity tech-lead --comment "LGTM, approved for merge"
✓ MRP seal verified (event #2)
✓ Signed approval with identity 'tech-lead'
✓ Event appended to lock.json

Bolt 'feature-login' is now approved for merge.
```

## Deliverables

1. **Verification module** (`src/geas_ai/verification.py`):
   - `validate_chain_integrity()` — Hash chain validation.
   - `validate_signatures()` — Signature verification.
   - `validate_workflow_compliance()` — Workflow policy check.
   - `validate_content_integrity()` — File hash verification.
   - `VerificationResult` aggregate model.

2. **CLI commands** (`src/geas_ai/cli/verify.py`, `src/geas_ai/cli/status.py`):
   - `geas verify` implementation.
   - `geas status` implementation.
   - `geas approve` implementation.

3. **Result models** (`src/geas_ai/schemas/verification.py`):
   - `ChainValidationResult`
   - `SignatureValidationResult`
   - `WorkflowValidationResult`
   - `ContentValidationResult`
   - `Violation` with code, message, event_id, details.

4. **Unit tests** (`tests/test_verification.py`):
   - Chain integrity with valid/broken chains.
   - Signature verification with valid/invalid/revoked keys.
   - Workflow compliance with complete/incomplete Bolts.
   - Content integrity with modified/missing files.

## Technical Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **Cryptography** | `cryptography` | Ed25519 signature verification. |
| **Schema Validation** | `pydantic` | Strict typing, validation. |
| **CLI Framework** | `typer` | Modern, type-hinted CLI. |
| **JSON Output** | `rich` | Beautiful console output with JSON support. |

## Acceptance Criteria

- [ ] Chain integrity correctly detects broken hash chains.
- [ ] Signature verification catches invalid or tampered signatures.
- [ ] Revoked keys are correctly rejected.
- [ ] Workflow compliance identifies missing stages.
- [ ] Role violations are detected (e.g., agent signing intent).
- [ ] Content integrity detects modified files.
- [ ] `geas verify` provides clear pass/fail output.
- [ ] `geas verify --json` outputs valid JSON for CI integration.
- [ ] `geas status` shows human-readable Bolt state.
- [ ] `geas approve` creates valid APPROVE event.
- [ ] All functions have type hints and docstrings.
- [ ] Test coverage > 85%.
