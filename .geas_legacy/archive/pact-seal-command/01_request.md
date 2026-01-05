# Feature Request: Implement `pact seal`

**Request:**
"let's work on the seal now."

**Context:**
The user wants to implement the `pact seal <target>` command.
According to `docs/TECHNICAL_SPECS.md` and `docs/WHITE_PAPER.md`, this is the cryptographic enforcement mechanism.

**Core Logic:**

1. `pact seal specs`:
    * Reads `02_specs.md`.
    * Calculates a SHA-256 hash.
    * Writes it to `approved.lock` (or specific lock file part).
2. `pact seal plan`:
    * Reads `03_plan.md`.
    * Calculates SHA-256 hash.
    * Writes it to `approved.lock`.

**Goal:**
Prevent "Agent Drift" by ensuring that the Plan matches the Specs and the Code matches the Plan? (Or at least ensuring files aren't changed after approval).
For v0.1: Simple locking mechanism. Creates/Updates an `approved.lock` file in the bolt directory containing the hash of the approved file.
