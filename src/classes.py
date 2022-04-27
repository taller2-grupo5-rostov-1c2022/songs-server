from pydantic import BaseModel
from typing import Optional

######################################## API V1 ########################################
class SongInfo(BaseModel):
    name: str
    artist_name: str


class Song(BaseModel):
    info: SongInfo
    file: bytes


class SongInfoUpdate(BaseModel):
    name: Optional[str] = None
    artist_name: Optional[str] = None


class SongUpdate(BaseModel):
    info: Optional[SongInfoUpdate]
    file: Optional[bytes] = None


######################################## API V2 ########################################


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str]
