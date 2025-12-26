# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- **Core CLI**: Implementation of `pact init` command using Typer.
- **Protocol**: Default templates for `agents.yaml` (Senior Roles) and `models.yaml`.
- **Manifesto**: `PACT_MANIFESTO.md` generation.
- **Task Lifecycle**: Implementation of `pact new` command.
- **Context Management**: Automatic updates to `.pacts/active_context.md`.
- **Integrity**: Implementation of `pact seal` (hashing and locking) + `verify` and `status`.
