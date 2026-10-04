from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_student
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services import device_service
from app.services import student_service

router = APIRouter(prefix="/devices", tags=["Student Devices"])


@router.post("/me", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(data: DeviceCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = student_service.get_by_user_id(db, current_user.user_id)
    item = device_service.register_for_student(db, student.student_id, data)
    db.commit()
    return item


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = student_service.get_by_user_id(db, current_user.user_id)
    device_service.delete_for_student(db, student.student_id)
    db.commit()


@router.get("/me", response_model=DeviceResponse)
def get_device(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = student_service.get_by_user_id(db, current_user.user_id)
    return device_service.get_for_student(db, student.student_id)


@router.patch("/me", response_model=DeviceResponse)
def update_device(data: DeviceUpdate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = student_service.get_by_user_id(db, current_user.user_id)
    item = device_service.update_for_student(db, student.student_id, data)
    db.commit()
    return item
