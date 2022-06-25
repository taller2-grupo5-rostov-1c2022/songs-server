from typing import List

from fastapi import HTTPException

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship, Session, contains_eager, joinedload
from . import templates, tables
from .artist import ArtistModel
from sqlalchemy.orm.query import Query


class SongModel(templates.ResourceWithFile):
    __tablename__ = "songs"

    sub_level = Column(Integer, nullable=False)

    artists = relationship(
        "ArtistModel",
        secondary=tables.song_artist_association_table,
        back_populates="songs",
        lazy="joined",
    )

    album = relationship("AlbumModel", back_populates="songs", lazy="joined")
    album_id = Column(
        Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("UserModel", back_populates="songs")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=tables.song_favorites_association_table,
        back_populates="favorite_songs",
    )

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        if query is None:
            query = pdb.query(cls)
        sub_level = kwargs.pop("sub_level", None)
        artist = kwargs.pop("artist", None)

        if sub_level is not None:
            query = query.filter(cls.sub_level == sub_level)
        if artist is not None:
            query = query.join(cls.artists).filter(
                ArtistModel.name.ilike(f"%{artist}%")
            )

        return super().search(pdb, query=query, **kwargs)

    def _update_artists(self, pdb: Session, artists_names: List[str]):
        artists = []
        for artist_name in artists_names:
            try:
                artist = ArtistModel.get(pdb, _id=artist_name)
            except (HTTPException, IndexError):
                artist = ArtistModel.create(pdb, name=artist_name, commit=False)
            artists.append(artist)
        self.artists = artists

    def update(self, pdb: Session, **kwargs):
        artists_names = kwargs.pop("artists_names", None)
        sub_level = kwargs.pop("sub_level", None)
        if artists_names is not None:
            self._update_artists(pdb, artists_names)
        if sub_level is not None:
            self.sub_level = sub_level

        return super().update(pdb, **kwargs)
