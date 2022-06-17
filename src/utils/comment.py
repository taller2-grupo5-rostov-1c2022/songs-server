from sqlalchemy.orm import Session

from fastapi import Depends, Body

from src import roles, utils
from src.database import models
from src import schemas
from src.database.access import get_db


def retrieve_comment_post(
    text: str = Body(..., embed=True),
    parent_id: int = Body(None, embed=True),
    uid: str = Depends(utils.user.retrieve_uid),
    album: models.AlbumModel = Depends(utils.album.get_album),
):
    return schemas.CommentPost(
        text=text, parent_id=parent_id, commenter_id=uid, album_id=album.id, uid=uid
    )


def get_comment(
    comment_id: int,
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(roles.get_role),
):
    comment: models.CommentModel = models.CommentModel.get(
        pdb, _id=comment_id, role=role
    )
    return comment
