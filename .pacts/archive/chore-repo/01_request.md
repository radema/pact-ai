# Feature Request: chore-repo

**Status:** PENDING

## Instructions

Initialize the repository with standard open-source hygiene and automation:

1. **Licensing**: Add LICENSE file (MIT/Apache-2.0 dual license, typical for modern Python/Rust tools like uv).
2. **Contribution Guide**: Create `CONTRIBUTING.md` outlining the development workflow (uv, pytest, pact protocol).
3. **Pre-commit**: Configure `.pre-commit-config.yaml` with Ruff (lint/format) and Mypy.
4. **CI**: Create GitHub Actions workflow (`.github/workflows/ci.yml`) to run tests and lints on every PR and push to main.
