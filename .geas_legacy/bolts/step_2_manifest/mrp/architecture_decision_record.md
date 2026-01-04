# Architecture Decision Record (ADR): Ledger Unification

**Date:** 2026-01-04
**Status:** APPROVED
**Topic:** Deprecation of `approved.lock` in favor of `lock.json`

## Context

Originally, GEAS used `approved.lock` (YAML) for simple artifact sealing (Phase 0) and planned to introduce `lock.json` (JSON Hash Chain) for the Intent Engine (Phase 2).

This created a "Split Brain" risk where seal state could exist in two places, violating the Single Source of Truth principle.

## Decision

1. **Single Ledger**: We define `lock.json` as the **sole** cryptographic ledger for the bolt.
2. **Deprecation**: `approved.lock` is deprecated immediately.
3. **Command Updates**:
    * `geas seal req` -> Writes `SEAL_REQ` event to `lock.json`.
    * `geas seal specs` -> Writes `SEAL_SPECS` event to `lock.json`.
    * `geas seal plan` -> Writes `SEAL_PLAN` event to `lock.json`.
    * `geas seal intent` -> Writes `SEAL_INTENT` event to `lock.json`.

## QA Implications

When validating the implementation of Phase 2, the QA Engineer must ensure:

* [ ] `geas seal` commands **DO NOT** create or update `approved.lock`.
* [ ] `geas seal` commands **DO** create/update `lock.json`.
* [ ] The `lock.json` structure follows the Hash Chain schema (events have `prev_hash`).
* [ ] Existing tests referencing `approved.lock` must be updated or marked as legacy/removed.
