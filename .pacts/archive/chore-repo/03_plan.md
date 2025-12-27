# Implementation Plan: chore-repo

**Status:** DRAFT
**Role:** Chief Domain Architect

## Overview

This bolt focuses on repository hygiene and automation. No logic changes will be made to the `src/` directory.

## Proposed Changes

### 1. Root Directory: Licensing

* **Action**: Create `LICENSE-MIT` and `LICENSE-APACHE`.
* **Action**: Update `README.md` to include a "License" section referencing both files.
* **Rationale**: Ensure legal clarity and follow modern tool standards.

### 2. Root Directory: Contribution Guide

* **Action**: Create `CONTRIBUTING.md`.
* **Content**:
  * Setup instructions using `uv sync`.
  * Workflow explanation: `pact new` -> Edit -> `pact seal` -> `pact status`.
  * Testing requirements: All new logic must have `pytest` cases.
  * Linting: Must pass `ruff` and `mypy`.
* **Rationale**: Standardize the contributor onboarding process.

### 3. Root Directory: Pre-commit Configuration

* **Action**: Create `.pre-commit-config.yaml`.
* **Hooks**:
  * `ruff`: For linting and formatting.
  * `mypy`: For static type checking.
  * `trailing-whitespace` & `end-of-file-fixer`: General hygiene.
* **Rationale**: Prevent broken or poorly formatted code from being committed.

### 4. GitHub Workflow: CI

* **Action**: Create `.github/workflows/ci.yml`.
* **Steps**:
  * Checkout code.
  * Install `uv`.
  * Set up Python (3.10+).
  * Install dependencies (`uv sync`).
  * Run `ruff check .`.
  * Run `ruff format --check .`.
  * Run `mypy src`.
  * Run `pytest`.
* **Rationale**: Ensure every PR is vetted by the automated quality gates.

## Verification Plan

### Automated Tests

* `pre-commit run --all-files`: Verify all current files pass the new quality gates.
* `pytest`: Ensure current tests still pass in the CI-like environment.

### Manual Verification

1. Verify `LICENSE-MIT` and `LICENSE-APACHE` are readable.
2. Verify `CONTRIBUTING.md` links and commands are correct.
3. Simulate a CI run locally using `uv run`.

## Constraints Check

* [x] No changes to `src/` logic.
* [x] Uses `uv` for dependency management.
* [x] Implements dual-licensing.
