from typing import List
from .album import Album
from ..song.base import SongBase


class AlbumGet(Album):
    songs: List[SongBase]
