from src.postgres import schemas
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src.repositories import album_utils, user_utils, comment_utils
from src.postgres.models import CommentModel

router = APIRouter(tags=["comments"])


@router.post("/albums/{album_id}/comments/", response_model=schemas.CommentGet)
def post_comment(
    comment_info: schemas.CommentBase,
    album: models.AlbumModel = Depends(album_utils.get_album),
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    if comment_info.text is None and comment_info.score is None:
        raise HTTPException(
            status_code=422, detail="Text and score cannot be None at the same time"
        )

    comment = (
        pdb.query(models.AlbumModel)
        .join(CommentModel.album)
        .filter(models.AlbumModel.id == album.id, CommentModel.commenter_id == uid)
        .first()
    )
    if comment is not None:
        raise HTTPException(
            status_code=403, detail=f"User {uid} already commented in album {album.id}"
        )

    new_comment = CommentModel(
        **comment_info.dict(), commenter=pdb.get(models.UserModel, uid), album=album
    )
    pdb.add(new_comment)
    pdb.commit()
    pdb.refresh(new_comment)
    return new_comment


@router.get("/albums/{album_id}/comments/", response_model=List[schemas.CommentGet])
def get_comments(
    album: models.AlbumModel = Depends(album_utils.get_album),
):
    return album.comments


@router.get("/albums/{album_id}/my_comment/", response_model=schemas.CommentBase)
def get_my_comment(comment: CommentModel = Depends(comment_utils.get_comment)):
    return comment


@router.put("/albums/{album_id}/comments/")
def edit_comment(
    comment_info_update: schemas.CommentUpdate,
    comment: CommentModel = Depends(comment_utils.get_comment),
    pdb: Session = Depends(get_db),
):
    comment_attrs = comment_info_update.dict()
    print(comment)
    for comment_attr_key in comment_attrs:
        if comment_attrs[comment_attr_key] is not None:
            setattr(comment, comment_attr_key, comment_attrs[comment_attr_key])

    pdb.commit()


@router.delete("/albums/{album_id}/comments/")
def delete_comment(
    comment: CommentModel = Depends(comment_utils.get_comment),
    pdb: Session = Depends(get_db),
):
    pdb.delete(comment)
    pdb.commit()


@router.get("/users/{uid}/comments/", response_model=List[schemas.CommentMyComments])
def get_comments_of_user(
    uid: str = Depends(user_utils.retrieve_uid), pdb: Session = Depends(get_db)
):
    return comment_utils.get_comments_by_uid(pdb, uid)
