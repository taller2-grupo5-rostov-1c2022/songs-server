from typing import List
from ..resource.base import ResourceBase


class PlaylistPost(ResourceBase):
    songs_ids: List[int]
    colabs_ids: List[str]

    class Config:
        orm_mode = True

