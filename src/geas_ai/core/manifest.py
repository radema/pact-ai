from typing import List, Dict
from datetime import datetime, timezone
from pydantic import BaseModel
import hashlib
from pathlib import Path

class TestResultInfo(BaseModel):
    passed: bool
    exit_code: int
    duration_seconds: float
    timestamp: datetime
    output: str = ""

class Manifest(BaseModel):
    bolt_id: str
    generated_at: datetime
    scope: List[str]
    files: Dict[str, str]  # Path -> SHA256
    root_hash: str
    test_result: TestResultInfo

def calculate_merkle_root(files: Dict[str, str]) -> str:
    """
    Calculates the Merkle Root from a dictionary of file paths and their SHA256 hashes.

    Logic:
    1. Leaves: Sort filepaths -> Extract hashes.
    2. Leaf Hashing: We use the hash provided in the dict (SHA256 of content).
    3. Tree Construction:
        - Pair adjacent nodes (A, B).
        - Parent = SHA256(A + B).
        - If odd count, Parent = SHA256(Last + Last).
        - Repeat until Root.
    """
    if not files:
        # Return hash of empty string if no files
        return hashlib.sha256(b"").hexdigest()

    # Sort by filepath to ensure deterministic ordering
    sorted_paths = sorted(files.keys())
    # Extract hashes
    leaves = [files[path] for path in sorted_paths]

    current_level = leaves

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i+1]
            else:
                # Odd count, duplicate last
                right = left

            # Combine hashes and hash again
            combined = (left + right).encode('utf-8')
            parent_hash = hashlib.sha256(combined).hexdigest()
            next_level.append(parent_hash)
        current_level = next_level

    return current_level[0]

def generate_manifest(bolt_id: str, scope: List[str], files: Dict[str, str], test_result: TestResultInfo) -> Manifest:
    """Generates the Manifest object."""
    root_hash = calculate_merkle_root(files)

    return Manifest(
        bolt_id=bolt_id,
        generated_at=datetime.now(timezone.utc),
        scope=scope,
        files=files,
        root_hash=root_hash,
        test_result=test_result
    )
