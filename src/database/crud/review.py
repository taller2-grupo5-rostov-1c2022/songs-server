from sqlalchemy.sql import and_
from typing import List
from sqlalchemy.orm import Session
from src.database import models
from src import schemas


def get_reviews_by_album_and_user(
    pdb: Session, album: models.AlbumModel, user: models.UserModel
) -> List[models.ReviewModel]:
    return (
        pdb.query(models.ReviewModel)
        .filter(models.ReviewModel.album == album, models.ReviewModel.reviewer == user)
        .all()
    )


def get_reviews_by_user(
    pdb: Session, user: models.UserModel, can_see_blocked: bool = False
) -> List[models.ReviewModel]:
    filters = [models.ReviewModel.reviewer == user]
    if not can_see_blocked:
        filters.append(models.AlbumModel.blocked == False)

    return (
        pdb.query(models.ReviewModel)
        .join(models.AlbumModel, models.AlbumModel.id == models.ReviewModel.album_id)
        .filter(and_(*filters))
        .all()
    )


def create_review(
    pdb: Session,
    album: models.AlbumModel,
    review_info: schemas.ReviewBase,
    user: models.UserModel,
) -> models.ReviewModel:
    review = models.ReviewModel(**review_info.dict(), reviewer=user, album=album)
    pdb.add(review)
    pdb.commit()
    pdb.refresh(review)

    return review
