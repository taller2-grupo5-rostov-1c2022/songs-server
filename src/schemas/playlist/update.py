from typing import List, Optional
from ..resource.update import ResourceUpdate


class PlaylistUpdate(ResourceUpdate):
    songs_ids: Optional[List[int]]
    colabs_ids: Optional[List[str]]
