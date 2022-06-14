from ..resource_creator.base import ResourceCreatorBase


class AlbumBase(ResourceCreatorBase):
    id: int
    name: str
    description: str
