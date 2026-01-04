# Request: Proof Engine / MRP (Phase 3)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 3)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Phase 3)
**Prerequisite:** Phase 2 (Intent Engine)

## Context

The Proof Engine generates the **Merge Request Package (MRP)** — a post-code evidence package that proves the validity of the implementation. It creates cryptographic evidence that "Code Version X passed Test Suite Y."

The MRP consists of:

- `mrp/summary.md` — Human-readable summary of what was built.
- `mrp/tests.log` — Captured test execution output.
- `mrp/manifest.json` — Cryptographic fingerprint (Merkle Tree) of the source code at proof time.

This phase implements the complete proof generation workflow, including test execution, code snapshotting, and MRP sealing.

## Goals

Implement the proof generation mechanism, test runner integration, and MRP sealing.

**Primary CLI Command:**

- `geas prove`: Run tests, generate MRP, and seal it with agent signature.

## Requirements

### 1. State Validation

Before generating proof, validate the Bolt state.

**Pre-conditions:**

1. GEAS is initialized in the repository.
2. An active Bolt exists.
3. Intent is already sealed (a `SEAL_INTENT` event exists in `lock.json`).
4. MRP is not already sealed (no `SEAL_MRP` event exists).

### 2. Test Runner Integration

Execute the configured test command and capture results.

**Configuration Source:** `workflow.yaml`

```yaml
test_command: "pytest -v"
test_timeout: 300  # seconds
```

**Function Signature:**

```python
def run_tests(command: str, timeout: int, cwd: Path) -> TestResult:
    """
    Execute the test command and capture output.

    Args:
        command: Shell command to execute.
        timeout: Maximum execution time in seconds.
        cwd: Working directory for test execution.

    Returns:
        TestResult with passed, exit_code, stdout, stderr, duration.

    Raises:
        TimeoutError: If execution exceeds timeout.

    Example:
        >>> result = run_tests("pytest -v", 300, Path("/project"))
        >>> result.passed
        True
        >>> result.duration_seconds
        12.5
    """
```

**TestResult Schema:**

```python
class TestResult(BaseModel):
    passed: bool               # True if exit_code == 0
    exit_code: int             # Process exit code
    stdout: str                # Standard output
    stderr: str                # Standard error
    duration_seconds: float    # Execution duration
    command: str               # Command that was executed
    timestamp: datetime        # When tests were run
```

### 3. Directory Walker with .gitignore Support

Walk source directories while respecting `.gitignore` rules.

**Function Signature:**

```python
def walk_source_files(
    root: Path,
    include_dirs: list[str],
    gitignore_path: Path | None = None
) -> Iterator[Path]:
    """
    Walk directories and yield files, respecting .gitignore.

    Args:
        root: Repository root path.
        include_dirs: Directories to include (e.g., ["src/", "tests/"]).
        gitignore_path: Path to .gitignore file (optional).

    Yields:
        Path objects for each included file.

    Example:
        >>> list(walk_source_files(Path("."), ["src/", "tests/"]))
        [Path("src/main.py"), Path("tests/test_main.py"), ...]
    """
```

**Implementation Notes:**

- Use `pathspec` library for correct `.gitignore` semantics.
- Handle nested `.gitignore` files.
- Exclude common patterns: `.git/`, `__pycache__/`, `*.pyc`, etc.

### 4. Manifest Generator

Generate the cryptographic manifest of source code.

**Manifest Schema (`mrp/manifest.json`):**

```json
{
  "generated_at": "2025-01-02T14:30:00Z",
  "bolt_id": "feature-login",
  "scope": ["src/", "tests/"],

  "files": {
    "src/auth/login.py": "sha256:...",
    "src/auth/oauth.py": "sha256:...",
    "tests/test_login.py": "sha256:..."
  },

  "root_hash": "sha256:...",

  "test_result": {
    "passed": true,
    "exit_code": 0,
    "duration_seconds": 12.5
  }
}
```

