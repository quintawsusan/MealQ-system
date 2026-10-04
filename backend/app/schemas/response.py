from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class StudentResponseChoice(str, Enum):
    GOING = "GOING"
    SKIPPED = "SKIPPED"


class StudentMealResponseCreate(BaseModel):
    response: StudentResponseChoice


class StudentMealResponseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    response_id: UUID
    session_id: UUID
    student_id: UUID
    batch_id: UUID
    response: str
    responded_at: datetime | None
