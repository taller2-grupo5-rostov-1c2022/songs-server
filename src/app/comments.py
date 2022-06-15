from src import utils
from src import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models, crud

router = APIRouter(tags=["comments"])


@router.get("/albums/{album_id}/comments/", response_model=List[schemas.CommentGet])
def get_album_comments(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
):
    return crud.comment.get_comments(pdb, album)


@router.post("/albums/{album_id}/comments/", response_model=schemas.CommentGet)
def post_album_comment(
    album: models.AlbumModel = Depends(utils.album.get_album),
    comment_info: schemas.CommentPost = Depends(utils.comment.retrieve_comment_post),
    pdb: Session = Depends(get_db),
):

    comment = crud.comment.create_comment(pdb, album, comment_info)

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

    comment = crud.comment.edit_comment(pdb, comment, comment_update)

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

    crud.comment.set_text_none(pdb, comment)


@router.get("/users/comments/", response_model=List[schemas.CommentGet])
def get_user_comments(
    uid: models.UserModel = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):

    return crud.comment.get_comments_by_uid(pdb, uid)
