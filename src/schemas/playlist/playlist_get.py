from .base import PlaylistBase
from typing import List
from ..song.base import SongBase
from ..user.base import UserBase


class PlaylistGet(PlaylistBase):
    colabs: List[UserBase]
    songs: List[SongBase]
