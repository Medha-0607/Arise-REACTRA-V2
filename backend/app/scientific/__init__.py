"""REACTRA V2 — Scientific Module Exports."""

from app.scientific.profiles import (
    ScientificAssayProfile,
    CalibrationPatchDef,
    ReactionRoiDef,
    QualityThresholds,
    get_scientific_profile,
    STANDARD_GRID_PROFILE,
)
from app.scientific.image_io import (
    ingest_image_data,
    IngestedImage,
    ImageValidationError,
)
from app.scientific.card_detection import (
    detect_reference_card,
    CardDetectionResult,
    order_corners,
)
from app.scientific.perspective import (
    normalize_card_perspective,
    PerspectiveResult,
)
from app.scientific.blur import evaluate_blur, BlurMetricResult
from app.scientific.exposure import evaluate_exposure, ExposureMetricResult
from app.scientific.glare import detect_specular_glare, GlareMetricResult
from app.scientific.color import rgb_to_lab, delta_e_76
from app.scientific.calibration import (
    calibrate_reference_card,
    CalibrationResult,
)
from app.scientific.roi import extract_reaction_rois, ExtractedRoi
from app.scientific.robust_estimation import (
    robust_estimate_well_color,
    WellColorMeasurement,
)
from app.scientific.timing_gate import (
    evaluate_reaction_timing,
    TimingGateResult,
)
from app.scientific.quality import (
    aggregate_quality_diagnostics,
    QualityDiagnostics,
)
from app.scientific.measurement import (
    execute_scientific_measurement,
    ValidatedMeasurement,
    MeasurementQualityError,
)

__all__ = [
    "ScientificAssayProfile",
    "CalibrationPatchDef",
    "ReactionRoiDef",
    "QualityThresholds",
    "get_scientific_profile",
    "STANDARD_GRID_PROFILE",
    "ingest_image_data",
    "IngestedImage",
    "ImageValidationError",
    "detect_reference_card",
    "CardDetectionResult",
    "order_corners",
    "normalize_card_perspective",
    "PerspectiveResult",
    "evaluate_blur",
    "BlurMetricResult",
    "evaluate_exposure",
    "ExposureMetricResult",
    "detect_specular_glare",
    "GlareMetricResult",
    "rgb_to_lab",
    "delta_e_76",
    "calibrate_reference_card",
    "CalibrationResult",
    "extract_reaction_rois",
    "ExtractedRoi",
    "robust_estimate_well_color",
    "WellColorMeasurement",
    "evaluate_reaction_timing",
    "TimingGateResult",
    "aggregate_quality_diagnostics",
    "QualityDiagnostics",
    "execute_scientific_measurement",
    "ValidatedMeasurement",
    "MeasurementQualityError",
]
