from sqlalchemy import Column, Table, ForeignKey
from src.database.access import Base


song_artist_association_table = Table(
    "song_artist_association",
    Base.metadata,
    Column(
        "artist_name",
        ForeignKey("artists.name", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
    Column(
        "song_id",
        ForeignKey("songs.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    ),
)

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
    Column("user_id", ForeignKey("users.id", onupdate="CASCADE"), primary_key=True),
    Column(
        "playlist_id", ForeignKey("playlists.id", onupdate="CASCADE"), primary_key=True
    ),
)
