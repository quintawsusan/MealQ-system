from datetime import datetime, timedelta, timezone
import base64, hashlib, hmac, os
import jwt
from fastapi import HTTPException, status
from app.core.config import get_settings

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = encoded.split("$", 2)
        if scheme != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def hash_token(token: str) -> str:
    return hmac.new(get_settings().secret_key.encode(), token.encode(), hashlib.sha256).hexdigest()

def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"}) from exc

def create_mfa_challenge_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=5)
    payload = {"sub": subject,"purpose": "mfa_challenge","iat": int(now.timestamp()),"exp": expire,}
    return jwt.encode(payload,settings.secret_key,algorithm=settings.algorithm,)


def decode_mfa_challenge_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        if payload.get("purpose") != "mfa_challenge":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA challenge",
            )
        return payload

    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA challenge",
        ) from exc