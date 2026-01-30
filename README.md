# GEAS-AI: Protocol for Agent Control & Trust

**Status**: v0.1.3 (Archived)

GEAS is a repository-native governance protocol designed for **Software Engineering 3.0**. It enforces a strict "Spec-First" workflow for AI Agents, ensuring that no code is written without a cryptographically sealed Blueprint.

> **Note**: While GEAS provides a default "Spec-First" workflow, the protocol is theoretically configurable. It can be used as a standalone tool to drive agents during coding sessions, ensuring cryptographic provenance even without a full governance team.

## 📋 Project Post-Mortem: Lessons Learned

### The Genesis - First Agent-Driven Project

GEAS-AI began as an experiment in agent-driven development, built by a developer curious about solving the "agent trust" problem. The initial excitement stemmed from envisioning a world where AI agents could collaborate with humans on software engineering projects under a robust governance framework. The project represented an ambitious attempt to create a protocol that would enable trustworthy, auditable, and controllable AI agent interactions in software development workflows.

### The Discovery Phase - Testing Against Reality

Real-world experimentation with agentic systems revealed a different landscape than initially anticipated. Testing against modern tools like Cursor, Windsurf, and Opencode showed that the agent framework ecosystem, while promising, was still in its early stages. Observations indicated that many "agent" solutions were essentially sophisticated toolchains rather than truly autonomous systems. The maturity gap between vision and reality became apparent, suggesting that the industry was still solving foundational problems rather than governance challenges.

### The Technical Realization

The project's core technical insight came from understanding GPG (GNU Privacy Guard) - a battle-tested cryptographic system for digital signatures and encryption. GEAS was built around Ed25519 keys and GPG-like operations to ensure cryptographic provenance of all agent activities. However, a critical realization emerged: the project was over-engineered for the problem it. The complexity analysis revealed that most of the governance mechanisms being built were redundant, as existing tools like Git with GPG signatures already provided the cryptographic guarantees needed for trustworthy development workflows.

### The Conclusion - Project Closure

After months of development and experimentation, the decision was made to close the GEAS-AI experiment. The key insight was that Git and GPG already solve the same problems that GEAS attempted to address, without imposing additional change management burden. While the protocol was technically sound and implemented correctly, it represented a solution looking for a problem that didn't truly exist in practice. The project served as an excellent learning experience in first-principles thinking and the importance of validating assumptions against reality.

### Lessons for Future Projects

**MVP Testing Value**: Building a minimal viable product early has revealed the redundancy of the solution much faster, saving significant development time.

**Importance of Honest Retrospectives**: Regular, honest reassessment of the project's value proposition versus complexity has led to an earlier pivot or conclusion. This allow me to work on other ideas or projects knowing why this one failed.

---

*GEAS-AI is now archived but remains publicly available as a learning resource for those interested in governance protocols, cryptographic provenance, and the evolution of agent-driven development paradigms.*

## 🚀 Getting Started

> **Note**: The following documentation remains for archival and reference purposes. While the tool is functional, it is no longer actively maintained.

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
