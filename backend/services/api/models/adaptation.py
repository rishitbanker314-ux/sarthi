import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, JSON, CheckConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from services.api.models.base import Base
from services.api.models.enums import AdaptationTrigger, AdaptationAction

class AdaptationEvent(Base):
    __tablename__ = "adaptation_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    
    trigger: Mapped[AdaptationTrigger] = mapped_column(ENUM(AdaptationTrigger, name="adaptation_trigger", create_type=True), nullable=False)
    action: Mapped[AdaptationAction] = mapped_column(ENUM(AdaptationAction, name="adaptation_action", create_type=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    timeline_impact: Mapped[str] = mapped_column(Text, nullable=False)
    
    before: Mapped[dict] = mapped_column(JSONB, nullable=False)
    after: Mapped[dict] = mapped_column(JSONB, nullable=False)
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        CheckConstraint("length(reason) > 0", name="adaptation_events_reason_check"),
        CheckConstraint("length(timeline_impact) > 0", name="adaptation_events_timeline_impact_check"),
        Index("ix_adaptation_events_user_id_created_at", "user_id", "created_at", postgresql_using="btree", postgresql_ops={"created_at": "DESC"}),
    )
