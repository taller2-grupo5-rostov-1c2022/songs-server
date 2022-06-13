from pydantic import BaseModel
from typing import Optional


class ResourceBase(BaseModel):
    id: Optional[int]
    name: str
    description: str
    blocked: bool
    creator_id: Optional[str]

    class Config:
        orm_mode = True

