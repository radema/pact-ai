# Feature Specs: PACT Seal Mechanism (`pact seal`)

**Feature:** `pact seal`
**Role:** Spec Writer
**Status:** DRAFT

## 1. Overview

The `pact seal` command acts as the cryptographic "Sign-off" in the PACT workflow. It locks a specific stage of the bolt (Specs or Plan) by hashing the content of the relevant markdown file and storing it in `approved.lock`. This ensures that subsequent steps are based on immutable, approved instructions.

## 2. User Stories

### US 2.1: Seal the Specs

**As a** Spec Writer or PM
**I want to** run `pact seal specs`
**So that** the `02_specs.md` is locked and ready for the Architect to plan against.

### US 2.2: Seal the Plan

**As a** Architect
**I want to** run `pact seal plan`
**So that** the `03_plan.md` is locked and ready for the Developer to execute.

## 3. Implementation Details (Requirements)

### 3.1 Input Arguments

* **Target** (String, Required). Allowed values:
  * `specs` -> Targets `02_specs.md`
  * `mrp` -> Targets `mrp/summary.md` (Optional for now, but good for completeness).
  * `plan` -> Targets `03_plan.md`

### 3.2 Logic Flow

The command MUST:

1. Identify the current bolt using `.pacts/active_context.md`.
    * **Validation**: If the folder pointed to by context does not exist, fail with "Active Bolt not found on disk".

2. Locate the target file in the active bolt directory.
    * If file missing, fail.
3. Calculate the **SHA-256** hash of the target file content.
    * *Note:* content should be normalized (strip trailing whitespace?) to avoid CRLF issues.
4. Update/Create `approved.lock` in the bolt directory.
    * Format: YAML Key-Value pairs.
    * Keys: `{target}_hash`, `{target}_sealed_at`.

### 3.3 The Lock File (`approved.lock`)

* It serves as the "Gate".
* If `pact seal specs` is run, it updates `specs_hash`.
* If `pact seal plan` is run, it updates `plan_hash`.
* If `pact seal mrp` is run, it updates `mrp_hash`.

### 3.4 Additional Commands

#### 3.4.1 `pact seal status`

* Reads `approved.lock` and prints a table of what is sealed and when.

#### 3.4.2 `pact seal verify`

* Re-calculates hashes of the actual files on disk.
* Compares them against `approved.lock`.
* Outputs PASS/FAIL for each artifact.

## 4. Gherkin Scenarios

```gherkin
Feature: Seal Bolt Stages

  Scenario: Seal Specs
    Given I am working on bolt "feature-x"
    And "02_specs.md" exists
    When I run "pact seal specs"
    Then "approved.lock" is created/updated
    And "approved.lock" contains keys "specs_hash" and "specs_sealed_at"

  Scenario: Seal Plan
    Given I am working on bolt "feature-x"
    And "03_plan.md" exists
    When I run "pact seal plan"
    Then "approved.lock" is created/updated
    And "approved.lock" contains keys "plan_hash" and "plan_sealed_at"

  Scenario: File Missing
    Given "03_plan.md" does not exist
    When I run "pact seal plan"
    Then exit with error "File 03_plan.md not found"
```
