from typing import List
from .base import PlaylistBase
from ..user.base import UserBase


class Playlist(PlaylistBase):
    colabs: List[UserBase]
