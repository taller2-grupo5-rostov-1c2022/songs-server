from sqlalchemy.orm import Session, joinedload
from src.postgres.models import PlaylistModel, UserModel
from typing import Optional
from fastapi import HTTPException
from src.postgres import schemas


def get_playlists(pdb: Session, creator_id: Optional[str]):
    if creator_id is not None:
        if pdb.query(UserModel).filter_by(id=creator_id).first() is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {creator_id} not found"
            )

        return pdb.query(PlaylistModel).filter(PlaylistModel.creator_id == creator_id).all()
    else:
        return pdb.query(PlaylistModel).all()


def get_playlist_by_id(pdb: Session, playlist_id: int) -> schemas.PlaylistBase:
    try:
        playlist = (
            pdb.query(PlaylistModel)
            .options(joinedload(PlaylistModel.songs))
            .filter(PlaylistModel.id == playlist_id)
            .first()
        )
        playlist_schema = schemas.PlaylistBase(**playlist.__dict__.copy())

        return playlist_schema
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Playlist '{str(playlist_id)}' not found",
        ) from entry_not_found
