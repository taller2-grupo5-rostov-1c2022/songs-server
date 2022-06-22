from pydantic import BaseModel
from pydantic.networks import HttpUrl
from pydantic.utils import GetterDict
from typing import Optional, List, Any
from datetime import datetime
from .song import SongBase
from .album import AlbumBase
from .playlist import PlaylistBase


__all__ = ["UserBase", "UserCreate", "UserUpdateCollector", "UserUpdate", "User"]


class UserBase(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    uid: str
    name: str
    location: str
    interests: str


class UserGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "uid":
            return self._obj.attrib.get("id", default)
        else:
            try:
                return self._obj.find(key).attrib["Value"]
            except (AttributeError, KeyError):
                return default


class UserUpdateCollector(BaseModel):
    name: Optional[str]
    location: Optional[str]
    interests: Optional[str]


class UserUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    interests: Optional[str]


class User(UserBase):
    songs: List[SongBase]
    albums: List[AlbumBase]
    my_playlists: List[PlaylistBase]

    wallet: str
    sub_level: int
    sub_expires: Optional[datetime]
    location: str
    interests: str
    pfp: Optional[HttpUrl] = None
