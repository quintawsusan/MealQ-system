from datetime import datetime
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, Column, func
from app.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    actor_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String(80), nullable=False, index=True)
    target_id = Column(Uuid(as_uuid=True), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    metadata_json = Column("metadata", JSON, nullable=True)

class MFAOTP(Base):
    __tablename__ = "mfa_otps"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"),nullable=False,)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)