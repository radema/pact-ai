# Feature Specs: PACT CLI Task Lifecycle (`pact new`)

**Feature:** `pact new`
**Role:** Spec Writer
**Status:** DRAFT

## 1. Overview

The `pact new` command initiates a new Unit of Work (a "Bolt"). It orchestrates the creation of the bolt's workspace and updates the global context to focus the Agentic IDE on this new task.

## 2. User Stories

### US 2.1: Start a New Task

**As a** Developer or PM
**I want to** run `pact new <bolt_name>`
**So that** a dedicated workspace is created for the feature and the AI agent knows where to work.

### US 2.2: Context Switching

**As a** Developer
**I want to** have an `active_context.md` file automatically updated
**So that** my AI tool (cursor/antigravity) always knows the current active task without manual prompting.

## 3. Implementation Details (Requirements)

### 3.1 Input Arguments

* **Argument**: `bolt_name` (String, Required).
  * Constraint: Must be URL-safe (kebab-case recommended). If the user provides "My Feature", it should ideally be slugified or rejected. **Decision**: Reject invalid characters (allow alphanumeric, hyphens, underscores).

### 3.2 File System Operations

The command MUST:

1. Check if `.pacts` exists (Pre-condition). If not, fail with "PACT not initialized".
2. Create directory: `.pacts/bolts/<bolt_name>/`.
3. Create file: `.pacts/bolts/<bolt_name>/01_request.md`
    * the request file is created by default with a template similar this bolt's request

### 3.3 Context Management

The command MUST create/overwrite `.pacts/active_context.md` with the following format:

```markdown
# Active Context

**Current Bolt:** <bolt_name>
**Path:** .pacts/bolts/<bolt_name>
**Started:** <timestamp>

## Instructions for Agent
You are currently working on the Bolt listed above.
1. Read the `01_request.md` in the target directory.
2. If strictly following PACT, do not edit code until `03_plan.md` is sealed.
```

### 3.4 Error Handling

The command MUST fail if:

* The `.pacts` directory does not exist.
* A bolt with the same `<bolt_name>` already exists in `.pacts/bolts/`.
  * Error Message: "Bolt '<bolt_name>' already exists."

## 4. Gherkin Scenarios

```gherkin
Feature: Create New Bolt

  Scenario: Create a valid bolt
    Given PACT is initialized
    When I run "pact new feature-login"
    Then the directory ".pacts/bolts/feature-login" is created
    And the file ".pacts/bolts/feature-login/01_request.md" exists
    And the file ".pacts/active_context.md" contains "Current Bolt: feature-login"

  Scenario: PACT not initialized
    Given the ".pacts" folder does not exist
    When I run "pact new some-feature"
    Then the command exits with error "PACT is not initialized"

  Scenario: Bolt already exists
    Given ".pacts/bolts/existing-feature" exists
    When I run "pact new existing-feature"
    Then the command exits with error "Bolt 'existing-feature' already exists"
```
