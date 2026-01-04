# Specs: Proof Engine (Phase 3)

**Status:** APPROVED
**Source:** [01_request.md](./01_request.md)
**Prerequisites:** Phase 2 (Intent Engine)

## 1. Architecture & Modules

The Proof Engine binds the Code Implementation to the Sealed Intent via Test Evidence.

### 1.1 Module Organization

* `src/geas_ai/core/testing.py`: Test runner execution and result capture.
* `src/geas_ai/core/walker.py`: File system traversal with `.gitignore` support.
* `src/geas_ai/core/manifest.py`: Cryptographic manifest generation and Merkle Tree logic.
* `src/geas_ai/commands/prove.py`: Implementation of `geas prove`.

## 2. Data Structures

### 2.1 Manifest Models (`src/geas_ai/schemas/manifest.py`)

```python
class TestResultInfo(BaseModel):
    passed: bool
    exit_code: int
    duration_seconds: float
    timestamp: datetime

class Manifest(BaseModel):
    bolt_id: str
    generated_at: datetime
    scope: List[str]
    files: Dict[str, str]  # Path -> SHA256
    root_hash: str
    test_result: TestResultInfo
```

## 3. Core Logic & Algorithms

### 3.1 Merkle Root Calculation (`manifest.py`)

1. **Input**: Dictionary of `{filepath: hash}`.
2. **Leaves**: Sort filepaths -> Extract hashes.
3. **Leaf Hashing**: Double-hash usually not needed for simple integrity, but we hash the leaf *value*.
4. **Tree Construction**:
    * Pair adjacent nodes `(A, B)`.
    * Parent = `SHA256(A + B)`.
    * If odd count, `Parent = SHA256(Last + Last)`.
    * Repeat until Root.

### 3.2 Directory Walking (`walker.py`)

* **Libraries**: Use `pathspec` for robust gitignore matching.
* **Logic**:
    1. Recursively list files in `scope` directories.
    2. Filter against `.gitignore` (if present).
    3. Exclude `.geas/`, `__pycache__`, `.git`.

### 3.3 Test Execution (`testing.py`)

* **Logic**: `subprocess.run(shlex.split(command), timeout=N, capture_output=True)`.
* **Safety**: Ensure cwd is set to project root.

## 4. CLI Specifications: `geas prove`

* **Arguments**:
  * `--scope`: (Optional) Comma-separated dirs (def: `src,tests`).
  * `--skip-tests`: (Flag) For manual override/debugging.
* **Logic**:
    1. **Helper check**: `ensure_geas_root`, `get_active_bolt`.
    2. **State check**: Is `SEAL_INTENT` present?
    3. **Testing**: Run tests (unless skipped). If fail -> Exit.
    4. **Manifesting**: Walk files -> Hash -> Merkle Root.
    5. **Artifact Generation**: Write `mrp/manifest.json`, `mrp/tests.log`.
    6. **Output**: Print success message instructing the Agent to write `mrp/summary.md` and then run `geas seal mrp`.

*Note: `geas prove` does NOT seal the MRP. This allows the QA Agent to write the `summary.md` qualitative report before final sealing.*

## 5. Dependencies

* `pathspec` (New): For gitignore parsing.
* `pydantic` (Existing).
* `cryptography` (Existing).

## 6. Testing Strategy

### 6.1 Unit Tests

* `test_merkle_root`: Verify root calculation against known vectors.
* `test_walker`: Verify exclusion of ignored files.
* `test_runner`: Mock subprocess to verify timeout/output capture.

### 6.2 Integration Tests

* `test_prove_flow`: Full `geas prove` execution with dummy tests.

## 7. Behavioral Specifications (Gherkin)

**Feature:** Prove Implementation Verification
  As a QA Engineer
  I want to generate cryptographic proof of code validity
  So that I can verify the implementation matches the sealed execution plan

  **Scenario:** Successful Proof Generation
    Given the Intent is sealed for bolt "feature-login"
    And valid tests exist in "tests/"
    And a valid agent identity "claude-qa" is configured
    When I run "geas prove --identity claude-qa"
    Then the tests should execute successfully
    And a "mrp/manifest.json" file should be created
    And the "lock.json" ledger should contain a "SEAL_MRP" event
    And the event should be signed by "claude-qa"

  **Scenario:** Test Failure Abort
    Given the tests are configured to fail
    When I run "geas prove"
    Then the command should fail with exit code 1
    And no "SEAL_MRP" event should be added to the ledger
    And "mrp/manifest.json" should not be created (or be marked invalid)

  **Scenario:** Unsealed Intent Block
    Given the Intent is NOT sealed
    When I run "geas prove"
    Then the command should fail with "Intent not sealed"
