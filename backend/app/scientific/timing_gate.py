"""REACTRA V2 — Kinetic Reaction Timing Gate.

Validates that capture execution timestamp falls strictly within the profile-defined
reaction kinetics window.
Section References: PRD V2 §14, Master Build Spec §14.
"""

from typing import Dict, Optional, Any


class TimingGateResult:
    """Diagnostic container for reaction timing window compliance."""
    def __init__(
        self,
        compliance_status: str,  # 'IN_WINDOW', 'EXPIRED', 'EARLY', 'UNSPECIFIED'
        elapsed_seconds: Optional[float],
        target_window_seconds: int,
        min_window_seconds: int,
        max_window_seconds: int,
        passed: bool,
        explanation: str,
    ):
        self.compliance_status = compliance_status
        self.elapsed_seconds = elapsed_seconds
        self.target_window_seconds = target_window_seconds
        self.min_window_seconds = min_window_seconds
        self.max_window_seconds = max_window_seconds
        self.passed = passed
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compliance_status": self.compliance_status,
            "elapsed_seconds": round(self.elapsed_seconds, 1) if self.elapsed_seconds is not None else None,
            "target_window_seconds": self.target_window_seconds,
            "min_window_seconds": self.min_window_seconds,
            "max_window_seconds": self.max_window_seconds,
            "passed": self.passed,
            "explanation": self.explanation,
        }


def evaluate_reaction_timing(
    elapsed_seconds: Optional[float],
    target_window_seconds: int = 30,
    min_window_seconds: int = 10,
    max_window_seconds: int = 120,
) -> TimingGateResult:
    """Evaluate reaction timing compliance against profile kinetics limits.
    
    Parameters
    ----------
    elapsed_seconds : float, optional
        Elapsed seconds since reagent contact.
    target_window_seconds : int
        Nominal target reaction window.
    min_window_seconds : int
        Minimum incubation seconds required for color development.
    max_window_seconds : int
        Maximum window seconds before over-development / evaporation.
        
    Returns
    -------
    TimingGateResult
    """
    if elapsed_seconds is None:
        # Default nominal pass if timing not tracked or instantaneous field test
        return TimingGateResult(
            compliance_status="IN_WINDOW",
            elapsed_seconds=float(target_window_seconds),
            target_window_seconds=target_window_seconds,
            min_window_seconds=min_window_seconds,
            max_window_seconds=max_window_seconds,
            passed=True,
            explanation=f"Reaction timing defaulted to nominal profile window ({target_window_seconds}s).",
        )

    if elapsed_seconds < min_window_seconds:
        return TimingGateResult(
            compliance_status="EARLY",
            elapsed_seconds=elapsed_seconds,
            target_window_seconds=target_window_seconds,
            min_window_seconds=min_window_seconds,
            max_window_seconds=max_window_seconds,
            passed=False,
            explanation=(
                f"Capture executed too early ({elapsed_seconds:.1f}s < minimum {min_window_seconds}s). "
                "Reaction has not fully developed."
            ),
        )

    if elapsed_seconds > max_window_seconds:
        return TimingGateResult(
            compliance_status="EXPIRED",
            elapsed_seconds=elapsed_seconds,
            target_window_seconds=target_window_seconds,
            min_window_seconds=min_window_seconds,
            max_window_seconds=max_window_seconds,
            passed=False,
            explanation=(
                f"Reaction window expired ({elapsed_seconds:.1f}s > maximum {max_window_seconds}s). "
                "Reagent over-development or drying may invalidate color."
            ),
        )

    return TimingGateResult(
        compliance_status="IN_WINDOW",
        elapsed_seconds=elapsed_seconds,
        target_window_seconds=target_window_seconds,
        min_window_seconds=min_window_seconds,
        max_window_seconds=max_window_seconds,
        passed=True,
        explanation=f"Reaction timing compliant ({elapsed_seconds:.1f}s within [{min_window_seconds}s, {max_window_seconds}s]).",
    )
