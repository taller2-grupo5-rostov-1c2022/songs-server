import json
from src.database import models
from fastapi import HTTPException, Depends, Form
from src.postgres import schemas
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import roles, utils
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
        utils.resource.retrieve_resource_creator_update
    ),
    artists_names: Optional[List[str]] = Depends(
        utils.artist.retrieve_artists_names_update
    ),
):
    return schemas.SongUpdate(
        artists_names=artists_names, **resource_creator_update.dict()
    )


def get_song(
    song_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    song = get_song_by_id(pdb, role, song_id)
    print(song)
    print(user)

    if song.sub_level > user.sub_level:
        raise HTTPException(
            status_code=403,
            detail=f"You are not allowed to see this song, expected at least level {song.sub_level}, you have level {user.sub_level}",
        )
    return song


def get_song_from_form(
    song_id: int = Form(...),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    return get_song(song_id=song_id, role=role, pdb=pdb, user=user)
