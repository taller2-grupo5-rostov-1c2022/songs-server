from datetime import datetime
from .update import AlbumUpdate


class AlbumUpdateCover(AlbumUpdate):
    cover_last_update: datetime
