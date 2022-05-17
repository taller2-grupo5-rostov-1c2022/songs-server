from sqlalchemy.orm import Session, joinedload
from src import roles
from src.postgres.models import PlaylistModel, UserModel
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import or_


def get_playlists(pdb: Session, colab_id: Optional[str]):
    queries = []
    if colab_id is not None:
        queries.append(
            or_(PlaylistModel.creator_id == colab_id, UserModel.id == colab_id)
        )

    playlists = (
        pdb.query(PlaylistModel).join(UserModel.other_playlists).filter(*queries).all()
    )

    return playlists


def get_playlist_by_id(pdb: Session, playlist_id: int):
    playlist = (
        pdb.query(PlaylistModel)
        .options(joinedload(PlaylistModel.songs))
        .options(joinedload(PlaylistModel.colabs))
        .filter(PlaylistModel.id == playlist_id)
        .first()
    )
    if playlist is None:
        raise HTTPException(
            status_code=404,
            detail=f"Playlist '{playlist_id}' not found",
        )
    return playlist
