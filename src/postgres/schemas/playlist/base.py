from typing import List
from ..resource.base import ResourceBase
from ..song.base import SongBase
from ..user.base import UserBase


class PlaylistBase(ResourceBase):
    songs: List[SongBase]
    colabs: List[UserBase]

    class Config:
        orm_mode = True
