from typing import Optional

from pydantic import BaseModel, field_validator


class RouteBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry: Optional[dict]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v.strip()


class GetRoutesResponse(RouteBase):
    id: int

    class Config:
        from_attributes = True
