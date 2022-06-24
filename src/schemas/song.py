from pydantic import BaseModel
from typing import Optional, List

from pydantic.fields import Field

from .resource import (
    ResourceBase,
    ResourceUpdate,
    ResourceUpdateCollector,
    ResourceCreateCollector,
    ResourceCreate,
)
from src.database import models
from sqlalchemy.orm import Session
from fastapi import Form, HTTPException, status


__all__ = [
    "SongBase",
    "SongGet",
    "SongCreate",
    "SongCreateCollector",
    "SongUpdate",
    "SongUpdateCollector",
    "SongResponse",
]

from .utils import as_form, decode_json_list
from .. import roles


class ArtistBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class SongBase(ResourceBase):
    artists: List[ArtistBase]
    sub_level: int
    genre: str


class SongGet(SongBase):
    from .album import AlbumBase

    album: Optional[AlbumBase] = None
    file_url: str = Field(..., alias="file")

    class Config:
        allow_population_by_field_name = True


@as_form
class SongCreateCollector(ResourceCreateCollector):
    # json encoded
    artists: str = Form(...)
    album_id: Optional[str] = Form(None)
    sub_level: Optional[int] = Form(0)
    genre: str = Form(...)


class SongCreate(ResourceCreate):
    artists: List[models.ArtistModel]
    album: Optional[models.AlbumModel] = None
    sub_level: int
    genre: str

    def __init__(
        self,
        pdb: Session,
        artists: str,
        album_id: Optional[str],
        sub_level: int,
        genre: str,
        role: roles.Role,
        **kwargs
    ):
        if not role.can_post_content():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to post content",
            )
        artists_names = decode_json_list(artists, False)

        artists = []
        for artist_name in artists_names:
            artist = models.ArtistModel.get_or_create(pdb, artist_name)
            artists.append(artist)
        self.artists = artists
        if album_id is not None:
            album = models.AlbumModel.get(pdb, _id=album_id, role=role)
            self.album = album
        self.sub_level = sub_level
        self.genre = genre
        super().__init__(**kwargs)

    def dict(self):
        _dict = super().dict()
        _dict["artists"] = self.artists
        _dict["album"] = self.album
        _dict["sub_level"] = self.sub_level
        _dict["genre"] = self.genre
        return _dict


class SongResponse(BaseModel):
    success: bool
    id: str
    file: Optional[str] = Field(..., alias="file_url")


@as_form
class SongUpdateCollector(ResourceUpdateCollector):
    artists: Optional[str]
    sub_level: Optional[int]
    genre: Optional[str]


class SongUpdate(ResourceUpdate):
    artists: Optional[List[models.ArtistModel]]
    sub_level: Optional[int]
    genre: Optional[str]

    def __init__(
        self,
        pdb: Session,
        artists: Optional[str],
        sub_level: Optional[int],
        genre: Optional[str],
        **kwargs
    ):
        super().__init__(**kwargs)
        if artists is not None:
            artists_names = decode_json_list(artists, False)
            artists = []
            for artist_name in artists_names:
                artist = models.ArtistModel.get_or_create(pdb, name=artist_name)
                artists.append(artist)
            self.artists = artists
        else:
            self.artists = None
        self.sub_level = sub_level
        self.genre = genre

    def dict(self, exclude_none=False):
        _dict = super().dict(exclude_none=exclude_none)
        if exclude_none:
            if self.artists is not None:
                _dict["artists"] = self.artists
            if self.sub_level is not None:
                _dict["sub_level"] = self.sub_level
            if self.genre is not None:
                _dict["genre"] = self.genre
        else:
            _dict["artists"] = self.artists
            _dict["sub_level"] = self.sub_level
            _dict["genre"] = self.genre

        return _dict
