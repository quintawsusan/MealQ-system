from uuid import UUID

from app.schemas.auth import LoginResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_super_admin, require_admin
from app.models.user import User
from app.schemas.auth import *
from app.schemas.user import UserResponse
from app.services import auth_service
from app.core.security import decode_mfa_challenge_token
from app.core.exceptions import AuthenticationError
from app.models.security import AuditLog


router=APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/setup/status")
def setup_status(db: Session=Depends(get_db)):
    return {"first_super_admin_required": db.scalar(select(User).where(User.role=="SUPER_ADMIN")) is None}

@router.post("/setup/first-super-admin", response_model=UserResponse, status_code=201)
def first_super_admin(data: FirstSuperAdminCreateRequest, db: Session=Depends(get_db)):
    return auth_service.create_first_super_admin(db,data)

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: StudentRegisterRequest, db: Session=Depends(get_db)):
    return auth_service.register_student(db,data)

@router.get("/verify-email", response_model=UserResponse)
def verify_email_link(token: str, db: Session=Depends(get_db)):
    return auth_service.verify_email(db,token)

@router.post("/verify-email", response_model=UserResponse)
def verify_email(data: VerifyEmailRequest, db: Session=Depends(get_db)):
    return auth_service.verify_email(db,data.token)

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.login(db,data.identifier,data.password,)
    challenge_token = auth_service.create_mfa_challenge(user)
    return LoginResponse(mfa_required=True,challenge_token=challenge_token,)

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session=Depends(get_db)):
    access=auth_service.refresh_access_token(db,data.refresh_token)
    return TokenResponse(access_token=access,refresh_token=data.refresh_token)

@router.post("/setup-mfa")
def setup_mfa(current_user: User = Depends(get_current_user),db: Session = Depends(get_db),):
    return auth_service.start_mfa_setup(db, current_user)

@router.post("/verify-mfa", response_model=TokenResponse)
def verify_mfa(data: MFAVerifyRequest, db: Session = Depends(get_db)):
    payload = decode_mfa_challenge_token(data.challenge_token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid MFA challenge")
    access_token, refresh_token = auth_service.verify_mfa_otp(db,UUID(user_id),data.code,)
    return TokenResponse(access_token=access_token,refresh_token=refresh_token,)

@router.post("/logout", status_code=204)
def logout(data: RefreshRequest, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    auth_service.logout(db,data.refresh_token,current_user.user_id)

@router.post("/forgot-password", status_code=202)
def forgot_password(data: PasswordResetRequest, db: Session=Depends(get_db)):
    auth_service.request_password_reset(db,data.identifier)
    return {"detail":"If an account matches, a password reset email has been sent."}

@router.post("/reset-password", status_code=204)
def reset_password(data: PasswordResetConfirm, db: Session=Depends(get_db)):
    auth_service.reset_password(db,data.token,data.new_password)

@router.post("/change-password", status_code=204)
def change_password(data: ChangePasswordRequest,current_user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    auth_service.change_password(db,current_user,data.current_password,data.new_password)

@router.post("/admin/users", response_model=UserResponse, status_code=201)
def create_admin(data: AdminCreateRequest, current_user: User=Depends(require_super_admin), db: Session=Depends(get_db)):
    return auth_service.register_admin(db,data,current_user)

@router.post("/users/{user_id}/unlock", response_model=UserResponse)
def unlock(user_id, current_user: User=Depends(require_super_admin), db: Session=Depends(get_db)):
    return auth_service.unlock_account(db,current_user,UUID(str(user_id)))

@router.get("/me", response_model=UserResponse)
def me(current_user: User=Depends(get_current_user)): return current_user

@router.get("/audit-logs")
def audit_logs(current_user: User=Depends(require_super_admin), db: Session=Depends(get_db), limit:int=100):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(max(1,min(limit,500))).all()
