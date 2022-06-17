from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, Session, contains_eager
from sqlalchemy.sql import and_

from . import templates, tables
from .artist import ArtistModel
from .song import SongModel
from sqlalchemy.orm.query import Query
from fastapi import HTTPException, status


class AlbumModel(templates.ResourceWithFile):
    __tablename__ = "albums"

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    songs = relationship("SongModel", back_populates="album")

    reviews = relationship("ReviewModel", back_populates="album")
    comments = relationship("CommentModel", back_populates="album")

    favorited_by = relationship(
        "UserModel",
        secondary=tables.album_favorites_association_table,
        back_populates="favorite_albums",
    )

    @classmethod
    def create(cls, pdb: Session, *args, **kwargs):
        creator_id = kwargs.pop("creator_id")
        songs_ids = kwargs.pop("songs_ids")
        role = kwargs.pop("role")

        songs = []
        for song_id in songs_ids:
            song = SongModel.get(pdb, song_id, role=role)
            songs.append(song)
        album = super().create(
            pdb,
            creator_id=creator_id,
            songs=songs,
            **kwargs,
        )
        return album

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        if query is None:
            query = pdb.query(cls)

        artist = kwargs.pop("artist", None)
        role = kwargs.get("role", None)

        filters = []
        join_conditions = []
        if artist is not None:
            filters.append(SongModel.artists.any(ArtistModel.name.ilike(f"%{artist}%")))

        if not role.can_see_blocked():
            join_conditions.append(SongModel.blocked == False)

        query = (
            query.options(contains_eager("songs"))
            .join(cls.songs.and_(*join_conditions), full=True)
            .filter(*filters)
        )

        return super().search(pdb, query=query, **kwargs)

    @classmethod
    def get(cls, pdb: Session, **kwargs):
        album_id = kwargs.pop("_id")
        role = kwargs.pop("role")

        join_conditions = [SongModel.album_id == AlbumModel.id]
        filters = [album_id == cls.id]
        if not role.can_see_blocked():
            filters.append(cls.blocked == False)
            join_conditions.append(SongModel.blocked == False)

        albums = (
            pdb.query(cls)
            .options(contains_eager("songs"))
            .join(cls.songs.and_(*join_conditions), full=True)
            .filter(and_(True, *filters))
            .all()
        )

        if len(albums) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Album not found"
            )

        return albums[0]

    def update(self, pdb: Session, **kwargs):
        songs_ids = kwargs.pop("songs_ids", None)
        role = kwargs.get("role")

        if songs_ids is not None:
            songs = []
            for song_id in songs_ids:
                song = SongModel.get(pdb, song_id, role=role)
                songs.append(song)
            self.songs = songs
        return super().update(pdb, **kwargs)
