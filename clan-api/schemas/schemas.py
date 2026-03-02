import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ClanCreate(BaseModel):
    """Request body for creating a clan."""
    name: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=2, max_length=10)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Clan name cannot be blank")
        return v.strip()

    @field_validator("region")
    @classmethod
    def region_upper(cls, v):
        return v.strip().upper()


class ClanResponse(BaseModel):
    """Response body for clan endpoints."""
    id: uuid.UUID
    name: str
    region: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    id: uuid.UUID | None = None
