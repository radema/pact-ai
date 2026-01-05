import os
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from geas_ai.schemas.identity import Identity, IdentityRole, IdentityStore
from geas_ai.utils.crypto import (
    generate_keypair,
    sign,
    verify,
    canonicalize_json,
    load_private_key_from_bytes,
)
from geas_ai.core.identity import KeyManager, IdentityManager, KeyNotFoundError

# --- Crypto Tests ---


def test_key_generation():
    private_bytes, public_str = generate_keypair()
    assert isinstance(private_bytes, bytes)
    assert isinstance(public_str, str)
    assert public_str.startswith("ssh-ed25519")
    assert "BEGIN OPENSSH PRIVATE KEY" in private_bytes.decode()


def test_sign_verify():
    private_bytes, public_str = generate_keypair()
    private_key = load_private_key_from_bytes(private_bytes)

    payload = b"test message"
    signature = sign(private_key, payload)

    assert verify(public_str, signature, payload) is True


def test_sign_verify_tampered():
    private_bytes, public_str = generate_keypair()
    private_key = load_private_key_from_bytes(private_bytes)

    payload = b"test message"
    signature = sign(private_key, payload)

    assert verify(public_str, signature, b"tampered message") is False


def test_canonicalize_json():
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}

    # Should be identical bytes
    assert canonicalize_json(data1) == canonicalize_json(data2)
    # No whitespace
    assert b" " not in canonicalize_json(data1)
    # Sorted
    assert canonicalize_json(data1) == b'{"a":1,"b":2}'


# --- Schema Tests ---


def test_identity_model_valid():
    i = Identity(
        name="valid-name", role=IdentityRole.HUMAN, active_key="ssh-ed25519 AAA..."
    )
    assert i.name == "valid-name"


def test_identity_model_agent_validation():
    # Missing persona/model for agent
    with pytest.raises(ValueError, match="Field required for Agent role"):
        Identity(
            name="agent-x", role=IdentityRole.AGENT, active_key="ssh-ed25519 AAA..."
        )

    # Valid agent
    i = Identity(
        name="agent-x",
        role=IdentityRole.AGENT,
        persona="Developer",
        model="gpt-4",
        active_key="ssh-ed25519 AAA...",
    )
    assert i.persona == "Developer"


def test_identity_store():
    i1 = Identity(name="i1", role=IdentityRole.HUMAN, active_key="k1")
    store = IdentityStore(identities=[i1])
    assert store.get_by_name("i1") == i1
    assert store.get_by_name("i2") is None


# --- Core Logic Tests (KeyManager) ---


def test_resolution_env_priority(monkeypatch):
    # Setup keys
    priv_bytes, pub_str = generate_keypair()

    # Set env var
    monkeypatch.setenv("GEAS_KEY_MY_IDENTITY", priv_bytes.decode())

    # Resolve
    key = KeyManager.load_private_key("my-identity")
    assert isinstance(key, ed25519.Ed25519PrivateKey)

    # Verify it matches by comparing public keys (OpenSSH private key format has randomness)
    resolved_pub_bytes = key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    # pub_str contains "ssh-ed25519 <base64> <comment>" usually
    # resolved_pub_bytes matches the ssh format
    assert (
        resolved_pub_bytes.decode("utf-8")
        == pub_str.split()[0] + " " + pub_str.split()[1]
    )


def test_resolution_local_file(tmp_path, monkeypatch):
    # Setup keys
    priv_bytes, pub_str = generate_keypair()

    # Mock ~/.geas/keys
    keys_dir = tmp_path / ".geas" / "keys"
    keys_dir.mkdir(parents=True)
    key_file = keys_dir / "my-local.key"
    key_file.write_bytes(priv_bytes)

    # Monkeypatch expanduser to point to tmp_path
    monkeypatch.setattr(
        os.path, "expanduser", lambda x: str(tmp_path / x.replace("~/", ""))
    )

    key = KeyManager.load_private_key("my-local")
    assert isinstance(key, ed25519.Ed25519PrivateKey)


def test_resolution_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(
        os.path, "expanduser", lambda x: str(tmp_path / x.replace("~/", ""))
    )
    with pytest.raises(KeyNotFoundError):
        KeyManager.load_private_key("non-existent")


# --- Core Logic Tests (IdentityManager) ---


def test_identity_manager_load_save(tmp_path):
    config_file = tmp_path / "identities.yaml"
    manager = IdentityManager(config_path=config_file)

    # Initial load (empty)
    store = manager.load()
    assert len(store.identities) == 0

    # Add identity
    new_id = Identity(name="test", role=IdentityRole.HUMAN, active_key="key")
    manager.add_identity(new_id)

    # Reload
    store = manager.load()
    assert len(store.identities) == 1
    assert store.identities[0].name == "test"


def test_identity_manager_duplicate(tmp_path):
    config_file = tmp_path / "identities.yaml"
    manager = IdentityManager(config_path=config_file)

    new_id = Identity(name="test", role=IdentityRole.HUMAN, active_key="key")
    manager.add_identity(new_id)

    with pytest.raises(ValueError, match="already exists"):
        manager.add_identity(new_id)
