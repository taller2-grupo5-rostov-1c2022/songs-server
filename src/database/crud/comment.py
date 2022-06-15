import datetime

from sqlalchemy.orm import Session

from src import schemas
from src.database import models


def get_comments(pdb: Session, album: models.AlbumModel):
    return (
        pdb.query(models.CommentModel)
        .filter(
            models.CommentModel.album_id == album.id,
            models.CommentModel.parent_id == None,
        )
        .all()
    )


def create_comment(
    pdb: Session, album: models.AlbumModel, comment_info: schemas.CommentPost
) -> models.CommentModel:
    comment = models.CommentModel(
        **comment_info.dict(),
        created_at=datetime.datetime.now(),
    )

    if comment_info.parent_id is not None:
        parent = pdb.get(models.CommentModel, comment_info.parent_id)
        parent.responses.append(comment)
    else:
        album.comments.append(comment)

    pdb.commit()
    return comment


def edit_comment(
    pdb: Session, comment: models.CommentModel, comment_update: schemas.CommentUpdate
) -> models.CommentModel:
    comment_update = comment_update.dict()

    for comment_attr in comment_update:
        if comment_update[comment_attr] is not None:
            setattr(comment, comment_attr, comment_update[comment_attr])

    pdb.commit()
    return comment


def set_text_none(pdb: Session, comment: models.CommentModel):
    comment.text = None
    pdb.commit()


def get_comments_by_uid(pdb: Session, uid: str):
    return (
        pdb.query(models.CommentModel)
        .filter(models.CommentModel.commenter_id == uid)
        .all()
    )
