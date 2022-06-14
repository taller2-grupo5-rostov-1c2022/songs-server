from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.postgres.database import Base


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer = relationship("UserModel", back_populates="reviews")
    reviewer_id = Column(String, ForeignKey("users.id"))

    album = relationship("AlbumModel", back_populates="reviews")
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    score = Column(Integer, nullable=True)
    text = Column(String, nullable=True)
