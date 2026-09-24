"""
Ed25519 Cryptographic Signing & Verification Abstractions for REACTRA V2.
"""

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_device_keypair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """Generates a new device-bound Ed25519 keypair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def export_public_key_bytes(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """Exports public key in raw format."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


def sign_message(private_key: ed25519.Ed25519PrivateKey, message: bytes) -> bytes:
    """Signs a message using the device private key."""
    return private_key.sign(message)


def verify_signature(public_key: ed25519.Ed25519PublicKey, signature: bytes, message: bytes) -> bool:
    """Verifies an Ed25519 signature against a message."""
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False
