# Implementation Plan: Verification Engine

**Bolt:** step_4_archival
**Status:** DRAFT

## 1. Sequence of Operations

### Step 1: Foundations (Must be done first)

*Dependencies: None*

1. **Create `src/geas_ai/schemas/workflow.py`**:
   - Define `WorkflowStage` (id, action, role, prerequisite).
   - Define `WorkflowConfig` (intent, stages, tests).
2. **Update `src/geas_ai/schemas/verification.py`**:
   - Define `ViolationCode` Enum.
   - Define `ValidationResult` and its subclasses.
3. **Update `src/geas_ai/schemas/ledger.py`**:
   - Add `APPROVE` to `LedgerAction` enum.
4. **Create `src/geas_ai/core/workflow.py`**:
   - Implement `load_workflow_config()` to read `.geas/config/workflow.yaml`.
   - Implement default workflow generation if file missing.

### Step 2: Parallel Development Tracks

This phase can be split into two parallel tracks.

#### Track A: Core Verification Logic

*Dependencies: Step 1*

1. **Create `src/geas_ai/core/verification.py`**:
   - **Chain Integrity**: Implement `validate_chain_integrity` (hash-chain traversal).
   - **Signatures**: Implement `validate_signatures` (key lookup & modification check).
   - **Workflow**: Implement `validate_workflow_compliance` (mapping ledger events to `WorkflowConfig` stages).
   - **Content**: Implement `validate_content_integrity` (re-hashing files).

#### Track B: Ledger Visualization (Status CLI)

*Dependencies: Step 1 (Ledger Schemas)*

1. **Refactor `src/geas_ai/commands/status.py`**:
   - **Delete**: Remove all legacy PACT code reading `approved.lock`.
   - **Implement**: Load `lock.json` using existing `LedgerManager`.
   - **Display**: Create a Rich Table showing the event history (Sequence, Timestamp, Action, Signer).
   - **Features**: Show "Current State" based on the last event type.

### Step 3: Verification & Approval CLI

*Dependencies: Track A & Track B*

1. **Refactor `src/geas_ai/commands/verify.py`**:
   - **Delete**: Remove legacy PACT verification.
   - **Integration**: Call `core.verification` functions.
   - **Formatting**: Implement nice Rich output for PASS/FAIL.
   - **Flags**: Add `--content` and `--json`.
2. **Create `src/geas_ai/commands/approve.py`**:
   - Implement `geas approve` command.
   - Validate identity is Human.
   - Create `APPROVE` event payload (`{"mrp_hash": ...}`).
   - Append to Ledger.

### Step 4: Configuration Cleanup

1. **Bootstrap**: Update `geas init` logic (in `init.py` or `main.py`) to create a default `workflow.yaml` if it doesn't exist, ensuring new repos work out of the box.

### Step 5: Testing

1. **Unit Tests**:
   - `tests/core/test_verification.py`: Test logic in isolation.
   - `tests/schemas/test_workflow.py`: Test config parsing.
2. **Integration Tests**:
   - `tests/commands/test_verify.py`: Run verify on a manufactured "bad" bolt and a "good" bolt.
   - `tests/commands/test_status.py`: Verify output format.

## 2. Checkpoints

- **CP1**: Foundation Schemas & Config Loader complete.
- **CP2**: Core Verification Logic (Track A) complete & Tested.
- **CP3**: Status Command (Track B) working.
- **CP4**: Verify & Approve Commands complete.

## 3. Risks & Mitigations

- **Risk**: Legacy PACT code in `verify.py` might be entangled with `utils.py`.
  - **Mitigation**: Carefully inspect imports. If `utils.py` has legacy code, deprecate or remove it safely.
- **Risk**: Missing `workflow.yaml` in existing bolts.
  - **Mitigation**: Verification should fail gracefully (or warn) if workflow is missing, or default to a minimal implicit workflow.
