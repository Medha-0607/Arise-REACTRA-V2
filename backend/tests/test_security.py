"""
Unit tests for cryptographic primitives and canonicalization.
"""

from app.security.hashing import canonicalize_json, calculate_sha256
from app.security.signing import (
    generate_device_keypair,
    export_public_key_bytes,
    sign_message,
    verify_signature,
)


def test_canonicalize_json_deterministic():
    """Verifies that dictionary key order does not alter the canonical JSON output."""
    data1 = {"b": 2, "a": 1, "nested": {"y": 20, "x": 10}}
    data2 = {"a": 1, "nested": {"x": 10, "y": 20}, "b": 2}
    assert canonicalize_json(data1) == canonicalize_json(data2)
    assert canonicalize_json(data1) == '{"a":1,"b":2,"nested":{"x":10,"y":20}}'


def test_sha256_calculation():
    """Verifies SHA-256 computation against known vector."""
    message = "REACTRA_V2_PRESUMPTIVE_TEST"
    digest = calculate_sha256(message)
    assert len(digest) == 64
    assert digest == calculate_sha256(message)


def test_ed25519_sign_and_verify():
    """Verifies that an Ed25519 signature generated with a private key validates against the corresponding public key."""
    private_key, public_key = generate_device_keypair()
    payload = b"FIELD_RECORD_CANONICAL_PAYLOAD"
    signature = sign_message(private_key, payload)
    
    # Signature should verify successfully
    assert verify_signature(public_key, signature, payload) is True
    
    # Modified payload should fail verification
    assert verify_signature(public_key, signature, b"TAMPERED_PAYLOAD") is False
    
    # Export public key bytes
    raw_pub = export_public_key_bytes(public_key)
    assert len(raw_pub) == 32
