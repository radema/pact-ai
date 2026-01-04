# Merge Readiness Pack (MRP)

**Bolt:** feature-pact-new
**Status:** READY TO MERGE
**QA Engineer:** @qa_engineer
**Date:** 2025-12-26

## 1. Compliance Checklist

- [x] **Specs Met**: `pact new` creates bolt directory and active_context.md.
- [x] **Validation**: Invalid slugs are rejected.
- [x] **Idempotency**: Duplicate bolts are blocked.
- [x] **Templates**: 01_request.md is created from template.
- [x] **Documentation**: README and CHANGELOG updated.

## 2. Verification Evidence

### Manual Test 1: Successful Creation

* **Input**: `pact new feature-login`
- **Result**: Success message. Context updated. Folders created.
- **Verdict**: PASS

### Manual Test 2: Validation

* **Input**: `pact new "Invalid Name"`
- **Result**: "Invalid slug format" error.
- **Verdict**: PASS

### Manual Test 3: Duplication

* **Input**: `pact new feature-login` (Twice)
- **Result**: "Bolt 'feature-login' already exists."
- **Verdict**: PASS

### 3. Logic Proof

```text
$ mkdir new_bolt_test && cd new_bolt_test && uv run --project .. pact init && uv run --project .. pact new feature-login

╭───────────────────────── PACT Protocol ─────────────────────────╮
│ Success! PACT initialized at /root/pact-ai/new_bolt_test/.pacts │
...
╰─────────────────────────────────────────────────────────────────╯
╭────────────────────── Bolt: feature-login ──────────────────────╮
│ Bolt Started!                                                   │
│                                                                 │
│ Workspace: .pacts/bolts/feature-login                           │
│ Context: Updated                                                │
╰─────────────────────────────────────────────────────────────────╯

$ uv run --project .. pact new "Invalid Name"
Error: Invalid name 'Invalid Name'. Use only lowercase letters, numbers, hyphens, and underscores.
...
Exit code: 2

$ uv run --project .. pact new feature-login
Error: Bolt 'feature-login' already exists.
Exit code: 1
```

## 4. Artifacts

* Source Code: `src/pact_cli/commands/new.py`
- Source Code: `src/pact_cli/utils.py`
- Templates: `src/pact_cli/core/content.py`
