from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import Table

from src.postgres.database import Base


colab_playlist_association_table = Table('colab_playlist_association', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('playlist_id', ForeignKey('playlists.id'), primary_key=True)
)

song_playlist_association_table = Table('song_playlist_association', Base.metadata,
    Column('playlist_id', ForeignKey('playlists.id'), primary_key=True),
    Column('song_id', ForeignKey('songs.id'), primary_key=True)
)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True)
    songs = relationship("SongModel", back_populates="creator")
    albums = relationship("AlbumModel", back_populates="creator")

    my_playlists = relationship("PlaylistModel", back_populates="creator")
    other_playlists = relationship("PlaylistModel", back_populates="creator")
    other_playlists = relationship(
        "PlaylistModel",
        secondary=colab_playlist_association_table,
        back_populates="colabs")


class AlbumModel(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)
    sub_level = Column(Integer, nullable=False)

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"))

    songs = relationship("SongModel", back_populates="album")


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


class ColabPlaylistModel(Base):
    __tablename__ = "colab_playlist"

    id = Column(Integer, primary_key=True, nullable=False, index=True)

    colab_id = Column(Integer, ForeignKey("users.id"))
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
        back_populates="other_playlists")
    creator = relationship("UserModel", back_populates="my_playlists")
    creator_id = Column(String, ForeignKey("users.id"))
