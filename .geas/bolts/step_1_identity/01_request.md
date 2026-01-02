# Request: Identity & Keyring (Phase 1)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 1)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Phase 1)

## Context

GEAS requires a robust mechanism to identify actors (Humans and Agents) to ensure **non-repudiation** of actions. This is the "Identity" pillar of the Trinity Lock.

The Identity system must:

1. Establish a public registry of authorized identities (`.geas/config/identities.yaml`).
2. Support SSH-format Ed25519 keys for compatibility with existing tooling.
3. Enable key resolution from environment variables (CI) or local keyring (humans).
4. Integrate with the existing `agents.yaml` (personas) and `models.yaml` (providers) through logical references.

## Goals

Implement the foundational identity management for GEAS, enabling the signing and verification of sealing operations.

**Primary CLI Commands:**

- `geas init`: Initialize the GEAS directory structure and configuration files.
- `geas identity add`: Register a new identity (human or agent) with key generation.
- `geas identity list`: List all registered identities.
- `geas identity show <name>`: Display details for a specific identity.
- `geas identity revoke <name>`: Revoke an identity's active key.

## Requirements

### 1. Identity Store Schema

Create `.geas/config/identities.yaml` as a public registry of authorized actors.

**Schema:**

```yaml
identities:
  # Human identity
  - name: "arch-lead"
    role: "human"
    active_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... arch-lead@company.com"
    revoked_keys: []

  # Agent identity (references agents.yaml and models.yaml)
  - name: "claude-developer"
    role: "agent"
    persona: "developer"           # Must exist in agents.yaml
    model: "claude_sonnet"         # Must exist in models.yaml
    active_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... claude-developer@geas"
    revoked_keys: []
```

**Validation Rules:**

- `name`: Unique identifier across all identities.
- `role`: Must be `"human"` or `"agent"`.
- `active_key`: Must be a valid SSH-format Ed25519 public key.
- `persona` (agents only): Must reference a valid key in `agents.yaml`.
- `model` (agents only): Must reference a valid key in `models.yaml`.
- `revoked_keys`: List of previously valid keys (for audit trail).

### 2. Key Format

Use **SSH-format Ed25519 keys** for compatibility with existing tooling.

**Key Generation Example:**

```bash
ssh-keygen -t ed25519 -f ~/.geas/keys/my-identity.key -N "" -C "my-identity@geas"
```

**Key Storage Locations:**

| Actor Type | Private Key Location | Public Key Location |
|------------|---------------------|---------------------|
| Human | `~/.geas/keys/{name}.key` | `.geas/config/identities.yaml` |
| Agent (CI) | `GEAS_KEY_{NAME}` env var | `.geas/config/identities.yaml` |

### 3. Key Resolution Strategy

Implement a secure mechanism to locate the Private Key for signing.

**Priority Logic:**

1. **Environment Variable:** `GEAS_KEY_{NAME}` (Preferred for CI/Agents)
   - The env var contains the **private key content** (base64 or PEM).
2. **Local Keyring:** `~/.geas/keys/{name}.key` (Preferred for Humans)
   - File contains the private key in OpenSSH format.
3. **Fallback:** Abort with clear error message if identity not found.

### 4. Cryptographic Primitives

Implement the following capabilities:

| Function | Description |
|----------|-------------|
| `generate_keypair(name)` | Generate a new Ed25519 keypair in SSH format. |
| `sign(payload, identity_name)` | Sign a UTF-8 string payload with the identity's private key. Return base64-encoded signature. |
| `verify(payload, signature, public_key)` | Verify a signature against a public key. Return `True`/`False`. |
| `load_private_key(identity_name)` | Load private key using the resolution strategy. |
| `canonicalize_json(obj)` | Serialize JSON deterministically (sorted keys, no whitespace). |

### 5. CLI Commands

#### `geas init`

Initialize GEAS in the current repository.

**Behavior:**

1. Create `.geas/` directory structure.
2. Create default `config/agents.yaml` if not exists (or leave empty).
3. Create default `config/models.yaml` if not exists (or leave empty).
4. Create empty `config/identities.yaml`.
5. Create empty `bolts/` directory.
6. Print success message with next steps.

**Example:**

```bash
$ geas init
✓ Created .geas/config/
✓ Created .geas/bolts/
✓ GEAS initialized. Run 'geas identity add' to register your first identity.
```

