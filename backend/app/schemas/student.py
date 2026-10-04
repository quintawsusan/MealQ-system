from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class StudentCreate(BaseModel):
    user_id: UUID
    student_number: int = Field(gt=0)
    class_name: str = Field(validation_alias=AliasChoices("class", "class_name"), min_length=1)
    
class StudentUpdate(BaseModel):
    class_name: str | None = Field(default=None, validation_alias=AliasChoices("class", "class_name"), max_length=100)
    
class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    student_id: UUID
    user_id: UUID
    student_number: int
    class_id: UUID
    class_name: str | None = None
    created_at: datetime

class StudentImportRow(BaseModel):
    student_number: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    class_name: str = Field(
        validation_alias=AliasChoices("class", "class_name"),
        min_length=1,
        max_length=100,
    )