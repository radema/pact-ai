# GEAS-AI Repository Context for Agents

**Document Version:** 2.0
**Last Updated:** 2026-01-03
**Purpose:** Provide comprehensive context for AI agents working on the GEAS-AI codebase.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Repository Overview](#repository-overview)
3. [Architecture](#architecture)
4. [Directory Structure](#directory-structure)
5. [Technology Stack](#technology-stack)
6. [Naming Conventions](#naming-conventions)
7. [Code Quality Standards](#code-quality-standards)
8. [Development Workflow](#development-workflow)
9. [Testing Guidelines](#testing-guidelines)
10. [CLI Command Reference](#cli-command-reference)
11. [Key Concepts & Domain Vocabulary](#key-concepts--domain-vocabulary)
12. [File Templates & Schemas](#file-templates--schemas)
13. [CI/CD Pipeline](#cicd-pipeline)
14. [Agent Personas](#agent-personas)
15. [Current Development Status](#current-development-status)
16. [Critical Rules for Agents](#critical-rules-for-agents)

---

## Executive Summary

**GEAS-AI** (Governance Enforcement for Agent Systems) is a **repository-native governance protocol** for AI-driven software development. It enforces a "Spec-First" workflow where:

- **Intent** documents (specs, plans) are cryptographically sealed *before* code is written.
- **Code** remains freely mutable during development.
- **Evidence** (the MRP - Merge Request Package) is sealed *after* tests pass.

The protocol creates **non-repudiable, tamper-evident proof** of the entire development lifecycle using Ed25519 cryptographic signatures.

### Core Philosophy
>
> *"A Geas is a magical obligation. If the hero breaks the vow, they lose their power."*

In GEAS:

| Element | Meaning |
|---------|---------|
| **The Hero** | The AI Agent(s) |
| **The Vow** | The Intent Documents (requirements, specs, plan) |
| **The Power** | The ability to merge code |

### Why GEAS over Git?

Git provides versioning, but Git authorship is **trivially spoofable**. GEAS adds cryptographic non-repudiation:

| Capability | Git | GEAS |
|------------|-----|------|
| Track changes | ✅ | ✅ |
| Author attribution | ⚠️ Spoofable | ✅ Ed25519 signatures |
| Intent-to-code binding | ❌ | ✅ Sealed specs → manifest |
| Prove tests passed for code version X | ❌ | ✅ MRP with test logs + code snapshot |
| Role-based workflow enforcement | ❌ | ✅ Configurable stages |

---

## Repository Overview

| Attribute | Value |
|-----------|-------|
| **Package Name** | `geas-ai` |
| **Current Version** | `0.1.1` (Alpha) |
| **Python Version** | `>=3.10` |
| **License** | Dual MIT / Apache-2.0 |
| **Package Manager** | `uv` |
| **CLI Entry Point** | `geas` (→ `geas_ai.main:main`) |
| **Documentation** | MkDocs (Material theme) |
| **Primary Author** | Raul De Maio |

---

## Architecture

### High-Level Design: "Steering & Engine"

GEAS consists of two components:

| Component | Role | Examples |
|-----------|------|----------|
| **The Steering** (Protocol) | The `geas` CLI manages Bolt lifecycles and acts as the notary. | `geas new`, `geas seal`, `geas prove` |
| **The Engine** (Agent) | Your existing AI tool acts as the runtime. It reads GEAS state to understand its boundaries. | Cursor, Windsurf, Aider, Claude Code |

### The Trinity Lock

The cryptographic engine binds three pillars:

| Pillar | Concept | Implementation |
|--------|---------|----------------|
| **Physical Integrity** | "The content hasn't changed." | SHA-256 hashes / Merkle Trees |
| **Identity** | "We know who authorized this." | Ed25519 Signatures (SSH format) |
| **Audit History** | "We know the sequence of events." | Hash-Chain Ledger (`lock.json`) |

### Locking Scope

| Layer | Content | Lock State |
|-------|---------|------------|
| **INTENT** | `01_request.md`, `02_specs.md`, `03_plan.md` | **Immutable** after seal |
| **CODE** | `src/`, `tests/` | **Mutable** (evolves freely) |
| **MRP** | `mrp/summary.md`, `mrp/tests.log`, `mrp/manifest.json` | **Immutable** after seal |

---

## Directory Structure

```
geas-ai/
├── .geas/                          # GEAS Protocol Directory
│   ├── active_context.md           # Current bolt pointer
│   ├── archive/                    # Completed bolts
│   ├── bolts/                      # Active work units
│   │   └── <bolt-name>/
│   │       ├── 01_request.md       # Feature request
│   │       ├── 02_specs.md         # Specifications
│   │       ├── 03_plan.md          # Implementation plan
│   │       ├── approved.lock       # Cryptographic ledger (YAML)
│   │       └── mrp/                # Merge Request Package
│   │           ├── summary.md
│   │           ├── tests.log
│   │           └── manifest.json
│   └── config/
│       ├── agents.yaml             # Agent persona definitions
│       ├── models.yaml             # LLM provider configs
│       ├── identities.yaml         # Cryptographic identities (planned)
│       └── workflow.yaml           # Governance rules (planned)
│
├── src/geas_ai/                    # Source Code
│   ├── __init__.py
│   ├── main.py                     # CLI entry point (Typer app)
│   ├── utils.py                    # Utility functions
│   ├── commands/                   # CLI command modules
│   │   ├── __init__.py
│   │   ├── init.py                 # `geas init`
│   │   ├── lifecycle.py            # `geas new`, `checkout`, `delete`, `archive`
│   │   ├── seal.py                 # `geas seal`
│   │   ├── status.py               # `geas status`
│   │   ├── verify.py               # `geas verify`
│   │   └── agents.py               # `geas agents`
│   └── core/
│       ├── __init__.py
│       └── content.py              # Templates and default content
│
├── tests/                          # Test Suite
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_core.py                # Core CLI tests
│   └── test_agents.py              # Agent-related tests
│
├── docs/                           # Documentation (MkDocs)
│   ├── WHITE_PAPER.md              # Protocol specification
│   ├── TRINITY_LOCK.md             # Cryptographic specification
│   ├── AGENT_CONTEXT.md            # This document
│   ├── getting_started.md          # User guide
│   └── reference.md                # API reference
│
├── strategic_docs/                 # Strategic planning
│   └── ROADMAP.md                  # Development roadmap
│
├── .github/workflows/              # CI/CD
│   ├── ci.yml                      # Test & lint pipeline
│   ├── docs.yml                    # Documentation deployment
│   └── publish.yml                 # PyPI publication
│
└── Configuration Files
    ├── pyproject.toml              # Project metadata & dependencies
    ├── .pre-commit-config.yaml     # Pre-commit hooks
    ├── mkdocs.yml                  # Documentation config
    └── uv.lock                     # Dependency lock file
```

---

## Technology Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| **Language** | Python 3.10+ | Core implementation |
| **Package Manager** | `uv` | Fast dependency management |
| **CLI Framework** | `typer` | Type-hinted CLI |
| **Output Formatting** | `rich` | Terminal formatting & tables |
| **YAML Parsing** | `pyyaml` | Configuration parsing |
| **Linting** | `ruff` | Fast Python linter/formatter |
| **Type Checking** | `mypy` (strict mode) | Static type analysis |
| **Testing** | `pytest` | Test framework |
| **Pre-commit** | `pre-commit` | Git hook management |
| **Documentation** | `mkdocs-material` | Documentation site |
| **Cryptography** (planned) | `cryptography` | Ed25519 signatures |

### Dependency Groups

```toml
[project]
dependencies = [
    "pre-commit>=4.5.1",
    "pyyaml>=6.0.3",
    "rich>=14.2.0",
    "typer>=0.21.0",
]

[dependency-groups]
dev = ["mypy>=1.19.1", "pre-commit>=4.5.1", "pytest>=9.0.2", "ruff>=0.14.10"]
docs = ["mike>=2.1.3", "mkdocs>=1.6.1", "mkdocs-material>=9.7.1", "mkdocstrings[python]>=1.0.0"]
```

---

## Naming Conventions

### File Naming

| Context | Convention | Examples |
|---------|------------|----------|
| Python modules | `snake_case.py` | `lifecycle.py`, `content.py` |
| Test files | `test_<module>.py` | `test_core.py`, `test_agents.py` |
| Config files | `<name>.yaml` | `agents.yaml`, `models.yaml` |
| Intent documents | `<NN>_<name>.md` | `01_request.md`, `02_specs.md`, `03_plan.md` |
| Bolt folders | `kebab-case` or `snake_case` | `feature-login`, `step_1_identity` |
| Lock files | `approved.lock` (YAML) or `lock.json` (JSON) | |

### Python Naming

| Element | Convention | Example |
|---------|------------|---------|
| Variables | `snake_case` | `bolt_path`, `lock_data` |
| Functions | `snake_case` | `get_active_bolt_path()`, `compute_sha256()` |
| Classes | `PascalCase` | `Console`, `Table` |
| Constants | `SCREAMING_SNAKE_CASE` | `DEFAULT_AGENTS_YAML`, `REQUEST_TEMPLATE` |
| Type hints | **Required on all functions** | `def new(name: str) -> None:` |
| Private functions | `_leading_underscore` | `_validate_config()` |

### CLI Commands

| Pattern | Example |
|---------|---------|
| Top-level verbs | `geas init`, `geas new`, `geas seal` |
| Kebab-case slugs | `geas new feature-login` |
| Flags with short forms | `--force/-f`, `--bolt/-b` |

### Slug Validation Rules

Bolt names must follow this regex pattern: `^[a-z0-9-_]+$`

- Only lowercase letters, numbers, hyphens, and underscores
- No spaces or special characters
- Examples: `feature-login`, `step_1_identity`, `bugfix-auth`

---

## Code Quality Standards

### Type Hints (Strict - MANDATORY)

All functions **MUST** have complete type annotations:

```python
def compute_sha256(file_path: Path) -> str:
    """Computes SHA256 hash of the file content (normalized)."""
    ...
```

### Docstrings (Google Style - MANDATORY)

All public functions require docstrings with:

- Description
- Args (if any)
- Returns (if applicable)
- Usage example (preferred)

```python
def new(name: str) -> None:
    """Start a new GEAS Unit of Work (Bolt).

    Creates .geas/bolts/<name>/ and updates .geas/active_context.md.

    Args:
        name: The name of the bolt (slugified).

    Usage:
        $ geas new feature-login
    """
```

### Pre-commit Hooks

The repository enforces these hooks automatically:

```yaml
hooks:
  - id: trailing-whitespace     # Remove trailing whitespace
  - id: end-of-file-fixer       # Ensure files end with newline
  - id: check-yaml              # Validate YAML syntax
  - id: check-added-large-files # Prevent large files
  - id: ruff                    # Linting with --fix
  - id: ruff-format             # Code formatting
  - id: mypy                    # Type checking (--strict)
```

### Error Handling Pattern

Use `typer.Exit(code=1)` for controlled CLI failures:

```python
if not bolt_dir.exists():
    console.print(f"[bold red]Error:[/bold red] Bolt '{name}' does not exist.")
    raise typer.Exit(code=1)
```

### DRY Principle

Extract repeated logic immediately. Use utility functions from `src/geas_ai/utils.py`:

| Function | Purpose |
|----------|---------|
| `get_geas_root()` | Returns Path to `.geas` directory |
| `ensure_geas_root()` | Validates GEAS is initialized |
| `validate_slug(name)` | Validates bolt name format |
| `compute_sha256(file_path)` | Compute normalized SHA-256 hash |
| `get_active_bolt_path()` | Get current bolt's Path |
| `get_active_bolt_name()` | Get current bolt's name |

---

## Development Workflow

### GEAS Protocol Workflow

```
1. geas new <bolt-name>       # Create workspace
2. Edit 01_request.md         # Define requirements
3. geas seal req              # Seal request
4. Create 02_specs.md         # Define specifications
5. geas seal specs            # Seal specs
6. Create 03_plan.md          # Define implementation plan
7. geas seal plan             # Seal plan
8. Implement in src/          # Write code (mutable)
9. Run tests                  # Validate
10. Create MRP                # Generate evidence
11. geas seal mrp             # Seal MRP
12. geas verify               # Validate chain
13. geas archive <bolt-name>  # Archive completed bolt
```

### Seal Sequence Enforcement

The `geas verify` command enforces this seal order:

1. `req` → `specs` → `plan` → `mrp`

A bolt cannot be archived unless all four artifacts are sealed AND verified.

### Git Workflow

1. Create feature branch
2. Follow GEAS lifecycle above
3. Ensure all tests pass: `uv run pytest`
4. Ensure linting passes: `uv run ruff check .`
5. Submit PR

### Local Development Setup

```bash
# Clone and setup
git clone <repo-url>
cd geas-ai

# Sync environment
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

---

## Testing Guidelines

### Framework & Structure

- **Framework:** `pytest`
- **Location:** `tests/`
- **Fixtures:** `tests/conftest.py`

### Coverage Target

**>85% code coverage** is required.

### Test Patterns

```python
# Fixture for temporary GEAS environment
@pytest.fixture
def setup_geas_environment(tmp_path):
    """Sets up a temporary GEAS environment."""
    geas_dir = tmp_path / ".geas"
    geas_dir.mkdir()
    config_dir = geas_dir / "config"
    config_dir.mkdir()
    # ... setup ...
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)
```

```python
# CLI test using CliRunner
def test_init_command(runner, tmp_path):
    """Test 'geas init' creates the necessary structure."""
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Success! GEAS initialized" in result.stdout
        assert (tmp_path / ".geas").exists()
    finally:
        os.chdir(cwd)
```

### Test Categories

| Category | Purpose |
|----------|---------|
| Unit tests | Test individual functions/modules |
| Integration tests | Test CLI command workflows |
| Seal/Verify tests | Test cryptographic integrity |

### TDD Approach

1. Write tests BEFORE implementation
2. Tests must cover happy paths, edge cases, and failure modes
3. Never commit code without passing tests

---

## CLI Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `geas init` | Initialize GEAS in repository | `geas init` |
| `geas new <name>` | Create new bolt workspace | `geas new feature-login` |
| `geas checkout <name>` | Switch active bolt context | `geas checkout feature-login` |
| `geas seal <target>` | Seal artifact (req/specs/plan/mrp) | `geas seal specs` |
| `geas status` | Display current bolt status | `geas status` |
| `geas verify` | Verify bolt integrity & sequence | `geas verify` |
| `geas delete <name>` | Delete a bolt | `geas delete old-feature` |
| `geas archive <name>` | Archive completed bolt | `geas archive feature-login` |
| `geas agents` | List available agent personas | `geas agents` |
| `geas version` | Show GEAS version | `geas version` |

### Seal Targets

| Target | File |
|--------|------|
| `req` | `01_request.md` |
| `specs` | `02_specs.md` |
| `plan` | `03_plan.md` |
| `mrp` | `mrp/summary.md` |

### Command Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (validation failed, file not found, etc.) |

---

## Key Concepts & Domain Vocabulary

| Term | Definition |
|------|------------|
| **Bolt** | A unit of work (equivalent to a Sprint in Agile). Lives in `.geas/bolts/<name>/`. |
| **Intent** | Collection of preliminary documents (request, specs, plan) that define what to build. |
| **MRP** | Merge Request Package - post-code evidence proving implementation validity. |
| **Trinity Lock** | The cryptographic engine binding Identity, Integrity, and Audit. |
| **Seal** | Cryptographic lock operation that hashes content and records it in the ledger. |
| **Active Context** | The currently selected bolt (tracked in `.geas/active_context.md`). |
| **Persona** | Behavioral template for agents (defined in `agents.yaml`). |
| **Identity** | Cryptographic identity with Ed25519 keys (stored in `identities.yaml`). |
| **Drift** | Unauthorized modification of sealed content (detected by hash mismatch). |
| **Geas** | A magical obligation/vow (the protocol's namesake metaphor). |
| **Manifest** | Cryptographic fingerprint (Merkle Tree) of source code at proof time. |
| **Workflow** | Governance policy defining required seals and role constraints. |

---

## File Templates & Schemas

### Request Template (`01_request.md`)

```markdown
# Feature Request: {bolt_name}

**Status:** PENDING

## Instructions
Describe your feature request here. The Spec Writer will use this to generate the specifications.
```

### Context Template (`active_context.md`)

```markdown
# Active Context

**Current Bolt:** {bolt_name}
**Path:** .geas/bolts/{bolt_name}
**Started:** {timestamp}

## Instructions for Agent
You are currently working on the Bolt listed above.
1. Read the `01_request.md` in the target directory.
2. If strictly following GEAS, do not edit code until `03_plan.md` is sealed.
```

### Lock File Schema (`approved.lock`)

```yaml
req_hash: "abc123..."
req_sealed_at: "2025-01-02T10:00:00"
specs_hash: "def456..."
specs_sealed_at: "2025-01-02T11:00:00"
plan_hash: "ghi789..."
plan_sealed_at: "2025-01-02T12:00:00"
mrp_hash: "jkl012..."
mrp_sealed_at: "2025-01-02T14:00:00"
```

### Agents YAML Schema (`agents.yaml`)

```yaml
agents:
  spec_writer:
    role: "Senior Product Owner"
    goal: "Transform vague inputs into rigorous specifications."
    backstory: |
      You are a veteran Product Owner who adheres to INVEST...

  developer:
    role: "Senior Implementation Specialist"
    goal: "Execute the sealed plan into production-grade code."
    backstory: |
      You are a code craftsman. You value readability and type safety...
```

### Models YAML Schema (`models.yaml`)

```yaml
models:
  gpt4_turbo:
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model_name: "gpt-4-turbo"

  claude_sonnet:
    provider: "anthropic"
    base_url: "https://api.anthropic.com"
    api_key: "${ANTHROPIC_API_KEY}"
    model_name: "claude-sonnet-4-20250514"
```

---

## CI/CD Pipeline

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push/PR to `main` | Run tests, linting, type checking |
| `docs.yml` | Push to `main` | Build and deploy documentation |
| `publish.yml` | Release tag | Publish to PyPI |

### CI Steps

```yaml
steps:
  - uses: actions/checkout@v4
  - name: Install uv
  - name: Set up Python (3.12)
  - name: Install dependencies (uv sync)
  - name: Run Ruff Check
  - name: Run Ruff Format Check
  - name: Run MyPy
  - name: Run Tests
```

---

## Agent Personas

Defined in `.geas/config/agents.yaml`:

| Persona | Role | Goal |
|---------|------|------|
| `spec_writer` | Senior Product Owner | Transform vague inputs into rigorous specifications using INVEST & Gherkin |
| `architect` | Chief Domain Architect | Design scalable file structures enforcing DOMA boundaries and SOLID/DRY principles |
| `developer` | Senior Implementation Specialist | Execute sealed plans into production-grade, typed, tested code (TDD) |
| `doc_writer` | Lead Technical Writer | Maintain documentation following Diátaxis framework |
| `qa_engineer` | QA Automation Engineer | Validate compliance with specs and generate MRP |

### Agent Workflow Constraints

- **spec_writer**: Cannot start until `01_request.md` is sealed
- **architect**: Cannot start until `02_specs.md` is sealed
- **developer**: Cannot start until `03_plan.md` is sealed
- **qa_engineer**: Validates against sealed specs and generates MRP

---

## Current Development Status

### Implemented (v0.1.x)

- [x] `geas init` - Initialize GEAS directory structure
- [x] `geas new` - Create bolt workspace
- [x] `geas checkout` - Switch bolt context
- [x] `geas seal` - Hash and lock artifacts
- [x] `geas status` - Display seal status
- [x] `geas verify` - Verify integrity and sequence
- [x] `geas delete` - Delete bolt
- [x] `geas archive` - Archive completed bolt
- [x] `geas agents` - List personas

### In Progress (Phase 1: Identity)

See `.geas/bolts/step_1_identity/01_request.md` for details:

- [ ] Ed25519 key generation (SSH format)
- [ ] `geas identity add` - Register identities
- [ ] `geas identity list` - List identities
- [ ] `geas identity show` - Show identity details
- [ ] `geas identity revoke` - Revoke keys
- [ ] Sign/verify functions
- [ ] Key resolution (env var → local keyring)

### Roadmap

| Phase | Objective |
|-------|-----------|
| **Phase 1** | Identity & Keyring (`geas identity`) |
| **Phase 2** | Intent Engine (`geas seal intent` with signatures) |
| **Phase 3** | Proof Engine (`geas prove` - test + manifest + MRP) |
| **Phase 4** | Verification Engine (workflow-based validation) |
| **Phase 5** | Lifecycle Management (enhanced `archive`/`delete`) |
| **Phase 6** | CI/CD Integration (GitHub Actions/GitLab CI templates) |

---

## Critical Rules for Agents

### Before Starting Work

1. **Read** `.geas/active_context.md` to identify current bolt
2. **Check** the bolt's `approved.lock` for sealed artifacts
3. **Follow** the seal sequence: `req` → `specs` → `plan` → code → `mrp`
4. **Do NOT** edit code until `03_plan.md` is sealed (if strictly following GEAS)

### During Development

- **Source code location:** `src/geas_ai/`
- **Tests location:** `tests/`
- **Run tests:** `uv run pytest`
- **Run linting:** `uv run ruff check .`
- **Type check:** `uv run mypy src`

### Key Files to Understand

| File | Purpose |
|------|---------|
| `src/geas_ai/main.py` | CLI entry point, command registration |
| `src/geas_ai/utils.py` | Shared utilities (hashing, path resolution) |
| `src/geas_ai/core/content.py` | Templates and default YAML content |
| `src/geas_ai/commands/*.py` | Individual CLI command implementations |

### Error Patterns

- Use `typer.Exit(code=1)` for controlled failures
- Use `console.print("[bold red]Error:[/bold red] ...")` for error messages
- Validate GEAS initialization with `utils.ensure_geas_root()`
- Validate slugs with `utils.validate_slug(name)`

### Code Quality Checklist

Before submitting any code:

- [ ] All functions have type hints
- [ ] All public functions have Google-style docstrings
- [ ] Tests cover happy paths, edge cases, and failure modes
- [ ] `uv run pytest` passes
- [ ] `uv run ruff check .` passes
- [ ] `uv run mypy src` passes
- [ ] No repeated logic (DRY principle applied)

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                     GEAS-AI Quick Reference                      │
├─────────────────────────────────────────────────────────────────┤
│ Package: geas-ai          │ Python: >=3.10                      │
│ CLI: geas                 │ Manager: uv                         │
├─────────────────────────────────────────────────────────────────┤
│ GEAS COMMANDS                                                    │
│   geas init               │ Initialize GEAS                     │
│   geas new <name>         │ Create bolt                         │
│   geas seal <target>      │ Seal artifact (req/specs/plan/mrp)  │
│   geas status             │ Show status                         │
│   geas verify             │ Verify integrity                    │
│   geas checkout <name>    │ Switch context                      │
│   geas archive <name>     │ Archive bolt                        │
├─────────────────────────────────────────────────────────────────┤
│ DEV COMMANDS                                                     │
│   uv sync                 │ Install dependencies                │
│   uv run pytest           │ Run tests                           │
│   uv run ruff check .     │ Lint code                          │
│   uv run mypy src         │ Type check                          │
├─────────────────────────────────────────────────────────────────┤
│ SEAL SEQUENCE: req → specs → plan → [code] → mrp                 │
├─────────────────────────────────────────────────────────────────┤
│ PATHS                                                            │
│   .geas/active_context.md │ Current bolt pointer                │
│   .geas/bolts/<name>/     │ Bolt workspace                      │
│   src/geas_ai/            │ Source code                         │
│   tests/                  │ Test suite                          │
└─────────────────────────────────────────────────────────────────┘
```

---

*This document should be read by any AI agent before contributing to the GEAS-AI repository.*
