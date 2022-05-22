from pydantic.main import BaseModel
from typing import Optional, List


class ResourceBase(BaseModel):
    id: Optional[int]
    name: str
    description: str
    blocked: bool
    creator_id: str

    class Config:
        orm_mode = True


class ResourceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    blocked: Optional[bool]

    class Config:
        orm_mode = True


class ResourceCreator(ResourceBase):
    genre: str
    sub_level: int

    class Config:
        orm_mode = True


class ResourceCreatorUpdate(ResourceUpdate):
    genre: Optional[str]
    sub_level: Optional[int]

    class Config:
        orm_mode = True


class AlbumInfoBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class ArtistBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class SongBase(ResourceCreator):
    artists: List[ArtistBase]
    album: Optional[AlbumInfoBase] = None

    class Config:
        orm_mode = True


class SongPost(ResourceCreator):
    artists_names: List[str]
    album: Optional[AlbumInfoBase] = None

    class Config:
        orm_mode = True


class SongUpdate(ResourceCreatorUpdate):
    artists_names: Optional[List[str]]

    class Config:
        orm_mode = True


class SongGet(SongBase):
    file: str


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str]


class AlbumBase(ResourceCreator):
    songs: List[SongBase]

    class Config:
        orm_mode = True


class AlbumPost(ResourceCreator):
    songs_ids: List[int]


class AlbumUpdate(ResourceCreatorUpdate):
    songs_ids: Optional[List[int]]


class AlbumGet(AlbumBase):
    cover: str

    class Config:
        orm_mode = True


class PlaylistBase(ResourceBase):
    songs: List[SongBase]
    colabs: List[UserInfo]

    class Config:
        orm_mode = True


class PlaylistPost(ResourceBase):
    songs_ids: List[int]
    colabs_ids: List[str]

    class Config:
        orm_mode = True


class PlaylistUpdate(ResourceUpdate):
    songs_ids: Optional[List[int]]
    colabs_ids: Optional[List[str]]

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
