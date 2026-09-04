import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, JSON, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base
from .enums import SignalType, MessageRole

class LessonContent(Base):
    __tablename__ = "lesson_contents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"))
    profile_version: Mapped[int] = mapped_column(Integer)
    blocks: Mapped[dict] = mapped_column(JSON)
    token_cost: Mapped[int] = mapped_column(Integer)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("lesson_id", "profile_version", name="uq_lesson_profile_version"),
    )

    lesson = relationship("Lesson", foreign_keys=[lesson_id])

class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    items: Mapped[dict] = mapped_column(JSON)

    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    user = relationship("User", foreign_keys=[user_id])
    attempts = relationship("CheckpointAttempt", back_populates="checkpoint", cascade="all, delete-orphan")

class CheckpointAttempt(Base):
    __tablename__ = "checkpoint_attempts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    checkpoint_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("checkpoints.id", ondelete="CASCADE"))
    responses: Mapped[dict] = mapped_column(JSON)
    score: Mapped[float] = mapped_column(Numeric)
    mastery_deltas: Mapped[dict] = mapped_column(JSON)
    feedback: Mapped[dict] = mapped_column(JSON)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    checkpoint = relationship("Checkpoint", back_populates="attempts")

class MasteryState(Base):
    __tablename__ = "mastery_states"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    concept_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("concepts.id", ondelete="CASCADE"))
    score: Mapped[float] = mapped_column(Numeric)
    confidence: Mapped[float] = mapped_column(Numeric)
    attempts: Mapped[int] = mapped_column(Integer)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_mastery_user_concept"),
    )

    user = relationship("User", foreign_keys=[user_id])
    concept = relationship("Concept", foreign_keys=[concept_id])

class TutorThread(Base):
    __tablename__ = "tutor_threads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"))

    user = relationship("User", foreign_keys=[user_id])
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
    messages = relationship("TutorMessage", back_populates="thread", cascade="all, delete-orphan", order_by="TutorMessage.created_at")

class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    thread_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tutor_threads.id", ondelete="CASCADE"))
    role: Mapped[MessageRole] = mapped_column(ENUM(MessageRole, name="message_role", create_type=True), nullable=False)
    content: Mapped[str] = mapped_column(String)
    blocks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    thread = relationship("TutorThread", back_populates="messages")

class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    block_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    type: Mapped[SignalType] = mapped_column(ENUM(SignalType, name="signal_type", create_type=True), nullable=False)
    value: Mapped[dict] = mapped_column(JSON)

    user = relationship("User", foreign_keys=[user_id])
    lesson = relationship("Lesson", foreign_keys=[lesson_id])
