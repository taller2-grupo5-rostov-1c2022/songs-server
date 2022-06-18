from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserUpdateSub(BaseModel):
    sub_level: int
    sub_expires: Optional[datetime]
