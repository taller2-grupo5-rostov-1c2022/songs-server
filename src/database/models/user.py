import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship, Session, contains_eager
from typing.io import IO

from . import tables
from .song import SongModel
from .album import AlbumModel
from .crud_template import CRUDMixin
from fastapi import HTTPException, status

from ... import roles
from ...constants import SUPPRESS_BLOB_ERRORS


class UserModel(CRUDMixin):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True)
    sub_level = Column(Integer, nullable=False)
    sub_expires = Column(DateTime, nullable=True)

    wallet = Column(String, nullable=True, index=True)
    location = Column(String, nullable=False, index=True)
    interests = Column(String, nullable=False, index=True)
    pfp_last_update = Column(TIMESTAMP, nullable=True)

    songs = relationship("SongModel", back_populates="creator")
    albums = relationship("AlbumModel", back_populates="creator")
    comments = relationship("CommentModel", back_populates="commenter")

    my_playlists = relationship("PlaylistModel", back_populates="creator")
    other_playlists = relationship(
        "PlaylistModel",
        secondary=tables.colab_playlist_association_table,
        back_populates="colabs",
    )

    reviews = relationship("ReviewModel", back_populates="reviewer")

    favorite_songs = relationship(
        "SongModel",
        lazy="dynamic",
        secondary=tables.song_favorites_association_table,
        back_populates="favorited_by",
    )
    favorite_albums = relationship(
        "AlbumModel",
        lazy="dynamic",
        secondary=tables.album_favorites_association_table,
        back_populates="favorited_by",
    )
    favorite_playlists = relationship(
        "PlaylistModel",
        lazy="dynamic",
        secondary=tables.playlist_favorite_association_table,
        back_populates="favorited_by",
    )

    streaming = relationship("StreamingModel", back_populates="artist", uselist=False)

    def upload_pfp(self, pdb: Session, pfp: IO, bucket):
        try:
            blob = bucket.blob(f"pfp/{self.id}")
            blob.upload_from_file(pfp)
            blob.make_public()
            self.pfp_last_update = datetime.datetime.now()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                self.expire(pdb)
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload pfp for for User with id {self.id}: {e}",
                )

    def delete_pfp(self, bucket):
        try:
            blob = bucket.blob(f"pfp/{self.id}")
            blob.delete()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload pfp for for User with id {self.id}: {e}",
                )

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        if "sub_level" not in kwargs:
            kwargs["sub_level"] = 0

        pfp = kwargs.pop("pfp", None)
        user = super().create(pdb, **kwargs, commit=False)

        if pfp is not None:
            bucket = kwargs.pop("bucket")
            user.upload_pfp(pdb, pfp, bucket)
        user.save(pdb)

        return user

    def update(self, pdb: Session, **kwargs):
        pfp = kwargs.pop("pfp", None)
        if pfp is not None:
            bucket = kwargs.pop("bucket")
            self.pfp_last_update = datetime.datetime.now()
            self.upload_pfp(pdb, pfp, bucket)
        return super().update(pdb, **kwargs)

    def delete(self, pdb: Session, **kwargs):
        bucket = kwargs.pop("bucket")

        if self.pfp_last_update is not None:
            self.delete_pfp(bucket)
        return super().delete(pdb, **kwargs)

    def get_favorite_songs(self, **kwargs):
        role: roles.Role = kwargs.pop("role")
        filters = []

        if not role.can_see_blocked():
            filters.append(SongModel.blocked == False)

        return self.favorite_songs.filter(*filters, **kwargs).all()

    def add_favorite_song(self, pdb: Session, **kwargs):
        song = kwargs.pop("song")
        self.favorite_songs.append(song)
        self.save(pdb)
        return self

    def remove_favorite_song(self, pdb: Session, **kwargs):
        song = kwargs.pop("song")
        self.favorite_songs.remove(song)
        self.save(pdb)

    def get_favorite_albums(self, **kwargs):
        role: roles.Role = kwargs.pop("role")
        filters = []
        join_conditions = []

        if not role.can_see_blocked():
            filters.append(AlbumModel.blocked == False)
            join_conditions.append(SongModel.blocked == False)

        albums = (
            self.favorite_albums.options(contains_eager("songs"))
            .join(SongModel.album.and_(*join_conditions), full=True)
            .filter(*filters)
            .all()
        )
        return albums

    def add_favorite_album(self, pdb: Session, **kwargs):
        album = kwargs.pop("album")
        self.favorite_albums.append(album)
        self.save(pdb)
        return self

    def remove_favorite_album(self, pdb: Session, **kwargs):
        album = kwargs.pop("album")
        self.favorite_albums.remove(album)
        self.save(pdb)

    def get_favorite_playlists(self, **kwargs):
        role: roles.Role = kwargs.pop("role")
        filters = []
        join_conditions = []
        # FIXME: Circular dependency
        from .playlist import PlaylistModel

        if not role.can_see_blocked():
            filters.append(PlaylistModel.blocked == False)
            join_conditions.append(SongModel.blocked == False)
        return (
            self.favorite_playlists.options(contains_eager("songs"))
            .join(PlaylistModel.songs.and_(*join_conditions), isouter=True)
            .filter(*filters, **kwargs)
            .all()
        )

    def add_favorite_playlist(self, pdb: Session, **kwargs):
        playlist = kwargs.pop("playlist")
        self.favorite_playlists.append(playlist)
        self.save(pdb)
        return self

    def remove_favorite_playlist(self, pdb: Session, **kwargs):
        playlist = kwargs.pop("playlist")
        self.favorite_playlists.remove(playlist)
        self.save(pdb)
