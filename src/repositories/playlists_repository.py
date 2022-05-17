from sqlalchemy.orm import Session, joinedload
from src import roles
from src.postgres.models import PlaylistModel, UserModel, SongModel
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import or_


def get_playlists(pdb: Session, role: roles.Role, colab_id: Optional[str]):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(PlaylistModel.blocked == False)

    if colab_id is not None:
        queries.append(
            or_(PlaylistModel.creator_id == colab_id, UserModel.id == colab_id)
        )

    playlists = (
        pdb.query(PlaylistModel)
        .join(UserModel.other_playlists, full=True)
        .filter(*queries)
        .all()
    )

    return playlists


def get_playlist_by_id(pdb: Session, role: roles.Role, playlist_id: int):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(PlaylistModel.blocked == False)

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
    if playlist.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail="Playlist is blocked")

    return playlist
