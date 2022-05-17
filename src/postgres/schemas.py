from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Classes used to provide type checking


class ArtistBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class AlbumInfoBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class SongBase(BaseModel):
    id: int
    name: str
    description: str
    artists: List[ArtistBase]
    genre: str
    sub_level: int
    album: Optional[AlbumInfoBase] = None

    class Config:
        orm_mode = True


class SongGet(SongBase):
    file: str


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str]


class AlbumBase(BaseModel):
    id: int
    name: str
    description: str
    album_creator_id: str
    genre: str
    sub_level: int

    songs: List[SongBase]

    class Config:
        orm_mode = True


class AlbumGet(AlbumBase):
    cover: str

    class Config:
        orm_mode = True


class AlbumCreate(BaseModel):
    name: str
    description: str
    creator: str
    artists: List[str]
    genre: str
    songs_ids: List[str]


class AlbumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    artists: Optional[List[str]] = None
    genre: Optional[str] = None
    songs_ids: Optional[List[str]] = None


class UserColab(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class PlaylistBase(BaseModel):
    id: int
    name: str
    description: str
    songs: List[SongBase]
    colabs: List[UserColab]
    creator_id: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: str
    name: str
    wallet: Optional[str] = None
    location: str
    interests: str
    pfp: Optional[str] = None

    songs: List[SongBase]
    albums: List[AlbumBase]
    my_playlists: List[PlaylistBase]

    class Config:
        orm_mode = True
