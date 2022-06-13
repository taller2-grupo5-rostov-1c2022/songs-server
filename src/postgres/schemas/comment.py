from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .album.base import AlbumBase
from .user.base import UserBase


class CommentGet(BaseModel):
    id: int
    text: Optional[str]
    created_at: datetime
    commenter: UserBase
    responses: List["CommentGet"]
    album: AlbumBase

    class Config:
        orm_mode = True


class CommentInfo(BaseModel):
    text: str
    parent_id: Optional[int] = None

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentPost(BaseModel):
    text: str
    parent_id: Optional[int] = None
    album_id: int
    commenter_id: str

    class Config:
        orm_mode = True

