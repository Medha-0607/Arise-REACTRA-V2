"""
Authoritative Domain State Machine for REACTRA V2.
Based on PRD Section 33 & Master Build Spec.
Defines all 10 workflow states, allowed transitions, and quality-gate invariants.
"""

from enum import Enum
from typing import Set, Dict, Union


class SessionState(str, Enum):
    """The 10 Authoritative Test Session States from PRD Section 33."""
    DRAFT = "DRAFT"
    CAPTURED = "CAPTURED"
    QUALITY_CHECKING = "QUALITY_CHECKING"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    READY_FOR_CLASSIFICATION = "READY_FOR_CLASSIFICATION"
    CLASSIFIED = "CLASSIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REFERRAL_REQUIRED = "REFERRAL_REQUIRED"
    EVIDENCE_SEALED = "EVIDENCE_SEALED"
    COMPLETED = "COMPLETED"


class OutcomeState(str, Enum):
    """The 4 Presumptive Outcome States from Master Build Spec Section 11."""
    PRESUMPTIVE_POSITIVE = "PRESUMPTIVE_POSITIVE"
    PRESUMPTIVE_NEGATIVE = "PRESUMPTIVE_NEGATIVE"
    INCONCLUSIVE = "INCONCLUSIVE"
    INVALID_CAPTURE = "INVALID_CAPTURE"


class TransitionTrigger(str, Enum):
    """Action or event triggering a state machine transition."""
    INITIALIZE = "INITIALIZE"
    CAPTURE = "CAPTURE"
    START_QUALITY_CHECK = "START_QUALITY_CHECK"
    QUALITY_PASS = "QUALITY_PASS"
    QUALITY_FAIL = "QUALITY_FAIL"
    CLASSIFY = "CLASSIFY"
    REQUEST_REVIEW = "REQUEST_REVIEW"
    REQUEST_REFERRAL = "REQUEST_REFERRAL"
    SEAL_EVIDENCE = "SEAL_EVIDENCE"
    COMPLETE = "COMPLETE"


class CaptureSource(str, Enum):
    """Origin of the visual test card evidence."""
    LIVE_CAMERA = "LIVE_CAMERA"
    IMPORTED_IMAGE = "IMPORTED_IMAGE"
    # Legacy alias for backwards compatibility
    DIRECT_CAMERA = "LIVE_CAMERA"


class GpsStatus(str, Enum):
    """Location provenance classification."""
    ACQUIRED = "ACQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    OPERATOR_DECLARED = "OPERATOR_DECLARED"


class SyncState(str, Enum):
    """Offline/Sync status for local records."""
    LOCAL_ONLY = "LOCAL_ONLY"
    QUEUED_FOR_EXPORT = "QUEUED_FOR_EXPORT"
    EXPORTED = "EXPORTED"


class InvalidTransitionError(Exception):
    """Raised when an illegal state transition is requested."""
    def __init__(self, current_state: Union[SessionState, str], target_state: Union[SessionState, str], reason: str = ""):
        self.current_state = SessionState(current_state) if isinstance(current_state, str) else current_state
        self.target_state = SessionState(target_state) if isinstance(target_state, str) else target_state
        self.reason = reason
        curr_val = self.current_state.value if hasattr(self.current_state, "value") else str(self.current_state)
        targ_val = self.target_state.value if hasattr(self.target_state, "value") else str(self.target_state)
        message = f"Illegal transition from {curr_val} to {targ_val}."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message)


class SessionStateMachine:
    """
    Authoritative state machine enforcing deterministic transition rules.
    Guarantees invalid measurements cannot bypass quality gating to reach classification.
    """

    # Allowed transitions map: CurrentState -> Set of valid TargetStates
    VALID_TRANSITIONS: Dict[SessionState, Set[SessionState]] = {
        SessionState.DRAFT: {
            SessionState.CAPTURED,
        },
        SessionState.CAPTURED: {
            SessionState.QUALITY_CHECKING,
            SessionState.DRAFT,  # Allow resetting draft
        },
        SessionState.QUALITY_CHECKING: {
            SessionState.VALIDATION_FAILED,
            SessionState.READY_FOR_CLASSIFICATION,
            SessionState.CAPTURED,  # Recapture flow
        },
        SessionState.VALIDATION_FAILED: {
            SessionState.CAPTURED,  # Recapture flow
            SessionState.DRAFT,     # Reset flow
        },
        SessionState.READY_FOR_CLASSIFICATION: {
            SessionState.CLASSIFIED,
            SessionState.REVIEW_REQUIRED,
            SessionState.CAPTURED,  # Recapture/remeasure flow
            SessionState.DRAFT,     # Reset flow
        },
        SessionState.CLASSIFIED: {
            SessionState.REVIEW_REQUIRED,
            SessionState.REFERRAL_REQUIRED,
            SessionState.EVIDENCE_SEALED,
            SessionState.COMPLETED,
        },
        SessionState.REVIEW_REQUIRED: {
            SessionState.REFERRAL_REQUIRED,
            SessionState.EVIDENCE_SEALED,
            SessionState.COMPLETED,
        },
        SessionState.REFERRAL_REQUIRED: {
            SessionState.EVIDENCE_SEALED,
            SessionState.COMPLETED,
        },
        SessionState.EVIDENCE_SEALED: {
            SessionState.COMPLETED,
        },
        SessionState.COMPLETED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(cls, current_state: Union[SessionState, str], target_state: Union[SessionState, str]) -> bool:
        """Checks if a transition between two states is valid."""
        curr = SessionState(current_state) if isinstance(current_state, str) else current_state
        targ = SessionState(target_state) if isinstance(target_state, str) else target_state
        allowed_targets = cls.VALID_TRANSITIONS.get(curr, set())
        return targ in allowed_targets

    @classmethod
    def validate_transition(
        cls,
        current_state: Union[SessionState, str],
        target_state: Union[SessionState, str],
        quality_passed: bool | None = None,
    ) -> None:
        """
        Validates transition and raises InvalidTransitionError if disallowed.
        Enforces specific domain constraints such as quality gating.
        """
        curr = SessionState(current_state) if isinstance(current_state, str) else current_state
        targ = SessionState(target_state) if isinstance(target_state, str) else target_state

        if not cls.can_transition(curr, targ):
            raise InvalidTransitionError(
                curr,
                targ,
                reason="Transition path is not permitted by domain state machine.",
            )

        # Domain Guard: Transition to READY_FOR_CLASSIFICATION requires quality validation pass
        if targ == SessionState.READY_FOR_CLASSIFICATION and quality_passed is False:
            raise InvalidTransitionError(
                curr,
                targ,
                reason="Capture failed quality filters (blur/glare/exposure) and cannot enter classification.",
            )
