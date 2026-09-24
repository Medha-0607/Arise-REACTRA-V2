"""REACTRA V2 — Classifier Request & Response Schemas (Pydantic V2)."""

from typing import Tuple, Optional
from pydantic import BaseModel, ConfigDict
from app.domain.state_machine import OutcomeState


class ClassificationExplanationResponse(BaseModel):
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
    threshold_status: str
    presumptive_disclaimer: str
    model_config = ConfigDict(from_attributes=True)


class ClassificationResponse(BaseModel):
    session_id: str
    session_status: str
    outcome: OutcomeState
    class_distance_1: float
    class_distance_2: float
    decision_margin: float
    explanation: ClassificationExplanationResponse
    threshold_status: str
    model_config = ConfigDict(from_attributes=True)
