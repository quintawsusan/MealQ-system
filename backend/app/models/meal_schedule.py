from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Time, UniqueConstraint, Uuid, func, Column
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4

class MealSchedule(Base):
    __tablename__ = "meal_schedules"
    schedule_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    meal_type_id = Column(Uuid(as_uuid=True), ForeignKey("meal_types.meal_id"), nullable=False)
    meal_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    menu_description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    meal_type = relationship("MealType", back_populates="schedules")
    creator = relationship("User", back_populates="created_schedules")
    session = relationship("MealSession", back_populates="schedule", uselist=False, cascade="all, delete-orphan")
