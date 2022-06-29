from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from .album import AlbumBase
from .user import UserBase


class CommentGet(BaseModel):
    id: int
    text: Optional[str]
    created_at: datetime
    commenter: Optional[UserBase]
    responses: List["CommentGet"]
    album: AlbumBase

    class Config:
        orm_mode = True


class CommentPost(BaseModel):
    text: str
    parent_id: Optional[int] = None
    album_id: int
    commenter_id: str

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    text: str

    class Config:
        orm_mode = True
