from src.exceptions import MessageException
from src import utils
from src import schemas
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from fastapi import Query

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["comments"])


@router.get(
    "/albums/{album_id}/comments/", response_model=CustomPage[schemas.CommentGet]
)
def get_album_comments(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return models.CommentModel.get_roots_by_album(
        pdb, album, limit=limit, offset=offset
    )


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
        raise MessageException(
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
        raise MessageException(
            status_code=403, detail="You are not allowed to delete this comment"
        )

    comment.soft_delete(pdb)


@router.get("/users/comments/", response_model=CustomPage[schemas.CommentGet])
def get_user_comments(
    uid: models.UserModel = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):

    return models.CommentModel.search(pdb, commenter_id=uid, limit=limit, offset=offset)
