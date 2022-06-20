from typing import Optional, List
from .resource import (
    ResourceBase,
    ResourceUpdate,
    ResourceUpdateCollector,
    ResourceCreate,
    ResourceCreateCollector,
)
from .song import SongBase
from sqlalchemy.orm import Session
from fastapi import Form


__all__ = [
    "PlaylistBase",
    "PlaylistGet",
    "PlaylistUpdate",
    "PlaylistCreate",
    "PlaylistCreateCollector",
]

from .utils import as_form, decode_json_list
from .. import roles
from ..database import models


class PlaylistBase(ResourceBase):
    pass


@as_form
class PlaylistCreateCollector(ResourceCreateCollector):
    songs_ids: str = Form(...)
    colabs_ids: str = Form(...)


class PlaylistCreate(ResourceCreate):
    songs: List[models.SongModel]
    colabs: List[models.UserModel]

    def __init__(
        self, pdb: Session, songs_ids: str, colabs_ids: str, role: roles.Role, **kwargs
    ):
        songs_ids = decode_json_list(songs_ids, True)
        colabs_ids = decode_json_list(colabs_ids, True)

        songs = []
        colabs = []

        for song_id in songs_ids:
            song = models.SongModel.get(pdb, _id=song_id, role=role)
            songs.append(song)
        self.songs = songs
        for colab_id in colabs_ids:
            colab = models.UserModel.get(pdb, colab_id)
            colabs.append(colab)
        self.colabs = colabs
        super().__init__(**kwargs)

    def dict(self, exclude_none=False):
        _dict = super().dict()
        if exclude_none:
            if self.songs is None:
                _dict["songs"] = self.songs
            if self.colabs is None:
                _dict["colabs"] = self.colabs
        else:
            _dict["songs"] = self.songs
            _dict["colabs"] = self.colabs
        return _dict


class PlaylistGet(PlaylistBase):
    from .user import UserBase

    colabs: List[UserBase]
    songs: List[SongBase]


class PlaylistUpdateCollector(ResourceUpdateCollector):
    songs_ids: Optional[List[int]]
    colabs_ids: Optional[List[str]]


class PlaylistUpdate(ResourceUpdate):
    songs: Optional[List[models.SongModel]]
    colabs: Optional[List[models.UserModel]]

    def __init__(
        self,
        pdb: Session,
        songs_ids: Optional[List[str]] = None,
        colabs_ids: Optional[List[str]] = None,
        **kwargs
    ):
        if songs_ids is not None:
            songs = []
            for song_id in songs_ids:
                song = models.SongModel.get(pdb, _id=song_id)
                songs.append(song)
            self.songs = songs
        if colabs_ids is not None:
            colabs = []
            for colab_id in colabs_ids:
                colab = models.UserModel.get(pdb, _id=colab_id)
                colabs.append(colab)
            self.colabs = colabs
        super().__init__(**kwargs)
