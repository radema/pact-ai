# Specifications: feature-bolt-commands

**Status:** DRAFT
**Role:** Senior Product Owner

## User Stories

### US1: Sealing the Request

As a user, I want to cryptographically lock my initial request (`01_request.md`) so that the baseline for the Bolt is immutable once defined.

**Acceptance Criteria:**

* **AC 1.1:** `pact seal req` must be a valid command.
* **AC 1.2:** It must calculate the SHA-256 hash of `01_request.md`.
* **AC 1.3:** The hash and timestamp must be stored in `approved.lock`.

### US2: Enhanced Status & Verification

As a user, I want dedicated commands to check the status and verify the integrity of my bolts, with clear sequence validation.

**Acceptance Criteria:**

* **AC 2.1:** Implement `pact status [-b <bolt-name>]`. By default, it shows the status of the active bolt.
* **AC 2.2:** Implement `pact verify [-b <bolt-name>]`.
* **AC 2.3:** `pact verify` must check the cryptographic integrity of all sealed artifacts.
* **AC 2.4:** `pact verify` must enforce "Sequence Verification": `req` must be sealed before `specs`, `specs` before `plan`, and `plan` before `mrp`.
* **AC 2.5:** `pact seal status` and `pact seal verify` should be deprecated or redirected to the new top-level commands.

### US3: Context Switching (Checkout)

As a developer, I want to easily switch between different units of work (bolts) using a familiar command.

**Acceptance Criteria:**

* **AC 3.1:** Implement `pact checkout <bolt-name>`.
* **AC 3.2:** The command must update `.pacts/active_context.md` with the new bolt's details.
* **AC 3.3:** It must fail if the `<bolt-name>` does not exist in `.pacts/bolts/`.

### US4: Bolt Cleanup (Delete)

As a user, I want to remove bolts that are no longer needed to keep my workspace clean.

**Acceptance Criteria:**

* **AC 4.1:** Implement `pact delete <bolt-name>`.
* **AC 4.2:** It must NOT allow deleting the currently active bolt (as defined in `active_context.md`).
* **AC 4.3:** It must prompt for confirmation before deletion (or provide a `--force` flag).

### US5: Bolt Archival

As a maintainer, I want to move completed and verified bolts to an archive to preserve the audit trail without cluttering the active bolts directory.

**Acceptance Criteria:**

* **AC 5.1:** Implement `pact archive <bolt-name>`.
* **AC 5.2:** It must only succeed if the bolt is "Fully Verified" (all artifacts `req`, `specs`, `plan`, `mrp` are sealed and hashes match).
* **AC 5.3:** Upon success, the entire bolt folder must be moved from `.pacts/bolts/` to `.pacts/archive/`.

## Constraints

1. **Immutability**: Once an artifact is sealed, any change should cause `pact verify` to fail.
2. **Active Context**: The `active_context.md` file must always reflect the current bolt.
3. **No Logic Drift**: These commands manage the protocol state, not the application logic in `src/`.
