import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import String, DateTime, Integer, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from services.api.models.base import Base
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    profile_version: Mapped[int] = mapped_column(Integer, nullable=False)
    
    prior_knowledge: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    
    pace: Mapped[Pace] = mapped_column(ENUM(Pace, name="pace_enum", create_type=True), nullable=False)
    representation_pref: Mapped[RepresentationPref] = mapped_column(ENUM(RepresentationPref, name="representation_pref_enum", create_type=True), nullable=False)
    scaffolding_pref: Mapped[ScaffoldingPref] = mapped_column(ENUM(ScaffoldingPref, name="scaffolding_pref_enum", create_type=True), nullable=False)
    depth_pref: Mapped[DepthPref] = mapped_column(ENUM(DepthPref, name="depth_pref_enum", create_type=True), nullable=False)
    motivation: Mapped[Motivation] = mapped_column(ENUM(Motivation, name="motivation_enum", create_type=True), nullable=False)
    
    session_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    accessibility: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'profile_version', name='uq_learner_profile_user_version'),
    )