**Algorithm:**

1. Walk all source files using the directory walker.
2. Hash each file with SHA-256.
3. Sort file paths alphabetically for deterministic output.
4. Calculate Merkle root hash from sorted file hashes.
5. Include test result metadata.

**Function Signature:**

```python
def generate_manifest(
    bolt_id: str,
    scope: list[str],
    root: Path,
    test_result: TestResult
) -> Manifest:
    """
    Generate the code manifest with Merkle root.

    Args:
        bolt_id: Identifier of the current Bolt.
        scope: List of directories to include.
        root: Repository root path.
        test_result: Results from test execution.

    Returns:
        Manifest object with file hashes and root hash.

    Example:
        >>> manifest = generate_manifest("feature-login", ["src/"], Path("."), test_result)
        >>> manifest.root_hash
        "sha256:abc123..."
    """
```

### 5. Merkle Root Calculation

Calculate the Merkle root hash from file hashes.

**Algorithm:**

1. Collect all file hashes as leaf nodes.
2. Sort leaves alphabetically by file path.
3. Pair leaves and hash pairs to create parent nodes.
4. Recurse until a single root hash remains.
5. If odd number of leaves, duplicate the last leaf.

**Function Signature:**

```python
def calculate_merkle_root(file_hashes: dict[str, str]) -> str:
    """
    Calculate Merkle root from file hashes.

    Args:
        file_hashes: Dict mapping file paths to their SHA-256 hashes.

    Returns:
        Merkle root hash in format "sha256:hexdigest".

    Example:
        >>> hashes = {"a.py": "sha256:aaa...", "b.py": "sha256:bbb..."}
        >>> calculate_merkle_root(hashes)
        "sha256:abc123..."
    """
```

### 6. MRP Artifact Generation

Generate all MRP artifacts in the `mrp/` folder.

**Artifacts:**

| File | Purpose | Content |
|------|---------|---------|
| `mrp/manifest.json` | Code snapshot | File hashes + Merkle root |
| `mrp/tests.log` | Test output | stdout + stderr from test run |
| `mrp/summary.md` | Human summary | Template with completion status |

**Summary Template (`mrp/summary.md`):**

```markdown
# Merge Request Package Summary

**Bolt:** feature-login
**Generated:** 2025-01-02T14:30:00Z

## Test Results

- **Status:** PASSED ✅
- **Duration:** 12.5 seconds
- **Exit Code:** 0

## Code Manifest

- **Files:** 15
- **Scope:** src/, tests/
- **Root Hash:** sha256:abc123...

## Intent Reference

This implementation fulfills the requirements sealed in:
- 01_request.md (sha256:a1b2c3...)
- 02_specs.md (sha256:d4e5f6...)

---

*This MRP was generated by GEAS v3.1*
```

### 7. SEAL_MRP Event

Seal the MRP with agent signature.

**Event Structure:**

```json
{
  "sequence": 2,
  "timestamp": "2025-01-02T14:30:00Z",
  "action": "SEAL_MRP",

  "payload": {
    "files": {
      "mrp/manifest.json": "sha256:...",
      "mrp/tests.log": "sha256:...",
      "mrp/summary.md": "sha256:..."
    },
    "manifest_root_hash": "sha256:...",
    "test_passed": true
  },

  "prev_hash": "sha256:...",

  "identity": {
    "signer_id": "claude-developer",
    "public_key": "ssh-ed25519 AAAAC3...",
    "signature": "base64_signature_of_canonical_payload"
  },

  "event_hash": "sha256:..."
}
```

### 8. CLI Command: `geas prove`

Run tests, generate MRP, and seal it.

**Behavior:**

1. **Validate State**: Ensure Intent is sealed, MRP not yet sealed.
2. **Run Tests**: Execute configured test command.
3. **Check Result**: If tests fail, abort with error (no MRP generated).
4. **Generate Manifest**: Walk source directories, hash files, calculate Merkle root.
5. **Write MRP Artifacts**: Create `mrp/` folder with manifest, test log, summary.
6. **Seal MRP**: Hash MRP files, sign with agent identity, append to ledger.
7. **Report**: Display summary of actions taken.

