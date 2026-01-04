# Technical Specification: The Trinity Lock Protocol

Version: 3.1

---

## Overview

The **Trinity Lock** is the cryptographic engine behind GEAS. It replaces simple file hashing with a multi-layered security model that provides **non-repudiable proof** of who authorized what, and when.

### Design Principles

1. **Repository Native** — Lives entirely in folders; no external database.
2. **Git Independent** — Validates without relying on `.git` history.
3. **Agent-First** — Designed for multi-agent environments.
4. **Workflow Agnostic** — Configurable governance policies.
5. **Cryptographically Secured** — Ed25519 signatures for non-repudiation.

### Why Cryptographic Signing?

Git authorship (`git config user.name`) is trivially spoofable. Anyone with repo access can claim to be any author. GEAS uses Ed25519 signatures to prove:

- **Non-repudiation**: The holder of the private key signed this event.
- **Tamper evidence**: If `lock.json` is manually edited, signatures won't verify.
- **Independent verification**: The chain can be verified without trusting Git history.

---

## The Scope of Locking

The Trinity Lock applies strictly to **Governance Artifacts**. It does **NOT** lock source code files, allowing development to remain fluid.

| Layer | Content | Lock State | Purpose |
|-------|---------|------------|---------|
| **INTENT** | `01_request.md`, `02_specs.md`, `03_plan.md`, custom docs | Immutable | Defines what must be built. Sealed before coding starts. |
| **CODE** | `src/`, `tests/` | **Mutable** | The implementation. Evolves freely during the Bolt lifecycle. |
| **MRP** | `mrp/summary.md`, `mrp/tests.log`, `mrp/manifest.json` | Immutable | The evidence. Sealed after tests pass. |

---

## The Three Pillars

The Trinity Lock is defined by the convergence of three cryptographic proofs:

| Pillar | Concept | Implementation |
|--------|---------|----------------|
| **Identity** | Non-Repudiation | Ed25519 Signatures (SSH format). Every seal must be signed by a registered actor. |
| **Integrity** | Physical State | SHA-256 hashes. A map of file paths to their content hashes. |
| **Audit** | Traceability | Hash Chain. Each event references the hash of the previous event, forming a local ledger. |

---

## Configuration Architecture

GEAS uses three configuration files, **logically coupled by reference**:

```
.geas/config/
├── agents.yaml        # Persona definitions (behavior)
├── models.yaml        # Provider configs (runtime)
└── identities.yaml    # Cryptographic identities (security)
```

### 1. Agents Configuration (`agents.yaml`)

Defines **personas**—the behavioral templates for agents.

```yaml
# .geas/config/agents.yaml

agents:
  spec_writer:
    role: "Senior Product Owner"
    goal: "Transform vague inputs into rigorous, unambiguous functional specifications."
    backstory: |
      You are a veteran Product Owner who adheres to the INVEST mnemonic...

  developer:
    role: "Senior Implementation Specialist"
    goal: "Execute the sealed plan into production-grade, typed, and tested code."
    backstory: |
      You are a code craftsman. You value readability and type safety...

  qa_engineer:
    role: "QA Automation Engineer"
    goal: "Validate compliance with specs and generate the Merge Readiness Pack (MRP)."
    backstory: |
      You trust nothing. You verify that the produced code strictly satisfies...
```

### 2. Models Configuration (`models.yaml`)

Defines **providers**—the LLM backends that power agents.

```yaml
# .geas/config/models.yaml

models:
  gpt4_turbo:
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model_name: "gpt-4-turbo"

  claude_sonnet:
    provider: "anthropic"
    base_url: "https://api.anthropic.com"
    api_key: "${ANTHROPIC_API_KEY}"
    model_name: "claude-sonnet-4-20250514"

  local_llama:
    provider: "ollama"
    base_url: "http://localhost:11434/v1"
    model_name: "llama3:7b"
```

### 3. Identities Configuration (`identities.yaml`)

Defines **cryptographic identities**—the keys used for signing seals.

```yaml
# .geas/config/identities.yaml

identities:
  # Humans
  - name: "arch-lead"
    role: "human"
    active_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... arch-lead@company.com"
    revoked_keys: []

  # Agent instances (references persona + model)
  - name: "claude-developer"
    role: "agent"
    persona: "developer"           # References agents.yaml
    model: "claude_sonnet"         # References models.yaml
    active_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... claude-developer@geas"
    revoked_keys: []

  - name: "gpt-qa"
    role: "agent"
    persona: "qa_engineer"
    model: "gpt4_turbo"
    active_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... gpt-qa@geas"
    revoked_keys: []
```

**Key Resolution Logic:**

1. Check environment variable: `GEAS_KEY_{NAME}` (for CI/agents).
2. Check local keyring: `~/.geas/keys/{name}.key` (for humans).
3. If not found → Abort with "Identity not found" error.

