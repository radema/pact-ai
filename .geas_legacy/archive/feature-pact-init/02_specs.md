# Feature Specs: PACT CLI Initialization

**Feature:** `pact init`
**Role:** Spec Writer
**Status:** DRAFT

## 1. Overview

The `pact init` command bootstraps the PACT governance protocol in a repository. It creates the necessary directory structure and configuration files to enable Agentic workflows.

## 2. User Stories

### US 2.1: Bootstrap Repository

**As a** Developer
**I want to** initialize PACT in my project
**So that** I can start using the Agentic Governance Layer.

## 3. Implementation Details (Requirements)

The command `pact init` MUST perform the following operations atomically.

### 3.1 Pre-conditions

* The command checks if the `.pacts` directory already exists in the current working directory.
* If `.pacts` exists, the command MUST abort with an error message: "PACT is already initialized."

### 3.2 Directory Structure

The command MUST create the following directory tree:

```
root/
├── .pacts/
│   ├── config/
│   ├── bolts/
│   └── archive/
```

### 3.3 Configuration Generation

The command MUST generate the following files within `.pacts/config/` with default content.

#### 3.3.1 `agents.yaml`

Should contain the 5 default personas (Spec Writer, Architect, Developer, Doc Writer, QA Engineer) as defined in `docs/TECHNICAL_SPECS.md`.

#### 3.3.2 `models.yaml`

Should contain the infrastructure skeleton for LLM providers (e.g., OpenAI, Local Mistral).

### 3.4 Manifesto Creation

The command MUST write a `PACT_MANIFESTO.md` file in the project solution root.

* **Content:** A brief declaration of the PACT protocol axioms (as summarized from `WHITE_PAPER.md`).

## 4. Gherkin Scenarios

```gherkin
Feature: PACT Initialization

  Scenario: Successful Initialization
    Given the directory does not contain a ".pacts" folder
    When I run "pact init"
    Then the ".pacts" directory is created
    And the ".pacts/config" directory is created
    And the ".pacts/bolts" directory is created
    And the ".pacts/archive" directory is created
    And the file ".pacts/config/agents.yaml" exists
    And the file ".pacts/config/models.yaml" exists
    And the file "PACT_MANIFESTO.md" exists

  Scenario: Already Initialized
    Given the directory contains a ".pacts" folder
    When I run "pact init"
    Then the command exits with an error code
    And the message "PACT is already initialized" is displayed
```
