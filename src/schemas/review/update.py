from typing import Optional
from pydantic import BaseModel


# This is identical to ReviewBase, but
# they are conceptually different
class ReviewUpdate(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True
