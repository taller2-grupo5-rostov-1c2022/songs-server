import json
from src.repositories import resource_utils, song_utils
from sqlalchemy.orm import joinedload
from src import roles
from src.postgres import models, schemas
from typing import Optional, List
from fastapi import HTTPException, Depends, Form
from sqlalchemy import or_


def get_playlists(pdb, role: roles.Role, colab_id: Optional[str]):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(models.SongModel).filter(models.SongModel.blocked == True).delete()
        queries.append(models.PlaylistModel.blocked == False)

    if colab_id is not None:
        queries.append(
            or_(
                models.PlaylistModel.creator_id == colab_id,
                models.UserModel.id == colab_id,
            )
        )

    playlists = (
        pdb.query(models.PlaylistModel)
        .join(models.UserModel.other_playlists, full=True)
        .filter(*queries)
        .all()
    )

    return playlists


def get_playlist_by_id(pdb, role: roles.Role, playlist_id: int):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(models.SongModel).filter(models.SongModel.blocked == True).delete()
        queries.append(models.PlaylistModel.blocked == False)

    playlist = (
        pdb.query(models.PlaylistModel)
        .options(joinedload(models.PlaylistModel.songs))
        .options(joinedload(models.PlaylistModel.colabs))
        .filter(models.PlaylistModel.id == playlist_id)
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


def get_songs_list(pdb, role: roles.Role, songs_ids: List[int]):
    songs = []
    for song_id in songs_ids:
        song = song_utils.get_song_by_id(pdb, role, song_id)
        songs.append(song)
    return songs


def get_colabs_list(pdb, colabs_ids: List[str]):
    colabs = []
    for colab_id in colabs_ids:
        colab = pdb.get(models.UserModel, colab_id)
        if colab is None:
            raise HTTPException(
                status_code=404, detail=f"User with id {colab_id} not found"
            )
        colabs.append(colab)
    return colabs


def retrieve_colabs_ids(colabs_ids: Optional[str] = Form(None)):
    if colabs_ids is None:
        return []
    else:
        try:
            colabs_ids = json.loads(colabs_ids)
        except ValueError as e:
            raise HTTPException(
                status_code=422, detail="Colabs string is not well encoded"
            ) from e
    return colabs_ids


def retrieve_colabs_ids_update(colabs_ids: Optional[str] = Form(None)):
    if colabs_ids is None:
        return None
    else:
        return retrieve_colabs_ids(colabs_ids=colabs_ids)


def retrieve_playlist(
    resource: schemas.ResourceBase = Depends(resource_utils.retrieve_resource),
    songs_ids: List[int] = Depends(song_utils.retrieve_songs_ids),
    colabs_ids: List[str] = Depends(retrieve_colabs_ids),
):
    return schemas.PlaylistPost(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource.dict()
    )


def retrieve_playlist_update(
    resource_update: schemas.ResourceUpdate = Depends(
        resource_utils.retrieve_resource_update
    ),
    songs_ids: Optional[List[int]] = Depends(song_utils.retrieve_songs_ids_update),
    colabs_ids: Optional[List[str]] = Depends(retrieve_colabs_ids),
):
    return schemas.PlaylistUpdate(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource_update.dict()
    )
