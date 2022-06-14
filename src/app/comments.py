import datetime

from src import utils
from src.postgres import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.database import models

router = APIRouter(tags=["comments"])


@router.get("/albums/{album_id}/comments/", response_model=List[schemas.CommentGet])
def get_album_comments(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
):
    return (
        pdb.query(models.CommentModel)
        .filter(
            models.CommentModel.album_id == album.id,
            models.CommentModel.parent_id == None,
        )
        .all()
    )


@router.post("/albums/{album_id}/comments/", response_model=schemas.CommentGet)
def post_album_comment(
    album: models.AlbumModel = Depends(utils.album.get_album),
    comment: schemas.CommentPost = Depends(utils.comment.retrieve_comment_post),
    pdb: Session = Depends(get_db),
):

    comment_model = models.CommentModel(
        **comment.dict(),
        created_at=datetime.datetime.now(),
    )
    if comment.parent_id is not None:
        parent = pdb.get(models.CommentModel, comment.parent_id)
        parent.responses.append(comment_model)
    else:
        album.comments.append(comment_model)

    pdb.commit()
    return comment_model


@router.put("/albums/comments/{comment_id}/", response_model=schemas.CommentGet)
def edit_album_comment(
    comment_update: schemas.CommentUpdate,
    comment: models.CommentModel = Depends(utils.comment.get_comment),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):

    if comment.commenter_id != uid:
        raise HTTPException(
            status_code=403, detail="You are not allowed to edit this comment"
        )

    comment_update = comment_update.dict()

    for comment_attr in comment_update:
        if comment_update[comment_attr] is not None:
            setattr(comment, comment_attr, comment_update[comment_attr])

    pdb.commit()
    return comment


@router.delete("/albums/comments/{comment_id}/")
def delete_album_comment(
    comment: models.CommentModel = Depends(utils.comment.get_comment),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    if comment.commenter_id != uid:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this comment"
        )
    comment.text = None
    pdb.commit()


@router.get("/users/comments/", response_model=List[schemas.CommentGet])
def get_user_comments(
    uid: models.UserModel = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    return (
        pdb.query(models.CommentModel)
        .filter(models.CommentModel.commenter_id == uid)
        .all()
    )
