# Development Guidelines

## Setup with uv

We use uv for fast, reliable package management.

### 1. Initialize

```bash
mkdir pact-ai
cd pact-ai
uv init
```

# 2. Dependencies

```bash
uv add pyyaml
# Optional: uv add rich (for better CLI colors/tables)
```

# 3. Dev Dependencies

```bash
uv add --dev pytest ruff twine build
```

## Package Structure

The repository must follow the src layout for PyPI standards.

```bash
pact-ai/
├── pyproject.toml
├── src/
│   └── pact_cli/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py    # Refactor helper functions here
```

## PyPI Configuration (pyproject.toml)

```toml
[project]
name = "pact-ai"
version = "0.1.0"
description = "Protocol for Agent Control & Trust"
dependencies = ["pyyaml"]
readme = "README.md"
requires-python = ">=3.10"

[project.scripts]
pact = "pact_cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Quality Gates

* Ruff: Use ruff check . to ensure Pythonic code.

* Type Safety: Ensure strict typing for the hashing and file I/O operations.

* Security: Verify that pact seal correctly handles file encoding to prevent hash collisions (git CRLF/LF issues).

## Publishing

```bash
uv build
uv run twine upload dist/*
```
