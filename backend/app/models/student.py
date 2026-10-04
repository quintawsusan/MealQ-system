from __future__ import annotations
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid, func, Column
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("user_id", name="uq_students_user_id"),)
    student_id = Column(Uuid(as_uuid=True), primary_key=True, default=__import__("uuid").uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    student_number = Column(Integer, unique=True, nullable=False)
    class_id = Column(Uuid(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    user = relationship("User", back_populates="student")
    classroom = relationship("Classroom", back_populates="students")
    device = relationship("StudentDevice", back_populates="student", uselist=False, cascade="all, delete-orphan")
    batch_memberships = relationship("StudentBatch", back_populates="student")
    meal_responses = relationship("StudentMealResponse", back_populates="student")
    @property
    def class_name(self):
        return self.classroom.name if self.classroom else None
