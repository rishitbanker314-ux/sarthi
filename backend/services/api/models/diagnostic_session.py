import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from services.api.models.base import Base
from services.api.models.enums import DiagnosticStatus

class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    status: Mapped[DiagnosticStatus] = mapped_column(ENUM(DiagnosticStatus, name="diagnostic_status_enum", create_type=True), nullable=False)
    
    transcript: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=list)
    derived_profile: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
