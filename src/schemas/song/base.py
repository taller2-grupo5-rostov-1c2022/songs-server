from typing import List
from ..resource_creator.base import ResourceCreatorBase
from ..artist import ArtistBase


class SongBase(ResourceCreatorBase):
    artists: List[ArtistBase]
    sub_level: int

    class Config:
        orm_mode = True
