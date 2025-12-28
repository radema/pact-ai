# Requirements Specification: The Trinity Lock Protocol

**Project:** PACT-AI (Protocol for Agent Control & Trust)
**Module:** Governance / File Locking
**Status:** Draft Specification v1.0

---

## 1. Context

In "Software Engineering 3.0" (Agentic Workflows), code generation is driven by autonomous AI agents acting upon rigorous specifications ("Blueprints").

The current governance model relies on `pact seal`, which uses simple cryptographic hashing to verify file integrity. This existing model has three critical deficiencies:

1. **Lack of Attribution:** It proves *that* a file changed, but not *who* (which Agent or Human) authorized the change.
2. **Mutability:** It does not prevent accidental modification at the Operating System level, allowing Agents to overwrite approved specs during execution.
3. **Ephemeral History:** It lacks a persistent audit trail. Once a file is unsealed and re-sealed, the history of the previous state is lost (outside of Git), making root-cause analysis of "Agent Drift" difficult.

## 2. Goal

To implement a **Trinity Lock Protocol** that enforces file immutability through three simultaneous pillars:

1. **Integrity (Content):** Mathematical proof that the file matches its record.
2. **Identity (Trust):** Cryptographic proof that a registered, authorized actor signed the record.
3. **Physical (Access):** OS-level enforcement of Read-Only permissions.

Crucially, this system must maintain a **Tamper-Evident Audit Ledger** (a local "micro-blockchain") for every governed bolt (unit of work), ensuring a permanent, verifiable history of all state changes without reliance on external version control systems (Git).

---

## 3. Detailed Requirements

### 3.1. Identity & Trust Store

The system must bridge the gap between cryptographic keys and Agent Roles and Human Supervisors/Colleagues.

* **REQ-ID-01 (Trust Store):** The system SHALL utilize `.pacts/config/agents.yaml` as the authoritative source of truth (Trust Store). This file maps Agent Roles (e.g., "Architect", "QA") to their public keys (Ed25519).
* **REQ-ID-02 (Key Injection):** The system MUST support injecting private keys via environment variables (`PACT_SIGNING_KEY`) to support containerized Agent execution, while retaining support for local key files (`~/.pact/credentials`) for human users.
* **REQ-ID-03 (Authorization Check):** The system MUST reject any `seal` or `unseal` operation if the cryptographic signature does not correspond to a public key currently listed in the Trust Store.

### 3.2. The Ledger (Data Structure)

The locking mechanism must not be a disposable boolean state but a persistent log.

* **REQ-DATA-01 (Sidecar File):** Every governed bolt (unit of work) MUST have a corresponding persistent ledger file (e.g., `bolt-name.lock`).
* **REQ-DATA-02 (Hash Chaining):** Each entry in the ledger MUST contain a `previous_event_hash` field. This field MUST be the SHA-256 hash of the entire preceding event object, creating an unbroken cryptographic chain from the genesis event to the current state.
* **REQ-DATA-03 (Event Schema):** Each ledger entry MUST record:
* `action`: (SEAL | OPEN)
* `timestamp`: ISO 8601 UTC
* `actor_id`: The name of the agent/user from the Trust Store.
* `reason`: Text justification (Mandatory for OPEN actions).
* `file_hash`: SHA-256 of the target file content (at time of action).
* `signature`: Cryptographic signature of the event data.

### 3.3. The Locking Workflow (`pact seal`)

This workflow secures the artifact.

* **REQ-FLOW-01 (Integrity Calculation):** The system SHALL calculate the SHA-256 hash of the target file's current content.
* **REQ-FLOW-02 (Ledger Appending):** The system SHALL append a `SEAL` event to the ledger. This event must link to the previous head of the chain.
* **REQ-FLOW-03 (Physical Enforcement):** Upon successful writing of the ledger, the system SHALL modify the target file's OS permissions to **Read-Only** (Linux/Mac: `0444`, Windows: Read-Only Attribute).
* **REQ-FLOW-04 (Idempotency):** If the file is already sealed and the hash has not changed, the command SHALL exit successfully without adding a duplicate ledger entry.

