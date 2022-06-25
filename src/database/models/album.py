from typing import Optional

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, Session, contains_eager
from sqlalchemy.sql import and_
from . import templates, tables
from .artist import ArtistModel
from .song import SongModel
from sqlalchemy.orm.query import Query
from fastapi import HTTPException, status
from sqlalchemy.sql import func

from ...schemas.pagination import CustomPage


class AlbumModel(templates.ResourceWithFile):
    __tablename__ = "albums"

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    songs = relationship("SongModel", back_populates="album")

    reviews = relationship(
        "ReviewModel", back_populates="album", cascade="all, delete-orphan"
    )
    comments = relationship(
        "CommentModel", back_populates="album", cascade="all, delete-orphan"
    )

    favorited_by = relationship(
        "UserModel",
        secondary=tables.album_favorites_association_table,
        back_populates="favorite_albums",
    )

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        query: Query = kwargs.pop("query", None)
        if query is None:
            query = pdb.query(cls)

        artist_name = kwargs.pop("artist", None)
        if artist_name is not None:
            query = (
                query.options(contains_eager("songs"))
                .join(SongModel, full=True)
                .filter(
                    SongModel.artists.any(
                        func.lower(ArtistModel.name).contains(artist_name.lower())
                    )
                )
            )

        albums = super().search(pdb, query=query, **kwargs)
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

    @property
    def score(self):
        if self.scores_amount == 0:
            return 0
        return (
            sum([review.score for review in self.reviews if review.score is not None])
            / self.scores_amount
        )

    @property
    def scores_amount(self):
        return len(
            [self.reviews for review in self.reviews if review.score is not None]
        )

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

    def get_reviews(self, pdb: Session, limit: int, offset: Optional[str]):
        from .review import ReviewModel
        from .user import UserModel

        query = (
            pdb.query(ReviewModel)
            .join(UserModel.reviews)
            .filter(ReviewModel.album_id == self.id)
            .order_by(UserModel.id)
        )

        if offset is None:
            items = query.limit(limit).all()
        else:
            items = query.filter(UserModel.id > offset).limit(limit).all()
        offset = items[-1].reviewer_id if len(items) > 0 else None

        total = query.count()

        return CustomPage(items=items, limit=limit, total=total, offset=offset)
