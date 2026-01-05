# Request: CI/CD Integration (Phase 6)

**Status:** PENDING
**Source:** [TRINITY_LOCK.md](../../../docs/TRINITY_LOCK.md) (Phase 6)
**Related:** [WHITE_PAPER.md](../../../docs/WHITE_PAPER.md) (Phase 6)
**Prerequisite:** Phase 5 (Lifecycle Management)

## Context

CI/CD Integration enables enterprise automation of the GEAS workflow. This phase provides templates and tooling for running GEAS in continuous integration pipelines, with secure key injection and PR status checks.

GEAS follows a **proactive MRP model**:

1. Agents generate code and run `geas prove` in CI.
2. CI prepares the MRP and pushes for human review.
3. Merge is blocked until a valid MRP exists.
4. Reviewers run `geas verify` before approving PRs.

## Goals

Enable enterprise automation with CI/CD integration.

**Primary Deliverables:**

- GitHub Actions workflow templates
- GitLab CI templates
- Documentation for key injection in CI
- PR status checks (block merge without valid MRP)

## Requirements

### 1. GitHub Actions Workflow

**Template (`.github/workflows/geas-verify.yml`):**

```yaml
name: GEAS Verification

on:
  pull_request:
    branches: [main, develop]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install GEAS
        run: pip install geas-ai

      - name: Inject Agent Keys
        env:
          GEAS_KEY_CLAUDE_DEV: ${{ secrets.GEAS_KEY_CLAUDE_DEV }}
        run: echo "Keys injected"

      - name: Verify Bolt
        run: geas verify --json > verification.json

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: geas-verification
          path: verification.json
```

### 2. GitLab CI Template

**Template (`.gitlab-ci.yml`):**

```yaml
geas-verify:
  stage: test
  image: python:3.11
  script:
    - pip install geas-ai
    - geas verify --json > verification.json
  artifacts:
    paths:
      - verification.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### 3. Key Injection Documentation

Document secure key management for CI environments:

- Environment variable format: `GEAS_KEY_{NAME}` (uppercase, base64-encoded)
- Secret storage in GitHub/GitLab
- Key rotation procedures

### 4. PR Status Checks

Implement a command for CI that outputs GitHub/GitLab-compatible status:

```bash
$ geas ci-status
# Outputs status in format understood by CI systems
```

## Deliverables

1. **Templates** (`src/geas_ai/templates/ci/`):
   - `github-actions.yml.template`
   - `gitlab-ci.yml.template`

2. **CLI command** (`src/geas_ai/cli/ci.py`):
   - `geas ci-status` — Output CI-compatible status.
   - `geas ci-setup` — Generate CI templates.

3. **Documentation** (`docs/ci-integration.md`)

4. **Unit tests** (`tests/test_ci.py`)

## Acceptance Criteria

- [ ] GitHub Actions template runs successfully.
- [ ] GitLab CI template runs successfully.
- [ ] Key injection documented with examples.
- [ ] `geas verify --json` outputs CI-parseable results.
- [ ] PR merge blocked without valid MRP (documented).
- [ ] Test coverage > 85%.
