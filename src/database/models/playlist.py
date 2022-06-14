from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from . import templates, tables


class PlaylistModel(templates.ResourceModel):
    __tablename__ = "playlists"

    songs = relationship(
        "SongModel",
        secondary=tables.song_playlist_association_table,
    )

    colabs = relationship(
        "UserModel",
        secondary=tables.colab_playlist_association_table,
        back_populates="other_playlists",
    )
    creator = relationship("UserModel", back_populates="my_playlists")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=tables.playlist_favorite_association_table,
        back_populates="favorite_playlists",
    )
