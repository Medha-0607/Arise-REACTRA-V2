from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CustodyCreateRequest(BaseModel):
    receiver_name: str = Field(..., min_length=1, max_length=128)
    receiver_agency: str = Field(..., min_length=1, max_length=128)
    receiver_badge_or_id: str = Field(..., min_length=1, max_length=64)
    package_seal_verified: bool = Field(default=True)
    notes: Optional[str] = None


class CustodyEventResponse(BaseModel):
    id: str
    evidence_id: str
    session_id: str
    sender_operator_id: str
    receiver_name: str
    receiver_agency: str
    receiver_badge_or_id: str
    package_seal_verified: bool
    notes: Optional[str] = None
    transferred_at_utc: Union[datetime, str]
    model_config = ConfigDict(from_attributes=True)