**Options:**

- `--identity <name>`: Signer identity (defaults to first agent identity).
- `--scope <dirs>`: Override default scope (default: `src/,tests/`).
- `--skip-tests`: Skip test execution (use existing test results).

**Example (Success):**

```bash
$ geas prove --identity claude-developer
✓ Intent seal verified (event #1)
✓ Running tests: pytest -v
  ... test output ...
✓ Tests passed in 12.5s (exit code 0)
✓ Generated manifest with 15 files
✓ Merkle root: sha256:abc123...
✓ Created MRP artifacts
✓ Sealed with identity 'claude-developer'

MRP Summary:
  Files:      15
  Root Hash:  sha256:abc123...
  Test Time:  12.5s

Bolt 'feature-login' is ready for review.
```

**Example (Failure):**

```bash
$ geas prove --identity claude-developer
✓ Intent seal verified (event #1)
✓ Running tests: pytest -v
  ... test output with failures ...
✗ Tests FAILED (exit code 1)

MRP generation aborted. Fix the tests and try again.
```

**Error Cases:**

| Condition | Error Message |
|-----------|---------------|
| Intent not sealed | "Intent not sealed. Run 'geas seal intent' first." |
| MRP already sealed | "MRP already sealed. Cannot re-prove." |
| Tests failed | "Tests FAILED. MRP generation aborted." |
| Test timeout | "Tests timed out after 300s." |
| Identity not found | "Identity 'claude-developer' not found." |
| Identity is not agent | "SEAL_MRP requires agent identity (got 'human')." |

## Deliverables

1. **Test runner module** (`src/geas_ai/testing.py`):
   - `run_tests()` — Execute test command with timeout.
   - `TestResult` Pydantic model.

2. **Directory walker module** (`src/geas_ai/walker.py`):
   - `walk_source_files()` — Gitignore-aware file walker.
   - `load_gitignore()` — Parse .gitignore patterns.

3. **Manifest module** (`src/geas_ai/manifest.py`):
   - `Manifest` Pydantic model.
   - `generate_manifest()` — Create manifest with file hashes.
   - `calculate_merkle_root()` — Merkle tree calculation.

4. **MRP module** (`src/geas_ai/mrp.py`):
   - `generate_mrp()` — Create all MRP artifacts.
   - `generate_summary()` — Create human-readable summary.

5. **CLI command** (`src/geas_ai/cli/prove.py`):
   - `geas prove` implementation.

6. **Unit tests** (`tests/test_prove.py`, `tests/test_manifest.py`):
   - Test runner execution.
   - Gitignore parsing.
   - Manifest generation.
   - Merkle root calculation.
   - Full prove workflow.

## Technical Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **Process Execution** | `subprocess` | Standard library, cross-platform. |
| **Gitignore Parsing** | `pathspec` | Correct .gitignore semantics. |
| **Hashing** | `hashlib` | Standard library, no dependencies. |
| **Schema Validation** | `pydantic` | Strict typing, validation. |

## Acceptance Criteria

- [ ] `geas prove` only runs if Intent is already sealed.
- [ ] Test command is executed and output captured.
- [ ] Tests failure aborts MRP generation with clear message.
- [ ] Manifest includes all files in scope, respecting .gitignore.
- [ ] File hashes are deterministically calculated (sorted paths).
- [ ] Merkle root is correctly calculated from file hashes.
- [ ] MRP artifacts are written to `mrp/` folder.
- [ ] `SEAL_MRP` event is signed by agent identity.
- [ ] Event is correctly linked in hash chain.
- [ ] Cannot prove twice (idempotency check).
- [ ] All functions have type hints and docstrings.
- [ ] Test coverage > 85%.
