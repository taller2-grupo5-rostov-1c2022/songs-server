from src.exceptions import MessageException
from typing import Optional, List

from pydantic.fields import Field

from .resource import (
    ResourceBase,
    ResourceUpdate,
    ResourceCreateCollector,
    ResourceUpdateCollector,
    ResourceCreate,
)
from sqlalchemy.orm import Session
from fastapi import Form, status


__all__ = [
    "AlbumBase",
    "Album",
    "AlbumGet",
    "AlbumCreateCollector",
    "AlbumCreate",
    "AlbumUpdate",
    "AlbumUpdateCollector",
]

from .utils import as_form, decode_json_list
from .. import roles
from ..database import models


class AlbumBase(ResourceBase):
    genre: str


class Album(AlbumBase):
    file_url: str = Field(alias="cover")
    score: float
    scores_amount: int

    class Config:
        allow_population_by_field_name = True


class AlbumGet(Album):
    from .song import SongBase

    songs: List[SongBase]


@as_form
class AlbumCreateCollector(ResourceCreateCollector):
    # json encoded
    songs_ids: str = Form(...)
    genre: str = Form(...)


class AlbumCreate(ResourceCreate):
    songs: List[models.SongModel]
    genre: str

    def __init__(
        self,
        pdb: Session,
        songs_ids: str,
        genre: str,
        role: roles.Role,
        creator_id: str,
        **kwargs
    ):
        if not role.can_post_content():
            raise MessageException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to post content",
            )
        super().__init__(creator_id=creator_id, **kwargs)
        songs_ids = decode_json_list(songs_ids, True)
        songs = []
        for song_id in songs_ids:
            song = models.SongModel.get(pdb, song_id, role=role)
            if song.creator_id != creator_id:
                raise MessageException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't add songs from other users",
                )
            songs.append(song)
        self.songs = songs
        self.genre = genre

    def dict(self):
        _dict = super().dict()
        _dict["songs"] = [song for song in self.songs]
        _dict["genre"] = self.genre
        return _dict


@as_form
class AlbumUpdateCollector(ResourceUpdateCollector):
    songs_ids: Optional[str] = None
    genre: Optional[str] = None


class AlbumUpdate(ResourceUpdate):
    songs: Optional[List[models.SongModel]]
    genre: Optional[str]

    def __init__(
        self,
        pdb: Session,
        songs_ids: Optional[str],
        genre: str,
        creator_id: str,
        role: roles.Role,
        album: models.AlbumModel,
        **kwargs
    ):
        super().__init__(creator_id=creator_id, **kwargs)
        if songs_ids is not None:
            songs_ids = decode_json_list(songs_ids, True)
            songs = []
            for song_id in songs_ids:
                song = models.SongModel.get(pdb, _id=song_id, role=role)
                if song.creator_id != creator_id:
                    raise MessageException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can't add songs from other users",
                    )
                if song.album_id is not None and song.album_id != album.id:
                    raise MessageException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can't add songs that belong to another album",
                    )
                songs.append(song)
            self.songs = songs
        else:
            self.songs = None
        self.genre = genre

    def dict(self, exclude_none=False):
        _dict = super().dict(exclude_none=exclude_none)
        if exclude_none:
            if self.songs is not None:
                _dict["songs"] = self.songs
            if self.genre is not None:
                _dict["genre"] = self.genre
        else:
            _dict["songs"] = self.songs
            _dict["genre"] = self.genre
        return _dict
