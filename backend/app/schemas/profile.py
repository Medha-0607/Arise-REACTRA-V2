"""
Pydantic Schemas for Assay Profiles (Pydantic V2).
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AssayProfileBase(BaseModel):
    profile_id: str = Field(..., description="Unique profile identifier, e.g. marquis-standard-v1")
    profile_name: str = Field(..., description="Human-readable profile name")
    profile_version: str = Field(default="v1.0.0", description="Profile release version")
    status: str = Field(default="ACTIVE", description="Profile operational status")
    manufacturer_or_source: Optional[str] = None
    reference_card_version: str = Field(default="ref-card-grid-3x2")
    t_min_seconds: float = Field(default=15.0)
    t_max_seconds: float = Field(default=60.0)
    kinetic_window_required: bool = True
    threshold_configuration: Optional[Dict[str, Any]] = None
    calibration_targets: Optional[Dict[str, Any]] = None
    classifier_configuration: Optional[Dict[str, Any]] = None
    reaction_start_definition: Optional[str] = None
    reaction_roi_definition: Optional[Dict[str, Any]] = None


class AssayProfileCreate(AssayProfileBase):
    pass


class AssayProfileResponse(AssayProfileBase):
    profile_effective_from_utc: datetime
    profile_effective_until_utc: Optional[datetime] = None
    profile_snapshot_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
