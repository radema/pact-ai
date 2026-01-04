# GEAS Technical Debt & Improvements

## Phase 4: Verification Engine (Completed)

- [x] **Foundations**: Implement Workflow and Verification schemas (`src/geas_ai/schemas/`).
- [x] **Core Logic**: Implement verification pillars (`chain`, `signatures`, `workflow`, `content`).
- [x] **CLI**: Refactor `verify` and `status` to use the new engine.
- [x] **CLI**: Implement `approve` command.
- [x] **Config**: Bootstrap `workflow.yaml` in `geas init`.

## Minor Fixes

- [ ] **Schema**: Make `model` field optional for `Identity` (Agent role). Not all agents are bound to a specific model instance in `models.yaml`.
