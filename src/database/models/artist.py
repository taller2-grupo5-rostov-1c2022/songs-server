from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Session
from . import tables
from .crud_template import CRUDMixin


class ArtistModel(CRUDMixin):
    __tablename__ = "artists"

    name = Column(String, primary_key=True, nullable=False, index=True)
    songs = relationship(
        "SongModel",
        secondary=tables.song_artist_association_table,
        back_populates="artists",
    )

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        return super().create(pdb, **kwargs)
