"""
Unit tests for Domain Session State Machine.
"""

import pytest
from app.domain.state_machine import SessionState, SessionStateMachine, InvalidTransitionError


def test_valid_transitions():
    """Verifies that allowed transition paths succeed without error."""
    valid_paths = [
        (SessionState.DRAFT, SessionState.CAPTURED),
        (SessionState.CAPTURED, SessionState.QUALITY_CHECKING),
        (SessionState.QUALITY_CHECKING, SessionState.VALIDATION_FAILED),
        (SessionState.QUALITY_CHECKING, SessionState.READY_FOR_CLASSIFICATION),
        (SessionState.VALIDATION_FAILED, SessionState.CAPTURED),
        (SessionState.READY_FOR_CLASSIFICATION, SessionState.CLASSIFIED),
        (SessionState.READY_FOR_CLASSIFICATION, SessionState.REVIEW_REQUIRED),
        (SessionState.CLASSIFIED, SessionState.EVIDENCE_SEALED),
        (SessionState.REVIEW_REQUIRED, SessionState.REFERRAL_REQUIRED),
        (SessionState.REFERRAL_REQUIRED, SessionState.EVIDENCE_SEALED),
        (SessionState.EVIDENCE_SEALED, SessionState.COMPLETED),
    ]
    for current, target in valid_paths:
        assert SessionStateMachine.can_transition(current, target) is True
        # Should not raise exception
        SessionStateMachine.validate_transition(current, target, quality_passed=True)


def test_invalid_transitions_rejected():
    """Verifies that illegal jumps are rejected with InvalidTransitionError."""
    invalid_paths = [
        (SessionState.DRAFT, SessionState.CLASSIFIED),
        (SessionState.DRAFT, SessionState.EVIDENCE_SEALED),
        (SessionState.CAPTURED, SessionState.CLASSIFIED),
        (SessionState.VALIDATION_FAILED, SessionState.CLASSIFIED),
        (SessionState.VALIDATION_FAILED, SessionState.READY_FOR_CLASSIFICATION),
        (SessionState.VALIDATION_FAILED, SessionState.EVIDENCE_SEALED),
        (SessionState.COMPLETED, SessionState.DRAFT),
    ]
    for current, target in invalid_paths:
        assert SessionStateMachine.can_transition(current, target) is False
        with pytest.raises(InvalidTransitionError):
            SessionStateMachine.validate_transition(current, target)


def test_quality_gate_guardrail():
    """Verifies that transition to READY_FOR_CLASSIFICATION fails if quality_passed is False."""
    with pytest.raises(InvalidTransitionError) as exc_info:
        SessionStateMachine.validate_transition(
            current_state=SessionState.QUALITY_CHECKING,
            target_state=SessionState.READY_FOR_CLASSIFICATION,
            quality_passed=False,
        )
    assert "Capture failed quality filters" in str(exc_info.value)
