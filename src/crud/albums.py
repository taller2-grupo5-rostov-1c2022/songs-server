from sqlalchemy.orm import Session, joinedload
from src.postgres.models import AlbumModel, UserModel
from typing import Optional
from fastapi import HTTPException
from src.postgres import schemas


def get_albums(pdb: Session, creator_id: Optional[str]):
    if creator_id is not None:
        if pdb.query(UserModel).filter_by(id=creator_id).first() is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {creator_id} not found"
            )

        return pdb.query(AlbumModel).filter(AlbumModel.creator_id == creator_id).all()
    else:
        return pdb.query(AlbumModel).all()


def get_album_by_id(pdb: Session, album_id: int) -> schemas.AlbumBase:
    try:
        album = (
            pdb.query(AlbumModel)
            .options(joinedload(AlbumModel.songs))
            .filter(AlbumModel.id == album_id)
            .first()
        )
        album_schema = schemas.AlbumBase(**album.__dict__.copy())

        return album_schema
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Album '{str(album_id)}' not found",
        ) from entry_not_found
