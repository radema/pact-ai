# GEAS: Governance Enforcement for Agent Systems

**Protocol for the "Software Engineering 3.0" Era**

Version: 3.1

---

## Executive Summary

GEAS (pronounced *gesh*) is a repository-native governance protocol designed to solve the "Day 2" problem of AI-driven development: **Trust**.

As software engineering shifts from Human-Authored to Agent-Generated, the bottleneck moves from velocity to verification. Organizations face a new risk: **"Agent Drift"**—autonomous models deviating from intent, hallucinating features, or introducing subtle bugs that bypass traditional review.

GEAS solves this by treating Agent instructions as a **Binding Vow** (a Geas). It enforces a strict "Filesystem Sovereignty" model where:

1. **Intent** is cryptographically sealed before work begins.
2. **Code** remains freely mutable during development.
3. **Evidence** (the MRP) is cryptographically sealed before code is merged.

### Why Not Just Git?

Git provides versioning and history, but Git authorship is trivially spoofable—anyone with repo access can set any author string. GEAS adds **cryptographic non-repudiation**:

| Capability | Git | GEAS |
|------------|-----|------|
| Track changes | ✅ | ✅ |
| Author attribution | ⚠️ Spoofable | ✅ Ed25519 signatures |
| Intent-to-code binding | ❌ | ✅ Sealed specs → manifest |
| Prove tests passed for code version X | ❌ | ✅ MRP with test logs + code snapshot |
| Role-based workflow enforcement | ❌ | ✅ Configurable stages |

---

## The Core Philosophy

### The Metaphor: The Geas

In mythology, a *Geas* is a magical obligation. If the hero breaks the vow, they lose their power.

In our protocol:

| Element | Meaning |
|---------|---------|
| **The Hero** | The AI Agent(s) |
| **The Vow** | The Intent Documents (requirements, specs, architecture, plan) |
| **The Power** | The ability to merge code |

### The "Day 2" Reality

Current agentic tools focus on code generation. GEAS focuses on the **Chain of Custody**:

- **Identity**: Who authorized this feature? (Cryptographically proven)
- **Integrity**: Have the Intent documents changed during development?
- **Audit**: Can we prove the tests passed for *this specific* version of the code?

---

## The Architecture: "Steering & Engine"

GEAS is **not** a SaaS platform. It is a local protocol defined by a hidden directory structure (`.geas/`) that lives alongside your code.

```
.geas/
├── config/
│   ├── agents.yaml        # Agent personas (role, goal, backstory)
│   ├── models.yaml        # Model providers (API keys, endpoints)
│   ├── identities.yaml    # Cryptographic identities (public keys)
│   └── workflow.yaml      # Governance rules (seal sequence, roles)
└── bolts/
    └── feature-login/     # One Bolt = One unit of work
        ├── 01_request.md
        ├── 02_specs.md
        ├── 03_plan.md
        ├── lock.json      # The cryptographic ledger
        └── mrp/           # Merge Request Package
```

### The Three Configuration Files

| File | Purpose | Contents |
|------|---------|----------|
| `agents.yaml` | **Persona definitions** | Role, goal, backstory for each agent type |
| `models.yaml` | **Provider configs** | API endpoints, model names, credentials |
| `identities.yaml` | **Cryptographic identities** | Public keys for humans and agents |

These files are **logically coupled by reference**:

- An identity in `identities.yaml` references a persona from `agents.yaml`
- An identity may be backed by a model from `models.yaml`

### The Two Components

| Component | Role | Example |
|-----------|------|---------|
| **The Steering** (Protocol) | The `geas` CLI manages Bolt lifecycles and acts as the notary. | `geas new`, `geas seal`, `geas prove` |
| **The Engine** (Agent) | Your existing AI tool (Claude, GPT, local LLM) acts as the runtime. It reads GEAS state to understand its boundaries. | Cursor, Windsurf, Aider, custom agents |

---

## Core Concepts

### The Bolt

A **Bolt** is the fundamental unit of work in GEAS—equivalent to a *Sprint* in Agile methodology.

Each Bolt:

- Represents a discrete feature, fix, or task.
- Lives in its own folder under `.geas/bolts/<bolt-name>/`.
- Contains all governance artifacts: Intent documents, lock ledger, and MRP.
- Has a defined lifecycle: `active` → `sealed` → `archived`.

### The Intent

**Intent** is the collection of all preliminary documents that provide context for building code:

- `01_request.md` — The business request or user story.
- `02_specs.md` — Functional and technical specifications.
- `03_plan.md` — Implementation plan and architecture notes.
- (Extensible) — Research notes, design decisions, API contracts, etc.

The Intent is **abstractable by design**. GEAS does not dictate which documents you must have—it enforces that *whatever* documents you define as Intent are sealed and immutable before code generation begins.

### The MRP (Merge Request Package)

The MRP is a **post-code evidence package** proving the validity of the implementation:

- `mrp/summary.md` — Human-readable summary of what was built.
- `mrp/tests.log` — Captured test execution output.
- `mrp/manifest.json` — Cryptographic fingerprint (Merkle Tree) of the source code at proof time.

The MRP is sealed after tests pass, creating permanent evidence that "Code Version X passed Test Suite Y."

---

## The Lifecycle of a Bolt

### Phase I: The Ritual (Intent)

