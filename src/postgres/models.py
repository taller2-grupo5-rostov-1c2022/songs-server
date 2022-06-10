from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Table

from src.postgres.database import Base


colab_playlist_association_table = Table(
    "colab_playlist_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column(
        "playlist_id",
        ForeignKey("playlists.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)

song_playlist_association_table = Table(
    "song_playlist_association",
    Base.metadata,
    Column(
        "playlist_id",
        ForeignKey("playlists.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "song_id",
        ForeignKey("songs.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)

song_artist_association_table = Table(
    "song_artist_association",
    Base.metadata,
    Column(
        "artist_id",
        ForeignKey("artists.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "song_id",
        ForeignKey("songs.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)


song_favorites_association_table = Table(
    "song_favorites_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", onupdate="CASCADE"), primary_key=True),
    Column("song_id", ForeignKey("songs.id", onupdate="CASCADE"), primary_key=True),
)


album_favorites_association_table = Table(
    "album_favorites_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", onupdate="CASCADE"), primary_key=True),
    Column("album_id", ForeignKey("albums.id", onupdate="CASCADE"), primary_key=True),
)


playlist_favorite_association_table = Table(
    "playlist_favorite_association",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "playlist_id",
        ForeignKey("playlists.id", onupdate="CASCADE"),
        primary_key=True,
    ),
)


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
        secondary=colab_playlist_association_table,
        back_populates="colabs",
    )

    reviews = relationship("ReviewModel", back_populates="reviewer")

    favorite_songs = relationship(
        "SongModel",
        lazy="dynamic",
        secondary=song_favorites_association_table,
        back_populates="favorited_by",
    )
    favorite_albums = relationship(
        "AlbumModel",
        lazy="dynamic",
        secondary=album_favorites_association_table,
        back_populates="favorited_by",
    )
    favorite_playlists = relationship(
        "PlaylistModel",
        lazy="dynamic",
        secondary=playlist_favorite_association_table,
        back_populates="favorited_by",
    )

    streaming = relationship("StreamingModel", back_populates="artist", uselist=False)


class StreamingModel(Base):
    __tablename__ = "streamings"

    listener_token = Column(String, primary_key=True)
    artist_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    artist = relationship("UserModel", back_populates="streaming")

    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)


class ResourceModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    blocked = Column(Boolean, nullable=False, index=True)


class ResourceCreatorModel(ResourceModel):
    __abstract__ = True
    genre = Column(String, nullable=False, index=True)
    sub_level = Column(Integer, nullable=False)


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer = relationship("UserModel", back_populates="reviews")
    reviewer_id = Column(String, ForeignKey("users.id"))

    album = relationship("AlbumModel", back_populates="reviews")
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    score = Column(Integer, nullable=True)
    text = Column(String, nullable=True)


class AlbumModel(ResourceCreatorModel):
    __tablename__ = "albums"

    cover_last_update = Column(TIMESTAMP, nullable=False)

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    songs = relationship("SongModel", back_populates="album")

    reviews = relationship("ReviewModel", back_populates="album")
    comments = relationship("CommentModel", back_populates="album")

    favorited_by = relationship(
        "UserModel",
        secondary=album_favorites_association_table,
        back_populates="favorite_albums",
    )


class ArtistModel(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    songs = relationship(
        "SongModel",
        secondary=song_artist_association_table,
        back_populates="artists",
    )


class SongModel(ResourceCreatorModel):
    __tablename__ = "songs"

    file_last_update = Column(TIMESTAMP, nullable=False)

    artists = relationship(
        "ArtistModel", secondary=song_artist_association_table, back_populates="songs"
    )

    album = relationship("AlbumModel", back_populates="songs", lazy="joined")
    album_id = Column(
        Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("UserModel", back_populates="songs")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=song_favorites_association_table,
        back_populates="favorite_songs",
    )


class PlaylistModel(ResourceModel):
    __tablename__ = "playlists"

    songs = relationship(
        "SongModel",
        secondary=song_playlist_association_table,
    )

    colabs = relationship(
        "UserModel",
        secondary=colab_playlist_association_table,
        back_populates="other_playlists",
    )
    creator = relationship("UserModel", back_populates="my_playlists")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=playlist_favorite_association_table,
        back_populates="favorite_playlists",
    )


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False)

    commenter = relationship("UserModel", back_populates="comments")
    commenter_id = Column(String, ForeignKey("users.id"))

    album = relationship("AlbumModel", back_populates="comments")
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    responses = relationship("CommentModel", back_populates="parent")
    parent = relationship("CommentModel", remote_side=[id], back_populates="responses")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
