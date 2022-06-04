import json

from src.postgres.database import get_db
from src.postgres.models import song_playlist_association_table
from src.repositories import resource_utils, song_utils
from src import roles
from src.postgres import models, schemas
from typing import Optional, List
from fastapi import HTTPException, Depends, Form
from sqlalchemy import or_, and_
from sqlalchemy.orm import contains_eager

from src.roles import get_role


def get_playlists(pdb, role: roles.Role, colab_id: Optional[str]):
    queries = []
    join_conditions = []
    if not role.can_see_blocked():
        queries.append(models.PlaylistModel.blocked == False)
        join_conditions.append(models.SongModel.blocked == False)

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
        .join(models.SongModel, and_(True, *join_conditions), full=True)
        .filter(*queries)
        .all()
    )

    return playlists


def get_playlist_by_id(pdb, role: roles.Role, playlist_id: int):
    join_conditions = [models.SongModel.id == song_playlist_association_table.c.song_id]
    filters = [playlist_id == models.PlaylistModel.id]

    if not role.can_see_blocked():
        join_conditions.append(models.SongModel.blocked == False)
        filters.append(models.PlaylistModel.blocked == False)

    playlists = (
        pdb.query(models.PlaylistModel)
        .join(
            song_playlist_association_table,
            song_playlist_association_table.c.playlist_id == models.PlaylistModel.id,
            isouter=True,
        )
        .join(models.SongModel, and_(True, *join_conditions), isouter=True)
        .options(contains_eager("songs"))
        .filter(and_(True, *filters))
    ).all()

    if len(playlists) == 0:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlists[0]


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


def get_playlist(
    playlist_id: int, role: roles.Role = Depends(get_role), pdb=Depends(get_db)
):
    return get_playlist_by_id(pdb, role, playlist_id)
