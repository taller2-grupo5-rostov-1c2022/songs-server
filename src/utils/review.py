from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.access import get_db
from src import roles, utils
from src.database import models, crud


def get_reviews_by_uid(pdb, uid: str):

    return (
        pdb.query(models.ReviewModel)
        .filter(models.ReviewModel.reviewer_id == uid)
        .all()
    )


def get_review(
    album: models.AlbumModel = Depends(utils.album.get_album),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    return crud.review.get_reviews_by_user(pdb, album, user, role.can_see_blocked())
