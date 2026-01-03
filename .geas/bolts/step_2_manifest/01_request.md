# Request: Intent Engine (Phase 2)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 2)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Phase 2)
**Prerequisite:** Phase 1 (Identity & Keyring)

## Context

The Intent Engine is responsible for sealing preliminary documents (Intent) with cryptographic proof. This phase implements the core sealing mechanism that binds human-approved requirements to a cryptographic ledger.

In GEAS, **Intent** represents the collection of all preliminary documents that define what must be built:

- `01_request.md` — The business request or user story.
- `02_specs.md` — Functional and technical specifications.
- `03_plan.md` — Implementation plan and architecture notes.
- (Extensible) — Research notes, design decisions, API contracts, etc.

The Intent Engine ensures these documents are **sealed and immutable** before code generation begins, preventing "Agent Drift" by creating a cryptographic record of authorized instructions.

## Goals

Implement the Intent sealing mechanism, including the hash-chain ledger and workflow configuration.

**Primary CLI Command:**

- `geas seal intent`: Seal Intent documents with human signature.

## Requirements

### 1. Workflow Configuration Parser

Implement parsing and validation of `.geas/config/workflow.yaml`.

**Schema:**

```yaml
workflow:
  name: "standard"
  version: "1.0"

  intent_documents:
    required:
      - "01_request.md"
      - "02_specs.md"
    optional:
      - "03_plan.md"
      - "04_architecture.md"

  stages:
    - id: "intent"
      action: "SEAL_INTENT"
      required_role: "human"
      description: "Human must seal all Intent documents before coding begins."

    - id: "proof"
      action: "SEAL_MRP"
      required_role: "agent"
      prerequisite: "intent"
      description: "Agent seals MRP after tests pass."

    - id: "approval"
      action: "APPROVE"
      required_role: "human"
      prerequisite: "proof"
      description: "Human approves the MRP for merge."

  test_command: "pytest -v"
  test_timeout: 300
```

**Validation Rules:**

- `name`: Non-empty string identifier.
- `intent_documents.required`: List of required document filenames.
- `intent_documents.optional`: List of optional document filenames.
- `stages[].id`: Unique identifier across all stages.
- `stages[].action`: Must be one of `SEAL_INTENT`, `SEAL_MRP`, `APPROVE`.
- `stages[].required_role`: Must be `human` or `agent`.
- `stages[].prerequisite`: Must reference a valid stage `id` (optional).

### 2. Lock Ledger Structure

Create and manage the Bolt's `lock.json` file as an append-only cryptographic ledger.

**Initial Structure (on Bolt creation):**

```json
{
  "version": "3.1",
  "bolt_id": "feature-login",
  "created_at": "2025-01-02T10:00:00Z",
  "head_hash": null,
  "events": []
}
```

**Updated Structure (after SEAL_INTENT):**

```json
{
  "version": "3.1",
  "bolt_id": "feature-login",
  "created_at": "2025-01-02T10:00:00Z",
  "head_hash": "sha256:abc123...",
  "events": [
    {
      "sequence": 1,
      "timestamp": "2025-01-02T12:05:00Z",
      "action": "SEAL_INTENT",
      "payload": {
        "files": {
          "01_request.md": "sha256:a1b2c3...",
          "02_specs.md": "sha256:d4e5f6...",
          "03_plan.md": "sha256:g7h8i9..."
        },
        "context": "Approved by Architecture Board"
      },
      "prev_hash": null,
      "identity": {
        "signer_id": "arch-lead",
        "public_key": "ssh-ed25519 AAAAC3...",
        "signature": "base64_signature_of_canonical_payload"
      },
      "event_hash": "sha256:abc123..."
    }
  ]
}
```

### 3. File Hashing

Implement SHA-256 content hashing for Intent documents.

**Function Signature:**

```python
def hash_file(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of file content.

    Args:
        file_path: Path to the file to hash.

    Returns:
        Hash string in format "sha256:hexdigest".

    Raises:
        FileNotFoundError: If file does not exist.

    Example:
        >>> hash_file(Path("01_request.md"))
        "sha256:a1b2c3d4e5f6..."
    """
```

### 4. Hash Chain Algorithm

Implement the hash chain for event linking.

**Algorithm:**

1. For the first event: `prev_hash` = `null`.
2. For subsequent events: `prev_hash` = `event_hash` of the previous event.
3. Calculate `event_hash` as: `SHA-256(canonical_json(event_without_event_hash))`.

**Function Signature:**

```python
def calculate_event_hash(event: dict) -> str:
    """
    Calculate the hash of an event for the hash chain.

    Args:
        event: The event dictionary (without event_hash field).

    Returns:
        Hash string in format "sha256:hexdigest".

    Example:
        >>> event = {"sequence": 1, "action": "SEAL_INTENT", ...}
        >>> calculate_event_hash(event)
        "sha256:abc123..."
    """
```

