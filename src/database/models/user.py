from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from src.database.access import Base
from . import tables


class UserModel(Base):
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
