from typing import List
from ..album.base import AlbumBase
from ..song.base import SongBase


class Album(AlbumBase):
    songs: List[SongBase]
