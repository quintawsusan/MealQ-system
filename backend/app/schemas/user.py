from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.common import UserRole

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    first_name: str
    last_name: str
    user_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    email_verified: bool
    failed_attempts: int
    locked: bool
    created_at: datetime
    updated_at: datetime
    
class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None
