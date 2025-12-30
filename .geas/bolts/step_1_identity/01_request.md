# Request: Identity & Keyring (Phase 1)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 1)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Step 1)

## Context

GEAS requires a robust mechanism to identify actors (Humans and Agents) to ensure non-repudiation of actions. This is the "Identity" pillar of the Trinity Lock. Steps must be taken to establish a "Keyring" and a public registry of authorized identities.

## Goals

Implement the foundational identity management for GEAS, enabling the signing and verification of operations.
Integrate the identity system with the agents registry. It is important to adopt the most suitable storage medium for the identity system and the agents registry to be scalable to a multi-agents environment.

- **Primary CLI Commands:**
  - `geas init`: Initialize the identity store.
  - `geas identity`: Manage local identities.

## Requirements

### 1. Identity Store

Create a schema for `.geas/config/identities.yaml` to act as a public registry of authorized actors.

**Schema:**

```yaml
identities:
  - name: <string> (unique identifier, e.g., "arch-lead")
    role: "human" | "agent"
    public_key: <string> (Ed25519 public key)
```

### 2. Key Resolution Strategy

Implement a secure mechanism to locate the Private Key for signing.

**Priority Logic:**

1. **Environment Variable:** `GEAS_AGENT_KEY_{NAME}` (Preferred for CI/Agents)
2. **Local Keyring:** `~/.geas/keys/{name}.key` (Preferred for Humans)
3. **Fallback:** Abort if identity not found.

**Libraries:**

- `python-dotenv` for environment variables.
- `cryptography.hazmat` for loading keys.

### 3. Cryptographic Primitives

- Use **Ed25519** for signatures.
- Implement capability to:
  - Generate new Ed25519 keypairs.
  - Sign a simple string payload.
  - Verify a signature against a public key.

## Deliverables

- Functional `geas init` command that sets up the structure.
- Functional `geas identity` command to list or show current identity.
- Core Python module handling Key/Identity resolution and signing/verification.
