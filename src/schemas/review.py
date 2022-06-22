from pydantic import BaseModel
from typing import Optional
from .user import UserBase
from .album import AlbumBase


__all__ = [
    "ReviewBase",
    "ReviewGet",
    "ReviewMyReviews",
    "ReviewUpdateCollector",
    "ReviewUpdate",
]


class ReviewBase(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True


class ReviewGet(ReviewBase):
    reviewer: UserBase


class ReviewMyReviews(ReviewBase):
    album: AlbumBase


# This is identical to ReviewBase, but
# they are conceptually different
class ReviewUpdateCollector(BaseModel):
    text: Optional[str] = None
    score: Optional[float] = None

    class Config:
        orm_mode = True


class ReviewUpdate(BaseModel):
    text: Optional[str]
    score: Optional[float]

    class Config:
        orm_mode = True
