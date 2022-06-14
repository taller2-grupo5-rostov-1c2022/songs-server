from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from . import templates, tables


class SongModel(templates.ResourceCreatorModel):
    __tablename__ = "songs"

    sub_level = Column(Integer, nullable=False)

    file_last_update = Column(TIMESTAMP, nullable=False)

    artists = relationship(
        "ArtistModel",
        secondary=tables.song_artist_association_table,
        back_populates="songs",
    )

    album = relationship("AlbumModel", back_populates="songs", lazy="joined")
    album_id = Column(
        Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("UserModel", back_populates="songs")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    favorited_by = relationship(
        "UserModel",
        secondary=tables.song_favorites_association_table,
        back_populates="favorite_songs",
    )
