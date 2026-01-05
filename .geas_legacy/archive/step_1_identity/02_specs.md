# Specs: Identity & Keyring (Phase 1)

**Status:** APPROVED
**Source:** [01_request.md](./01_request.md)

## 1. Architecture & Modules

The Identity system will be implemented as a core module within the `geas` package.

### 1.1 Directory Structure Impact

```
.geas/
├── bolts/                  # Project management bolts
├── config/
│   ├── identities.yaml     # Public registry of identities
│   ├── agents.yaml         # Existing agent definitions
│   └── models.yaml         # Existing model definitions
└── keys/                   # (Local only, .gitignore) Private keys
```

### 1.2 Module Organization

* `src/geas/core/identity.py`: Core logic for Identity management, key resolution, and signing/verification.
* `src/geas/schemas/identity.py`: Pydantic models for identity data structures.
* `src/geas/commands/init.py`: Implementation of `geas init`.
* `src/geas/commands/identity.py`: Implementation of `geas identity` subcommands.
* `src/geas/utils/crypto.py`: Low-level cryptographic primitives (wrapping `cryptography.hazmat`).

## 2. Data Structures

Defined in `src/geas/schemas/identity.py`.

### 2.1 Enums

```python
class IdentityRole(str, Enum):
    HUMAN = "human"
    AGENT = "agent"
```

### 2.2 Models

```python
class Identity(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9-]+$")
    role: IdentityRole
    persona: Optional[str] = None  # Required if role == AGENT
    model: Optional[str] = None    # Required if role == AGENT
    active_key: str  # SSH-format public key (e.g., "ssh-ed25519 ...")
    revoked_keys: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("persona", "model")
    def validate_agent_fields(cls, v, values):
        if values.get("role") == IdentityRole.AGENT and not v:
            raise ValueError("Field required for Agent role")
        return v
```

```python
class IdentityStore(BaseModel):
    identities: List[Identity]

    def get_by_name(self, name: str) -> Optional[Identity]:
        return next((i for i in self.identities if i.name == name), None)
```

## 3. Core Logic & Algorithms

### 3.1 Key Resolution Strategy (`load_private_key`)

1. **Input**: `identity_name`
2. **Environment Check**:
    * Construct var name: `GEAS_KEY_{identity_name.upper().replace('-', '_')}`.
    * If var exists:
        * Decode value (check if Base64 or plain PEM).
        * Parse Private Key object.
        * **Return** Key.
3. **Local File Check**:
    * Construct path: `~/.geas/keys/{identity_name}.key` (Expansion of `~` required).
    * If file exists:
        * Read file content.
        * Parse OpenSSH key format.
        * **Return** Key.
4. **Error State**:
    * Raise `KeyNotFoundError` with descriptive message.

### 3.2 Canonicalization (`canonicalize_json`)

To ensure deterministic signing, JSON payloads must be canonicalized:

1. Input: Python Dictionary/Object.
2. Process:
    * Sort keys alphabetically.
    * Remove all insignificant whitespace (separators: `(',', ':')`).
    * Ensure UTF-8 encoding.
3. Output: Bytes.

### 3.3 Signing & Verification

* **Algorithm**: Ed25519
* **Sign**: `Private Key` + `Payload (bytes)` -> `Signature (raw bytes)` -> `Base64 encode`.
* **Verify**: `Public Key` + `Payload (bytes)` + `Signature (Base64 decode)` -> `Boolean`.

## 4. CLI Specifications

Using `typer` for CLI definition.

### 4.1 `geas init`

* **Logic**:
    1. `os.makedirs(".geas/config", exist_ok=True)`
    2. `os.makedirs(".geas/bolts", exist_ok=True)`
    3. Create files if not exist: `identities.yaml`, `agents.yaml`, `models.yaml`.
    4. Output success status.

### 4.2 `geas identity add`

* **Arguments**:
  * `--name`: string (Required)
  * `--role`: enum [human, agent] (Required)
  * `--persona`: string (Optional, required if role=agent)
  * `--model`: string (Optional, required if role=agent)
* **Logic**:
    1. Load `identities.yaml` (if exists).
    2. Check uniqueness of `name`.
    3. Verify `persona`/`model` refs if applicable (warn if missing).
    4. **Crypto**: Generate Ed25519 Private/Public pair.
    5. **IO**:
        * Write private key to `~/.geas/keys/{name}.key` (mode 0600).
        * Append new `Identity` object to `identities.yaml`.
    6. **Output**:
        * Success message.
        * Environment variable export command (for Agents).

### 4.3 `geas identity list`

* **Output Format**: Table (using `rich` library is recommended for formatting).
* **Columns**: Name, Role, Persona, Model, Active Key (Truncated).

## 5. Dependencies

* `cryptography`: For Ed25519 and SSH key serialization.
* `pydantic`: For data validation.
* `typer`: CLI framework.
* `ruamel.yaml`: For YAML manipulation.
* `rich`: For pretty terminal output.

## 6. Testing Strategy

### 6.1 Unit Tests (`tests/core/test_identity.py`)

* `test_key_generation`: Verify keys are valid Ed25519.
* `test_sign_verify`: Roundtrip signature verification.
* `test_sign_verify_tampered`: Ensure signature fails for altered payload.
* `test_resolution_env_priority`: Set env var and ensure it overrides local file.
* `test_resolution_missing`: Ensure appropriate exception.

### 6.2 Integration Tests (`tests/commands/test_cli_identity.py`)

* `test_init`: Run `geas init` in temp dir, check file structure.
* `test_add_identity`: Run `geas identity add`, check `identities.yaml` content and key file.
* `test_add_identity_duplicate`: Ensure error on duplicate name.
