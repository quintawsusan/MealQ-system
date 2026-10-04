from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4
class ServingBatch(Base):
    __tablename__ = "serving_batches"
    __table_args__ = (
        UniqueConstraint("session_id", "batch_number", name="uq_serving_batches_session_number"),
        UniqueConstraint("session_id", "batch_id", name="uq_serving_batches_session_batch"),
        CheckConstraint("status IN ('WAITING', 'CALLED', 'COMPLETED')", name="ck_serving_batches_status"),
    )
    batch_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Uuid(as_uuid=True), ForeignKey("meal_sessions.session_id", ondelete="CASCADE"), nullable=False)
    batch_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="WAITING")
    called_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    session = relationship("MealSession", back_populates="batches")
    members = relationship("StudentBatch", back_populates="batch", cascade="all, delete-orphan", order_by="StudentBatch.student_position")
    responses = relationship("StudentMealResponse", back_populates="batch")
