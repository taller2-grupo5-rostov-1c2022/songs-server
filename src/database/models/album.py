from sqlalchemy import Column, ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import relationship
from . import templates, tables


class AlbumModel(templates.ResourceCreatorModel):
    __tablename__ = "albums"

    cover_last_update = Column(TIMESTAMP, nullable=False)

    creator = relationship("UserModel", back_populates="albums")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)

    songs = relationship("SongModel", back_populates="album")

    reviews = relationship("ReviewModel", back_populates="album")
    comments = relationship("CommentModel", back_populates="album")

    favorited_by = relationship(
        "UserModel",
        secondary=tables.album_favorites_association_table,
        back_populates="favorite_albums",
    )
