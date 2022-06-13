from typing import Optional, List
from ..resource_creator.base import ResourceCreatorBase
from ..artist import ArtistBase
from ..album.base import AlbumBase


class SongBase(ResourceCreatorBase):
    artists: List[ArtistBase]
    album: Optional[AlbumBase] = None
    sub_level: int

    class Config:
        orm_mode = True
