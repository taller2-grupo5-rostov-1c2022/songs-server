from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.access import get_db
from src import utils
from src.database import models, crud


def get_reviews_by_uid(pdb, uid: str):

    return (
        pdb.query(models.ReviewModel)
        .filter(models.ReviewModel.reviewer_id == uid)
        .all()
    )


def get_review(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    reviews = crud.review.get_reviews_by_album_and_user(pdb, album, user)
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found for this album and user",
        )
    return reviews[0]
