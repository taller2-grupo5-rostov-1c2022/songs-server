from typing import Optional
from pydantic import BaseModel


class ReviewBase(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True