### 3.4. The Unlocking Workflow (`pact unseal`)

This workflow allows controlled modification.

* **REQ-FLOW-05 (Mandatory Reasoning):** The system MUST require a `--reason` string argument from the user.
* **REQ-FLOW-06 (Ledger Appending):** The system SHALL append an `OPEN` event to the ledger, signed by the requestor, recording the reason for opening.
* **REQ-FLOW-07 (Physical Release):** Upon successful writing of the ledger, the system SHALL modify the target file's OS permissions to **Read/Write** (Linux/Mac: `0644`).

### 3.5. Verification (`pact verify`)

This workflow audits the artifact's state.

* **REQ-VER-01 (Chain Validation):** The system SHALL iterate through the entire ledger history. It MUST fail if any `previous_event_hash` does not mathematically match the preceding entry.
* **REQ-VER-02 (Signature Audit):** The system SHALL verify that every signature in the chain corresponds to a valid public key in the Trust Store.
* **REQ-VER-03 (Current State Check):** The system SHALL verify that the actual file on disk matches the `file_hash` recorded in the most recent `SEAL` event.
* **REQ-VER-04 (Physical Check):** The system SHALL verify that the file is currently Read-Only at the OS level.

### 3.6. Non-Functional Requirements (Constraints)

* **REQ-NFR-01 (Git Independence):** The system MUST function correctly in a "detached" environment (e.g., a zipped folder sent via email) without access to a `.git` directory.
* **REQ-NFR-02 (Performance):** Chain verification for a history of 100 events MUST complete in under 500ms on standard hardware.
* **REQ-NFR-03 (Cross-Platform):** Physical locking implementations MUST abstract OS differences between POSIX (Linux/macOS) and NT (Windows) systems.

---

### 4. Acceptance Criteria

* [ ] A user can generate an identity key pair.
* [ ] A file cannot be sealed if the user's public key is not in `agents.yaml`.
* [ ] `pact seal` makes a file read-only on the file system.
* [ ] `pact unseal` requires a reason and logs it.
* [ ] Manually deleting a line from the `.lock` file causes `pact verify` to fail with a "Tamper Detected" error.

---

# PACT-AI Module: The Trinity Lock Protocol

