import json
from base64 import b64encode, b64decode
from typing import Tuple, Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class CryptoError(Exception):
    """Base exception for crypto operations."""

    pass


def generate_keypair() -> Tuple[bytes, str]:
    """
    Generates an Ed25519 keypair.

    Returns:
        Tuple[bytes, str]: (private_bytes_openssh, public_key_ssh_format)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()

    # Serialize private key to OpenSSH format (bytes)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Serialize public key to OpenSSH format (string)
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    return private_bytes, public_bytes.decode("utf-8")


def load_private_key_from_bytes(key_bytes: bytes) -> ed25519.Ed25519PrivateKey:
    """
    Loads an Ed25519 private key from bytes (PEM/OpenSSH).
    """
    try:
        key = serialization.load_ssh_private_key(key_bytes, password=None)
        if not isinstance(key, ed25519.Ed25519PrivateKey):
            raise CryptoError(
                f"Unsupported key type: {type(key)}. Only Ed25519 is supported."
            )
        return key
    except Exception as e:
        raise CryptoError(f"Failed to load private key: {e}")


def sign(private_key: ed25519.Ed25519PrivateKey, payload_bytes: bytes) -> str:
    """
    Signs the payload with the private key.

    Returns:
        str: Base64 encoded signature.
    """
    signature = private_key.sign(payload_bytes)
    return b64encode(signature).decode("utf-8")


def verify(public_key_str: str, signature_b64: str, payload_bytes: bytes) -> bool:
    """
    Verifies the signature against the payload using the public key.
    """
    try:
        public_key = serialization.load_ssh_public_key(public_key_str.encode("utf-8"))
        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            return False
        signature = b64decode(signature_b64)
        public_key.verify(signature, payload_bytes)
        return True
    except Exception:
        return False


def canonicalize_json(data: Any) -> bytes:
    """
    Canonicalizes a JSON object (dict/list) for consistent signing.
    Sorts keys, removes insignificant whitespace, and encodes to UTF-8.
    """
    return json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
