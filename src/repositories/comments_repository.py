from sqlalchemy.orm import Session

from src.postgres.models import CommentModel


def get_comments_by_uid(pdb: Session, uid: str):

    return pdb.query(CommentModel).filter(CommentModel.commenter_id == uid).all()
