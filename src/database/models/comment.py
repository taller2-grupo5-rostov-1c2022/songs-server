from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from src.postgres.database import Base


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False)

    commenter = relationship("UserModel", back_populates="comments")
    commenter_id = Column(String, ForeignKey("users.id"))

    album = relationship("AlbumModel", back_populates="comments")
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    responses = relationship("CommentModel", back_populates="parent")
    parent = relationship("CommentModel", remote_side=[id], back_populates="responses")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
