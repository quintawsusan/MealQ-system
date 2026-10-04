from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service
router=APIRouter(prefix="/users", tags=["Users"])
@router.get("", response_model=list[UserResponse])
def list_users(offset:int=Query(0,ge=0),limit:int=Query(100,ge=1,le=500),current_user:User=Depends(require_admin),db:Session=Depends(get_db)):
    users=user_service.list_user(db,offset,limit)
    if current_user.role=="ADMIN": users=[u for u in users if u.role=="STUDENT"]
    return users
@router.get("/{user_id}",response_model=UserResponse)
def get_user(user_id:UUID,current_user:User=Depends(require_admin),db:Session=Depends(get_db)):
    user=user_service.get_user(db,user_id)
    if current_user.role=="ADMIN" and user.role!="STUDENT": from fastapi import HTTPException; raise HTTPException(403,"Admins can only manage students")
    return user
@router.patch("/{user_id}",response_model=UserResponse)
def update_user(user_id:UUID,data:UserUpdate,current_user:User=Depends(require_admin),db:Session=Depends(get_db)):
    return user_service.update_user(db,user_id,data,current_user.user_id)
@router.delete("/{user_id}",status_code=204)
def delete_user(user_id:UUID,current_user:User=Depends(require_admin),db:Session=Depends(get_db)):
    user_service.delete_user(db,user_id,current_user.user_id)

from app.models.security import AuditLog
@router.get("/audit-logs", include_in_schema=True)
def list_audit_logs(current_user: User=Depends(require_admin), db: Session=Depends(get_db), limit:int=Query(100,ge=1,le=500)):
    if current_user.role=="ADMIN":
        from fastapi import HTTPException
        raise HTTPException(403,"Only Super Admin can view audit logs")
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
