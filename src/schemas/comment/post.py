from pydantic import BaseModel
from typing import Optional


class CommentPost(BaseModel):
    text: str
    parent_id: Optional[int] = None
    album_id: int
    commenter_id: str

    class Config:
        orm_mode = True
