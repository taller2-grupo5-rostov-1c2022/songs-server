from pydantic import BaseModel
from typing import Optional
from .album.base import AlbumBase
from .user.base import UserBase


class ReviewBase(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True


class ReviewMyReviews(ReviewBase):
    album: AlbumBase

    class Config:
        orm_mode = True


class ReviewGet(ReviewBase):
    reviewer: UserBase

    class Config:
        orm_mode = True


# This is identical to ReviewBase, but
# they are conceptually different
class ReviewUpdate(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True

