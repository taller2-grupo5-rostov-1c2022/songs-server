from pydantic import BaseModel
from typing import Optional


class ResourceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    blocked: Optional[bool]

    class Config:
        orm_mode = True
