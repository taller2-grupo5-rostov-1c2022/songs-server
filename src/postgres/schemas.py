from typing import List, Optional
from fastapi import UploadFile, Form, UploadFile
from pydantic import BaseModel

# Classes used to provide type checking


class ArtistBase(BaseModel):
    artist_name: str

    class Config:
        orm_mode = True


class AlbumInfoBase(BaseModel):
    album_id: int
    album_name: str

    class Config:
        orm_mode = True


class SongBase(BaseModel):
    id: int
    name: str
    description: str
    artists: List[ArtistBase]
    genre: str
    album_info: Optional[AlbumInfoBase]

    class Config:
        orm_mode = True


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str]


class AlbumBase(BaseModel):
    id: int
    name: str
    description: str
    creator_id: str
    artists: List[ArtistBase]
    genre: str

    songs: List[SongBase]

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


class UserBase(BaseModel):
    id: str
    name: str
    songs: List[SongBase]
    albums: List[AlbumBase]

    class Config:
        orm_mode = True
