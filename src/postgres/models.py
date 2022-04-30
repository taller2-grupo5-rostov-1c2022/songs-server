from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.postgres.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True)
    songs = relationship("SongModel", back_populates="creator")
    albums = relationship("AlbumModel", back_populates="creator")


class AlbumModel(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"))

    artists = relationship("ArtistAlbumModel", back_populates="album")
    songs = relationship("SongModel", back_populates="album")


class ArtistAlbumModel(Base):
    __tablename__ = "artists_album"

    artist_name = Column(String, primary_key=True, nullable=False, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("AlbumModel", back_populates="artists")


class ArtistSongModel(Base):
    __tablename__ = "artists_song"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    artist_name = Column(String, nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"))
    song = relationship("SongModel", back_populates="artists")


class SongModel(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)

    artists = relationship("ArtistSongModel", back_populates="song")

    album = relationship("AlbumModel", back_populates="songs")
    album_id = Column(Integer, ForeignKey("albums.id"))

    creator = relationship("UserModel", back_populates="songs")
    creator_id = Column(String, ForeignKey("users.id"))
