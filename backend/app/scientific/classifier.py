"""REACTRA V2 — Presumptive Colorimetric Classifier Engine.

Executes profile-bound color distance matching on ValidatedMeasurement objects.
Decoupled Invariant: Operates ONLY on ValidatedMeasurement domain data, NEVER raw pixels.
Section References: PRD V2 §17-19, Master Build Spec §16-18.
"""

import math
from typing import Tuple, Optional, List
from pydantic import BaseModel, Field
from app.domain.state_machine import OutcomeState
from app.scientific.measurement import ValidatedMeasurement
from app.scientific.profiles import ScientificAssayProfile


class ClassificationPreconditionError(Exception):
    """Raised when measurement fails mandatory pre-classification gates."""
    pass


class ClassificationExplanation(BaseModel):
    """Authoritative structured explanation of the classifier decision."""
    outcome: OutcomeState
    measured_lab: Tuple[float, float, float]
    target_centroid_lab: Tuple[float, float, float]
    control_centroid_lab: Tuple[float, float, float]
    distance_to_target: float
    distance_to_control: float
    positive_threshold: float
    negative_threshold: float
    decision_margin: float
    profile_id: str
    profile_version: str
    algorithm_version: str
    measurement_id: str
    timing_validity: str
    calibration_status: str
    quality_status: str
    threshold_status: str = "HEURISTIC_SPECIFICATION_DERIVED"
    presumptive_disclaimer: str = (
        "Preliminary presumptive colorimetric indication only. Requires confirmatory "
        "laboratory testing (GC-MS / HPLC) for forensic evidentiary confirmation. "
        "Does not constitute definitive chemical identification or legal proof."
    )


class ClassificationResult(BaseModel):
    """Consolidated outcome of the presumptive classification engine."""
    outcome: OutcomeState
    class_distance_1: float
    class_distance_2: float
    decision_margin: float
    explanation: ClassificationExplanation
    threshold_status: str = "HEURISTIC_SPECIFICATION_DERIVED"


def delta_e_76(lab1: Tuple[float, float, float] | List[float], lab2: Tuple[float, float, float] | List[float]) -> float:
    """Computes standard CIE 1976 Delta E Euclidean distance between two Lab points."""
    dL = float(lab1[0]) - float(lab2[0])
    da = float(lab1[1]) - float(lab2[1])
    db = float(lab1[2]) - float(lab2[2])
    return math.sqrt(dL * dL + da * da + db * db)


def validate_measurement_preconditions(
    measurement: ValidatedMeasurement,
    profile: ScientificAssayProfile,
) -> None:
    """
    Enforces strict scientific invariants prior to classification.
    Raises ClassificationPreconditionError if any mandatory condition is unsatisfied.
    """
    if measurement is None:
        raise ClassificationPreconditionError("ValidatedMeasurement object is missing or null.")

    # 1. Quality Guard Validation
    if not measurement.quality_diagnostics.passed_all_hard_gates:
        raise ClassificationPreconditionError(
            f"Measurement rejected by Adaptive Capture Guard: {measurement.quality_diagnostics.failure_reasons}"
        )

    # 2. Calibration Validation
    if not measurement.calibration_passed:
        raise ClassificationPreconditionError(
            f"Measurement color calibration failed: residual {measurement.calibration_mean_delta_e:.2f} Delta E"
        )

    # 3. Timing Gate Validation
    if measurement.timing_compliance == "INVALID":
        raise ClassificationPreconditionError("Measurement reaction incubation timing gate failed compliance.")

    # 4. Profile & Version Binding Validation
    if measurement.profile_id != profile.profile_id:
        raise ClassificationPreconditionError(
            f"Profile mismatch: Measurement bound to '{measurement.profile_id}', requested profile is '{profile.profile_id}'."
        )

    if measurement.profile_version != profile.profile_version:
        raise ClassificationPreconditionError(
            f"Profile version mismatch: Measurement bound to version '{measurement.profile_version}', "
            f"profile is version '{profile.profile_version}'."
        )

    if measurement.algorithm_version != profile.algorithm_version:
        raise ClassificationPreconditionError(
            f"Algorithm version incompatibility: Measurement used '{measurement.algorithm_version}', "
            f"profile expects '{profile.algorithm_version}'."
        )

    # 5. Required ROIs presence
    cfg = profile.classifier_config
    if cfg.target_roi_id not in measurement.well_measurements:
        raise ClassificationPreconditionError(
            f"Required target reaction ROI '{cfg.target_roi_id}' not found in measurement data."
        )

    target_well = measurement.well_measurements[cfg.target_roi_id]
    if not target_well.is_valid:
        raise ClassificationPreconditionError(
            f"Target reaction ROI '{cfg.target_roi_id}' is marked invalid: {target_well.rejection_reason}"
        )


