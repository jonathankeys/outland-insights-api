from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CreateActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    time_started: Optional[datetime] = None
    time_ended: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters')
        return v.strip()


class CreateActivityRequest(CreateActivityBase):
    class Config:
        from_attributes = True


class CreateActivityResponse(CreateActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
