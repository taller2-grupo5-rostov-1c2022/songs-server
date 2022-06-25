from src import utils, schemas
from src.database.access import get_db
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import models

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["reviews"])


@router.post("/albums/{album_id}/reviews/", response_model=schemas.ReviewGet)
def post_review(
    review_info: schemas.ReviewBase,
    album: models.AlbumModel = Depends(utils.album.get_album),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if review_info.text is None and review_info.score is None:
        raise HTTPException(
            status_code=422, detail="Text and score cannot be None at the same time"
        )

    review = models.ReviewModel.get(
        pdb, album=album, reviewer=user, raise_if_not_found=False
    )
    if review:
        raise HTTPException(
            status_code=403,
            detail=f"User {user.id} already reviewed in album {album.id}",
        )

    review = models.ReviewModel.create(
        pdb, album=album, **review_info.dict(), reviewer=user
    )

    return review


@router.get("/albums/{album_id}/reviews/", response_model=CustomPage[schemas.ReviewGet])
def get_reviews(
    album: models.AlbumModel = Depends(utils.album.get_album),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    pdb: Session = Depends(get_db),
):
    return album.get_reviews(pdb, limit, offset)


@router.get("/albums/{album_id}/my_review/", response_model=schemas.ReviewBase)
def get_my_review(review: models.ReviewModel = Depends(utils.review.get_review)):
    return review


@router.put("/albums/{album_id}/reviews/")
def edit_review(
    review_info_update: schemas.ReviewUpdate,
    review: models.ReviewModel = Depends(utils.review.get_review),
    pdb: Session = Depends(get_db),
):
    review.update(pdb, **review_info_update.dict(exclude_none=True))


@router.delete("/albums/{album_id}/reviews/")
def delete_review(
    review: models.ReviewModel = Depends(utils.review.get_review),
    pdb: Session = Depends(get_db),
):
    review.delete(pdb)


@router.get("/users/{uid}/reviews/", response_model=CustomPage[schemas.ReviewMyReviews])
def get_reviews_of_user(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return models.ReviewModel.get_by_reviewer(pdb, user, limit, offset)
