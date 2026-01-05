# GEAS-AI: Protocol for Agent Control & Trust

**Status**: v0.1.3 (Alpha)

GEAS is a repository-native governance protocol designed for **Software Engineering 3.0**. It enforces a strict "Spec-First" workflow for AI Agents, ensuring that no code is written without a cryptographically sealed Blueprint.

> **Note**: While GEAS provides a default "Spec-First" workflow, the protocol is theoretically configurable. It can be used as a standalone tool to drive agents during coding sessions, ensuring cryptographic provenance even without a full governance team.

## 🚀 Getting Started

### Installation

```bash
# Requires Python 3.10+
uv pip install geas-ai
# OR run directly
uv run geas --help
```

### Initialization

Bootstrap the governance layer in your project:

```bash
uv run geas init
```

This creates the `.geas/` directory structure:

* `config/identities.yaml`: Registry of authorized Ed25519 public keys.
* `config/agents.yaml`: Defines your AI team personas.
* `config/models.yaml`: Configures LLM providers.
* `bolts/`: The home for your Features (Units of Work).

### Task Lifecycle

Start a new "Bolt" (Unit of Work):

```bash
uv run geas new feature-login
```

This:

1. Creates `.geas/bolts/feature-login/`.
2. Initializes the cryptographic ledger (`lock.json`).
3. Updates `.geas/active_context.md`.

### The Workflow

1. **Request**: Create a `01_request.md` in a new bolt folder.
2. **Specs**: The Spec Writer defines `02_specs.md`.
3. **Plan**: The Architect defines `03_plan.md`.
4. **Intent**: Seal the blueprint with your signature:

   ```bash
   geas seal intent --identity arch-lead
   ```

5. **Code**: The Developer executes the plan.
6. **Prove**: Generate cryptographic evidence (Manifest + Test Logs):

   ```bash
   geas prove
   ```

7. **MRP**: QA verifies the evidence, writes the summary, and seals the package:

   ```bash
   geas seal mrp
   ```

8. **Approve**: A Human identity (e.g., Tech Lead) signs off on the sealed package for merge:

   ```bash
   geas approve --identity tech-lead --comment "LGTM"
   ```

### Identity Management

GEAS enforces strict identity verification for all actors (Human or Agent).

1. **Create an Identity**:

   ```bash
   uv run geas identity add --name alice --role human
   uv run geas identity add --name bot-dev --role agent --persona "Senior Dev" --model "gpt-4"
   ```

2. **List Identities**:

   ```bash
   uv run geas identity list
   ```

3. **Show Details**:

   ```bash
   uv run geas identity show bot-dev
   ```

4. **Key Rotation**:
   Securely revoke and rotate keys for compromised identities:

   ```bash
   uv run geas identity revoke bot-dev
   ```

## 🤝 Contributing

* See [LICENSE-APACHE](LICENSE-APACHE) for details.
