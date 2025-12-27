# Specifications: chore-repo

**Status:** DRAFT
**Role:** Senior Product Owner

## User Stories

### US1: Repository Licensing

As a maintainer, I want the project to have a clear legal framework so that contributors and users know their rights and obligations.

**Acceptance Criteria:**

* **AC 1.1:** A `LICENSE-MIT` file must be present in the root.
* **AC 1.2:** A `LICENSE-APACHE` file must be present in the root.
* **AC 1.3:** The `README.md` must mention the dual-licensing at the bottom.

### US2: Contribution Guidelines

As a new contributor, I want to understand how to set up my environment and submit changes so that I can contribute effectively without friction.

**Acceptance Criteria:**

* **AC 2.1:** A `CONTRIBUTING.md` file must exist in the root.
* **AC 2.2:** It must include a "Local Setup" section using `uv`.
* **AC 2.3:** It must explain the PACT protocol workflow (how to use `pact` commands).
* **AC 2.4:** It must define the Pull Request process (testing and linting requirements).

### US3: Automated Pre-commit Quality Gates

As a developer, I want my code to be automatically checked for linting and type errors before I commit, so that I maintain high code quality standards.

**Acceptance Criteria:**

* **AC 3.1:** A `.pre-commit-config.yaml` file must be configured.
* **AC 3.2:** It must include `ruff` for linting and formatting.
* **AC 3.3:** It must include `mypy` for static type checking.
* **AC 3.4:** The documentation must explain how to install and run pre-commit.

### US4: Continuous Integration (CI)

As a maintainer, I want all Pull Requests and pushes to the main branch to be automatically tested and linted in a clean environment to prevent regressions.

**Acceptance Criteria:**

* **AC 4.1:** A GitHub Actions workflow file must exist at `.github/workflows/ci.yml`.
* **AC 4.2:** The CI must trigger on `push` to `main` and all `pull_request` events.
* **AC 4.3:** The CI must install dependencies using `uv`.
* **AC 4.4:** The CI must run `ruff check`, `ruff format --check`, `mypy`, and `pytest`.
* **AC 4.5:** The CI must fail if any of the above checks fail.

## Constraints

1. **No Code Change**: This bolt must not modify any logic in `src/`.
2. **Standards**: All configuration must follow the latest `uv` and `ruff` best practices.
3. **Idempotency**: Rerunning the CI or pre-commit must yield consistent results.
