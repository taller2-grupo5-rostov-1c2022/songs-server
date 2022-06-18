from datetime import datetime

from .update import SongUpdate


class SongUpdateFile(SongUpdate):
    file_last_update: datetime
