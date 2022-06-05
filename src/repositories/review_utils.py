from fastapi import Depends
from sqlalchemy.orm import Session

from src.postgres.database import get_db
from src.repositories import album_utils, user_utils
from src import roles
from src.postgres import models


def get_reviews_by_uid(pdb, uid: str):

    return (
        pdb.query(models.ReviewModel)
        .filter(models.ReviewModel.reviewer_id == uid)
        .all()
    )


def get_review(
    album: models.AlbumModel = Depends(album_utils.get_album),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
    uid: str = Depends(user_utils.retrieve_uid),
):
    return album_utils.get_review_by_uid(pdb, role, album, uid)
