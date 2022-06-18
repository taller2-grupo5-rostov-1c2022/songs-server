from typing import List, Optional
from ..resource_creator.update import ResourceCreatorUpdate


class SongUpdate(ResourceCreatorUpdate):
    artists_names: Optional[List[str]]
    sub_level: Optional[int]

    class Config:
        orm_mode = True
