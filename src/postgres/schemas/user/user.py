from typing import List, Optional
from datetime import datetime
from .base import UserBase
from ..playlist.base import PlaylistBase
from ..song.base import SongBase
from ..album.base import AlbumBase


class User(UserBase):
    songs: List[SongBase]
    albums: List[AlbumBase]
    my_playlists: List[PlaylistBase]

    wallet: str
    sub_level: int
    sub_expires: Optional[datetime]
    location: str
    interests: str
    pfp: Optional[str] = None
