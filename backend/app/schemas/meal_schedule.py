from uuid import UUID
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class MealScheduleCreate(BaseModel):
    meal_type_id: UUID
    meal_date: date
    start_time: time
    end_time: time
    menu_description: str | None = None
    is_active: bool = True


class MealScheduleUpdate(BaseModel):
    meal_type_id: UUID | None = None
    meal_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    menu_description: str | None = None
    is_active: bool | None = None


class MealScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule_id: UUID
    meal_type_id: UUID
    meal_date: date
    start_time: time
    end_time: time
    menu_description: str | None
    is_active: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
