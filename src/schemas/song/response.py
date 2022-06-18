from typing import Optional
from pydantic import BaseModel


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str]
