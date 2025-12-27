# PACT-AI: Protocol for Agent Control & Trust

**Status**: v0.1.0 (Alpha)

PACT is a repository-native governance protocol designed for **Software Engineering 3.0**. It enforces a strict "Spec-First" workflow for AI Agents, ensuring that no code is written without a cryptographically sealed Blueprint.

## 🚀 Getting Started

### Installation

```bash
# Requires Python 3.10+
uv pip install pact-ai
# OR run directly
uv run pact --help
```

### Initialization

Bootstrap the governance layer in your project:

```bash
uv run pact init
```

This creates the `.pacts/` directory structure:

* `config/agents.yaml`: Defines your AI team personas.
* `config/models.yaml`: Configures LLM providers.
* `bolts/`: The home for your Features (Units of Work).

### Task Lifecycle

Start a new "Bolt" (Unit of Work):

```bash
uv run pact new feature-login
```

This:

1. Creates `.pacts/bolts/feature-login/`.
2. Updates `.pacts/active_context.md` (The Pointer).

### The Workflow

1. **Request**: Create a `01_request.md` in a new bolt folder.
2. **Specs**: The Spec Writer defines `02_specs.md`.
3. **Plan**: The Architect defines `03_plan.md`.
4. **Seal**: Lock your artifacts with `pact seal [specs|plan|mrp]`.
    * Verify integrity anytime with `pact seal verify`.
5. **Code**: The Developer executes the plan.
6. **MRP**: QA verifies the output.

## 🤝 Contributing

See `CONTRIBUTING.md` for development instructions.

## 📄 License

PACT-AI is dual-licensed under the **MIT License** and the **Apache License 2.0**.

* See [LICENSE-MIT](LICENSE-MIT) for details.
* See [LICENSE-APACHE](LICENSE-APACHE) for details.
