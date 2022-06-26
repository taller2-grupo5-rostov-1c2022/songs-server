from src.exceptions import MessageException

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, Session
from typing.io import IO

from .crud_template import CRUDMixin
from fastapi import status

from ...constants import SUPPRESS_BLOB_ERRORS


class StreamingModel(CRUDMixin):
    __tablename__ = "streamings"

    listener_token = Column(String, primary_key=True)
    artist_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    artist = relationship("UserModel", back_populates="streaming")

    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)

    def upload_img(self, pdb: Session, img_id: str, img: IO, bucket):
        try:
            blob = bucket.blob(f"streaming_imgs/{img_id}")
            blob.upload_from_file(img)
            blob.make_public()
            self.img_url = blob.public_url
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                self.expire(pdb)
                raise MessageException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload streaming img: {e}",
                )

    @staticmethod
    def delete_img(img_id: str, bucket):
        try:
            blob = bucket.blob(f"streaming_imgs/{img_id}")
            blob.delete()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                raise MessageException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Could not upload streaming img: {e}",
                )

    @classmethod
    def create(cls, pdb: Session, **kwargs):
        listener_token = kwargs.pop("listener_token")
        artist = kwargs.pop("artist")
        name = kwargs.pop("name")
        img = kwargs.pop("img", None)

        streaming = super().create(
            pdb,
            listener_token=listener_token,
            artist=artist,
            name=name,
            **kwargs,
            commit=False,
        )
        if img:
            bucket = kwargs.pop("bucket")
            streaming.upload_img(pdb, img_id=artist.id, img=img, bucket=bucket)
        streaming.save(pdb)

        return streaming

    def delete(self, pdb: Session, **kwargs):
        bucket = kwargs.pop("bucket")
        if self.img_url is not None:
            self.delete_img(self.artist.id, bucket)
        return super().delete(pdb, **kwargs)
