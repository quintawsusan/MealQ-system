from pydantic import BaseModel, EmailStr, Field, AliasChoices
from app.schemas.common import UserRole
from app.schemas.user import UserResponse

class StudentRegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    user_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    student_number: int = Field(gt=0)
    class_name: str = Field(validation_alias=AliasChoices("class", "class_name"), min_length=1)

class AdminCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    user_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

class LoginResponse(BaseModel):
    mfa_required: bool
    challenge_token: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"

class MFAVerifyRequest(BaseModel):
    challenge_token: str
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class MFASetupConfirmRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

class FirstSuperAdminCreateRequest(AdminCreateRequest):
    pass

__all__ = [
    "StudentRegisterRequest",
    "AdminCreateRequest",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "VerifyEmailRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ChangePasswordRequest",
    "FirstSuperAdminCreateRequest",
    "MFAVerifyRequest",
    "MFASetupConfirmRequest",
    "UserResponse",
]