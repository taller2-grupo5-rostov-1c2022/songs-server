from typing import List, Optional
from ..resource_creator.base import ResourceCreatorBase
from ..album.base import AlbumBase


class SongPost(ResourceCreatorBase):
    artists_names: List[str]
    album: Optional[AlbumBase] = None
    sub_level: int

    class Config:
        orm_mode = True
