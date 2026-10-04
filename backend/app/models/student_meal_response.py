from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4
class StudentMealResponse(Base):
    __tablename__ = "student_meal_responses"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_student_meal_response_session_student"),
        CheckConstraint("response IN ('GOING', 'SKIPPED', 'NO_RESPONSE')", name="ck_student_meal_response_value"),
    )
    response_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Uuid(as_uuid=True), ForeignKey("meal_sessions.session_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Uuid(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("serving_batches.batch_id", ondelete="CASCADE"), nullable=False)
    response = Column(String(20), nullable=False, default="NO_RESPONSE")
    responded_at = Column(DateTime(timezone=True), nullable=True)
    session = relationship("MealSession", back_populates="responses")
    student = relationship("Student", back_populates="meal_responses")
    batch = relationship("ServingBatch", back_populates="responses")
