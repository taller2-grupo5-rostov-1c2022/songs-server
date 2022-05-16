from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean
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


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True)

    wallet = Column(String, nullable=True, index=True)
    location = Column(String, nullable=False, index=True)
    interests = Column(String, nullable=False, index=True)
    pfp_last_update = Column(TIMESTAMP, nullable=False)

    songs = relationship("SongModel", back_populates="creator")
    albums = relationship("AlbumModel", back_populates="album_creator")

    my_playlists = relationship("PlaylistModel", back_populates="creator")
    other_playlists = relationship(
        "PlaylistModel",
        secondary=colab_playlist_association_table,
        back_populates="colabs",
    )


class AlbumModel(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)
    sub_level = Column(Integer, nullable=False)
    cover_last_update = Column(TIMESTAMP, nullable=False)
    blocked = Column(Boolean, nullable=False, index=True)

    album_creator = relationship("UserModel", back_populates="albums")
    album_creator_id = Column(String, ForeignKey("users.id"))

    songs = relationship("SongModel", back_populates="album")


class ArtistModel(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    songs = relationship(
        "SongModel",
        secondary=song_artist_association_table,
        back_populates="artists",
    )


class SongModel(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)
    sub_level = Column(Integer, nullable=False, index=True)
    file_last_update = Column(TIMESTAMP, nullable=False)
    blocked = Column(Boolean, nullable=False, index=True)

    artists = relationship(
        "ArtistModel",
        secondary=song_artist_association_table,
        back_populates="songs",
        lazy="joined",
    )

    album = relationship("AlbumModel", back_populates="songs", lazy="joined")
    album_id = Column(
        Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("UserModel", back_populates="songs")
    creator_id = Column(String, ForeignKey("users.id"))


class ColabPlaylistModel(Base):
    __tablename__ = "colab_playlist"

    id = Column(Integer, primary_key=True, nullable=False, index=True)

    colab_id = Column(String, ForeignKey("users.id"))
    playlist_id = Column(Integer, ForeignKey("playlists.id"))


class PlaylistModel(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    songs = relationship("SongModel", secondary=song_playlist_association_table)

    colabs = relationship(
        "UserModel",
        secondary=colab_playlist_association_table,
        back_populates="other_playlists",
    )
    creator = relationship("UserModel", back_populates="my_playlists")
    creator_id = Column(String, ForeignKey("users.id"))
