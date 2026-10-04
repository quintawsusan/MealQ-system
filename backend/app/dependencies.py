from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status_code=401, detail="Authentication required")
    payload=decode_access_token(credentials.credentials)
    try: user_id=UUID(str(payload.get("sub")))
    except (ValueError, TypeError): raise HTTPException(status_code=401, detail="Invalid access token")
    user=db.get(User,user_id)
    if not user or not user.is_active or user.locked or not user.email_verified:
        raise HTTPException(status_code=401, detail="User account is inactive, locked, or unverified")
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("ADMIN","SUPER_ADMIN"): raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "SUPER_ADMIN": raise HTTPException(status_code=403, detail="Super Admin access required")
    return current_user

def require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "STUDENT": raise HTTPException(status_code=403, detail="Student access required")
    return current_user
