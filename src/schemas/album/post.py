from typing import List
from ..resource_creator.base import ResourceCreatorBase


class AlbumPost(ResourceCreatorBase):
    songs_ids: List[int]
