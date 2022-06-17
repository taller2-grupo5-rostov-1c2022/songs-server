from pydantic import BaseModel
from typing import Optional


class UserUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    interests: Optional[str]
