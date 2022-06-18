from typing import List, Optional
from ..resource_creator.base import ResourceCreatorBase


class SongPost(ResourceCreatorBase):
    artists_names: List[str]
    album_id: Optional[str] = None
    sub_level: int

    class Config:
        orm_mode = True
