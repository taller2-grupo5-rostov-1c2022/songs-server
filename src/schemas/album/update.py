from typing import List, Optional

from ..resource_creator.update import ResourceCreatorUpdate


class AlbumUpdate(ResourceCreatorUpdate):
    songs_ids: Optional[List[int]]
