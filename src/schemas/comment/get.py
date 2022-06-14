from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from ..user.base import UserBase
from ..album.base import AlbumBase


class CommentGet(BaseModel):
    id: int
    text: Optional[str]
    created_at: datetime
    commenter: UserBase
    responses: List["CommentGet"]
    album: AlbumBase

    class Config:
        orm_mode = True
