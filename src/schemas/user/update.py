from pydantic import BaseModel
from typing import Optional


class UserUpdate(BaseModel):
    location: Optional[str]
    interests: Optional[str]
    pfp: Optional[str]
