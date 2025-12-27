# Contributing to PACT-AI

Thank you for your interest in PACT-AI! We follow a strict protocol-driven development process to ensure reliability and trust in our agentic workflows.

## 🛠 Local Setup

We use `uv` for lightning-fast dependency management and project isolation.

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/pact-ai.git
    cd pact-ai
    ```

2. **Synchronize environment**:

    ```bash
    uv sync
    ```

3. **Install pre-commit hooks**:

    ```bash
    uv run pre-commit install
    ```

## 🔄 The PACT Workflow

All contributions must follow the PACT (Protocol for Agent Control & Trust) lifecycle.

1. **Initialize a Bolt**: Create a new unit of work.

    ```bash
    uv run pact new <bolt-name>
    ```

2. **Define Requests**: Elaborate the `01_request.md`.
3. **Draft Specs**: Let the `spec_writer` generate `02_specs.md`.
4. **Architect Plan**: Let the `architect` generate `03_plan.md`.
5. **Seal Artifacts**: Cryptographically lock the specs and plan.

    ```bash
    uv run pact seal specs
    uv run pact seal plan
    ```

6. **Implement**: Write the code in `src/`.
7. **QA & MRP**: Generate the Merge Readiness Pack.

    ```bash
    uv run pact mrp
    ```

## 🧪 Testing & Quality

* **TDD**: We practice Test-Driven Development. New features must include tests in `tests/`.
* **Coverage**: Aim for **>85%** test coverage.
* **Linting**: We use `ruff` for formatting and `mypy` for type checking.
* **CI**: Every Pull Request is automatically vetted via GitHub Actions.

## 📄 Pull Request Process

1. Ensure all tests pass: `uv run pytest`.
2. Ensure linting passes: `uv run ruff check .`.
3. Ensure your bolt is "Ready to Merge" (MRP contains the keyword).
4. Submit your PR!

---

By contributing, you agree that your contributions will be dual-licensed under the MIT and Apache 2.0 Licenses.
