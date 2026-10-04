from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4

class MealSession(Base):
    __tablename__ = "meal_sessions"
    __table_args__ = (
        UniqueConstraint("schedule_id", name="uq_meal_sessions_schedule_id"),
        CheckConstraint("batch_size > 0", name="ck_meal_sessions_batch_size_positive"),
        CheckConstraint("release_interval_seconds > 0", name="ck_meal_sessions_release_interval_positive"),
        CheckConstraint("response_window > 0", name="ck_meal_sessions_response_window_positive"),
        CheckConstraint("status IN ('SCHEDULED', 'ACTIVE', 'PAUSED', 'COMPLETED')", name="ck_meal_sessions_status"),
    )
    session_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    schedule_id = Column(Uuid(as_uuid=True), ForeignKey("meal_schedules.schedule_id"), nullable=False)
    status = Column(String(20), nullable=False, default="SCHEDULED")
    batch_size = Column(Integer, nullable=False, default=5)
    release_interval_seconds = Column(Integer, nullable=False, default=180)
    response_window = Column(Integer, nullable=False, default=60)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    schedule = relationship("MealSchedule", back_populates="session")
    creator = relationship("User", back_populates="created_sessions")
    batches = relationship("ServingBatch", back_populates="session", cascade="all, delete-orphan", order_by="ServingBatch.batch_number")
    responses = relationship("StudentMealResponse", back_populates="session", cascade="all, delete-orphan")
