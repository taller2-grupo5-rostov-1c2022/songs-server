from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.access import get_db
from src import roles, utils
from src.database import models


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
    uid: str = Depends(utils.user.retrieve_uid),
):
    return utils.album.get_review_by_uid(pdb, role, album, uid)
