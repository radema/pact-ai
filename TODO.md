# GEAS Technical Debt & Improvements

## Minor Fixes

- [ ] **Schema**: Make `model` field optional for `Identity` (Agent role). Not all agents are bound to a specific model instance in `models.yaml`.

## Protocol & Governance Improvements

- [ ] **Verification**: Relax condition for verification.
- [ ] **CLI Configuration**: Verify that the workflow can be configured through CLI (and the same for required files).
- [ ] **Decoupling**: Verify that required and optional files are not hardcoded.
- [ ] **Archival**: Apply a signature also in case of archivation.
- [ ] **Workflow**: define a system based on subworflows

## Documentation Updates

- [ ] **Workflow Lifecycle**: Explicitly document the "Standard Workflow" (Req -> Spec -> Plan -> Intent -> MRP -> Approve) in `WHITE_PAPER.md` or `TRINITY_LOCK.md`. Clarify that `SEAL_INTENT` aggregates the previous three artifacts.