**Version:** draft
**Context:** [radema/pact-ai](https://github.com/radema/pact-ai)
**Target Users:** AI Agents (Architects, Coders, QA) & Human Supervisors.

## 1. Executive Summary

The **Trinity Lock** is a repository-native governance protocol designed for "Software Engineering 3.0" (Agentic Workflows). It replaces simple file locking with a **Tamper-Evident Audit Ledger**.

It ensures that critical artifacts (Specs, Plans) adhere to three pillars:

1. **Integrity:** The content has not changed (Hash).
2. **Identity:** The change was authorized by a known Agent/Human (Signature + Trust Store).
3. **Physical:** The file is effectively immutable on disk (OS Permissions).

---

## 2. Core Solution Architecture

### 2.1 The Trust Store (such as `agents.yaml`)

Identity is not just a key pair; it is a **Role**. The system validates signatures against a committed configuration file acting as the "Phonebook" for the team.

**File Location:** `.pacts/config/agents.yaml`

```yaml
agents:
  - name: "Architect-Prime"
    role: "architect"
    # The Public Key (Ed25519) used to verify signatures
    public_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5..."
  - name: "Human-Lead"
    role: "admin"
    public_key: "ssh-ed25519 AAAAE5Chk..."

```

### 2.2 The Ledger (The `.lock` file)

Every governed file (e.g., `02_specs.md`) has a permanent sidecar ledger (`02_specs.md.lock`). This ledger is a **Hash Chain** (Micro-Blockchain) where every event is cryptographically linked to the previous one.

**Event Schema:**

---

## 3. Functional Requirements

### 3.1 Identity Management (FR-ID)

**FR-ID-01: Trust Validation**

* The system must refuse to `seal` or `unseal` a file if the signer's Public Key is not listed in `.pacts/config/agents.yaml`.
* **Error:** *"Unauthorized: Key X is not a registered agent."*

**FR-ID-02: Agent Key Injection**

* To support AI Agents in containers, the CLI must verify identity using a Private Key provided via the environment variable `PACT_SIGNING_KEY`.
* Humans may fallback to a local key file (`~/.pact/credentials`).

### 3.2 The Locking Workflow (FR-LOCK)

**FR-LOCK-01: Sealing (Locking)**

* **Command:** `pact seal <file>`
* **Logic:**

1. **Identify:** Load Private Key (Env or File).
2. **Hash:** Calculate `SHA256` of the target file content.
3. **Chain:** Read `head_event_hash` from the ledger.
4. **Sign:** Create and sign a `SEAL` event linking to the chain head.
5. **Physical:** Execute `chmod 444` (Read-Only) on the target file.

### 3.3 The Unlocking Workflow (FR-UNLOCK)

**FR-UNLOCK-01: Controlled Opening**

* **Command:** `pact unseal <file> --reason "..."`
* **Constraint:** A textual `--reason` is mandatory.
* **Logic:**

1. **Verify:** Check if the requester is in `agents.yaml`.
2. **Log:** Append an `OPEN` event to the ledger (maintaining the chain).
3. **Physical:** Execute `chmod 644` (Read/Write) on the target file.

### 3.4 Verification (FR-VERIFY)

**FR-VERIFY-01: Deep Audit**

* **Command:** `pact verify <file>`
* **Checks:**

1. **Chain Integrity:** Re-calculate hashes for the entire history. Does  mathematically prove ?
2. **Author Authenticity:** Do all signatures in the chain correspond to valid keys in `agents.yaml`?
3. **Current State:** Does the actual file on disk match the `file_hash` of the last `SEAL` event?
4. **Physical State:** Is the file actually Read-Only?

---

## 4. Technical Specifications

### 4.1 Data Structure (JSON Ledger)

```json
{
  "target": "02_specs.md",
  "head_hash": "e3b0...",
  "history": [
    {
      "sequence": 1,
      "action": "SEAL",
      "timestamp": "2024-03-27T10:00:00Z",
      "actor_name": "Architect-Prime",
      "file_hash": "sha256:abc...",
      "previous_hash": null,
      "signature": "base64_sig..."
    },
    {
      "sequence": 2,
      "action": "OPEN",
      "timestamp": "2024-03-27T12:00:00Z",
      "actor_name": "Dev-Agent-01",
      "reason": "Fixing logic gap in Step 3",
      "previous_hash": "hash_of_seq_1",
      "signature": "base64_sig..."
    }
  ]
}

```

### 4.2 Security Constraints

* **Root of Trust:** The integrity of `agents.yaml` is assumed to be protected by the repository's standard Code Review / Pull Request process.
* **Algorithm:**
* Hashing: `SHA-256`
* Signing: `Ed25519` (via `PyNaCl` or `cryptography` lib)

---

## 5. Non-Functional Requirements (NFR)

* **NFR-01 (Git Independence):** The verification must succeed even if the `.git` folder is deleted. The trust is self-contained in `agents.yaml` + Ledger.
* **NFR-02 (Cross-Platform):** Physical locking must support Linux/macOS (`chmod`) and Windows (`attrib`).
* **NFR-03 (Agent Native):** Output logs must be structured (JSON/YAML) when requested, to allow Agents to parse *why* a verification failed.

---

## 6. Implementation Roadmap

1. **Milestone 1:** `pact identity`

* Generate keys.
* Parse `agents.yaml`.
* Verify `PACT_SIGNING_KEY` injection.

1. **Milestone 2:** `pact seal` (Core)

* Implement Hash Chaining logic.
* Implement File I/O for the JSON Ledger.

1. **Milestone 3:** `pact verify` (Auditor)

* Build the chain traversal engine.
* Implement the visual report ("Who changed what").
