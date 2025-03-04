from typing import Optional, List

from pydantic import BaseModel, field_validator
from werkzeug.datastructures import FileStorage


class RouteBase(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v.strip()


class UploadRouteRequest(RouteBase):
    files: List[FileStorage] = []

    @field_validator('files')
    @classmethod
    def validate_files(cls, v: List[FileStorage]) -> List[FileStorage]:
        if not v:
            raise ValueError('No files uploaded')

        for file in v:
            if not isinstance(file, FileStorage):
                raise ValueError('Invalid file type')
            if not file.filename:
                raise ValueError('Invalid file name')
        return v

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UploadRouteResponse(RouteBase):
    id: int
    geometry: Optional[dict]

    class Config:
        from_attributes = True


class CreateRouteRequest(RouteBase):
    dataset: str

    class Config:
        from_attributes = True


class CreateRouteResponse(RouteBase):
    id: int
    geometry: Optional[dict]

    class Config:
        from_attributes = True


class GetRouteResponse(RouteBase):
    id: int
    geometry: Optional[dict]

    class Config:
        from_attributes = True
