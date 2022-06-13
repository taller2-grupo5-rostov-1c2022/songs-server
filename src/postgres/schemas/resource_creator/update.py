from typing import Optional
from ..resource.update import ResourceUpdate


class ResourceCreatorUpdate(ResourceUpdate):
    genre: Optional[str]
    sub_level: Optional[int]

    class Config:
        orm_mode = True

