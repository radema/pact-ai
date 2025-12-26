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

## 🛠️ The Workflow

1. **Request**: Create a `01_request.md` in a new bolt folder.
2. **Specs**: The Spec Writer defines `02_specs.md`.
3. **Plan**: The Architect defines `03_plan.md`.
4. **Seal**: Lock the files (Coming Soon).
5. **Code**: The Developer executes the plan.
6. **MRP**: QA verifies the output.

## 🤝 Contributing

See `docs/DEV_GUIDELINES.md` for development instructions.
