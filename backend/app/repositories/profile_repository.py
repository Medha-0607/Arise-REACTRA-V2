"""
Repository for Assay Profiles.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models.profile import AssayProfile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_version(self, profile_id: str, version: str = "v1.0.0") -> Optional[AssayProfile]:
        return (
            self.db.query(AssayProfile)
            .filter(AssayProfile.profile_id == profile_id, AssayProfile.profile_version == version)
            .first()
        )

    def list_active(self) -> List[AssayProfile]:
        return self.db.query(AssayProfile).filter(AssayProfile.status == "ACTIVE").all()

    def create(self, profile: AssayProfile) -> AssayProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
