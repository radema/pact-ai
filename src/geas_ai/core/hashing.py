import hashlib
from pathlib import Path
from typing import Any, Dict

from geas_ai.utils.crypto import canonicalize_json


def file_sha256(file_path: Path) -> str:
    """Computes SHA256 hash of the file content (normalized to UTF-8 text if possible)."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to be memory efficient
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"


def calculate_event_hash(event_data: Dict[str, Any]) -> str:
    """
    Calculates the SHA-256 hash of a ledger event.

    The event dictionary should exclude the 'event_hash' field itself
    before calling this function if it was already present.
    """
    canonical_bytes = canonicalize_json(event_data)
    sha256_hash = hashlib.sha256(canonical_bytes).hexdigest()
    return f"sha256:{sha256_hash}"
