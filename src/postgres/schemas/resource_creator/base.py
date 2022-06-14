from ..resource.base import ResourceBase


class ResourceCreatorBase(ResourceBase):
    genre: str

    class Config:
        orm_mode = True
