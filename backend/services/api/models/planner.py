import uuid
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import String, Date, Integer, ForeignKey, JSON, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base
from .enums import JobKind, JobStatus

class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    raw_input: Mapped[str] = mapped_column(String)
    normalized_topic: Mapped[str] = mapped_column(String)
    target_level: Mapped[str] = mapped_column(String)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    motivation_hint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_educational: Mapped[bool] = mapped_column(default=True, server_default="true")
    clarification_needed: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="goals")
    plans = relationship("Plan", back_populates="goal", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    rationale: Mapped[str] = mapped_column(String)
    profile_version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("goal_id", "version", name="uq_plan_goal_version"),
    )

    goal = relationship("Goal", back_populates="plans")
    modules = relationship("Module", back_populates="plan", cascade="all, delete-orphan", order_by="Module.order_index")

class Module(Base):
    __tablename__ = "modules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"))
    order_index: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    objective: Mapped[str] = mapped_column(String)
    rationale: Mapped[str] = mapped_column(String)
    est_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)

    __table_args__ = (
        Index("idx_modules_plan_order", "plan_id", "order_index"),
    )

    plan = relationship("Plan", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    module_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"))
    order_index: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    objective: Mapped[str] = mapped_column(String)
    concept_ids: Mapped[List[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)))
    est_minutes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)

    __table_args__ = (
        Index("idx_lessons_module_order", "module_id", "order_index"),
    )

    module = relationship("Module", back_populates="lessons")

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[JobKind] = mapped_column(ENUM(JobKind, name="job_kind", create_type=True), nullable=False)
    status: Mapped[JobStatus] = mapped_column(ENUM(JobStatus, name="job_status", create_type=True), nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    progress_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="chk_progress_range"),
        Index("idx_jobs_user_status", "user_id", "status"),
    )

    user = relationship("User", back_populates="jobs")
