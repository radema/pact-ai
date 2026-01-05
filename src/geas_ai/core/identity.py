import os
from pathlib import Path
from typing import Optional
from ruamel.yaml import YAML
from geas_ai.schemas.identity import Identity, IdentityStore
from geas_ai.utils.crypto import load_private_key_from_bytes, CryptoError
from geas_ai.utils import get_geas_root

class KeyNotFoundError(Exception):
    """Raised when a private key cannot be resolved."""
    pass

class KeyManager:
    """Handles resolution and loading of private keys."""

    @staticmethod
    def load_private_key(identity_name: str) -> object:
        """
        Resolves and loads the private key for the given identity name.

        Priority:
        1. Environment Variable: GEAS_KEY_{NAME} (Content: PEM or Base64)
        2. Local File: ~/.geas/keys/{name}.key

        Returns:
            Ed25519PrivateKey object.

        Raises:
            KeyNotFoundError: If no key is found.
            CryptoError: If the key is invalid.
        """
        # Validate identity_name to prevent path traversal
        if any(sep in identity_name for sep in [os.sep, os.altsep] if sep):
             raise ValueError(f"Invalid identity name: '{identity_name}'. Must not contain path separators.")

        # 1. Environment Variable Check
        env_var_name = f"GEAS_KEY_{identity_name.upper().replace('-', '_')}"
        env_val = os.getenv(env_var_name)
        if env_val:
            try:
                # Handle Base64 encoded or direct PEM content
                # If it looks like PEM (starts with -----BEGIN), use as is
                if env_val.strip().startswith("-----BEGIN"):
                     key_bytes = env_val.encode("utf-8")
                else:
                    # Assume base64
                    import base64
                    key_bytes = base64.b64decode(env_val)
                return load_private_key_from_bytes(key_bytes)
            except Exception as e:
                # Fallthrough not implied by spec but good practice to log?
                # Spec says "Decode value... Parse... Return". If fail, maybe raise?
                # Spec says "Error State: Raise KeyNotFoundError" if *not found*.
                # If found but invalid, CryptoError seems appropriate.
                raise CryptoError(f"Invalid key in environment variable {env_var_name}: {e}")

        # 2. Local File Check
        key_path = Path(os.path.expanduser(f"~/.geas/keys/{identity_name}.key"))
        if key_path.exists():
            try:
                key_bytes = key_path.read_bytes()
                return load_private_key_from_bytes(key_bytes)
            except Exception as e:
                raise CryptoError(f"Invalid key in file {key_path}: {e}")

        # 3. Not Found
        raise KeyNotFoundError(f"Private key for '{identity_name}' not found in env ({env_var_name}) or local storage ({key_path}).")

class IdentityManager:
    """Manages reading and writing identities to identities.yaml."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = get_geas_root() / "config" / "identities.yaml"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def load(self) -> IdentityStore:
        """Loads identities from the YAML file."""
        if not self.config_path.exists():
            return IdentityStore(identities=[])

        try:
            with open(self.config_path, "r") as f:
                data = self.yaml.load(f) or {}
                # Handle empty file or null data
                if not data:
                    return IdentityStore(identities=[])
                # If data has 'identities' key, use it. If list, wrap it?
                # Spec implies structure is: identities: [ ... ]
                if "identities" not in data:
                    return IdentityStore(identities=[])

                # Convert raw dicts to Identity objects
                # Pydantic validation happens here
                return IdentityStore(**data)
        except Exception as e:
            # Maybe raise a custom error or return empty?
            # For now, let's propagate or raise helpful error
            raise ValueError(f"Failed to load identities from {self.config_path}: {e}")

    def save(self, store: IdentityStore) -> None:
        """Saves the IdentityStore to the YAML file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Dump to dict
        data = store.model_dump(mode='json')

        with open(self.config_path, "w") as f:
            self.yaml.dump(data, f)

    def add_identity(self, identity: Identity) -> None:
        """Adds a new identity and saves."""
        store = self.load()
        # Check uniqueness
        if store.get_by_name(identity.name):
            raise ValueError(f"Identity with name '{identity.name}' already exists.")

        store.identities.append(identity)
        self.save(store)
