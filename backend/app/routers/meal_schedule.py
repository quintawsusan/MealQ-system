from uuid import UUID
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.meal_schedule import MealScheduleCreate, MealScheduleResponse, MealScheduleUpdate
from app.services import meal_schedule_service

router = APIRouter(prefix="/meal-schedules", tags=["Meal Schedules"])


@router.get("", response_model=list[MealScheduleResponse])
def list_schedules(
    start_date: date | None = None,
    end_date: date | None = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    return meal_schedule_service.list_schedule(db, start_date, end_date, active_only)


@router.get("/upcoming", response_model=list[MealScheduleResponse])
def upcoming_schedules(
    days: int = Query(default=7, ge=1, le=31),
    db: Session = Depends(get_db),
):
    today = date.today()
    return meal_schedule_service.list_schedule(db, today, today + timedelta(days=days), True)


@router.post("", response_model=MealScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(data: MealScheduleCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = meal_schedule_service.create_schedule(db, data, current_user.user_id)
    db.commit()
    return item


@router.get("/{schedule_id}", response_model=MealScheduleResponse)
def get_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    return meal_schedule_service.get_schedule(db, schedule_id)


@router.patch("/{schedule_id}", response_model=MealScheduleResponse)
def update_schedule(schedule_id: UUID, data: MealScheduleUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = meal_schedule_service.update_schedule(db, schedule_id, data)
    db.commit()
    return item


@router.delete("/{schedule_id}", response_model=MealScheduleResponse)
def deactivate_schedule(schedule_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = meal_schedule_service.deactivate_schedule(db, schedule_id)
    db.commit()
    return item
