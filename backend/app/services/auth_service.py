import pyotp
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from secrets import randbelow
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.exceptions import (AuthenticationError,BusinessRuleError,ConflictError,NotFoundError,)
from app.core.security import (create_access_token, create_mfa_challenge_token,hash_password,hash_token,verify_password,)
from app.models.classroom import Classroom
from app.models.security import (AuditLog,MFAOTP,PasswordResetToken,RefreshToken,VerificationToken,)
from app.models.student import Student
from app.models.user import User
from app.schemas.auth import AdminCreateRequest, StudentRegisterRequest
from app.services.email_service import send_email,build_verification_email

ALLOWED_CLASSES = ("Anita B", "Ada Lab", "Lovelace")


def _utc(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def audit(db, action, actor_id=None, target_id=None, metadata=None):
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_id=target_id,
            metadata_json=metadata,
        )
    )
    db.flush()


def _unique_user(db, data):
    if db.scalar(select(User).where(User.email == str(data.email).lower().strip())):
        raise ConflictError("An account with that email already exists")
    if db.scalar(select(User).where(User.user_name == data.user_name.strip())):
        raise ConflictError("That username is already registered")


def _verification(db, user: User):
    settings = get_settings()
    token = VerificationToken(user_id=user.user_id,expires_at=datetime.now(timezone.utc)+ timedelta(hours=settings.verification_token_expire_hours),)
    db.add(token)
    db.flush()
    verification_url = (f"{settings.app_base_url}"f"/api/v1/auth/verify-email?token={token.id}")
    email_body = build_verification_email(recipient_name=user.first_name,verification_url=verification_url,)
    send_email(user.email,"Verify your MealQ account",email_body,)
    return token

def _create_user(db, *, first_name, last_name, user_name, email, password, role):
    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        user_name=user_name.strip(),
        email=str(email).lower().strip(),
        password_hash=hash_password(password),
        role=role,
        is_active=False if get_settings().email_verification_required else True,
        email_verified=not get_settings().email_verification_required,
    )
    db.add(user)
    db.flush()
    if get_settings().email_verification_required:
        _verification(db, user)
    return user


def register_student(db: Session, data: StudentRegisterRequest) -> User:
    _unique_user(db, data)
    if data.class_name not in ALLOWED_CLASSES:
        raise BusinessRuleError("class must be one of: Anita B, Ada Lab, Lovelace")
    if db.scalar(select(Student).where(Student.student_number == data.student_number)):
        raise ConflictError("That student number is already registered")

    classroom = db.scalar(select(Classroom).where(Classroom.name == data.class_name))
    if not classroom:
        raise BusinessRuleError("Configured class does not exist")

    user = _create_user(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        user_name=data.user_name,
        email=data.email,
        password=data.password,
        role="STUDENT",
    )
    db.add(Student(user_id=user.user_id, student_number=data.student_number, class_id=classroom.id))
    audit(db, "USER_CREATED", target_id=user.user_id, metadata={"role": "STUDENT"})
    db.commit()
    db.refresh(user)
    return user


def create_first_super_admin(db: Session, data: AdminCreateRequest) -> User:
    if db.scalar(select(User).where(User.role == "SUPER_ADMIN")):
        raise ConflictError("The first Super Admin has already been created")
    _unique_user(db, data)
    user = _create_user(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        user_name=data.user_name,
        email=data.email,
        password=data.password,
        role="SUPER_ADMIN",
    )
    audit(db, "USER_CREATED", target_id=user.user_id, metadata={"role": "SUPER_ADMIN"})
    db.commit()
    db.refresh(user)
    return user


def register_admin(db: Session, data: AdminCreateRequest, actor: User) -> User:
    if actor.role != "SUPER_ADMIN":
        raise BusinessRuleError("Only the Super Admin can create Admin accounts")
    _unique_user(db, data)
    user = _create_user(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        user_name=data.user_name,
        email=data.email,
        password=data.password,
        role="ADMIN",
    )
    audit(db, "ADMIN_CREATED", actor_id=actor.user_id, target_id=user.user_id)
    db.commit()
    db.refresh(user)
    return user


def verify_email(db: Session, token_value: str) -> User:
    try:
        token_id = UUID(token_value)
    except ValueError as exc:
        raise NotFoundError("Invalid verification token") from exc

    token = db.get(VerificationToken, token_id)
    now = datetime.now(timezone.utc)
    if not token or token.used_at or _utc(token.expires_at) < now:
        raise BusinessRuleError("Verification token is invalid or expired")

    user = db.get(User, token.user_id)
    token.used_at = now
    user.email_verified = True
    user.is_active = True
    audit(db, "EMAIL_VERIFIED", target_id=user.user_id)
    db.commit()
    db.refresh(user)
    return user


def _new_refresh(db, user: User):
    raw = str(uuid4())
    token = RefreshToken(
        user_id=user.user_id,
        token_hash=hash_token(raw),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=get_settings().refresh_token_expire_days),
    )
    db.add(token)
    db.flush()
    return raw

