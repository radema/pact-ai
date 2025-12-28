# Feature Request: Agent Configuration & Testing Infrastructure (Phase 1)

**Status:** APPROVED FOR PLANNING
**Bolt:** `feature-agents`

## Context

This bolt addresses the remaining pending tasks for **Phase 1: The Core Protocol** of the PACT-AI Roadmap.
The focus is on two key pillars:

1. **Agent Transparency**: enabling users to inspect the current agent configuration via the CLI.
2. **Quality Assurance**: establishing a robust testing framework (pytest) and integrating it into the CI pipeline.

## Goals

1. **Refine Agent Definitions**: Update the default system prompts for critical agents (such as `developer`, `qa_engineer`) to enforce testing standards.
2. **CLI Visibility**: Implement `pact agents` to allow users to view the current agent roster and configurations.
3. **Testing Infrastructure**: Integrate `pytest` and ensure tests run automatically in the CI pipeline.

## Detailed Requirements

### 1. Update Agent Descriptions (`agents.yaml` defaults)

* **Target File**: `src/pact_cli/core/content.py` (Source of Truth for default templates).
* **Action**: Update the default descriptions/system prompts for the entire agent roster to strictly enforce PACT methodology:
  * `spec_writer`: Enforce Gherkin syntax and "Acceptance Criteria" and sealing of `01_request.md` and then `02_specs.md`.
  * `architect`: Enforce "Clean Architecture" and sealing of `03_plan.md`.
  * `developer`: STRICT requirement for TDD, `pytest`, and halting if the plan is flawed.
  * `doc_writer`: Add responsibilities for "Context Window" maintenance and `mrp/summary.md` generation.
  * `qa_engineer`: Define role as the one who executes developer tests and blocks merge if docs/tests are missing.
* **Verification**: Ensure these changes propagate to `pact new` (when generating a new bolt) or `pact init`. Check for backward compatibility issues (breaking changes) when loading existing configs.

### 2. Implement `pact agents` Command

* **New Command**: `pact agents`
* **Functionality**:
  * Read the `agents.yaml` from the `active_bolt` (if set) or the global `.pacts` config (fallback).
  * Display a formatted list of available Agents (Name, Role, short Description/Model).
  * **Note**: Phase 2 will handle *creation/editing/deletion* and atomic file structures. This phase is **read-only**.

### 3. Testing Standard & CI Integration

* **Framework**: `pytest`.
* **Scope**:
  * Add unit tests scripts related to pact_cli.
  * Ensure critical paths (init, new, seal) have baseline coverage.
* **CI/CD**: Update the GitHub Actions workflow to run `pytest` on every push/PR.
