import uuid
from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation

class Accessibility(BaseModel):
    font_scale: float = Field(default=1.0, ge=1.0, le=2.0)
    reduced_motion: bool = Field(default=False)
    screen_reader: bool = Field(default=False)
    dyslexia_font: bool = Field(default=False)

class LearnerProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    profile_version: int
    prior_knowledge: dict[str, Any]
    pace: Pace
    representation_pref: RepresentationPref
    scaffolding_pref: ScaffoldingPref
    depth_pref: DepthPref
    motivation: Motivation
    session_minutes: int
    language: str
    accessibility: Accessibility
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LearnerProfilePatchRequest(BaseModel):
    prior_knowledge: dict[str, Any] | None = None
    pace: Pace | None = None
    representation_pref: RepresentationPref | None = None
    scaffolding_pref: ScaffoldingPref | None = None
    depth_pref: DepthPref | None = None
    motivation: Motivation | None = None
    session_minutes: int | None = None
    language: str | None = None
    accessibility: Accessibility | None = None
