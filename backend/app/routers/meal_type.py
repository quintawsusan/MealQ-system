from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.meal_type import MealTypeCreate, MealTypeResponse, MealTypeUpdate
from app.services import meal_type_service

router = APIRouter(prefix="/meal-types", tags=["Meal Types"])


@router.get("", response_model=list[MealTypeResponse])
def list_meal_types(db: Session = Depends(get_db)):
    return meal_type_service.list_meal_type(db)


@router.post("", response_model=MealTypeResponse, status_code=status.HTTP_201_CREATED)
def create_meal_type(data: MealTypeCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = meal_type_service.create_meal_type(db, data)
    db.commit()
    return item


@router.get("/{meal_id}", response_model=MealTypeResponse)
def get_meal_type(meal_id: UUID, db: Session = Depends(get_db)):
    return meal_type_service.get_meal_type(db, meal_id)


@router.patch("/{meal_id}", response_model=MealTypeResponse)
def update_meal_type(meal_id: UUID, data: MealTypeUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = meal_type_service.update_meal_type(db, meal_id, data)
    db.commit()
    return item


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_type(meal_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    meal_type_service.delete_meal_type(db, meal_id)
    db.commit()
