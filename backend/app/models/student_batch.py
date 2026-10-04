from sqlalchemy import ForeignKey, Integer, UniqueConstraint, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4
class StudentBatch(Base):
    __tablename__ = "student_batches"
    __table_args__ = (
        UniqueConstraint("batch_id", "student_id", name="uq_student_batches_member"),
        UniqueConstraint("batch_id", "student_position", name="uq_student_batches_position"),
    )
    batch_student_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    batch_id = Column(Uuid(as_uuid=True), ForeignKey("serving_batches.batch_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Uuid(as_uuid=True), ForeignKey("students.student_id"), nullable=False)
    student_position = Column(Integer, nullable=False)
    batch = relationship("ServingBatch", back_populates="members")
    student = relationship("Student", back_populates="batch_memberships")
