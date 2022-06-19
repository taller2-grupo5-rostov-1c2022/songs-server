from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from .crud_template import CRUDMixin
from fastapi import HTTPException, status
from .user import UserModel


class ReviewModel(CRUDMixin):
    __tablename__ = "reviews"

    reviewer = relationship("UserModel", back_populates="reviews")
    reviewer_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    album = relationship("AlbumModel", back_populates="reviews")
    album_id = Column(
        Integer, ForeignKey("albums.id"), primary_key=True, nullable=False
    )

    score = Column(Integer, nullable=True)
    text = Column(String, nullable=True)

    @classmethod
    def get(cls, pdb: Session, raise_if_not_found=True, **kwargs):
        reviewer = kwargs.pop("reviewer")
        album = kwargs.pop("album")

        review = pdb.query(cls).get((reviewer.id, album.id))
        if raise_if_not_found and review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found for this album and user",
            )
        return review

    @classmethod
    def get_by_reviewer(cls, pdb: Session, reviewer: UserModel):
        reviews = pdb.query(cls).filter(cls.reviewer == reviewer)
        return reviews.all()