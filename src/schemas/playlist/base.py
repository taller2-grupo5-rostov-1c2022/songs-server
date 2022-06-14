from typing import List
from ..resource.base import ResourceBase
from ..song.base import SongBase


class PlaylistBase(ResourceBase):
    songs: List[SongBase]