1. **`geas new <feature>`** — Creates the Bolt workspace.
2. **Drafting** — Human Architect (or Agent with Human approval) writes the Intent documents.
3. **`geas seal intent`** — Human signs and seals the Intent.
   - **Effect**: A cryptographic hash of these documents is recorded in `lock.json`, signed with the human's private key. The Agent cannot rewrite its own instructions without detection.

### Phase II: The Execution (Code)

1. **Coding** — The Agent reads the sealed Intent and generates/modifies implementation files in `src/`.
2. **Mutability** — Source code remains **freely mutable**. The Agent can iterate, refactor, and fix bugs without breaking any locks.

### Phase III: The Judgment (Proof)

1. **`geas prove`** — The System:
   - Runs the test suite (e.g., `pytest`).
   - Snapshots the code (generates `manifest.json`).
   - Generates the MRP artifacts.
   - Seals the MRP with the Agent's signature.
2. **Effect** — Cryptographic evidence is created. The Bolt is ready for merge review.

### Phase IV: The Merge

1. **Human Review** — A Human Approver reviews the sealed MRP.
2. **`geas verify`** — Validates the Bolt against the configured workflow (all required seals present, signatures valid, chain unbroken).
3. **Merge** — If verification passes, the code can be merged. PRs without a valid MRP are rejected.

---

## The Trinity Lock

The **Trinity Lock** is the cryptographic engine behind GEAS. Unlike a simple file hash, it binds three distinct pillars into a single cryptographic record:

| Pillar | Concept | Implementation |
|--------|---------|----------------|
| **Physical Integrity** | "The content hasn't changed." | SHA-256 hashes / Merkle Trees |
| **Identity** | "We know who authorized this." | Ed25519 Signatures (SSH format) |
| **Audit History** | "We know the sequence of events." | Hash-Chain Ledger |

Every seal operation appends an event to the Bolt's `lock.json`, where each event:

- Is cryptographically signed by the actor (human or agent)
- References the hash of the previous event (forming an immutable chain)
- Contains the hashes of the sealed files

This creates **tamper-evident, non-repudiable proof** of the governance process.

---

## Target Environment: Multi-Agent Enterprise

GEAS is designed for **professional agentic environments** where:

- Multiple AI agents collaborate on the same repository.
- Agents have different personas (spec_writer, architect, developer, qa_engineer).
- Human oversight is required for critical approvals.
- Enterprise compliance demands auditable, cryptographically-secured chains of custody.

### CI/CD Integration

GEAS follows a **proactive MRP model**:

1. Agents generate code and run `geas prove` locally or in CI.
2. CI prepares the MRP and pushes it for Human review.
3. **Merge is blocked** until an approved MRP exists.
4. Reviewers run `geas verify` to validate the full chain before approving the PR.

This ensures that no code enters the main branch without cryptographic proof of:

- What was requested (sealed Intent).
- What was built (sealed MRP with code manifest).
- Who authorized each step (signatures).

---

## The Workflow Configuration

GEAS is **workflow-agnostic**. Projects define their own governance policies in `.geas/config/workflow.yaml`:

```yaml
# Example: Standard multi-agent workflow
workflow:
  name: "standard"

  intent_documents:
    required: ["01_request.md", "02_specs.md"]
    optional: ["03_plan.md", "04_architecture.md"]

  stages:
    - id: "intent"
      action: "SEAL_INTENT"
      required_role: "human"

    - id: "proof"
      action: "SEAL_MRP"
      required_role: "agent"
      prerequisite: "intent"

    - id: "approval"
      action: "APPROVE"
      required_role: "human"
      prerequisite: "proof"
```

The `geas verify` command validates the current Bolt state against this workflow definition.

---

## Command Summary

| Command | Purpose |
|---------|---------|
| `geas init` | Initialize GEAS in a repository. |
| `geas identity` | Manage identities (register humans/agents, generate keys). |
| `geas new <name>` | Create a new Bolt workspace. |
| `geas checkout <name>` | Switch active Bolt context. |
| `geas seal intent` | Seal Intent documents (human signature required). |
| `geas prove` | Run tests, generate MRP, and seal it. |
| `geas verify` | Validate Bolt against the configured workflow. |
| `geas status` | Display current Bolt state and seal status. |
| `geas archive <name>` | Archive a completed Bolt. |
| `geas delete <name>` | Permanently delete a Bolt. |

---

## Roadmap Summary

| Phase | Objective | Deliverable |
|-------|-----------|-------------|
| **Phase 1: Identity** | Establish the Keyring | `geas init`, `geas identity`, SSH key generation |
| **Phase 2: Intent Engine** | Seal preliminary documents | `geas seal intent`, hash chain ledger |
| **Phase 3: Proof Engine** | Generate and seal MRP | `geas prove`, test runner, manifest generator |
| **Phase 4: Verification** | Workflow-based validation | `geas verify`, workflow configuration |
| **Phase 5: Lifecycle** | Bolt management | `geas archive`, `geas delete` |
| **Phase 6: CI Integration** | Enterprise automation | GitHub Actions / GitLab CI templates |

---

## Conclusion

GEAS provides the missing governance layer for the agentic development era. By separating **Intent** (what to build) from **Code** (how it's built) from **Proof** (evidence it works), and binding them with **cryptographic signatures**, GEAS creates an auditable, non-repudiable chain of custody that enables:

- **Trust** in agent-generated code.
- **Compliance** with enterprise security requirements.
- **Collaboration** between multiple agents and human overseers.

The future of software engineering is not just faster code generation—it's **verifiable** code generation. GEAS makes that possible.
