from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True
