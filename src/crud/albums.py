from sqlalchemy.orm import Session
from src.postgres.models import AlbumModel
from typing import Optional
from fastapi import HTTPException
from src.postgres import schemas


def get_albums(pdb: Session, creator_id: Optional[str]):
    if creator_id is not None:
        return pdb.query(AlbumModel).filter(AlbumModel.creator_id == creator_id).all()
    else:
        return pdb.query(AlbumModel).all()


def get_album_by_id(pdb: Session, album_id: int) -> schemas.AlbumBase:
    try:
        album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
        album_schema = schemas.AlbumBase(**album.__dict__.copy(), songs=album.songs)

        return album_schema
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Album '{str(album_id)}' not found",
        ) from entry_not_found
