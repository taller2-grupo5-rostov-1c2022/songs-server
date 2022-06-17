from sqlalchemy.orm import Session
from typing import List
from src.database import models


def get_streamings(pdb: Session) -> List[models.StreamingModel]:
    streamings = pdb.query(models.StreamingModel).all()
    return streamings


def create_streaming(
    pdb: Session, name: str, img_url: str, artist: models.UserModel, listener_token: str
) -> models.StreamingModel:
    streaming = models.StreamingModel(
        name=name, img_url=img_url, artist=artist, listener_token=listener_token
    )
    pdb.add(streaming)
    pdb.commit()
    pdb.refresh(streaming)
    return streaming


def delete_streaming(pdb: Session, streaming: models.StreamingModel):
    pdb.delete(streaming)
    pdb.commit()
