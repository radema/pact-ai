# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-03

### Added

- **Identity Management**: Added `Identity` and `KeyManager` core logic with Ed25519 cryptography.
- **CLI Commands**: Added `geas identity` command group:
  - `add`: Create new identities (Human/Agent) with auto-generated ssh keys.
  - `list`: View registered identities.
  - `show`: Detailed view of an identity including revocation history.
  - `revoke`: Revoke and rotate keys for compromised identities.
- **Security**: Strict key file permissions (0600) and environment variable integration for Agents.

## [0.1.0] - 2025-12-29

### Added

- **Core CLI**: Implementation of `geas init` command using Typer.
- **Protocol**: Default templates for `agents.yaml` (Senior Roles) and `models.yaml`.
- **Manifesto**: `GEAS_MANIFESTO.md` generation.
- **Task Lifecycle**: Implementation of `geas new` command.
- **Context Management**: Automatic updates to `.geas/active_context.md`.
- **Integrity**: Implementation of `geas seal` (hashing and locking) + `verify` and `status`.
