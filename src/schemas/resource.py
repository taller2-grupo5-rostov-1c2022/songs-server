from typing import Optional
from pydantic import BaseModel
from fastapi import Form


__all__ = [
    "ResourceBase",
    "ResourceUpdate",
    "ResourceCreateCollector",
    "ResourceCreate",
    "ResourceUpdateCollector",
]

from src.schemas.utils import as_form


class ResourceBase(BaseModel):
    id: Optional[int]
    name: str
    description: str
    blocked: bool
    creator_id: Optional[str]

    class Config:
        orm_mode = True


class ResourceCreateCollector(BaseModel):
    name: str = Form(...)
    description: str = Form(...)

    class Config:
        orm_mode = True


class ResourceCreate:
    name: str
    description: str
    blocked: bool
    creator_id: str

    class Config:
        orm_mode = True

    def __init__(self, name: str, description: str, creator_id: str):
        self.name = name
        self.description = description
        self.blocked = False
        self.creator_id = creator_id
        super().__init__()

    def dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "blocked": self.blocked,
            "creator_id": self.creator_id,
        }


@as_form
class ResourceUpdateCollector(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    blocked: Optional[bool] = None

    class Config:
        orm_mode = True


class ResourceUpdate:
    name: Optional[str]
    description: Optional[str]
    blocked: Optional[bool]

    class Config:
        orm_mode = True

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", None)
        self.description = kwargs.pop("description", None)
        self.blocked = kwargs.pop("blocked", None)
        super().__init__()

    def dict(self, exclude_none=False):
        _dict = {}
        if exclude_none:
            if self.name is not None:
                _dict["name"] = self.name
            if self.description is not None:
                _dict["description"] = self.description
            if self.blocked is not None:
                _dict["blocked"] = self.blocked
        else:
            _dict["name"] = self.name
            _dict["description"] = self.description
            _dict["blocked"] = self.blocked

        return _dict
