from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Uuid, func, Column, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('SUPER_ADMIN', 'ADMIN', 'STUDENT')", name="ck_users_role"),)

    user_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_name = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="STUDENT")
    is_active = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked = Column(Boolean, nullable=False, default=False)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    created_schedules = relationship("MealSchedule", back_populates="creator")
    created_sessions = relationship("MealSession", back_populates="creator")
