from typing import Optional

from .base import SongBase
from ..album.base import AlbumBase


class SongGet(SongBase):
    album: Optional[AlbumBase] = None
    file: str
