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

        artist_name = kwargs.pop("artist", None)

        albums = super().search(pdb, query=query, **kwargs)
        if artist_name is not None:
            albums_filtered = []
            for album in albums:
                for song in album.songs:
                    for artist in song.artists:
                        if artist_name.lower() in artist.name.lower():
                            albums_filtered.append(album)
                            break
            albums = albums_filtered
        return albums

    @classmethod
    def get(cls, pdb: Session, **kwargs):
        album_id = kwargs.pop("_id")
        role = kwargs.pop("role")
        requester_id = kwargs.get("requester_id")

        join_conditions = [SongModel.album_id == AlbumModel.id]
        filters = [album_id == cls.id]
        if not role.can_see_blocked():
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
        album = albums[0]
        if (
            album.blocked
            and not role.can_see_blocked()
            and album.creator_id != requester_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Album not found"
            )
        return album

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
