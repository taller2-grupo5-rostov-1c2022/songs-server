from src.exceptions import MessageException
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session, Query
from typing.io import IO

from . import tables
from .song import SongModel
from .album import AlbumModel
from .crud_template import CRUDMixin
from fastapi import status

from ... import roles
from ...constants import SUPPRESS_BLOB_ERRORS
from ...schemas.pagination import CustomPage


class UserModel(CRUDMixin):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True)
    sub_level = Column(Integer, nullable=False)
    sub_expires = Column(DateTime, nullable=True)

    wallet = Column(String, nullable=True, index=True)
    location = Column(String, nullable=False, index=True)
    interests = Column(String, nullable=False, index=True)
    pfp_url = Column(String, nullable=True)

    songs = relationship("SongModel", back_populates="creator")
    albums = relationship("AlbumModel", back_populates="creator")
    comments = relationship(
        "CommentModel", back_populates="commenter"
    )

    my_playlists = relationship("PlaylistModel", back_populates="creator")
    other_playlists = relationship(
        "PlaylistModel",
        secondary=tables.colab_playlist_association_table,
        back_populates="colabs",
    )

    reviews = relationship(
        "ReviewModel", back_populates="reviewer", cascade="all, delete-orphan"
    )

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

    streaming = relationship(
        "StreamingModel",
        back_populates="artist",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def upload_pfp(self, pdb: Session, pfp: IO, bucket):
        try:
            blob = bucket.blob(f"pfp/{self.id}")
            blob.upload_from_file(pfp)
            blob.make_public()
            timestamp = f"?t={str(int(datetime.timestamp(datetime.now())))}"
            self.pfp_url = blob.public_url + timestamp
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                self.expire(pdb)
                raise MessageException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload pfp for for User with id {self.id}: {e}",
                )

    def delete_pfp(self, bucket):
        try:
            blob = bucket.blob(f"pfp/{self.id}")
            blob.delete()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                raise MessageException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not delete pfp for for User with id {self.id}: {e}",
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

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query = kwargs.pop("query", None)
        if query is None:
            query = pdb.query(cls)

        expiration_date = kwargs.pop("expiration_date", None)
        if expiration_date is not None:
            query = query.filter(cls.sub_expires < expiration_date)
        return super().search(pdb, query=query, **kwargs)

    def update(self, pdb: Session, **kwargs):
        pfp = kwargs.pop("pfp", None)
        if pfp is not None:
            bucket = kwargs.pop("bucket")
            self.upload_pfp(pdb, pfp, bucket)
        return super().update(pdb, **kwargs)

    def delete(self, pdb: Session, **kwargs):
        bucket = kwargs.pop("bucket")

        if self.pfp_url is not None:
            self.delete_pfp(bucket)
        return super().delete(pdb, **kwargs)

    def get_favorite_songs(self, **kwargs):
        role: roles.Role = kwargs.pop("role")
        filters = []

        if not role.can_see_blocked():
            filters.append(SongModel.blocked == False)
        query = self.favorite_songs.filter(*filters)
        return self.paginate(query, SongModel, **kwargs)

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

        if not role.can_see_blocked():
            filters.append(AlbumModel.blocked == False)

        query = self.favorite_albums.filter(*filters)
        return self.paginate(query, AlbumModel, **kwargs)

    @staticmethod
    def paginate(query: Query, model, **kwargs):
        offset = kwargs.pop("offset")
        limit = kwargs.pop("limit")
        total = query.count()
        query = query.order_by(model.id).filter(model.id > offset).limit(limit)
        items = query.all()
        return CustomPage(items=items, total=total, offset=offset, limit=limit)

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
        # FIXME: Circular dependency
        from .playlist import PlaylistModel

        if not role.can_see_blocked():
            filters.append(PlaylistModel.blocked == False)
        query = self.favorite_playlists.filter(*filters)
        return self.paginate(query, PlaylistModel, **kwargs)

    def add_favorite_playlist(self, pdb: Session, **kwargs):
        playlist = kwargs.pop("playlist")
        self.favorite_playlists.append(playlist)
        self.save(pdb)
        return self

    def remove_favorite_playlist(self, pdb: Session, **kwargs):
        playlist = kwargs.pop("playlist")
        self.favorite_playlists.remove(playlist)
        self.save(pdb)
