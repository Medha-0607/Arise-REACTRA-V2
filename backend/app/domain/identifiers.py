"""
Deterministic Offline Identifier Generators for REACTRA V2.
Generates unique, structured, and auditable identifiers without central coordination.
"""

import uuid
from datetime import datetime, timezone


def generate_session_id() -> str:
    """Generates an offline-stable session ID with UTC date prefix."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:12].upper()
    return f"SES-{date_str}-{short_uuid}"


def generate_event_id() -> str:
    """Generates an audit event identifier."""
    return f"EVT-{uuid.uuid4().hex[:16].upper()}"


def generate_capture_id() -> str:
    """Generates a capture frame identifier."""
    return f"CAP-{uuid.uuid4().hex[:16].upper()}"


def generate_measurement_id() -> str:
    """Generates a scientific measurement identifier."""
    return f"MSR-{uuid.uuid4().hex[:16].upper()}"


def generate_envelope_id() -> str:
    """Generates a sealed evidence envelope identifier."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:12].upper()
    return f"ENV-{date_str}-{short_uuid}"
