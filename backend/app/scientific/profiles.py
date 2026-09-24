"""REACTRA V2 — Scientific Assay & Reference Card Profiles.

Profile-driven configuration for card geometries, reference calibration patches,
reaction ROIs, quality thresholds, and reaction timing windows.
Section References: PRD V2 §14-16, Master Build Spec §13-15.
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class CalibrationPatchDef(BaseModel):
    """Definition of a reference color patch on the canonical reference card."""
    patch_id: str
    name: str
    # Bounding box on canonical card: [x, y, width, height]
    bbox: Tuple[int, int, int, int]
    # Nominal reference color in CIE L*a*b* (D65/2°)
    nominal_lab: Tuple[float, float, float]


class ReactionRoiDef(BaseModel):
    """Definition of a reaction well / sampling region of interest."""
    roi_id: str
    name: str
    # Bounding box on canonical card: [x, y, width, height]
    bbox: Tuple[int, int, int, int]
    # Margin (in pixels) to erode from border to avoid plastic pouch edges
    inset_margin_px: int = 4
    # Minimum valid pixel count required after glare rejection
    min_valid_pixels: int = 50


class QualityThresholds(BaseModel):
    """Profile/device configured thresholds for the Adaptive Capture Guard."""
    # Laplacian blur variance threshold (Master Build Spec §10)
    min_laplacian_variance: float = 120.0
    # Exposure mean luminance range [0-255]
    min_mean_luminance: float = 40.0
    max_mean_luminance: float = 220.0
    # Maximum allowed fraction of underexposed pixels (< 15 luma)
    max_underexposure_fraction: float = 0.15
    # Maximum allowed fraction of overexposed / clipped pixels (> 245 luma)
    max_overexposure_fraction: float = 0.10
    # Specular glare threshold: maximum allowed fraction of ROI covered by glare
    max_glare_roi_fraction: float = 0.05  # 5%
    # Maximum acceptable mean calibration Delta E76 residual across reference patches
    max_calibration_delta_e: float = 18.0
    # Maximum allowed perspective skew angle (degrees)
    max_skew_angle_deg: float = 20.0


class ClassifierConfig(BaseModel):
    """Profile-specific classification centroids and decision boundaries."""
    target_roi_id: str = "well_1"
    control_roi_id: str = "well_2"
    # Nominal positive reaction centroid in CIE L*a*b* (D65)
    target_positive_lab: Tuple[float, float, float] = (35.0, 30.0, -15.0)
    # Nominal negative/blank control centroid in CIE L*a*b* (D65)
    negative_control_lab: Tuple[float, float, float] = (90.0, 0.0, 2.0)
    # Decision boundaries (Delta E distance in CIE L*a*b*)
    # Distance <= positive_threshold => PRESUMPTIVE_POSITIVE
    # Distance >= negative_threshold => PRESUMPTIVE_NEGATIVE
    # Otherwise => INCONCLUSIVE
    positive_distance_threshold: float = 25.0
    negative_distance_threshold: float = 45.0
    # Provenance of thresholds (strictly labeled as heuristic/specification-derived pending physical trials)
    threshold_status: str = "HEURISTIC_SPECIFICATION_DERIVED"


class ScientificAssayProfile(BaseModel):
    """Complete scientific profile defining optical parameters for analysis."""
    profile_id: str
    profile_name: str
    profile_version: str
    reference_card_version: str
    algorithm_version: str = "2.0.0"
    
    # Canonical reference card dimensions (width, height in pixels)
    canonical_card_width: int = 600
    canonical_card_height: int = 400
    card_aspect_ratio: float = 1.5  # 600 / 400
    
    # Reaction timing window in seconds
    target_reaction_window_seconds: int = 30
    min_reaction_window_seconds: int = 10
    max_reaction_window_seconds: int = 120
    
    # Quality thresholds
    thresholds: QualityThresholds = Field(default_factory=QualityThresholds)
    
    # Reference calibration patches
    calibration_patches: List[CalibrationPatchDef] = Field(default_factory=list)
    
    # Reaction well ROIs
    reaction_rois: List[ReactionRoiDef] = Field(default_factory=list)

    # Classification configuration
    classifier_config: ClassifierConfig = Field(default_factory=ClassifierConfig)


# Standard 3x2 Grid Reference Card Profile
# Card layout: 600x400 px
# Top row (Y=30 to Y=110): 6 Reference Calibration Patches (White, Neutral Gray 70%, Neutral Gray 40%, Black, Cyan, Magenta)
# Bottom rows (Y=160 to Y=350): Reaction wells
STANDARD_GRID_PROFILE = ScientificAssayProfile(
    profile_id="marquis-standard-v1",
    profile_name="Marquis Reagent Profile",
    profile_version="1.0.0",
    reference_card_version="ref-card-grid-3x2",
    canonical_card_width=600,
    canonical_card_height=400,
    card_aspect_ratio=1.5,
    target_reaction_window_seconds=30,
    min_reaction_window_seconds=10,
    max_reaction_window_seconds=120,
    thresholds=QualityThresholds(
        min_laplacian_variance=120.0,
        min_mean_luminance=40.0,
        max_mean_luminance=220.0,
        max_underexposure_fraction=0.15,
        max_overexposure_fraction=0.10,
        max_glare_roi_fraction=0.05,
        max_calibration_delta_e=18.0,
        max_skew_angle_deg=20.0,
    ),
    calibration_patches=[
        # Reference White Patch (L*=95.0, a*=0.0, b*=0.0)
        CalibrationPatchDef(patch_id="patch_white", name="Reference White", bbox=(40, 30, 60, 60), nominal_lab=(95.0, 0.0, 0.0)),
        # Light Neutral Gray (L*=70.0, a*=0.0, b*=0.0)
        CalibrationPatchDef(patch_id="patch_gray_light", name="Neutral Gray 70%", bbox=(130, 30, 60, 60), nominal_lab=(70.0, 0.0, 0.0)),
        # Mid Neutral Gray (L*=50.0, a*=0.0, b*=0.0)
        CalibrationPatchDef(patch_id="patch_gray_mid", name="Neutral Gray 50%", bbox=(220, 30, 60, 60), nominal_lab=(50.0, 0.0, 0.0)),
        # Reference Black Patch (L*=10.0, a*=0.0, b*=0.0)
        CalibrationPatchDef(patch_id="patch_black", name="Reference Black", bbox=(310, 30, 60, 60), nominal_lab=(10.0, 0.0, 0.0)),
        # Color Calibration Patch 1: Cyan / Primary (L*=60.0, a*=-30.0, b*=-25.0)
        CalibrationPatchDef(patch_id="patch_cyan", name="Reference Cyan", bbox=(400, 30, 60, 60), nominal_lab=(60.0, -30.0, -25.0)),
        # Color Calibration Patch 2: Magenta / Primary (L*=50.0, a*=55.0, b*=-15.0)
        CalibrationPatchDef(patch_id="patch_magenta", name="Reference Magenta", bbox=(490, 30, 60, 60), nominal_lab=(50.0, 55.0, -15.0)),
    ],
    reaction_rois=[
        # Primary Reaction Well 1 (Left Test Well)
        ReactionRoiDef(roi_id="well_1", name="Primary Reaction Well", bbox=(80, 180, 120, 120), inset_margin_px=8, min_valid_pixels=80),
        # Control / Secondary Reaction Well 2 (Right Control Well)
        ReactionRoiDef(roi_id="well_2", name="Negative Control Well", bbox=(400, 180, 120, 120), inset_margin_px=8, min_valid_pixels=80),
    ],
    classifier_config=ClassifierConfig(
        target_roi_id="well_1",
        control_roi_id="well_2",
        target_positive_lab=(35.0, 30.0, -15.0),  # Marquis purple/violet
        negative_control_lab=(90.0, 0.0, 2.0),
        positive_distance_threshold=25.0,
        negative_distance_threshold=45.0,
        threshold_status="HEURISTIC_SPECIFICATION_DERIVED",
    ),
)


REGISTERED_SCIENTIFIC_PROFILES: Dict[str, ScientificAssayProfile] = {
    "marquis-standard-v1": STANDARD_GRID_PROFILE,
    "scott-cocaine-v1": STANDARD_GRID_PROFILE.model_copy(
        update={
            "profile_id": "scott-cocaine-v1",
            "profile_name": "Scott Reagent Profile",
            "classifier_config": ClassifierConfig(
                target_roi_id="well_1",
                control_roi_id="well_2",
                target_positive_lab=(40.0, -15.0, -35.0),  # Cobalt blue
                negative_control_lab=(90.0, 0.0, 2.0),
                positive_distance_threshold=25.0,
                negative_distance_threshold=45.0,
                threshold_status="HEURISTIC_SPECIFICATION_DERIVED",
            ),
        }
    ),
    "duquenois-cannabis-v1": STANDARD_GRID_PROFILE.model_copy(
        update={
            "profile_id": "duquenois-cannabis-v1",
            "profile_name": "Duquenois-Levine Profile",
            "classifier_config": ClassifierConfig(
                target_roi_id="well_1",
                control_roi_id="well_2",
                target_positive_lab=(30.0, 20.0, -20.0),  # Purple-blue bottom layer
                negative_control_lab=(90.0, 0.0, 2.0),
                positive_distance_threshold=25.0,
                negative_distance_threshold=45.0,
                threshold_status="HEURISTIC_SPECIFICATION_DERIVED",
            ),
        }
    ),
    "mecke-opiates-v1": STANDARD_GRID_PROFILE.model_copy(
        update={
            "profile_id": "mecke-opiates-v1",
            "profile_name": "Mecke Reagent Profile",
            "classifier_config": ClassifierConfig(
                target_roi_id="well_1",
                control_roi_id="well_2",
                target_positive_lab=(35.0, -20.0, 15.0),  # Dark teal/green
                negative_control_lab=(90.0, 0.0, 2.0),
                positive_distance_threshold=25.0,
                negative_distance_threshold=45.0,
                threshold_status="HEURISTIC_SPECIFICATION_DERIVED",
            ),
        }
    ),
}


def get_scientific_profile(profile_id: str) -> ScientificAssayProfile:
    """Retrieve scientific profile configuration by identifier, falling back to standard grid."""
    return REGISTERED_SCIENTIFIC_PROFILES.get(profile_id, STANDARD_GRID_PROFILE)
