from src.postgres import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src.repositories import album_utils, user_utils, review_utils
from src.postgres.models import ReviewModel

router = APIRouter(tags=["reviews"])


@router.post("/albums/{album_id}/reviews/", response_model=schemas.ReviewGet)
def post_review(
    review_info: schemas.ReviewBase,
    album: models.AlbumModel = Depends(album_utils.get_album),
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    if review_info.text is None and review_info.score is None:
        raise HTTPException(
            status_code=422, detail="Text and score cannot be None at the same time"
        )
    review = (
        pdb.query(models.AlbumModel)
        .join(ReviewModel.album)
        .filter(models.AlbumModel.id == album.id, ReviewModel.reviewer_id == uid)
        .first()
    )
    if review is not None:
        raise HTTPException(
            status_code=403, detail=f"User {uid} already reviewed in album {album.id}"
        )

    new_review = ReviewModel(
        **review_info.dict(), reviewer=pdb.get(models.UserModel, uid), album=album
    )
    pdb.add(new_review)
    pdb.commit()
    pdb.refresh(new_review)
    return new_review


@router.get("/albums/{album_id}/reviews/", response_model=List[schemas.ReviewGet])
def get_reviews(
    album: models.AlbumModel = Depends(album_utils.get_album),
):
    return album.reviews


@router.get("/albums/{album_id}/my_review/", response_model=schemas.ReviewBase)
def get_my_review(review: ReviewModel = Depends(review_utils.get_review)):
    return review


@router.put("/albums/{album_id}/reviews/")
def edit_review(
    review_info_update: schemas.ReviewUpdate,
    review: ReviewModel = Depends(review_utils.get_review),
    pdb: Session = Depends(get_db),
):
    review_attrs = review_info_update.dict()
    for review_attr_key in review_attrs:
        if review_attrs[review_attr_key] is not None:
            setattr(review, review_attr_key, review_attrs[review_attr_key])

    pdb.commit()
    pdb.refresh(review)


@router.delete("/albums/{album_id}/reviews/")
def delete_review(
    review: ReviewModel = Depends(review_utils.get_review),
    pdb: Session = Depends(get_db),
):
    pdb.delete(review)
    pdb.commit()


@router.get("/users/{uid}/reviews/", response_model=List[schemas.ReviewMyReviews])
def get_reviews_of_user(
    uid: str = Depends(user_utils.retrieve_uid), pdb: Session = Depends(get_db)
):
    return review_utils.get_reviews_by_uid(pdb, uid)
