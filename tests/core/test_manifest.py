import hashlib
from datetime import datetime, timezone
from geas_ai.core.manifest import (
    calculate_merkle_root,
    generate_manifest,
    TestResultInfo,
    Manifest,
)


def test_merkle_root_empty():
    """Test Merkle Root calculation with empty input."""
    assert calculate_merkle_root({}) == hashlib.sha256(b"").hexdigest()


def test_merkle_root_single_file():
    """Test Merkle Root with a single file."""
    # Leaf hash is the content hash
    content_hash = hashlib.sha256(b"content").hexdigest()
    files = {"file1.txt": content_hash}

    # With 1 leaf, it is the root
    assert calculate_merkle_root(files) == content_hash


def test_merkle_root_two_files():
    """Test Merkle Root with two files."""
    h1 = hashlib.sha256(b"A").hexdigest()
    h2 = hashlib.sha256(b"B").hexdigest()
    files = {"a.txt": h1, "b.txt": h2}

    # Expected: SHA256(h1 + h2) because "a.txt" < "b.txt"
    expected = hashlib.sha256((h1 + h2).encode()).hexdigest()
    assert calculate_merkle_root(files) == expected


def test_merkle_root_three_files():
    """Test Merkle Root with three files (odd number logic)."""
    h1 = hashlib.sha256(b"A").hexdigest()
    h2 = hashlib.sha256(b"B").hexdigest()
    h3 = hashlib.sha256(b"C").hexdigest()

    files = {"a.txt": h1, "b.txt": h2, "c.txt": h3}

    # Layer 1: [h1, h2, h3]
    # Layer 2:
    #   Node1 = SHA256(h1 + h2)
    #   Node2 = SHA256(h3 + h3)  <-- Duplicated last node
    # Root = SHA256(Node1 + Node2)

    node1 = hashlib.sha256((h1 + h2).encode()).hexdigest()
    node2 = hashlib.sha256((h3 + h3).encode()).hexdigest()
    expected = hashlib.sha256((node1 + node2).encode()).hexdigest()

    assert calculate_merkle_root(files) == expected


def test_generate_manifest():
    test_result = TestResultInfo(
        passed=True,
        exit_code=0,
        duration_seconds=1.0,
        timestamp=datetime.now(timezone.utc),
    )
    files = {"file1.txt": "abc"}
    m = generate_manifest("bolt-123", ["src"], files, test_result)

    assert isinstance(m, Manifest)
    assert m.bolt_id == "bolt-123"
    assert m.scope == ["src"]
    assert m.files == files
    assert m.test_result == test_result
    assert m.root_hash == "abc"  # Single file
