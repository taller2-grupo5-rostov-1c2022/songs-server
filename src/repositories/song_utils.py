import json
from src.postgres import models
from fastapi import HTTPException, Depends, Form
from src.repositories import artist_utils, resource_utils
from src.postgres import schemas
from sqlalchemy import func
from .. import roles
from typing import List, Optional

from ..postgres.database import get_db
from ..roles import get_role


def create_song(pdb, song: schemas.SongBase):
    db_song = models.SongModel(**song.dict())
    pdb.add(db_song)
    pdb.commit()
    pdb.refresh(db_song)
    return db_song


def get_songs(
    pdb,
    role: roles.Role,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    name: str = None,
):
    queries = []
    if not role.can_see_blocked():
        queries.append(models.SongModel.blocked == False)

    if creator_id is not None:
        queries.append(models.SongModel.creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(models.ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(models.SongModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(models.SongModel.sub_level == sub_level)
    if name is not None:
        queries.append(func.lower(models.SongModel.name).contains(name.lower()))

    return (
        pdb.query(models.SongModel)
        .join(models.ArtistModel.songs)
        .filter(*queries)
        .all()
    )


def get_song_by_id(pdb, role: roles.Role, song_id: int):
    filters = [song_id == models.SongModel.id]
    if not role.can_see_blocked():
        filters.append(models.SongModel.blocked == False)

    song = (
        pdb.query(models.SongModel)
        .join(models.ArtistModel.songs)
        .filter(*filters)
        .first()
    )
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


def retrieve_songs_ids(songs_ids: Optional[str] = Form(None)):
    if songs_ids is None:
        return []
    try:
        songs_ids = json.loads(songs_ids)
        return songs_ids
    except ValueError:
        raise HTTPException(
            status_code=422, detail="Songs ids string is not well encoded"
        )


def retrieve_songs_ids_update(songs_ids: Optional[str] = Form(None)):
    if songs_ids is None:
        return []
    else:
        return retrieve_songs_ids(songs_ids=songs_ids)


def retrieve_song_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        resource_utils.retrieve_resource_creator_update
    ),
    artists_names: Optional[List[str]] = Depends(
        artist_utils.retrieve_artists_names_update
    ),
):
    return schemas.SongUpdate(
        artists_names=artists_names, **resource_creator_update.dict()
    )


def get_song(song_id: int, role: roles.Role = Depends(get_role), pdb=Depends(get_db)):
    return get_song_by_id(pdb, role, song_id)
