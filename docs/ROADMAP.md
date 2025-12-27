# PACT-AI Roadmap & Strategy

## Phase 1: The Core Protocol (v0.1)

Goal: A stable CLI that manages the .pacts folder structure and configuration.

[x] Develop main.py to basic commands.

[x] Implement pact init with the folder structure (Typer).

[x] Implement pact new (bolt creation) and pact seal (integrity locking).

[x] Refactor `pact seal status` and `pact seal verify` for better error reporting and robustness.

[x] Add 'req' as a valid target to 'pact seal'

[ ] Implement `pact edit agents`-like feature set to enable read, creation, editing, and deletion of the agents configuration.

[x] Implement pact checkout `<bolt-name>` (Context switching).

[x] Implement pact archive `<bolt-name>` (Move fully sealed bolts to archive).

[x] Implement pact delete `<bolt-name>` (Cleanup).

[x] Implement "Sequence Verification" (Ensure Specs locked -> Plan locked -> MRP locked). Make approval process an Hard constraint.

[x] Add `LICENSE` and `CONTRIBUTING.md` guides (git/uv style).

[x] Setup pre-commit hooks and GitHub Actions for CI.

[ ] Update `developer` and `qa_engineer` descriptions to integrate tests effectively.

[ ] Enhance MPR: add MPR guidelines and an MPR trust score.

[ ] Add tests for CI

[ ] Publish to PyPI.

## Phase 2: The SE 3.0 Workflow (v0.2)

Goal: Full support for the 5-Agent Roster and MRP.

[ ] Add pact mrp command validation.

[ ] Add "Multi-Lock" support (Locking specs AND plans separately).

## Phase 3: The Ecosystem (v0.3)

Goal: Native integration.

[ ] MCP Server: Expose PACT as a server for Claude Desktop/Cursor.

[ ] Git Hook: A pre-commit hook that rejects commits to src/ if the active bolt has no lock.

## Go-To-Market: "The Governance Standard"

### Positioning

Position PACT not as a "tool" but as a Methodology.

### Community Channels

* GitHub: Create a "Awesome-PACT" repo listing custom Agent Roles created by the community.

* Reddit (r/LocalLLaMA): Showcase the local_mistral config in models.yaml to attract the privacy-focused crowd.

* Twitter/X: Share screenshots of the approved.lock file preventing an Agent from deleting code. Title: "Saved by the Lock."
