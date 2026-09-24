"""
Assay Profile Endpoints for REACTRA V2.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.profile import AssayProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import AssayProfileCreate, AssayProfileResponse

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("", response_model=List[AssayProfileResponse])
async def list_profiles(db: Session = Depends(get_db)) -> List[AssayProfileResponse]:
    """Lists registered active colorimetric assay profiles."""
    repo = ProfileRepository(db)
    profiles = repo.list_active()
    
    # If table is empty, seed default standard profiles
    if not profiles:
        default_profiles = [
            AssayProfile(
                profile_id="marquis-standard-v1",
                profile_name="Marquis Reagent Profile",
                profile_version="v1.0.0",
                status="ACTIVE",
                manufacturer_or_source="Standard Field Assay Registry",
                reference_card_version="ref-card-grid-3x2",
                t_min_seconds=15.0,
                t_max_seconds=60.0,
                kinetic_window_required=True,
            ),
            AssayProfile(
                profile_id="scott-cocaine-v1",
                profile_name="Scott Reagent Profile",
                profile_version="v1.0.0",
                status="ACTIVE",
                manufacturer_or_source="Standard Field Assay Registry",
                reference_card_version="ref-card-grid-3x2",
                t_min_seconds=10.0,
                t_max_seconds=45.0,
                kinetic_window_required=True,
            ),
            AssayProfile(
                profile_id="duquenois-cannabis-v1",
                profile_name="Duquenois-Levine Profile",
                profile_version="v1.0.0",
                status="ACTIVE",
                manufacturer_or_source="Standard Field Assay Registry",
                reference_card_version="ref-card-grid-3x2",
                t_min_seconds=30.0,
                t_max_seconds=120.0,
                kinetic_window_required=True,
            ),
        ]
        for p in default_profiles:
            repo.create(p)
        profiles = repo.list_active()
        
    return profiles


@router.post("", response_model=AssayProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    req: AssayProfileCreate,
    db: Session = Depends(get_db),
) -> AssayProfileResponse:
    """Registers a new assay profile definition."""
    repo = ProfileRepository(db)
    existing = repo.get_by_id_and_version(req.profile_id, req.profile_version)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile '{req.profile_id}' version '{req.profile_version}' is already registered.",
        )
    profile = AssayProfile(**req.model_dump())
    return repo.create(profile)
