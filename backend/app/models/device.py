from uuid import uuid4
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base

class StudentDevice(Base):
    __tablename__ = "student_devices"
    __table_args__ = (UniqueConstraint("student_id", name="uq_student_devices_student_id"),)
    device_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    student_id = Column(Uuid(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    device_identifier = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    student = relationship("Student", back_populates="device")
