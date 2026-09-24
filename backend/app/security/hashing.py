"""
Cryptographic Hashing and Canonicalization for REACTRA V2 Evidence Chain.
Uses standard SHA-256 with deterministic JSON formatting.
"""

import hashlib
import json
from typing import Any, Dict


def canonicalize_json(data: Dict[str, Any]) -> str:
    """Produces deterministic UTF-8 JSON representation for cryptographic operations."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def calculate_sha256(data: str | bytes) -> str:
    """Calculates standard SHA-256 hexadecimal digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
