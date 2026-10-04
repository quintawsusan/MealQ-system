from __future__ import annotations
from uuid import uuid4
from sqlalchemy import String, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base

class Classroom(Base):
    __tablename__ = "classes"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), unique=True, nullable=False)
    students = relationship("Student", back_populates="classroom")