#### `geas identity add`

Register a new identity with key generation.

**Options:**

- `--name <string>`: Unique identifier (required).
- `--role <human|agent>`: Actor type (required).
- `--persona <string>`: Reference to agents.yaml (required for agents).
- `--model <string>`: Reference to models.yaml (required for agents).

**Behavior:**

1. Validate that name is unique.
2. For agents, validate `persona` exists in `agents.yaml`.
3. For agents, validate `model` exists in `models.yaml`.
4. Generate Ed25519 keypair in SSH format.
5. Save private key to `~/.geas/keys/{name}.key`.
6. Append public key to `.geas/config/identities.yaml`.
7. Print the public key for CI configuration if agent.

**Example (Human):**

```bash
$ geas identity add --name arch-lead --role human
✓ Generated keypair for 'arch-lead'
✓ Private key saved to ~/.geas/keys/arch-lead.key
✓ Public key added to .geas/config/identities.yaml
```

**Example (Agent):**

```bash
$ geas identity add --name claude-dev --role agent --persona developer --model claude_sonnet
✓ Generated keypair for 'claude-dev'
✓ Private key saved to ~/.geas/keys/claude-dev.key
✓ Public key added to .geas/config/identities.yaml

For CI, set this environment variable:
  export GEAS_KEY_CLAUDE_DEV="$(cat ~/.geas/keys/claude-dev.key | base64)"
```

#### `geas identity list`

List all registered identities.

**Example:**

```bash
$ geas identity list
NAME            ROLE    PERSONA      MODEL
arch-lead       human   -            -
claude-dev      agent   developer    claude_sonnet
gpt-qa          agent   qa_engineer  gpt4_turbo
```

#### `geas identity show <name>`

Display details for a specific identity.

**Example:**

```bash
$ geas identity show claude-dev
Name:       claude-dev
Role:       agent
Persona:    developer
Model:      claude_sonnet
Active Key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... claude-dev@geas
Revoked:    0 keys
```

### 6. Integration with Existing Config Files

The identity system must validate references to:

- **`agents.yaml`**: Ensure `persona` field references a valid agent definition.
- **`models.yaml`**: Ensure `model` field references a valid model definition.

If referenced entries don't exist, the system should:

- Warn during `geas identity add` but allow creation (persona/model may be added later).
- Fail during `geas seal` or `geas prove` if references are invalid.

## Deliverables

1. **`geas init` command**: Sets up `.geas/` directory structure with default config files.
2. **`geas identity` subcommands**: `add`, `list`, `show`, `revoke`.
3. **Identity module** (`src/geas_ai/identity.py`):
   - `generate_keypair()` — SSH-format Ed25519 key generation.
   - `sign()` — Sign payloads with private key.
   - `verify()` — Verify signatures with public key.
   - `load_private_key()` — Key resolution (env var → local keyring).
   - `canonicalize_json()` — Deterministic JSON serialization.
4. **Schema validation** (`src/geas_ai/schemas/identity.py`):
   - Pydantic models for `Identity`, `IdentityStore`.
   - Validation of references to `agents.yaml` and `models.yaml`.
5. **Unit tests** (`tests/test_identity.py`):
   - Key generation and loading.
   - Sign/verify round-trip.
   - Key resolution priority logic.
   - Schema validation.

## Technical Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **Cryptography** | `cryptography` | Industry-standard, audited. |
| **SSH Key Parsing** | `cryptography` or `paramiko` | Native SSH format support. |
| **Schema Validation** | `pydantic` | Strict typing, excellent error messages. |
| **CLI Framework** | `typer` | Modern, type-hinted CLI. |
| **YAML Parsing** | `ruamel.yaml` | Preserves comments and formatting. |

## Acceptance Criteria

- [ ] `geas init` creates the expected directory structure.
- [ ] `geas identity add --role human` generates a valid SSH-format Ed25519 key.
- [ ] `geas identity add --role agent` validates `persona` and `model` references.
- [ ] Private keys are stored securely in `~/.geas/keys/`.
- [ ] Public keys are correctly appended to `identities.yaml`.
- [ ] `sign()` produces a base64-encoded Ed25519 signature.
- [ ] `verify()` correctly validates signatures against public keys.
- [ ] Key resolution correctly prioritizes env var over local keyring.
- [ ] All functions have type hints and docstrings.
- [ ] Test coverage > 85%.
