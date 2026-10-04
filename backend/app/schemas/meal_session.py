from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import MealSessionStatus


class MealSessionCreate(BaseModel):
    schedule_id: UUID
    batch_size: int = Field(default=5, gt=0)
    release_interval_seconds: int = Field(default=180, gt=0)
    response_window: int = Field(default=60, gt=0)

class MealSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    schedule_id: UUID
    status: MealSessionStatus
    batch_size: int
    release_interval_seconds: int
    response_window: int
    started_at: datetime | None
    ended_at: datetime | None
    created_by: UUID


class BatchMemberSummary(BaseModel):
    student_id: UUID
    student_number: int
    student_position: int
    response: str


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    batch_id: UUID
    session_id: UUID
    batch_number: int
    status: str
    called_at: datetime | None
    completed_at: datetime | None
    members: list[BatchMemberSummary] = []


class MyBatchResponse(BaseModel):
    session_id: UUID
    batch_id: UUID
    batch_number: int
    batch_status: str
    student_id: UUID
    student_number: int
    student_position: int
    response: str
    responded_at: datetime | None
    is_currently_called: bool
    response_window_open: bool


class SessionMonitorResponse(BaseModel):
    session: MealSessionResponse
    current_batch: BatchResponse | None
    total_students: int
    going: int
    skipped: int
    no_response: int
    waiting_batches: int
    called_batches: int
    completed_batches: int
