from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    device_identifier: str = Field(min_length=1, max_length=255)


class DeviceUpdate(BaseModel):
    is_active: bool | None = None
    device_identifier: str | None = Field(default=None, min_length=1, max_length=255)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    device_id: UUID
    student_id: UUID
    device_identifier: str
    is_active: bool