---

### 4. Workflow Configuration (`workflow.yaml`)

Defines the governance policy for the repository.

```yaml
# .geas/config/workflow.yaml

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

---

## Data Structures

### The Lock Ledger (`lock.json`)

Every Bolt folder contains a `lock.json` file. This is the append-only ledger of all governance events.

```json
{
  "version": "3.1",
  "bolt_id": "feature-login",
  "created_at": "2025-01-02T10:00:00Z",
  "head_hash": "sha256:abc123...",
  "events": [
    { /* Event 1: SEAL_INTENT */ },
    { /* Event 2: SEAL_MRP */ },
    { /* Event 3: APPROVE */ }
  ]
}
```

### Event Schema

Each event in the ledger follows this structure:

```json
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

  "prev_hash": "sha256:000000...",

  "identity": {
    "signer_id": "arch-lead",
    "public_key": "ssh-ed25519 AAAAC3...",
    "signature": "base64_signature_of_canonical_payload"
  },

  "event_hash": "sha256:abc123..."
}
```

**Event Types:**

| Action | Layer | Description |
|--------|-------|-------------|
| `SEAL_INTENT` | INTENT | Seals the Intent documents. |
| `SEAL_MRP` | MRP | Seals the Merge Request Package. |
| `APPROVE` | MRP | Human approval of sealed MRP. |

---

### The MRP Manifest (`mrp/manifest.json`)

Generated during `geas prove`. Captures the exact state of source code at proof time.

```json
{
  "generated_at": "2025-01-02T14:30:00Z",
  "bolt_id": "feature-login",
  "scope": ["src/", "tests/"],

  "files": {
    "src/auth/login.py": "sha256:...",
    "src/auth/oauth.py": "sha256:...",
    "tests/test_login.py": "sha256:..."
  },

  "root_hash": "sha256:...",

  "test_result": {
    "passed": true,
    "exit_code": 0,
    "duration_seconds": 12.5
  }
}
```

---

## Algorithms & Procedures

### 1. Sealing Intent (`geas seal intent`)

**Goal:** Freeze the preliminary documents with cryptographic proof.

**Procedure:**

1. **Identify Target Files**: Read `workflow.yaml` to determine which documents are required/optional.
2. **Validate Presence**: Ensure all required Intent documents exist.
3. **Calculate Hashes**: SHA-256 hash of each file's content.
4. **Resolve Identity**: Load the signer's private key (must be `role: human`).
5. **Construct Event**:
   - `action`: `SEAL_INTENT`
   - `payload.files`: Map of filename → hash
   - `prev_hash`: Hash of the last event (or `null` for genesis)
6. **Sign Event**: Sign the canonical JSON of the event payload using Ed25519.
7. **Append to Ledger**: Add the event to `lock.json`.
8. **Update Head Hash**: Set `head_hash` to the new event's hash.

---

### 2. Proving Work (`geas prove`)

**Goal:** Run tests, snapshot code, generate MRP, and seal it.

**Procedure:**

1. **Validate State**: Ensure Intent is already sealed.
2. **Run Tests**: Execute the configured test command. Capture stdout/stderr.
3. **Check Result**: If tests fail, abort with error.
4. **Generate Manifest**:
   - Walk `src/` and `tests/` directories.
   - Respect `.gitignore` rules (use `pathspec` library).
   - Hash each file (SHA-256).
   - Sort keys alphabetically for deterministic output.
   - Calculate Merkle root hash.
5. **Write MRP Artifacts**:
   - `mrp/manifest.json` — The code snapshot.
   - `mrp/tests.log` — Captured test output.
   - `mrp/summary.md` — Human-readable summary.
6. **Seal MRP**:
   - Hash the MRP files.
   - Resolve agent identity.
   - Construct and sign `SEAL_MRP` event.
   - Append to ledger.

---

### 3. Verifying a Bolt (`geas verify`)

**Goal:** Validate the Bolt against the configured workflow.

**Procedure:**

1. **Load Workflow**: Parse `.geas/config/workflow.yaml`.
2. **Load Ledger**: Parse the Bolt's `lock.json`.
3. **Validate Chain Integrity**:
   - For each event, verify `prev_hash` matches the hash of the previous event.
   - For the first event, verify `prev_hash` is `null`.
4. **Validate Signatures**:
   - For each event, resolve the signer's public key from `identities.yaml`.
   - Verify the signature matches the canonical payload.
   - Ensure the key is not in `revoked_keys`.
5. **Validate Workflow Compliance**:
   - Check that all required stages are present.
   - Check that prerequisites are satisfied (e.g., `proof` requires `intent`).
   - Check that role requirements are met (e.g., `intent` sealed by `human`).
6. **Validate Content Integrity** (optional, if files still exist):
   - Re-hash Intent files and compare against sealed hashes.
   - Re-hash MRP files and compare against sealed hashes.
7. **Return Result**: PASS with details, or FAIL with specific violation.

---

## Cryptographic Details

### Key Format

GEAS uses **SSH-format Ed25519 keys** for compatibility with existing tooling.

**Generate a new key:**

```bash
ssh-keygen -t ed25519 -f ~/.geas/keys/my-identity.key -N "" -C "my-identity@geas"
```

**Key storage:**

| Actor Type | Private Key Location | Public Key Location |
|------------|---------------------|---------------------|
| Human | `~/.geas/keys/{name}.key` | `.geas/config/identities.yaml` |
| Agent (CI) | `GEAS_KEY_{NAME}` env var | `.geas/config/identities.yaml` |

### Signature Algorithm

1. **Canonicalize Payload**: Sort JSON keys, no whitespace, UTF-8 encoding.
2. **Sign**: Ed25519 signature of the canonical bytes.
3. **Encode**: Base64-encode the signature for storage.

### Hash Chain

Each event's `event_hash` is calculated as:

```
event_hash = SHA-256(canonical_json(event_without_event_hash))
```

The next event's `prev_hash` must equal the previous event's `event_hash`.

---

## Implementation Roadmap

### Phase 1: Identity & Keyring

**Objective:** `geas init` and `geas identity`

**Deliverables:**

- SSH-format Ed25519 key generation.
- `identities.yaml` schema and parser.
- Key resolution logic (env var → local keyring).
- Sign/verify utility functions.

**Libraries:** `cryptography`, `paramiko` (for SSH key parsing).

---

### Phase 2: Intent Engine

**Objective:** `geas seal intent`

**Deliverables:**

- Workflow configuration parser.
- File hashing with SHA-256.
- Ledger append logic with hash chain.
- Event signing with Ed25519.

**Libraries:** `hashlib`, `pydantic` (schema validation).

---

### Phase 3: Proof Engine (MRP)

**Objective:** `geas prove`

**Deliverables:**

- Test runner integration (`subprocess`).
- Directory walker with `.gitignore` support.
- Manifest generator (deterministic JSON).
- MRP folder generation.
- `SEAL_MRP` event creation with agent signature.

**Libraries:** `pathspec` (gitignore parsing), `subprocess`.

---

### Phase 4: Verification Engine

**Objective:** `geas verify`

**Deliverables:**

- Chain integrity validator.
- Signature verification.
- Workflow compliance checker.
- Content integrity verification.

---

### Phase 5: Lifecycle Management

**Objective:** `geas archive`, `geas delete`

**Deliverables:**

- Bolt archival (move to `.geas/archive/`).
- Bolt deletion (with confirmation).

---

### Phase 6: CI/CD Integration

**Objective:** Enterprise automation

**Deliverables:**

- GitHub Actions workflow templates.
- GitLab CI templates.
- Documentation for key injection in CI.
- PR status checks (block merge without valid MRP).

---

## Technology Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **Cryptography** | `cryptography` | Industry-standard, audited. |
| **SSH Key Parsing** | `paramiko` or `cryptography` | Native SSH format support. |
| **Schema Validation** | `pydantic` | Strict typing, excellent errors. |
| **Gitignore Parsing** | `pathspec` | Correct `.gitignore` semantics. |
| **CLI Framework** | `typer` | Modern, type-hinted CLI. |
| **YAML Parsing** | `ruamel.yaml` | Preserves comments and formatting. |

---

## Appendix: Example Workflows

### Minimal Workflow (Solo Developer)

```yaml
workflow:
  name: "minimal"
  intent_documents:
    required: ["02_specs.md"]
  stages:
    - id: "intent"
      action: "SEAL_INTENT"
      required_role: "human"
    - id: "proof"
      action: "SEAL_MRP"
      required_role: "agent"
      prerequisite: "intent"
```

### Enterprise Workflow (Multi-Agent Team)

```yaml
workflow:
  name: "enterprise"
  intent_documents:
    required: ["01_request.md", "02_specs.md", "03_plan.md"]
    optional: ["04_architecture.md", "05_research.md"]
  stages:
    - id: "request"
      action: "SEAL_INTENT"
      files: ["01_request.md"]
      required_role: "human"
    - id: "specs"
      action: "SEAL_INTENT"
      files: ["02_specs.md", "03_plan.md"]
      required_role: "human"
      prerequisite: "request"
    - id: "proof"
      action: "SEAL_MRP"
      required_role: "agent"
      prerequisite: "specs"
    - id: "review"
      action: "APPROVE"
      required_role: "human"
      prerequisite: "proof"
```

---

## Conclusion

The Trinity Lock Protocol provides a rigorous, flexible, and auditable governance layer for agentic software development. By binding Identity, Integrity, and Audit into a cryptographic chain, GEAS ensures that every piece of generated code can be traced back to its authorized intent—with proof that cannot be forged or repudiated.
