import datetime
from fastapi import HTTPException, status
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship, Session
from .crud_template import CRUDMixin
from .user import UserModel
from .album import AlbumModel
from ... import roles
from ...schemas.pagination import CustomPage


class CommentModel(CRUDMixin):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)

    commenter = relationship("UserModel", back_populates="comments")
    commenter_id = Column(String, ForeignKey("users.id"))

    album = relationship("AlbumModel", back_populates="comments")
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    responses = relationship("CommentModel", back_populates="parent")
    parent = relationship("CommentModel", remote_side=[id], back_populates="responses")
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    @classmethod
    def create(cls, pdb: Session, *args, **kwargs):
        commenter_id = kwargs.pop("commenter_id")
        album: AlbumModel = kwargs.pop("album")

        parent_id = kwargs.pop("parent_id", None)

        commenter = UserModel.get(pdb, _id=commenter_id)
        if parent_id is not None:
            parent = CommentModel.get(pdb, _id=parent_id)
        else:
            parent = None

        comment = super().create(
            pdb,
            commenter=commenter,
            album=album,
            parent=parent,
            created_at=datetime.datetime.now(),
            **kwargs,
        )
        return comment

    @classmethod
    def get_roots_by_album(cls, pdb: Session, album: AlbumModel, **kwargs):
        query = pdb.query(cls).filter(cls.album_id == album.id, cls.parent_id == None)

        limit = kwargs.pop("limit")
        offset = kwargs.pop("offset")
        total = query.count()
        query.order_by(cls.id).filter(cls.id > offset).limit(limit)

        items = query.all()
        return CustomPage(items=items, limit=limit, offset=offset, total=total)

    @classmethod
    def search(cls, pdb: Session, **kwargs):
        commenter_id = kwargs.pop("commenter_id", None)
        query = kwargs.pop("query", None)

        if query is None:
            query = pdb.query(cls)

        if commenter_id is not None:
            query = query.filter(cls.commenter_id == commenter_id)

        return super().search(pdb, query=query, **kwargs)

    @classmethod
    def get(cls, pdb: Session, _id, raise_if_not_found=True, **kwargs):
        role: roles.Role = kwargs.get("role")
        comment: cls = super().get(
            pdb, _id, raise_if_not_found=raise_if_not_found, **kwargs
        )
        if comment.album.blocked and not role.can_see_blocked():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
        return comment

    def soft_delete(self, pdb: Session):
        self.text = None
        pdb.commit()