def classify_measurement(
    measurement: ValidatedMeasurement,
    profile: ScientificAssayProfile,
) -> ClassificationResult:
    """
    Authoritative Presumptive Classifier.
    
    Evaluates calibrated CIE L*a*b* color vectors from ValidatedMeasurement against
    profile reference centroids and decision boundaries.
    
    Parameters
    ----------
    measurement : ValidatedMeasurement
        Authoritative measurement output from Phase 3 pipeline.
    profile : ScientificAssayProfile
        Registered assay profile with bound classifier configuration.
        
    Returns
    -------
    ClassificationResult
        Four-state presumptive classification with complete explanatory metadata.
    """
    # 1. Hard preconditions check
    validate_measurement_preconditions(measurement, profile)

    cfg = profile.classifier_config
    target_well = measurement.well_measurements[cfg.target_roi_id]
    measured_lab: Tuple[float, float, float] = (
        target_well.calibrated_lab_median[0],
        target_well.calibrated_lab_median[1],
        target_well.calibrated_lab_median[2],
    )

    # 2. Distance Calculations (CIE Delta E 1976)
    dist_to_target = delta_e_76(measured_lab, cfg.target_positive_lab)
    dist_to_control = delta_e_76(measured_lab, cfg.negative_control_lab)

    # Decision Margin: difference between negative threshold and actual distance to target
    decision_margin = round(cfg.negative_distance_threshold - dist_to_target, 2)

    # 3. Decision Region Logic
    # distance <= positive_threshold => PRESUMPTIVE_POSITIVE
    # distance >= negative_threshold => PRESUMPTIVE_NEGATIVE
    # otherwise => INCONCLUSIVE
    if dist_to_target <= cfg.positive_distance_threshold:
        outcome = OutcomeState.PRESUMPTIVE_POSITIVE
    elif dist_to_target >= cfg.negative_distance_threshold:
        outcome = OutcomeState.PRESUMPTIVE_NEGATIVE
    else:
        outcome = OutcomeState.INCONCLUSIVE

    # 4. Construct Explanation
    explanation = ClassificationExplanation(
        outcome=outcome,
        measured_lab=(round(measured_lab[0], 2), round(measured_lab[1], 2), round(measured_lab[2], 2)),
        target_centroid_lab=cfg.target_positive_lab,
        control_centroid_lab=cfg.negative_control_lab,
        distance_to_target=round(dist_to_target, 2),
        distance_to_control=round(dist_to_control, 2),
        positive_threshold=cfg.positive_distance_threshold,
        negative_threshold=cfg.negative_distance_threshold,
        decision_margin=decision_margin,
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        algorithm_version=profile.algorithm_version,
        measurement_id=measurement.measurement_id,
        timing_validity=measurement.timing_compliance,
        calibration_status="PASSED" if measurement.calibration_passed else "FAILED",
        quality_status=measurement.quality_diagnostics.overall_status,
        threshold_status=cfg.threshold_status,
    )

    return ClassificationResult(
        outcome=outcome,
        class_distance_1=round(dist_to_target, 2),
        class_distance_2=round(dist_to_control, 2),
        decision_margin=decision_margin,
        explanation=explanation,
        threshold_status=cfg.threshold_status,
    )
