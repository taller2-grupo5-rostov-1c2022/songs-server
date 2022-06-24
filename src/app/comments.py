from src import utils
from src import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from fastapi_pagination import Page

router = APIRouter(tags=["comments"])


@router.get("/albums/{album_id}/comments/", response_model=List[schemas.CommentGet])
def get_album_comments(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
):
    return models.CommentModel.get_roots_by_album(pdb, album)


@router.post("/albums/{album_id}/comments/", response_model=schemas.CommentGet)
def post_album_comment(
    album: models.AlbumModel = Depends(utils.album.get_album),
    comment_info: schemas.CommentPost = Depends(utils.comment.retrieve_comment_post),
    pdb: Session = Depends(get_db),
):

    comment = models.CommentModel.create(pdb, album=album, **comment_info.dict())

    return comment


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

    comment = comment.update(pdb, **comment_update.dict())

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

    comment.soft_delete(pdb)


@router.get("/users/comments/", response_model=Page[schemas.CommentGet])
def get_user_comments(
    uid: models.UserModel = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):

    return models.CommentModel.search(pdb, commenter_id=uid)
