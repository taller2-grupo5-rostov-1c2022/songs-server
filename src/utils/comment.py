from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException

from src import roles, utils
from src.database import models
from src.postgres import schemas
from src.postgres.database import get_db


def retrieve_comment_post(
    comment_info: schemas.CommentInfo,
    uid: str = Depends(utils.user.retrieve_uid),
    album: models.AlbumModel = Depends(utils.album.get_album),
):
    return schemas.CommentPost(
        **comment_info.dict(), commenter_id=uid, album_id=album.id, uid=uid
    )


def get_comment(
    comment_id: int,
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(roles.get_role),
):
    comment = pdb.get(models.CommentModel, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    _ = utils.album.get_album(comment.album_id, role, pdb)
    return comment
