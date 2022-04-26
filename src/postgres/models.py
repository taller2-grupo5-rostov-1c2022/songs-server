from sqlalchemy import Integer, String
from sqlalchemy.sql.schema import Column
from src.postgres.database import Base


class SongModel(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creator = Column(String, nullable=False)
    artists = Column(String, nullable=False)
