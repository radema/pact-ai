# GEAS-AI: Protocol for Agent Control & Trust

**Status**: v0.1.0 (Alpha)

GEAS is a repository-native governance protocol designed for **Software Engineering 3.0**. It enforces a strict "Spec-First" workflow for AI Agents, ensuring that no code is written without a cryptographically sealed Blueprint.

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
2. Updates `.geas/active_context.md` (The Pointer).

### The Workflow

1. **Request**: Create a `01_request.md` in a new bolt folder.
2. **Specs**: The Spec Writer defines `02_specs.md`.
3. **Plan**: The Architect defines `03_plan.md`.
4. **Seal**: Lock your artifacts with `pact seal [specs|plan|mrp]`.
    * Verify integrity anytime with `pact seal verify`.
5. **Code**: The Developer executes the plan.
6. **MRP**: QA verifies the output.

### Identity Management (New v0.1.1)

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
