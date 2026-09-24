"""
Domain Enums and State Constants for REACTRA V2.
"""

from enum import Enum


class TestSessionState(str, Enum):
    """Authoritative state machine states for a test session."""
    IDLE = "IDLE"
    PROFILE_SELECTED = "PROFILE_SELECTED"
    CAPTURE_PENDING = "CAPTURE_PENDING"
    PRE_VALIDATED = "PRE_VALIDATED"
    EVALUATED = "EVALUATED"
    EVIDENCE_SEALED = "EVIDENCE_SEALED"
    REJECTED = "REJECTED"


class CaptureSource(str, Enum):
    """Source classification of test image captures."""
    LIVE_CAMERA = "LIVE_CAMERA"
    IMPORTED_IMAGE = "IMPORTED_IMAGE"
    DIRECT_CAMERA = "LIVE_CAMERA"


class CaptureQualityStatus(str, Enum):
    """Quality status from deterministic pre-classifier gating."""
    VALID = "VALID"
    BLUR_REJECTED = "BLUR_REJECTED"
    GLARE_REJECTED = "GLARE_REJECTED"
    EXPOSURE_REJECTED = "EXPOSURE_REJECTED"
    ALIGNMENT_REJECTED = "ALIGNMENT_REJECTED"
