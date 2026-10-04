from uuid import uuid4
from sqlalchemy import String, Uuid, Column
from sqlalchemy.orm import relationship
from app.database import Base

class MealType(Base):
    __tablename__ = "meal_types"
    meal_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(30), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    schedules = relationship("MealSchedule", back_populates="meal_type")
