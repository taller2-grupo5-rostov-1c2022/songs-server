from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database.access import Base
from . import tables


class ArtistModel(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    songs = relationship(
        "SongModel",
        secondary=tables.song_artist_association_table,
        back_populates="artists",
    )