def _generate_mfa_otp(db: Session, user: User):
    code = f"{randbelow(1_000_000):06d}"

    otp = MFAOTP(
        user_id=user.user_id,
        code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    db.add(otp)
    db.flush()

    send_email(
        user.email,
        "Your MealQ verification code",
        (
            f"Hello {user.first_name},\n\n"
            f"Your MealQ verification code is: {code}\n\n"
            f"This code expires in 5 minutes.\n\n"
            f"If you did not attempt to log in, please ignore this email."
        ),
    )

    return otp

def verify_mfa_otp(db: Session, user_id: UUID, code: str):
    otp = db.scalar(
        select(MFAOTP)
        .where(
            MFAOTP.user_id == user_id,
            MFAOTP.code == code,
            MFAOTP.used_at.is_(None),
        )
        .order_by(MFAOTP.expires_at.desc())
    )

    now = datetime.now(timezone.utc)

    if not otp or _utc(otp.expires_at) < now:
        raise AuthenticationError("Invalid or expired verification code")
    otp.used_at = now
    user = db.get(User, user_id)
    if not user:
        raise AuthenticationError("User not found")

    refresh = _new_refresh(db, user)
    audit(db, "MFA_VERIFIED", target_id=user.user_id)
    db.commit()
    return create_access_token(str(user.user_id), user.role), refresh

def create_mfa_challenge(user: User):
    return create_mfa_challenge_token(str(user.user_id))

def _invalidate_refresh(db, user_id):
    now = datetime.now(timezone.utc)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    ).update({"revoked_at": now}, synchronize_session=False)


def login(db: Session, identifier: str, password: str):
    user = db.scalar(
        select(User).where(
            or_(
                User.email == identifier.lower().strip(),
                User.user_name == identifier.strip(),
            )
        )
    )
    if not user:
        raise AuthenticationError("Incorrect username/email or password")

    if user.locked:
        raise AuthenticationError("Account is locked")
    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        audit(db, "LOGIN_FAILED", target_id=user.user_id)

        if user.failed_attempts >= 5:
            user.locked = True
            user.locked_at = datetime.now(timezone.utc)
            audit(db, "ACCOUNT_LOCKED", target_id=user.user_id)
        db.commit()
        raise AuthenticationError("Incorrect username/email or password")
    if not user.is_active or not user.email_verified:
        raise AuthenticationError("Account email must be verified before login")
    user.failed_attempts = 0
    _generate_mfa_otp(db, user)
    audit(db, "MFA_OTP_SENT", target_id=user.user_id)
    db.commit()
    return user

def refresh_access_token(db: Session, raw: str):
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
    now = datetime.now(timezone.utc)
    if not token or token.revoked_at or _utc(token.expires_at) < now:
        raise AuthenticationError("Invalid or expired refresh token")

    user = db.get(User, token.user_id)
    if not user or not user.is_active or user.locked:
        raise AuthenticationError("Account is inactive or locked")

    return create_access_token(str(user.user_id), user.role)


def logout(db: Session, raw: str, actor_id=None):
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
    if token:
        token.revoked_at = datetime.now(timezone.utc)
        audit(db, "LOGOUT", actor_id=actor_id or token.user_id)
        db.commit()


def request_password_reset(db: Session, identifier: str):
    user = db.scalar(
        select(User).where(
            or_(User.email == identifier.lower().strip(), User.user_name == identifier.strip())
        )
    )
    if not user:
        return

    token = PasswordResetToken(
        user_id=user.user_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=get_settings().password_reset_token_expire_minutes),
    )
    db.add(token)
    db.flush()
    audit(db, "PASSWORD_RESET_REQUESTED", target_id=user.user_id)
    db.commit()
    send_email(
        user.email,
        "MealQ password reset",
        f"Your password reset token is: {token.id}\nUse POST /api/v1/auth/reset-password with this token.",
    )


def reset_password(db: Session, token_value: str, new_password: str):
    try:
        token_id = UUID(token_value)
    except ValueError as exc:
        raise BusinessRuleError("Invalid password reset token") from exc

    token = db.get(PasswordResetToken, token_id)
    now = datetime.now(timezone.utc)
    if not token or token.used_at or _utc(token.expires_at) < now:
        raise BusinessRuleError("Password reset token is invalid or expired")

    user = db.get(User, token.user_id)
    user.password_hash = hash_password(new_password)
    user.failed_attempts = 0
    user.locked = False
    user.locked_at = None
    token.used_at = now
    _invalidate_refresh(db, user.user_id)
    audit(db, "PASSWORD_CHANGED", target_id=user.user_id)
    db.commit()


def change_password(db: Session, user: User, current: str, new: str):
    if not verify_password(current, user.password_hash):
        raise AuthenticationError("Current password is incorrect")

    user.password_hash = hash_password(new)
    _invalidate_refresh(db, user.user_id)
    audit(db, "PASSWORD_CHANGED", actor_id=user.user_id, target_id=user.user_id)
    db.commit()


def unlock_account(db: Session, actor: User, user_id: UUID):
    if actor.role not in ("ADMIN", "SUPER_ADMIN"):
        raise BusinessRuleError("Administrative access required")

    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    if actor.role == "ADMIN" and user.role != "STUDENT":
        raise BusinessRuleError("Admins can only unlock student accounts")

    user.locked = False
    user.locked_at = None
    user.failed_attempts = 0
    audit(db, "ACCOUNT_UNLOCKED", actor_id=actor.user_id, target_id=user.user_id)
    db.commit()
    db.refresh(user)
    return user

def start_mfa_setup(db: Session, user: User):
    if user.mfa_enabled:
        raise ConflictError("MFA is already enabled")

    secret = pyotp.random_base32()
    user.mfa_secret = secret
    db.commit()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.email,issuer_name="MealQ",)
    return {"secret": secret,"provisioning_uri": provisioning_uri,}

def confirm_mfa_setup(db: Session, user: User, code: str):
    if not user.mfa_secret:
        raise BusinessRuleError("MFA setup has not been started")
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(code):
        audit(db, "MFA_SETUP_FAILED", target_id=user.user_id)
        db.commit()
        raise AuthenticationError("Invalid MFA code")
    user.mfa_enabled = True
    audit(db, "MFA_ENABLED", target_id=user.user_id)
    db.commit()
    db.refresh(user)
    return user