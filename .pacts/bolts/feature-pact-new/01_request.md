# Feature Request: Implement `pact new`

**Request:**
"let's start a new bolt for pact new."

**Context:**
The user wants to implement the `pact new <bolt_name>` command.
According to `docs/TECHNICAL_SPECS.md`, this command is responsible for:

1. Creating the directory structure for a new bolt (`.pacts/bolts/<name>`).
2. Generating `active_context.md` (The Pointer) to guide the IDE Agent to the work.
