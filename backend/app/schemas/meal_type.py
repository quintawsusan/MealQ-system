from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class MealTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=255)


class MealTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=255)


class MealTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meal_id: UUID
    name: str
    description: str | None
