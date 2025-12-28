# Implementation Plan: feature-bolt-commands

**Status:** DRAFT
**Role:** Chief Domain Architect

## Overview

This bolt refactors the CLI structure to support advanced lifecycle management commands (`checkout`, `delete`, `archive`) and enhances the verification logic.

## Proposed Changes

### 1. Refactor `src/pact_cli/commands/seal.py`

* Add `"req": "01_request.md"` to the `valid_targets` map.
* Update the `seal` function to handle the new target.

### 2. Create `src/pact_cli/commands/status.py`

* Implement `status(bolt: Optional[str] = None)`.
* Logic:
  * If `bolt` is provided, use that path.
  * Otherwise, fetch from `utils.get_active_bolt_path()`.
  * Display the current seal status table (extracted from the current `seal status` logic).

### 3. Create `src/pact_cli/commands/verify.py`

* Implement `verify(bolt: Optional[str] = None)`.
* Logic:
  * Fetch `bolt_path`.
  * Run cryptographic hash checks.
  * **Sequence Check**: Verify timestamps in `approved.lock`: `req_sealed_at` <= `specs_sealed_at` <= `plan_sealed_at` <= `mrp_sealed_at`.
  * Report errors if the sequence is violated.

### 4. Create `src/pact_cli/commands/lifecycle.py`

* Implement `checkout(name: str)`: Updates `.pacts/active_context.md`.
* Implement `delete(name: str)`:
  * Prevents deleting the active bolt.
  * Uses `shutil.rmtree`.
* Implement `archive(name: str)`:
  * Runs a silent verification.
  * Moves the folder to `.pacts/archive/` using `shutil.move`.

### 5. Update `src/pact_cli/main.py`

* Register new commands: `pact status`, `pact verify`, `pact checkout`, `pact delete`, `pact archive`.
* Mark `pact seal status/verify` as deprecated in help text (or remove them).

### 6. Update `src/pact_cli/utils.py`

* Add helpers for sequence validation.
* Update `get_active_bolt_name()` if needed.

## Verification Plan

### Automated Tests

* `test_checkout`: Verify context file updates.
* `test_delete_active_bolt_fails`: Ensure safety check works.
* `test_verify_sequence`: Mock lock files with out-of-order timestamps and verify failure.
* `test_archive_unverified_fails`: Ensure archival requires a full pass.

### Manual Verification

1. Run `pact seal req` on the new bolt.
2. Run `pact status`.
3. Switch bolts with `pact checkout`.
4. Try to archive a bolt without a seal and expect failure.

## Constraints Check

* [x] No changes to existing bolt data.
* [x] Maintain backwards compatibility for existing `approved.lock` files where possible.
