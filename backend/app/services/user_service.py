from uuid import UUID
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.user import User
from app.services.auth_service import audit

def list_user(db, offset=0, limit=100): return db.query(User).offset(offset).limit(limit).all()
def get_user(db,user_id: UUID):
    item=db.get(User,user_id)
    if not item: raise NotFoundError("User not found")
    return item
def update_user(db,user_id:UUID,data,acting_user_id:UUID):
    user=get_user(db,user_id); actor=get_user(db,acting_user_id)
    values=data.model_dump(exclude_unset=True)
    if "role" in values:
        new_role=values["role"].value
        if actor.role != "SUPER_ADMIN": raise BusinessRuleError("Only Super Admin can change roles")
        if user.user_id == actor.user_id: raise BusinessRuleError("You cannot change your own role")
        if new_role == "SUPER_ADMIN":
            raise BusinessRuleError("Super Admin role cannot be assigned")
        if user.role == "SUPER_ADMIN": raise BusinessRuleError("The Super Admin role cannot be changed")
        values["role"]=new_role
    if actor.role=="ADMIN" and user.role!="STUDENT": raise BusinessRuleError("Admins can only manage student accounts")
    for k,v in values.items(): setattr(user,k,v)
    if "role" in values: audit(db,"ROLE_CHANGED",actor_id=actor.user_id,target_id=user.user_id,metadata={"role":values["role"]})
    db.commit(); db.refresh(user); return user
def delete_user(db,user_id,acting_user_id):
    user=get_user(db,user_id); actor=get_user(db,acting_user_id)
    if user.user_id==actor.user_id: raise BusinessRuleError("You cannot delete your own account")
    if user.role=="SUPER_ADMIN": raise BusinessRuleError("The Super Admin cannot be deleted")
    if actor.role=="ADMIN" and user.role!="STUDENT": raise BusinessRuleError("Admins can only manage student accounts")
    db.delete(user); db.commit()