### 5. Event Signing

Sign events with the actor's private key (using Phase 1 primitives).

**Algorithm:**

1. Construct the event payload (without signature fields).
2. Canonicalize the payload to deterministic JSON.
3. Sign the canonical bytes using Ed25519.
4. Base64-encode the signature.
5. Attach identity block (signer_id, public_key, signature).

### 6. CLI Command: `geas seal intent`

Seal all Intent documents with human signature.

**Behavior:**

1. **Validate State**: Ensure GEAS is initialized and active Bolt exists.
2. **Load Workflow**: Parse `workflow.yaml` to identify required/optional documents.
3. **Validate Documents**: Ensure all required documents exist in the Bolt folder.
4. **Calculate Hashes**: SHA-256 hash of each Intent document.
5. **Resolve Identity**: Load the signer's private key (must be `role: human`).
6. **Construct Event**:
   - `action`: `SEAL_INTENT`
   - `payload.files`: Map of filename → hash
   - `prev_hash`: Hash of the last event (or `null` for genesis)
7. **Sign Event**: Sign canonical JSON of event using Ed25519.
8. **Append to Ledger**: Add event to `lock.json`.
9. **Update Head Hash**: Set `head_hash` to new event's `event_hash`.

**Options:**

- `--identity <name>`: Signer identity (defaults to first human identity).
- `--context <string>`: Optional context message (e.g., "Approved by Architecture Board").

**Example:**

```bash
$ geas seal intent --identity arch-lead --context "Sprint 42 planning complete"
✓ Validated 3 Intent documents
✓ Calculated SHA-256 hashes
✓ Signed with identity 'arch-lead'
✓ Event appended to lock.json

Sealed Files:
  01_request.md  sha256:a1b2c3...
  02_specs.md    sha256:d4e5f6...
  03_plan.md     sha256:g7h8i9...
```

**Error Cases:**

| Condition | Error Message |
|-----------|---------------|
| No active Bolt | "No active Bolt. Run 'geas new <name>' first." |
| Missing required document | "Required document '02_specs.md' not found." |
| Identity not found | "Identity 'arch-lead' not found in identities.yaml." |
| Identity is not human | "SEAL_INTENT requires human identity. 'claude-dev' is an agent." |
| Intent already sealed | "Intent already sealed. Cannot re-seal." |

### 7. Bolt Creation Enhancement

Enhance `geas new` to initialize `lock.json` with empty events array.

**Current Behavior:**

- Creates Bolt folder with template documents.

**Enhanced Behavior:**

- Creates Bolt folder with template documents.
- Creates `lock.json` with initial structure.

## Deliverables

1. **Workflow module** (`src/geas_ai/workflow.py`):
   - `WorkflowConfig` Pydantic model.
   - `load_workflow()` — Parse and validate `workflow.yaml`.
   - `get_required_documents()` — Return list of required Intent documents.

2. **Ledger module** (`src/geas_ai/ledger.py`):
   - `Lock` Pydantic model for `lock.json`.
   - `Event` Pydantic model for ledger events.
   - `load_lock()` — Parse Bolt's `lock.json`.
   - `save_lock()` — Write `lock.json` (preserving formatting).
   - `append_event()` — Append a new event with hash chain linking.

3. **Hashing module** (`src/geas_ai/hashing.py`):
   - `hash_file()` — SHA-256 file hashing.
   - `hash_files()` — Hash multiple files, return dict.
   - `calculate_event_hash()` — Hash chain event calculation.

4. **CLI command** (`src/geas_ai/cli/seal.py`):
   - `geas seal intent` implementation.

5. **Unit tests** (`tests/test_intent.py`, `tests/test_ledger.py`):
   - Workflow parsing.
   - Hash calculation.
   - Event creation and chaining.
   - Seal command validation.

## Technical Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **Hashing** | `hashlib` | Standard library, no dependencies. |
| **Schema Validation** | `pydantic` | Strict typing, excellent error messages. |
| **YAML Parsing** | `ruamel.yaml` | Preserves comments and formatting. |
| **JSON Serialization** | `json` (stdlib) | Deterministic with `sort_keys=True`. |

## Acceptance Criteria

- [ ] `workflow.yaml` is correctly parsed and validated.
- [ ] `geas new <name>` creates `lock.json` with initial structure.
- [ ] `geas seal intent` calculates correct SHA-256 hashes for all Intent documents.
- [ ] Events are correctly linked with `prev_hash` chain.
- [ ] Events are signed with Ed25519 using the human's private key.
- [ ] `lock.json` is updated with the new event and `head_hash`.
- [ ] Error messages are clear and actionable.
- [ ] Cannot seal Intent twice (idempotency check).
- [ ] All functions have type hints and docstrings.
- [ ] Test coverage > 85%.
